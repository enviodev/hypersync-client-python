use decode::Decoder;
use pyo3::ffi::Py_uintptr_t;
use pyo3::{
    exceptions::{PyIOError, PyValueError},
    prelude::*,
};
use pyo3_asyncio::tokio::future_into_py;

use std::{collections::BTreeMap, sync::Arc};

use anyhow::{Context, Result};
use arrow2::array::StructArray;
use arrow2::datatypes::{DataType, Field};
use arrow2::ffi;
use skar_client::ArrowBatch;

use from_arrow::FromArrow;

mod config;
mod decode;
mod from_arrow;
mod query;
mod types;

use config::{Config, ParquetConfig};
use query::Query;
use types::{Block, Event, Log, Transaction};

#[pymodule]
fn hypersync(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<HypersyncClient>()?;
    m.add_class::<Decoder>()
}
#[pyclass]
pub struct HypersyncClient {
    inner: Arc<skar_client::Client>,
}

impl HypersyncClient {
    fn new_impl(config: Config) -> Result<HypersyncClient> {
        env_logger::try_init().ok();

        let config = config.try_convert().context("parse config")?;

        Ok(HypersyncClient {
            inner: Arc::new(skar_client::Client::new(config).context("create client")?),
        })
    }
}

#[pymethods]
impl HypersyncClient {
    /// Create a new client with given config
    #[new]
    fn new(config: Config) -> PyResult<HypersyncClient> {
        Self::new_impl(config).map_err(|e| PyIOError::new_err(format!("{:?}", e)))
    }

