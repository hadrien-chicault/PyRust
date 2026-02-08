use pyo3::prelude::*;
use pyo3::types::PyModule;

mod session;
mod dataframe;
mod utils;

use session::{PySparkSession, PySparkSessionBuilder, PyDataFrameReader};
use dataframe::{PyDataFrame, PyGroupedData};

/// PyRust - A Rust-based implementation of PySpark
#[pymodule]
fn _pyrust(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PySparkSession>()?;
    m.add_class::<PySparkSessionBuilder>()?;
    m.add_class::<PyDataFrameReader>()?;
    m.add_class::<PyDataFrame>()?;
    m.add_class::<PyGroupedData>()?;
    Ok(())
}
