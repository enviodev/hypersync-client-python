use anyhow::{Context, Result};
use mimalloc::MiMalloc;
use pyo3::prelude::*;
use pyo3_asyncio::tokio::future_into_py;

#[global_allocator]
static GLOBAL: MiMalloc = MiMalloc;

use std::sync::Arc;

mod arrow_ffi;
mod config;
mod decode;
mod decode_call;
mod query;
mod response;
mod types;

use arrow_ffi::response_to_pyarrow;
use config::{ClientConfig, StreamConfig};
use decode::Decoder;
use decode_call::CallDecoder;
use query::Query;
use response::{
    convert_event_response, convert_response, ArrowStream, EventStream, QueryResponseStream,
};

#[pymodule]
fn hypersync(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<HypersyncClient>()?;
    m.add_class::<Decoder>()?;
    m.add_class::<CallDecoder>()?;
    m.add_class::<ArrowStream>()?;
    m.add_class::<EventStream>()?;
    m.add_class::<QueryResponseStream>()?;
    m.add_function(wrap_pyfunction!(decode::signature_to_topic0, m)?)?;

    Ok(())
}

#[pyclass]
pub struct HypersyncClient {
    inner: Arc<hypersync_client::Client>,
}

#[pymethods]
impl HypersyncClient {
    /// Create a new client with given config
    #[new]
    fn new(config: ClientConfig) -> Result<HypersyncClient> {
        env_logger::try_init().ok();

        let config = config.try_convert().context("parse config")?;

        Ok(HypersyncClient {
            inner: Arc::new(hypersync_client::Client::new(config).context("create client")?),
        })
    }

    /// Get the height of the source hypersync instance
    pub fn get_height<'py>(&'py self, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);
        future_into_py::<_, u64>(py, async move {
            let height: u64 = inner.get_height().await?;

            Ok(height)
        })
    }

    /// Get the chain_id of the source hypersync instance
    pub fn get_chain_id<'py>(&'py self, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);
        future_into_py::<_, u64>(py, async move {
            let chain_id: u64 = inner.get_chain_id().await?;

            Ok(chain_id)
        })
    }

    pub fn collect<'py>(
        &'py self,
        query: Query,
        config: StreamConfig,
        py: Python<'py>,
    ) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let query = query.try_convert().context("parse query")?;
            let config = config.try_convert().context("parse config")?;

            let res = inner
                .collect(query, config)
                .await
                .context("collect arrow")?;

            let res = convert_response(res).context("convert response to pyarrow")?;

            Ok(res)
        })
    }

    pub fn collect_events<'py>(
        &'py self,
        query: Query,
        config: StreamConfig,
        py: Python<'py>,
    ) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let query = query.try_convert().context("parse query")?;
            let config = config.try_convert().context("parse config")?;

            let res = inner
                .collect_events(query, config)
                .await
                .context("collect arrow")?;

            let res = convert_event_response(res).context("convert response to pyarrow")?;

            Ok(res)
        })
    }

    pub fn collect_arrow<'py>(
        &'py self,
        query: Query,
        config: StreamConfig,
        py: Python<'py>,
    ) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let query = query.try_convert().context("parse query")?;
            let config = config.try_convert().context("parse config")?;

            let res = inner
                .collect_arrow(query, config)
                .await
                .context("collect arrow")?;

            let res = response_to_pyarrow(res).context("convert response to pyarrow")?;

            Ok(res)
        })
    }

    pub fn collect_parquet<'py>(
        &'py self,
        path: String,
        query: Query,
        config: StreamConfig,
        py: Python<'py>,
    ) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let query = query.try_convert().context("parse query")?;
            let config = config.try_convert().context("parse config")?;

            inner
                .collect_parquet(&path, query, config)
                .await
                .context("collect parquet")?;

            Ok(())
        })
    }

    pub fn get<'py>(&'py self, query: Query, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let query = query.try_convert().context("parse query")?;

            let res = inner.get(&query).await.context("get arrow")?;

            let res = convert_response(res).context("convert response to pyarrow")?;

            Ok(res)
        })
    }

    pub fn get_events<'py>(&'py self, query: Query, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let query = query.try_convert().context("parse query")?;

            let res = inner.get_events(query).await.context("get arrow")?;

            let res = convert_event_response(res).context("convert response to pyarrow")?;

            Ok(res)
        })
    }

    pub fn get_arrow<'py>(&'py self, query: Query, py: Python<'py>) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let query = query.try_convert().context("parse query")?;

            let res = inner.get_arrow(&query).await.context("get arrow")?;

            let res = response_to_pyarrow(res).context("convert response to pyarrow")?;

            Ok(res)
        })
    }

    pub fn stream<'py>(
        &'py self,
        query: Query,
        config: StreamConfig,
        py: Python<'py>,
    ) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let query = query.try_convert().context("parse query")?;
            let config = config.try_convert().context("parse config")?;

            let inner = inner
                .stream(query, config)
                .await
                .context("start inner stream")?;

            Ok(QueryResponseStream::new(inner))
        })
    }

    pub fn stream_events<'py>(
        &'py self,
        query: Query,
        config: StreamConfig,
        py: Python<'py>,
    ) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let query = query.try_convert().context("parse query")?;
            let config = config.try_convert().context("parse config")?;

            let inner = inner
                .stream_events(query, config)
                .await
                .context("start inner stream")?;

            Ok(EventStream::new(inner))
        })
    }

    pub fn stream_arrow<'py>(
        &'py self,
        query: Query,
        config: StreamConfig,
        py: Python<'py>,
    ) -> PyResult<&'py PyAny> {
        let inner = Arc::clone(&self.inner);

        future_into_py(py, async move {
            let query = query.try_convert().context("parse query")?;
            let config = config.try_convert().context("parse config")?;

            let inner = inner
                .stream_arrow(query, config)
                .await
                .context("start inner stream")?;

            Ok(ArrowStream::new(inner))
        })
    }
}
