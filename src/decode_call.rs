use crate::types::{DecodedSolValue, Trace, Transaction};
use anyhow::Context;
use hypersync_client::format::{Data, Hex};
use pyo3::{exceptions::PyValueError, pyclass, pymethods, Bound, PyAny, PyResult, Python};
use pyo3_async_runtimes::tokio::future_into_py;
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

    pub fn decode_inputs<'py>(
        &self,
        input: Vec<String>,
        py: Python<'py>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let decoder = self.clone();

        future_into_py(py, async move {
            let result = tokio::task::spawn_blocking(move || {
                Python::attach(|py| decoder.decode_inputs_sync(input, py))
            })
            .await
            .unwrap();
            Ok(result)
        })
    }

    pub fn decode_transactions_input<'py>(
        &self,
        txs: Vec<Transaction>,
        py: Python<'py>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let decoder = self.clone();

        future_into_py(py, async move {
            let result = tokio::task::spawn_blocking(move || {
                Python::attach(|py| decoder.decode_transactions_input_sync(txs, py))
            })
            .await
            .unwrap();
            Ok(result)
        })
    }

    pub fn decode_traces_input<'py>(
        &self,
        traces: Vec<Trace>,
        py: Python<'py>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let decoder = self.clone();

        future_into_py(py, async move {
            let result = tokio::task::spawn_blocking(move || {
                Python::attach(|py| decoder.decode_traces_input_sync(traces, py))
            })
            .await
            .unwrap();
            Ok(result)
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

    pub fn decode_outputs<'py>(
        &self,
        outputs: Vec<String>,
        signatures: Vec<String>,
        py: Python<'py>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let decoder = self.clone();

        future_into_py(py, async move {
            let result = tokio::task::spawn_blocking(move || {
                Python::attach(|py| decoder.decode_outputs_sync(outputs, signatures, py))
            })
            .await
            .unwrap();
            Ok(result)
        })
    }

    pub fn decode_traces_output<'py>(
        &self,
        traces: Vec<Trace>,
        signatures: Vec<String>,
        py: Python<'py>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let decoder = self.clone();

        future_into_py(py, async move {
            let result = tokio::task::spawn_blocking(move || {
                Python::attach(|py| decoder.decode_traces_output_sync(traces, signatures, py))
            })
            .await
            .unwrap();
            Ok(result)
        })
    }

    pub fn decode_outputs_sync(
        &self,
        outputs: Vec<String>,
        signatures: Vec<String>,
        py: Python,
    ) -> Vec<Option<Vec<DecodedSolValue>>> {
        assert_eq!(
+       outputs.len(),
+       signatures.len(),
+       "outputs and signatures must have the same length"
+        );
        outputs
            .into_iter()
            .zip(signatures.into_iter())
            .map(|(output, sig)| self.decode_output_impl(output.as_str(), sig.as_str(), py))
            .collect()
    }

    pub fn decode_traces_output_sync(
        &self,
        traces: Vec<Trace>,
        signatures: Vec<String>,
        py: Python,
    ) -> Vec<Option<Vec<DecodedSolValue>>> {
        traces
            .into_iter()
            .zip(signatures.into_iter())
            .map(|(trace, sig)| {
                trace
                    .output
                    .as_ref()
                    .and_then(|out| self.decode_output_impl(out.as_str(), sig.as_str(), py))
            })
            .collect()
    }

    pub fn decode_output_impl(&self, output: &str, signature: &str, py: Python) -> Option<Vec<DecodedSolValue>> {
        let data = Data::decode_hex(output).context("decode output").unwrap();
        let decoded_output = self
            .inner
            .decode_output(&data, signature)
            .context("decode output")
            .unwrap();
        decoded_output.map(|decoded| {
            decoded
                .into_iter()
                .map(|value| DecodedSolValue::new(py, value, self.checksummed_addresses))
                .collect()
        })
    }
}
