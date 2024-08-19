use anyhow::Context;
use hypersync_client::format::{Data, Hex};
use pyo3::{exceptions::PyValueError, pyclass, pymethods, PyAny, PyResult, Python};
use pyo3_asyncio::tokio::future_into_py;
use std::sync::Arc;

use crate::types::DecodedSolValue;

#[pyclass]
#[derive(Clone)]
pub struct CallDecoder {
    inner: Arc<hypersync_client::CallDecoder>,
    checksummed_addresses: bool,
}

#[pymethods]
impl CallDecoder {
    #[new]
    pub fn from_signatures(signatures: Vec<String>) -> PyResult<Self> {
        let inner = hypersync_client::CallDecoder::from_signatures(&signatures)
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

    pub fn decode_input_sync(&self, input: &str, py: Python) -> Option<Vec<DecodedSolValue>> {
        let input = Data::decode_hex(input).context("decode input").unwrap();

        self.inner
            .decode_input(&input)
            .context("decode log")
            .unwrap()
            .map(|v| {
                v.into_iter()
                    .map(|value| DecodedSolValue::new(py, value, self.checksummed_addresses))
                    .collect()
            })
    }
}
