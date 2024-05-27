use std::sync::Arc;

use anyhow::{Context, Result};
use hypersync_client::format::{Data, Hex, LogArgument};
use pyo3::{exceptions::PyValueError, pyclass, pymethods, PyAny, PyResult, Python};
use pyo3_asyncio::tokio::future_into_py;

use crate::types::{DecodedEvent, DecodedSolValue, Event, Log};

#[pyclass]
#[derive(Clone)]
pub struct Decoder {
    inner: Arc<hypersync_client::Decoder>,
    checksummed_addresses: bool,
}

#[pymethods]
impl Decoder {
    #[new]
    pub fn from_signatures(signatures: Vec<String>) -> PyResult<Self> {
        let inner = hypersync_client::Decoder::from_signatures(&signatures)
            .context("build inner decoder")
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

        Ok(Self {
            inner: Arc::new(inner),
            checksummed_addresses: false,
        })
    }

    pub fn enable_checksummed_addresses(&mut self) {
        self.checksummed_addresses = true;
    }

    pub fn disable_checksummed_addresses(&mut self) {
        self.checksummed_addresses = false;
    }

    pub fn decode_logs<'py>(&self, logs: Vec<Log>, py: Python<'py>) -> PyResult<&'py PyAny> {
        let decoder = self.clone();

        future_into_py(py, async move {
            Ok(tokio::task::spawn_blocking(move || {
                Python::with_gil(|py| decoder.decode_logs_sync(logs, py))
            })
            .await
            .unwrap())
        })
    }

    pub fn decode_logs_sync(&self, logs: Vec<Log>, py: Python) -> Vec<Option<DecodedEvent>> {
        logs.iter()
            .flat_map(|log| self.decode_impl(log, py).ok())
            .collect::<Vec<_>>()
    }

    pub fn decode_events<'py>(&self, events: Vec<Event>, py: Python<'py>) -> PyResult<&'py PyAny> {
        let decoder = self.clone();

        future_into_py(py, async move {
            Ok(tokio::task::spawn_blocking(move || {
                Python::with_gil(|py| decoder.decode_events_sync(events, py))
            })
            .await
            .unwrap())
        })
    }

    pub fn decode_events_sync(&self, events: Vec<Event>, py: Python) -> Vec<Option<DecodedEvent>> {
        events
            .iter()
            .flat_map(|event| self.decode_impl(&event.log, py).ok())
            .collect::<Vec<_>>()
    }
}

impl Decoder {
    fn decode_impl(&self, log: &Log, py: Python) -> Result<Option<DecodedEvent>> {
        let topics = log
            .topics
            .iter()
            .map(|v| {
                v.as_ref()
                    .map(|v| LogArgument::decode_hex(v).context("decode topic"))
                    .transpose()
            })
            .collect::<Result<Vec<_>>>()
            .context("decode topics")?;

        let topic0 = topics
            .first()
            .context("get topic0")?
            .as_ref()
            .context("topic0 is null")?;

        let data = log.data.as_ref().context("get log.data")?;
        let data = Data::decode_hex(data).context("decode data")?;

        let decoded = match self
            .inner
            .decode(topic0.as_slice(), &topics, &data)
            .context("decode log")?
        {
            Some(v) => v,
            None => return Ok(None),
        };

        Ok(Some(DecodedEvent {
            indexed: decoded
                .indexed
                .into_iter()
                .map(|v| DecodedSolValue::new(py, v, self.checksummed_addresses))
                .collect(),
            body: decoded
                .body
                .into_iter()
                .map(|v| DecodedSolValue::new(py, v, self.checksummed_addresses))
                .collect(),
        }))
    }
}
