// Allow non-local definitions for PyO3 macros
#![allow(non_local_definitions)]

use pyo3::prelude::*;

mod dataframe;
mod session;
mod utils;

use dataframe::{PyDataFrame, PyGroupedData};
use session::{PyDataFrameReader, PySparkSession, PySparkSessionBuilder};

/// PyRust - A Rust-based implementation of PySpark
#[pymodule]
fn _pyrust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySparkSession>()?;
    m.add_class::<PySparkSessionBuilder>()?;
    m.add_class::<PyDataFrameReader>()?;
    m.add_class::<PyDataFrame>()?;
    m.add_class::<PyGroupedData>()?;
    Ok(())
}
