use std::collections::HashMap;
use std::sync::Arc;

use alloy_json_abi::JsonAbi;
use anyhow::{anyhow, Context, Result};
use pyo3::{exceptions::PyValueError, pyclass, pymethods, PyAny, PyResult, Python};
use pyo3_asyncio::tokio::future_into_py;
use skar_format::{Address, Hex, LogArgument};

use crate::types::{DecodedEvent, DecodedSolValue, Event, Log};

#[pyclass]
#[derive(Clone)]
pub struct Decoder {
    inner: Arc<skar_client::Decoder>,
}

#[pymethods]
impl Decoder {
    #[new]
    // #[napi(ts_return_type = "Decoder")]
    pub fn new(json_abis: HashMap<String, serde_json::Value>) -> PyResult<Self> {
        let json_abis = json_abis
            .into_iter()
            .map(|(addr, abi)| {
                let json = serde_json::to_string(&abi).context("serialize json")?;
                let abi: JsonAbi = serde_json::from_str(&json).context("parse json abi")?;
                let addr = Address::decode_hex(&addr).context("decode hex address")?;
                Ok((addr, abi))
            })
            .collect::<Result<Vec<_>>>()
            .context("parse json abi list")
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

        let inner = skar_client::Decoder::new(&json_abis)
            .context("build inner decoder")
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

        Ok(Self {
            inner: Arc::new(inner),
        })
    }

    // returns python awaitable for PyResult<Vec<Option<DecodedEvent>>>
    pub fn decode_logs<'py>(&'py self, logs: Vec<Log>, py: Python<'py>) -> PyResult<&'py PyAny> {
        let decoder = self.clone();

        future_into_py::<_, Vec<Option<DecodedEvent>>>(py, async move {
            decoder.decode_logs_sync(logs)?
        })
    }

    // returns Result<Vec<Option<DecodedEvent>>>
    pub fn decode_logs_sync(&self, logs: Vec<Log>) -> PyResult<Vec<Option<PyAny>>> {
        logs.iter()
            .map(|log| self.decode_impl(log))
            .collect::<Result<Vec<_>>>()
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))
    }

    // returns python awaitable for PyResult<Vec<Option<DecodedEvent>>>
    pub fn decode_events<'py>(
        &'py self,
        events: Vec<Event>,
        py: Python<'py>,
    ) -> PyResult<&'py PyAny> {
        let decoder = self.clone();

        future_into_py::<_, Vec<Option<DecodedEvent>>>(py, async move {
            decoder.decode_events_sync(events)?
        })
    }

    // returns Result<Vec<Option<DecodedEvent>>>
    pub fn decode_events_sync(&self, events: Vec<Event>) -> PyResult<Vec<Option<PyAny>>> {
        events
            .iter()
            .map(|event| self.decode_impl(&event.log))
            .collect::<Result<Vec<_>>>()
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))
    }

    // returns Result<Option<DecodedEvent>>
    fn decode_impl(&self, log: &Log) -> Result<Option<PyAny>> {
        let address = log.address.as_ref().context("get address")?;
        let address = Address::decode_hex(address).context("decode address")?;

        let mut topics = Vec::new();

        for topic in log.topics.iter() {
            match topic {
                Some(topic) => {
                    let topic = LogArgument::decode_hex(topic).context("decode topic")?;
                    topics.push(Some(topic));
                }
                None => topics.push(None),
            }
        }

        let topics = topics
            .iter()
            .map(|t| t.as_ref().map(|t| t.as_slice()))
            .collect::<Vec<Option<&[u8]>>>();

        let topic0 = topics.get(0).context("get topic0")?.context("get topic0")?;

        let data = log.data.as_ref().context("get data field")?;
        let data: Vec<u8> =
            prefix_hex::decode(data).map_err(|e| anyhow!("decode data field: {}", e))?;

        let decoded = match self
            .inner
            .decode(address.as_slice(), topic0, &topics, &data)
            .context("decode log")?
        {
            Some(decoded) => decoded,
            None => return Ok(None),
        };

        Ok(Some(DecodedEvent {
            indexed: decoded
                .indexed
                .into_iter()
                .map(DecodedSolValue::new)
                .collect(),
            body: decoded.body.into_iter().map(DecodedSolValue::new).collect(),
        }))
    }
}
