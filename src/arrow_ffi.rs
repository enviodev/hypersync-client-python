use anyhow::{Context, Result};
use arrow::{
    array::RecordBatch,
    ffi_stream::FFI_ArrowArrayStream,
    record_batch::RecordBatchIterator,
};
use pyo3::{
    ffi::Py_uintptr_t,
    types::{PyAnyMethods, PyModule},
    Py, PyAny, PyErr, Python,
};

use crate::{
    response::{ArrowResponse, ArrowResponseData},
    types::RollbackGuard,
};

pub fn response_to_pyarrow(response: hypersync_client::ArrowResponse) -> Result<ArrowResponse> {
    let data = Python::attach(|py| {
        let pyarrow = py.import("pyarrow")?;
        Ok::<_, PyErr>(ArrowResponseData {
            blocks: convert_batches_to_pyarrow_table(py, &pyarrow, response.data.blocks)?,
            transactions: convert_batches_to_pyarrow_table(
                py,
                &pyarrow,
                response.data.transactions,
            )?,
            logs: convert_batches_to_pyarrow_table(py, &pyarrow, response.data.logs)?,
            traces: convert_batches_to_pyarrow_table(py, &pyarrow, response.data.traces)?,
            decoded_logs: convert_batches_to_pyarrow_table(
                py,
                &pyarrow,
                response.data.decoded_logs,
            )?,
        })
    })?;

    Ok(ArrowResponse {
        archive_height: response.archive_height,
        next_block: response.next_block,
        total_execution_time: response.total_execution_time,
        data,
        rollback_guard: response
            .rollback_guard
            .map(|rg| RollbackGuard::try_convert(rg).context("convert rollback guard"))
            .transpose()?,
    })
}

fn convert_batches_to_pyarrow_table<'py>(
    py: Python<'py>,
    pyarrow: &pyo3::Bound<'py, PyModule>,
    batches: Vec<RecordBatch>,
) -> Result<Py<PyAny>> {
    if batches.is_empty() {
        return Ok(py.None());
    }

    let schema = batches[0].schema();
    let reader = RecordBatchIterator::new(batches.into_iter().map(Ok), schema);
    let mut ffi_stream = FFI_ArrowArrayStream::new(Box::new(reader));

    let py_stream = pyarrow.getattr("RecordBatchReader")?.call_method1(
        "_import_from_c",
        (&mut ffi_stream as *mut FFI_ArrowArrayStream as Py_uintptr_t,),
    )?;
    let table = pyarrow
        .getattr("Table")
        .context("get pyarrow Table")?
        .call_method1("from_batches", (py_stream,))
        .context("call pyarrow::Table::from_batches")?;

    Ok(table.unbind())
}
