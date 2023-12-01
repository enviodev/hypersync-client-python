# PyO3 dev notes

## General
Node version is also written in Rust so should be fairly easy to port over.

for structs and (fieldless) enums annotate with `#[pyclass]`

- any `pyclass` must have no lifetime parameters, no generic parameters, and must implement `Send`
- use `#[pyclass(frozen)]` to declare the pyclass is immutable (disables ability to get mutable reference)
- can add `#[pyo3(get, set)]` to generate getters & setters for simple struct fields with no side effects.  For properties that require computation, can define `#[getter]` and `#[setter]` functions in the `#[pymethods]` block
- add class `Number` to module initializer `m.add_class::<Number>()?;` 

use `#[pymethods]` on the `impl` of a struct or enum

- use `#[new]` on the impl's constructor
- If no method marked with #[new] is declared, object instances can only be created from Rust, but not from Python.

When writing functions callable from Python (`#[pyfunction]` or in a `#[pymethods]` block), the trait `FromPyObject` (can `#[derive(FromPyObject)]`) is required for function arguments, and `IntoPy<PyObject>` (consumes `self`, `ToPyObject` is the same but doesn't consume `self`) (automatically implemented for any `#[pyclass]` that doesn't use `extends`) is required for function return values.

- see [Python->Rust argument types conversion table](https://pyo3.rs/v0.20.0/conversions/tables#argument-types) for the python argument type and the associated rust/PyO3 types.
- see [Rust->Python return type conversion table](https://pyo3.rs/v0.20.0/conversions/tables#returning-rust-values-to-python) for the returned rust type and the associated python value
- using the rust library types will incur a converstion cost.  The Python-native (PyO3) types are almost 0-cost.  But after the conversion cost of a rust library type has been paid, there are a number of benefits including functionality in native-speed Rust code, stricter type checking, interoperability with the rest of the rust ecosystem.  Usually the conversion cost is worth it.
- easiest way to convert a Python object to a Reust value is using `.extract()` which returns a `PyResult`.

In PyO3, holding the GIL (the Python Global Interpreter Lock) is modeling by acquiring a token of the type `Python<'py>`. See [PyO3 rust docs obtaining a Python token](https://docs.rs/pyo3/0.20.0/pyo3/marker/struct.Python.html#obtaining-a-python-token)

## GIL
GIL example: lifetime of each `hello` is bound to the `GILPool`, not the for loop.  It is only dropped at the end of the `with_gil` closure.
```
Python::with_gil(|py| -> PyResult<()> {
    for _ in 0..10 {
        let hello: &PyString = py.eval("\"Hello World!\"", None, None)?.extract()?;
        println!("Python says: {}", hello);
    }
    // There are 10 copies of `hello` on Python's heap here.
    Ok(())
})?;
```

To not have unbounded memory growth during loops, one workaround is to acquire and release the GIL with each iteration of the loop:
```
for _ in 0..10 {
    Python::with_gil(|py| -> PyResult<()> {
        let hello: &PyString = py.eval("\"Hello World!\"", None, None)?.extract()?;
        println!("Python says: {}", hello);
        Ok(())
    })?; // only one copy of `hello` at a time
}
```



- `#[pyfunction]` and `#[pymethods]` will create a GILPool which last the entire function call, releasing objects when the function returns.
- To get a reference to memory on Python's heap that can outlive the GIL, `Py<PyAny>` is analogous to `Arc<T>`, but for variables whose memory is allocated on Python's heap.  Cloning a `Py<PyAny>` increases its internal reference count just like cloning `Arc<T>`
- Need to reacquire the GIL to access the memory pointed to by the `Py<PyAny>`


## Performance notes
- Chains of `.extract` can be suboptimal.  use `.downcast`
- calling `Python::with_gil` is effectively a no-op when the GIL is already held, but checking that this is the case still has a cost.  If an existing GIL token can not be accessed but a GIL-bound reference is available, this cost can be avoided by exploting that access to GIL-bound references gives zero-cost access to a GIL token via `PyAny::py`

### for `async` and `await` use `pyo3-asyncio` crate 
