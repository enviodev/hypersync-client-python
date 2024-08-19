use std::sync::Arc;

use anyhow::{Context, Result};
use pyo3::{pyclass, pymethods, PyAny, PyErr, PyObject, PyResult, Python};
use pyo3_asyncio::tokio::future_into_py;
use tokio::sync::mpsc;

use crate::{
    arrow_ffi::response_to_pyarrow,
    types::{Block, Event, Log, RollbackGuard, Trace, Transaction},
};

#[pyclass]
#[pyo3(get_all)]
#[derive(Clone)]
pub struct ArrowResponse {
    /// Current height of the source hypersync instance
    pub archive_height: Option<u64>,
    /// Next block to query for, the responses are paginated so,
    ///  the caller should continue the query from this block if they
    ///  didn't get responses up to the to_block they specified in the Query.
    pub next_block: u64,
    /// Total time it took the hypersync instance to execute the query.
    pub total_execution_time: u64,
    /// Response data
    pub data: ArrowResponseData,
    /// Rollback guard, supposed to be used to detect rollbacks
    pub rollback_guard: Option<RollbackGuard>,
}

#[pyclass]
#[pyo3(get_all)]
#[derive(Clone, Debug)]
pub struct ArrowResponseData {
    pub blocks: PyObject,
    pub transactions: PyObject,
    pub logs: PyObject,
    pub traces: PyObject,
    pub decoded_logs: PyObject,
}

#[pyclass]
pub struct QueryResponseStream {
    inner: Arc<tokio::sync::Mutex<mpsc::Receiver<Result<hypersync_client::QueryResponse>>>>,
}

impl QueryResponseStream {
    pub fn new(inner: mpsc::Receiver<Result<hypersync_client::QueryResponse>>) -> Self {
        Self {
            inner: Arc::new(tokio::sync::Mutex::new(inner)),
        }
    }
}

#[pymethods]
impl QueryResponseStream {
    pub fn close<'py>(&'py self, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            inner.lock().await.close();
            Ok::<_, PyErr>(())
        })
    }

    pub fn recv<'py>(&self, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let resp = inner.lock().await.recv().await;

            resp.map(|r| convert_response(r?).context("convert response"))
                .transpose()
                .map_err(Into::into)
        })
    }
}

type HSEventResponse =
    hypersync_client::QueryResponse<Vec<Vec<hypersync_client::simple_types::Event>>>;

#[pyclass]
pub struct EventStream {
    inner: Arc<tokio::sync::Mutex<mpsc::Receiver<Result<HSEventResponse>>>>,
}

impl EventStream {
    pub fn new(inner: mpsc::Receiver<Result<HSEventResponse>>) -> Self {
        Self {
            inner: Arc::new(tokio::sync::Mutex::new(inner)),
        }
    }
}

#[pymethods]
impl EventStream {
    pub fn close<'py>(&'py self, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            inner.lock().await.close();
            Ok::<_, PyErr>(())
        })
    }

    pub fn recv<'py>(&self, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let resp = inner.lock().await.recv().await;

            resp.map(|r| convert_event_response(r?).context("convert response"))
                .transpose()
                .map_err(Into::into)
        })
    }
}

#[pyclass]
pub struct ArrowStream {
    inner: Arc<tokio::sync::Mutex<mpsc::Receiver<Result<hypersync_client::ArrowResponse>>>>,
}

impl ArrowStream {
    pub fn new(inner: mpsc::Receiver<Result<hypersync_client::ArrowResponse>>) -> Self {
        Self {
            inner: Arc::new(tokio::sync::Mutex::new(inner)),
        }
    }
}

#[pymethods]
impl ArrowStream {
    pub fn close<'py>(&'py self, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            inner.lock().await.close();
            Ok::<_, PyErr>(())
        })
    }

    pub fn recv<'py>(&self, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let resp = inner.lock().await.recv().await;

            resp.map(|r| response_to_pyarrow(r?).context("convert response"))
                .transpose()
                .map_err(Into::into)
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
    pub traces: Vec<Trace>,
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
    /// Rollback guard, supposed to be used to detect rollbacks
    pub rollback_guard: Option<RollbackGuard>,
}

#[pyclass]
#[pyo3(get_all)]
#[derive(Clone)]
pub struct EventResponse {
    /// Current height of the source hypersync instance
    pub archive_height: Option<i64>,
    /// Next block to query for, the responses are paginated so,
    ///  the caller should continue the query from this block if they
    ///  didn't get responses up to the to_block they specified in the Query.
    pub next_block: i64,
    /// Total time it took the hypersync instance to execute the query.
    pub total_execution_time: i64,
    /// Response data
    pub data: Vec<Event>,
    /// Rollback guard, supposed to be used to detect rollbacks
    pub rollback_guard: Option<RollbackGuard>,
}

#[pyclass]
#[pyo3(get_all)]
#[derive(Clone)]
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
    /// Rollback guard, supposed to be used to detect rollbacks
    pub rollback_guard: Option<RollbackGuard>,
}

pub fn convert_response(res: hypersync_client::QueryResponse) -> Result<QueryResponse> {
    let blocks = res
        .data
        .blocks
        .iter()
        .flat_map(|b| b.iter().map(Block::from))
        .collect::<Vec<_>>();

    let transactions = res
        .data
        .transactions
        .iter()
        .flat_map(|b| b.iter().map(Transaction::from))
        .collect::<Vec<_>>();

    let logs = res
        .data
        .logs
        .iter()
        .flat_map(|b| b.iter().map(Log::from))
        .collect::<Vec<_>>();

    let traces = res
        .data
        .traces
        .iter()
        .flat_map(|b| b.iter().map(Trace::from))
        .collect::<Vec<_>>();

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
            traces,
        },
        rollback_guard: res
            .rollback_guard
            .map(RollbackGuard::try_convert)
            .transpose()
            .context("convert rollback guard")?,
    })
}

pub fn convert_event_response(
    resp: hypersync_client::QueryResponse<Vec<Vec<hypersync_client::simple_types::Event>>>,
) -> Result<EventResponse> {
    let mut data = Vec::new();

    for batch in resp.data {
        for event in batch {
            data.push(Event {
                transaction: event.transaction.map(|v| Transaction::from(&*v)),
                block: event.block.map(|v| Block::from(&*v)),
                log: Log::from(&event.log),
            });
        }
    }

    Ok(EventResponse {
        archive_height: resp.archive_height.map(|v| v.try_into().unwrap()),
        next_block: resp.next_block.try_into().unwrap(),
        total_execution_time: resp.total_execution_time.try_into().unwrap(),
        data,
        rollback_guard: resp
            .rollback_guard
            .map(|rg| RollbackGuard::try_convert(rg).context("convert rollback guard"))
            .transpose()?,
    })
}
