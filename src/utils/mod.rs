// Utility functions for conversions between Python and Rust types
// For now, this module is a placeholder for future utilities

use pyo3::prelude::*;

/// Convert Python object to Rust string
pub fn pyobject_to_string(obj: &PyObject, py: Python) -> PyResult<String> {
    obj.extract::<String>(py)
}