    /// Get the height of the source hypersync instance
    pub fn get_height<'py>(&'py self, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);
        future_into_py::<_, u64>(py, async move {
            let height: u64 = inner
                .get_height()
                .await
                .map_err(|e| PyIOError::new_err(format!("{:?}", e)))?;

            Ok(height)
        })
    }

    /// Create a parquet file by executing a query.
    ///
    /// Path should point to a folder that will contain the parquet files in the end.
    pub fn create_parquet_folder<'py>(
        &'py self,
        query: Query,
        config: ParquetConfig,
        py: Python<'py>,
    ) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let query = query
                .try_convert()
                .map_err(|_e| PyValueError::new_err("parsing query"))?;

            let config = config
                .try_convert()
                .map_err(|e| PyValueError::new_err(format!("parsing config: {:?}", e)))?;

            inner
                .create_parquet_folder(query, config)
                .await
                .map_err(|e| PyIOError::new_err(format!("{:?}", e)))?;

            Ok(())
        })
    }

    /// Send a query request to the source hypersync instance.
    ///
    /// Returns a query response which contains block, tx and log data.
    pub fn send_req<'py>(&'py self, query: Query, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py::<_, QueryResponse>(py, async move {
            let query = query
                .try_convert()
                .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

            let res = inner
                .send::<skar_client::ArrowIpc>(&query)
                .await
                .map_err(|e| PyIOError::new_err(format!("{:?}", e)))?;

            let res = convert_response_to_query_response(res)
                .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

            Ok(res)
        })
    }

    /// Send a query request to the source hypersync instance.
    ///
    /// Returns a query response which contains block, tx and log data in pyarrow table.
    pub fn send_req_arrow<'py>(&'py self, query: Query, py: Python<'py>) -> PyResult<&'py PyAny> {
        // initialize an array
        let inner = Arc::clone(&self.inner);

        future_into_py::<_, QueryResponseArrow>(py, async move {
            let query = query
                .try_convert()
                .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

            let res = inner
                .send::<skar_client::ArrowIpc>(&query)
                .await
                .map_err(|e| PyIOError::new_err(format!("{:?}", e)))?;

            let blocks = res.data.blocks;
            let transactions = res.data.transactions;
            let logs = res.data.logs;

            let (blocks, transactions, logs) = Python::with_gil(|py| {
                let pyarrow = py.import("pyarrow")?;
                let blocks = convert_batch_to_pyarrow_table(py, pyarrow, blocks)?;
                let transactions = convert_batch_to_pyarrow_table(py, pyarrow, transactions)?;
                let logs = convert_batch_to_pyarrow_table(py, pyarrow, logs)?;
                Ok::<(PyObject, PyObject, PyObject), PyErr>((blocks, transactions, logs))
            })?;

            let query_response = compose_pyarrow_response(
                res.archive_height,
                res.next_block,
                res.total_execution_time,
                blocks,
                transactions,
                logs,
            )
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

            Ok(query_response)
        })
    }

    /// Send a event query request to the source hypersync instance.
    ///
    /// This executes the same query as send_events_req function on the source side but
    /// it groups data for each event(log) so it is easier to process it.
    pub fn send_events_req<'py>(&'py self, query: Query, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py::<_, Events>(py, async move {
            let mut query = query
                .try_convert()
                .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

            if !query.field_selection.block.is_empty() {
                for field in BLOCK_JOIN_FIELDS.iter() {
                    query.field_selection.block.insert(field.to_string());
                }
            }

            if !query.field_selection.transaction.is_empty() {
                for field in TX_JOIN_FIELDS.iter() {
                    query.field_selection.transaction.insert(field.to_string());
                }
            }

            if !query.field_selection.log.is_empty() {
                for field in LOG_JOIN_FIELDS.iter() {
                    query.field_selection.log.insert(field.to_string());
                }
            }

            let res = inner
                .send::<skar_client::ArrowIpc>(&query)
                .await
                .map_err(|e| PyIOError::new_err(format!("{:?}", e)))?;

            let res = convert_response_to_events(res)
                .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

            Ok(res)
        })
    }

    /// Returns a query for all Blocks and Transactions within the block range (from_block, to_block]
    /// If to_block is None then query runs to the head of the chain.
    pub fn preset_query_blocks_and_transactions<'py>(
        &'py self,
        py: Python<'py>,
        from_block: u64,
        to_block: Option<u64>,
    ) -> PyResult<PyObject> {
        let query: Query =
            skar_client::Client::preset_query_blocks_and_transactions(from_block, to_block)
                .try_into()
                .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;
        Ok(query.into_py(py))
    }

    /// Returns a query object for all Blocks and hashes of the Transactions within the block range
    /// (from_block, to_block].  Also returns the block_hash and block_number fields on each Transaction
    /// so it can be mapped to a block.  If to_block is None then query runs to the head of the chain.
    pub fn preset_query_blocks_and_transaction_hashes<'py>(
        &'py self,
        py: Python<'py>,
        from_block: u64,
        to_block: Option<u64>,
    ) -> PyResult<PyObject> {
        let query: Query =
            skar_client::Client::preset_query_blocks_and_transaction_hashes(from_block, to_block)
                .try_into()
                .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;
        Ok(query.into_py(py))
    }

    /// Returns a query object for all Logs within the block range from the given address.
    /// If to_block is None then query runs to the head of the chain.
    pub fn preset_query_logs<'py>(
        &'py self,
        py: Python<'py>,
        contract_address: &str,
        from_block: u64,
        to_block: Option<u64>,
    ) -> PyResult<PyObject> {
        // cut the "0x" off the address
        let address: &str = if &contract_address[..2] == "0x" {
            &contract_address[2..]
        } else {
            contract_address
        };
        let address = hex_str_address_to_byte_array(address)
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;
        let query: Query = skar_client::Client::preset_query_logs(from_block, to_block, address)
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?
            .try_into()
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;
        Ok(query.into_py(py))
    }

    /// Returns a query for all Logs within the block range from the given address with a
    /// matching topic0 event signature.  Topic0 is the keccak256 hash of the event signature.
    /// If to_block is None then query runs to the head of the chain.
    pub fn preset_query_logs_of_event<'py>(
        &'py self,
        py: Python<'py>,
        contract_address: &str,
        topic0: &str,
        from_block: u64,
        to_block: Option<u64>,
    ) -> PyResult<PyObject> {
        // cut the "0x" off the address
        let address: &str = if &contract_address[..2] == "0x" {
            &contract_address[2..]
        } else {
            contract_address
        };
        let address = hex_str_address_to_byte_array(address)
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

        // cut the "0x" off the topic0
        let topic0: &str = if &topic0[..2] == "0x" {
            &topic0[2..]
        } else {
            topic0
        };
        let topic0 = hex_str_topic0_to_byte_array(topic0)
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

        let query: Query =
            skar_client::Client::preset_query_logs_of_event(from_block, to_block, topic0, address)
                .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?
                .try_into()
                .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;
        Ok(query.into_py(py))
    }
}

