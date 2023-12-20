use pyo3::prelude::*;

// Returns the input for now.
#[pyfunction]
fn dir(request: String) -> PyResult<String> {
    Ok(request)
}

// Python module implemented in Rust.
#[pymodule]
fn stringtools(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(dir, m)?)?;
    Ok(())
}
