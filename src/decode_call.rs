use anyhow::{Context};
use hypersync_client::format::{Data, Hex};
use pyo3::{exceptions::PyValueError, pyclass, pymethods, PyAny, PyResult, Python};
use pyo3_asyncio::tokio::future_into_py;
use std::sync::Arc;

use crate::types::{DecodedSolValue};

#[pyclass]
#[derive(Clone)]
pub struct Decoder {
    inner: Arc<hypersync_client::CallDecoder>,
}

#[pymethods]
impl Decoder {
    #[new]
    pub fn from_signatures(signatures: Vec<String>) -> PyResult<Self> {
        let inner = hypersync_client::CallDecoder::from_signatures(&signatures)
            .context("build inner decoder")
            .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

        Ok(Self {
            inner: Arc::new(inner),
        })
    }

    pub fn decode_input<'py>(&self, input: String, py: Python<'py>) -> PyResult<&'py PyAny> {
        let decoder = self.clone();

        future_into_py(py, async move {
            Ok(tokio::task::spawn_blocking(move || {
                Python::with_gil(|py| decoder.decode_input_sync(input.as_str(), py))
            })
            .await
            .unwrap())
        })
    }

    pub fn decode_input_sync<'py>(&self, input: &str, py: Python<'py>) -> Option<Vec<DecodedSolValue>> {
        let input = Data::decode_hex(input).context("decode input").unwrap();

        match self.inner.decode_input(&input).context("decode log").unwrap() {
            Some(v) => Some(v.into_iter().map(|value| DecodedSolValue::new(py, value, false)).collect()),
            None => None,
        }
    }
}