// helper function to decode hex string as address
fn hex_str_address_to_byte_array(hex_str: &str) -> Result<[u8; 20], String> {
    match hex::decode(hex_str) {
        Ok(bytes) if bytes.len() == 20 => {
            let mut array = [0u8; 20];
            array.copy_from_slice(&bytes);
            Ok(array)
        }
        Ok(_) => Err("Decoded hex does not fit into a 20-byte array.".into()),
        Err(e) => Err(format!("Failed to decode hex string: {}", e)),
    }
}

// helper function to decode hex string as topic0
fn hex_str_topic0_to_byte_array(hex_str: &str) -> Result<[u8; 32], String> {
    match hex::decode(hex_str) {
        Ok(bytes) if bytes.len() == 32 => {
            let mut array = [0u8; 32];
            array.copy_from_slice(&bytes);
            Ok(array)
        }
        Ok(_) => Err("Decoded hex does not fit into a 32-byte array.".into()),
        Err(e) => Err(format!("Failed to decode hex string: {}", e)),
    }
}

#[pyclass]
#[pyo3(get_all)]
#[derive(Clone, Debug)]
pub struct QueryResponseData {
    pub blocks: Vec<Block>,
    pub transactions: Vec<Transaction>,
    pub logs: Vec<Log>,
}

#[pymethods]
impl QueryResponseData {
    fn __bool__(&self) -> bool {
        !self.blocks.is_empty() || !self.transactions.is_empty() || !self.logs.is_empty()
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }
}

#[pyclass]
#[pyo3(get_all)]
#[derive(Clone, Debug)]
pub struct QueryArrowResponse {
    pub blocks: PyObject,
    pub transactions: PyObject,
    pub logs: PyObject,
}

#[pymethods]
impl QueryArrowResponse {
    /// TODO: if we want to implement this method we could call _is_initialized method,
    /// but we will need py reference
    fn __bool__(&self) -> bool {
        true
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }
}

#[pyclass]
#[pyo3(get_all)]
#[derive(Clone, Debug)]
pub struct QueryResponse {
    /// Current height of the source hypersync instance
    pub archive_height: Option<i64>,
    /// Next block to query for, the responses are paginated so,
    ///  the caller should continue the query from this block if they
    ///  didn't get responses up to the to_block they specified in the Query.
    pub next_block: i64,
    /// Total time it took the hypersync instance to execute the query.
    pub total_execution_time: i64,
    /// Response data
    pub data: QueryResponseData,
}

#[pymethods]
impl QueryResponse {
    fn __bool__(&self) -> bool {
        self.archive_height.is_some()
            || self.next_block != i64::default()
            || self.total_execution_time != i64::default()
            || self.data.__bool__()
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }
}

#[pyclass]
#[pyo3(get_all)]
#[derive(Clone, Debug)]
pub struct QueryResponseArrow {
    /// Current height of the source hypersync instance
    pub archive_height: Option<i64>,
    /// Next block to query for, the responses are paginated so,
    ///  the caller should continue the query from this block if they
    ///  didn't get responses up to the to_block they specified in the Query.
    pub next_block: i64,
    /// Total time it took the hypersync instance to execute the query.
    pub total_execution_time: i64,
    /// Response data in pyarrow format
    pub data: QueryArrowResponse,
}

#[pymethods]
impl QueryResponseArrow {
    fn __bool__(&self) -> bool {
        self.archive_height.is_some()
            || self.next_block != i64::default()
            || self.total_execution_time != i64::default()
            || self.data.__bool__()
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }
}

const BLOCK_JOIN_FIELDS: &[&str] = &["number"];
const TX_JOIN_FIELDS: &[&str] = &["block_number", "transaction_index"];
const LOG_JOIN_FIELDS: &[&str] = &["log_index", "transaction_index", "block_number"];

#[pyclass]
#[pyo3(get_all)]
#[derive(Debug)]
pub struct Events {
    /// Current height of the source hypersync instance
    pub archive_height: Option<i64>,
    /// Next block to query for, the responses are paginated so,
    ///  the caller should continue the query from this block if they
    ///  didn't get responses up to the to_block they specified in the Query.
    pub next_block: i64,
    /// Total time it took the hypersync instance to execute the query.
    pub total_execution_time: i64,
    /// Response data
    pub events: Vec<Event>,
}

#[pymethods]
impl Events {
    fn __bool__(&self) -> bool {
        self.archive_height.is_some()
            || self.next_block != i64::default()
            || self.total_execution_time != i64::default()
            || !self.events.is_empty()
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }
}

