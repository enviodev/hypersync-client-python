use crate::types::{DecodedSolValue, Trace, Transaction};
use anyhow::Context;
use hypersync_client::format::{Data, Hex};
use pyo3::{exceptions::PyValueError, pyclass, pymethods, PyAny, PyResult, Python};
use pyo3_asyncio::tokio::future_into_py;
use std::sync::Arc;

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

    pub fn decode_inputs<'py>(&self, input: Vec<String>, py: Python<'py>) -> PyResult<&'py PyAny> {
        let decoder = self.clone();

        future_into_py(py, async move {
            Ok(tokio::task::spawn_blocking(move || {
                Python::with_gil(|py| decoder.decode_inputs_sync(input, py))
            })
            .await
            .unwrap())
        })
    }

    pub fn decode_transactions_input<'py>(
        &self,
        txs: Vec<Transaction>,
        py: Python<'py>,
    ) -> PyResult<&'py PyAny> {
        let decoder = self.clone();

        future_into_py(py, async move {
            Ok(tokio::task::spawn_blocking(move || {
                Python::with_gil(|py| decoder.decode_transactions_input_sync(txs, py))
            })
            .await
            .unwrap())
        })
    }

    pub fn decode_traces_input<'py>(
        &self,
        traces: Vec<Trace>,
        py: Python<'py>,
    ) -> PyResult<&'py PyAny> {
        let decoder = self.clone();

        future_into_py(py, async move {
            Ok(tokio::task::spawn_blocking(move || {
                Python::with_gil(|py| decoder.decode_traces_input_sync(traces, py))
            })
            .await
            .unwrap())
        })
    }

    pub fn decode_inputs_sync(
        &self,
        inputs: Vec<String>,
        py: Python,
    ) -> Vec<Option<Vec<DecodedSolValue>>> {
        inputs
            .into_iter()
            .map(|input| self.decode_impl(input.as_str(), py))
            .collect()
    }

    pub fn decode_transactions_input_sync(
        &self,
        txs: Vec<Transaction>,
        py: Python,
    ) -> Vec<Option<Vec<DecodedSolValue>>> {
        txs.into_iter()
            .map(|tx| self.decode_impl(tx.input?.as_str(), py))
            .collect()
    }

    pub fn decode_traces_input_sync(
        &self,
        traces: Vec<Trace>,
        py: Python,
    ) -> Vec<Option<Vec<DecodedSolValue>>> {
        traces
            .into_iter()
            .map(|trace| self.decode_impl(trace.input?.as_str(), py))
            .collect()
    }

    pub fn decode_impl(&self, input: &str, py: Python) -> Option<Vec<DecodedSolValue>> {
        let input = Data::decode_hex(input).context("decode input").unwrap();
        let decoded_input = self
            .inner
            .decode_input(&input)
            .context("decode log")
            .unwrap();
        decoded_input.map(|decoded_input| {
            decoded_input
                .into_iter()
                .map(|value| DecodedSolValue::new(py, value, self.checksummed_addresses))
                .collect()
        })
    }
}
