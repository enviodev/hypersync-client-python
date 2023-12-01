use pyo3::prelude::*;

mod config;
mod from_arrow;
mod query;
mod types;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyfunction]
fn send_req() -> PyResult<String> {
    Ok("Sent a super cool HyperSync skar query".to_string())
}

#[pyfunction]
fn rust_sleep(py: Python) -> PyResult<&PyAny> {
    pyo3_asyncio::tokio::future_into_py(py, async {
        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
        Ok(())
    })
}

/// A Python module implemented in Rust.
#[pymodule]
fn hypersync_client(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(send_req, m)?)?;
    m.add_function(wrap_pyfunction!(rust_sleep, m)?)?;
    Ok(())
}