fn convert_response_to_events(res: skar_client::QueryResponse) -> Result<Events> {
    let mut blocks = BTreeMap::new();

    for batch in res.data.blocks.iter() {
        let data = Block::from_arrow(batch).context("map blocks from arrow")?;

        for block in data {
            blocks.insert(block.number, block);
        }
    }

    let mut txs = BTreeMap::new();

    for batch in res.data.transactions.iter() {
        let data = Transaction::from_arrow(batch).context("map transactions from arrow")?;

        for tx in data {
            txs.insert((tx.block_number, tx.transaction_index), tx);
        }
    }

    let logs = res
        .data
        .logs
        .iter()
        .map(Log::from_arrow)
        .collect::<Result<Vec<_>>>()
        .context("map logs from arrow")?
        .concat();

    let mut events = Vec::with_capacity(logs.len());

    for log in logs.into_iter() {
        let transaction = txs.get(&(log.block_number, log.transaction_index)).cloned();
        let block = blocks.get(&log.block_number).cloned();

        events.push(Event {
            log,
            block,
            transaction,
        })
    }

    Ok(Events {
        archive_height: res.archive_height.map(|h| h.try_into().unwrap()),
        next_block: res.next_block.try_into().unwrap(),
        total_execution_time: res.total_execution_time.try_into().unwrap(),
        events,
    })
}

fn convert_response_to_query_response(res: skar_client::QueryResponse) -> Result<QueryResponse> {
    let blocks = res
        .data
        .blocks
        .iter()
        .map(Block::from_arrow)
        .collect::<Result<Vec<_>>>()
        .context("map blocks from arrow")?
        .concat();

    let transactions = res
        .data
        .transactions
        .iter()
        .map(Transaction::from_arrow)
        .collect::<Result<Vec<_>>>()
        .context("map transactions from arrow")?
        .concat();

    let logs = res
        .data
        .logs
        .iter()
        .map(Log::from_arrow)
        .collect::<Result<Vec<_>>>()
        .context("map logs from arrow")?
        .concat();

    Ok(QueryResponse {
        archive_height: res
            .archive_height
            .map(|h| h.try_into())
            .transpose()
            .context("convert height")?,
        next_block: res.next_block.try_into().context("convert next_block")?,
        total_execution_time: res
            .total_execution_time
            .try_into()
            .context("convert total_execution_time")?,
        data: QueryResponseData {
            blocks,
            transactions,
            logs,
        },
    })
}

/// Construct response and centralize error mapping for calling function.
fn compose_pyarrow_response(
    archive_height: Option<u64>,
    next_block: u64,
    total_execution_time: u64,
    blocks: PyObject,
    transactions: PyObject,
    logs: PyObject,
) -> Result<QueryResponseArrow> {
    Ok(QueryResponseArrow {
        archive_height: archive_height
            .map(|h| h.try_into())
            .transpose()
            .context("convert height")?,
        next_block: next_block.try_into().context("convert next_block")?,
        total_execution_time: total_execution_time
            .try_into()
            .context("convert total_execution_time")?,
        data: QueryArrowResponse {
            blocks,
            transactions,
            logs,
        },
    })
}

/// Uses RecordBatchReader to convert vector of ArrayBatch to reader by c-interface
/// and then crates table from this reader with method from_batches
fn convert_batch_to_pyarrow_table<'py>(
    py: Python<'py>,
    pyarrow: &'py PyModule,
    batches: Vec<ArrowBatch>,
) -> PyResult<PyObject> {
    if batches.is_empty() {
        return Ok(py.None());
    }

    let schema = batches.first().unwrap().schema.fields.clone();
    let field = Field::new("a", DataType::Struct(schema), true);

    let mut data = vec![];
    for batch in batches {
        data.push(
            StructArray::new(field.data_type.clone(), batch.chunk.arrays().to_vec(), None).boxed(),
        );
    }

    let iter = Box::new(data.into_iter().map(Ok)) as _;
    let stream = Box::new(ffi::export_iterator(iter, field));
    let py_stream = pyarrow.getattr("RecordBatchReader")?.call_method1(
        "_import_from_c",
        ((&*stream as *const ffi::ArrowArrayStream) as Py_uintptr_t,),
    )?;
    let table = pyarrow
        .getattr("Table")?
        .call_method1("from_batches", (py_stream,))?;

    Ok(table.to_object(py))
}
