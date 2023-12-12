use decode::Decoder;
use pyo3::{
    exceptions::{PyIOError, PyValueError},
    prelude::*,
};
use pyo3_asyncio::tokio::future_into_py;

use std::{collections::BTreeMap, sync::Arc};

use anyhow::{Context, Result};
use from_arrow::FromArrow;

mod config;
mod decode;
mod from_arrow;
mod query;
mod types;

use config::Config;
use query::Query;
use types::{Block, Event, Log, Transaction};

#[pymodule]
fn hypersync(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<HypersyncClient>()?;
    m.add_class::<Decoder>()
}
#[pyclass(name = "hypersync_client")]
pub struct HypersyncClient {
    inner: Arc<skar_client::Client>,
}

#[pymethods]
impl HypersyncClient {
    /// Create a new client with given config
    #[new]
    fn new(
        url: String,
        bearer_token: Option<String>,
        http_req_timeout_millis: Option<i64>,
    ) -> PyResult<HypersyncClient> {
        let cfg = Config::new(url, bearer_token, http_req_timeout_millis);

        let cfg = cfg
            .try_convert()
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

        let client =
            skar_client::Client::new(cfg).map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

        Ok(HypersyncClient {
            inner: Arc::new(client),
        })
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
    /// If the query can't be finished in a single request, this function will
    ///  keep on making requests using the pagination mechanism (next_block) until
    ///  it reaches the end. It will stream data into the parquet file as it comes from
    ///. the server.
    ///
    /// Path should point to a folder that will contain the parquet files in the end.
    pub fn create_parquet_folder<'py>(
        &'py self,
        query: Query,
        path: String,
        py: Python<'py>,
    ) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let query = query
                .try_convert()
                .map_err(|_e| PyValueError::new_err("parsing query"))?;

            inner
                .create_parquet_folder(query, path)
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

    /// Send a event query request to the source hypersync instance.
    ///
    /// This executes the same query as send_req function on the source side but
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
}

#[pyclass]
#[pyo3(get_all)]
#[derive(Clone)]
pub struct QueryResponseData {
    pub blocks: Vec<Block>,
    pub transactions: Vec<Transaction>,
    pub logs: Vec<Log>,
}

#[pyclass]
#[pyo3(get_all)]
#[derive(Clone)]
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

const BLOCK_JOIN_FIELDS: &[&str] = &["number"];
const TX_JOIN_FIELDS: &[&str] = &["block_number", "transaction_index"];
const LOG_JOIN_FIELDS: &[&str] = &["log_index", "transaction_index", "block_number"];

#[pyclass]
#[pyo3(get_all)]
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
