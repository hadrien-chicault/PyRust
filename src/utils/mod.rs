//! Utility functions for type conversions and interoperability.
//!
//! This module provides utility functions for converting between Python and Rust types,
//! and other helper functions used throughout PyRust.
//!
//! # Current Status
//!
//! This module is currently minimal, containing only basic conversion utilities.
//! Future versions will expand this with:
//! - Complex type conversions
//! - Data validation helpers
//! - Performance profiling utilities
//! - Logging and debugging helpers

use pyo3::prelude::*;

/// Converts a Python object to a Rust String.
///
/// This is a convenience wrapper around PyO3's extraction mechanism,
/// providing a consistent interface for string conversion throughout
/// the codebase.
///
/// # Arguments
///
/// * `obj` - The Python object to convert
/// * `py` - Python GIL token
///
/// # Returns
///
/// The extracted string or an error if conversion fails.
///
/// # Errors
///
/// Returns a `PyErr` if the Python object cannot be converted to a string.
///
/// # Example
///
/// ```rust,ignore
/// let py_str: PyObject = ...;
/// let rust_str = pyobject_to_string(&py_str, py)?;
/// ```
///
/// # Note
///
/// This function is currently unused but kept for future extensions.
#[allow(dead_code)]
pub fn pyobject_to_string(obj: &PyObject, py: Python) -> PyResult<String> {
    obj.extract::<String>(py)
}
