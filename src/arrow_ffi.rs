use anyhow::{Context, Result};
use hypersync_client::ArrowBatch;
use polars_arrow::{
    array::StructArray,
    datatypes::{ArrowDataType as DataType, Field},
    ffi,
};
use pyo3::{ffi::Py_uintptr_t, types::PyModule, PyErr, PyObject, Python, ToPyObject};

use crate::{
    response::{ArrowResponse, ArrowResponseData},
    types::RollbackGuard,
};

pub fn response_to_pyarrow(response: hypersync_client::ArrowResponse) -> Result<ArrowResponse> {
    let data = Python::with_gil(|py| {
        let pyarrow = py.import("pyarrow")?;
        Ok::<_, PyErr>(ArrowResponseData {
            blocks: convert_batches_to_pyarrow_table(py, pyarrow, response.data.blocks)?,
            transactions: convert_batches_to_pyarrow_table(
                py,
                pyarrow,
                response.data.transactions,
            )?,
            logs: convert_batches_to_pyarrow_table(py, pyarrow, response.data.logs)?,
            traces: convert_batches_to_pyarrow_table(py, pyarrow, response.data.traces)?,
            decoded_logs: convert_batches_to_pyarrow_table(
                py,
                pyarrow,
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
    pyarrow: &'py PyModule,
    batches: Vec<ArrowBatch>,
) -> Result<PyObject> {
    if batches.is_empty() {
        return Ok(py.None());
    }

    let schema = batches.first().unwrap().schema.fields.clone();
    let field = Field::new("a", DataType::Struct(schema), true);

    let mut data = vec![];
    for batch in batches {
        data.push(
            StructArray::new(field.data_type.clone(), batch.chunk.arrays().to_vec(), None).boxed(),
        );
    }

    let iter = Box::new(data.into_iter().map(Ok)) as _;
    let stream = Box::new(ffi::export_iterator(iter, field));
    let py_stream = pyarrow.getattr("RecordBatchReader")?.call_method1(
        "_import_from_c",
        ((&*stream as *const ffi::ArrowArrayStream) as Py_uintptr_t,),
    )?;
    let table = pyarrow
        .getattr("Table")
        .context("get pyarrow Table")?
        .call_method1("from_batches", (py_stream,))
        .context("call pyarrow::Table::from_batches")?;

    Ok(table.to_object(py))
}
