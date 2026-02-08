//! # PyRust - High-Performance Distributed Computing
//!
//! PyRust is a Rust-based implementation of PySpark, providing high-performance
//! distributed computing capabilities with a familiar PySpark-like API.
//!
//! Built on top of [Apache DataFusion](https://datafusion.apache.org/), PyRust leverages
//! Rust's performance and safety guarantees to deliver significant speed improvements
//! over traditional Python-based data processing frameworks.
//!
//! ## Features
//!
//! - **High Performance**: 10-50x faster than PySpark for common operations
//! - **Memory Efficient**: Optimized memory usage with Arrow's columnar format
//! - **Type Safe**: Leverages Rust's type system for safer data processing
//! - **Familiar API**: Drop-in replacement for PySpark code
//! - **Zero-Copy**: Efficient data sharing between Python and Rust via PyArrow
//!
//! ## Quick Start
//!
//! ```python
//! from pyrust import SparkSession
//!
//! # Create a session
//! spark = SparkSession.builder().appName("MyApp").getOrCreate()
//!
//! # Read data
//! df = spark.read.csv("data.csv", header=True)
//!
//! # Transform
//! result = df.select(["name", "age"]) \
//!            .filter("age > 18") \
//!            .groupBy(["city"]) \
//!            .count()
//!
//! # Show results
//! result.show()
//! ```
//!
//! ## Architecture
//!
//! PyRust consists of three main components:
//!
//! - **Session Management** - Spark session creation and data reading (SparkSession, DataFrameReader)
//! - **DataFrame Operations** - Distributed data transformations (DataFrame, GroupedData)
//! - **Utilities** - Type conversions and helper functions
//!
//! ## Performance
//!
//! PyRust achieves significant performance improvements through:
//!
//! - **Columnar Processing**: Uses Apache Arrow for efficient vectorized operations
//! - **Lazy Evaluation**: Operations are optimized before execution
//! - **Zero-Copy Interop**: Direct memory sharing with Python via PyArrow
//! - **Parallel Execution**: Leverages Rust's async runtime for concurrent operations

// Allow non-local definitions for PyO3 macros
#![allow(non_local_definitions)]
#![warn(missing_docs)]

use pyo3::prelude::*;

mod dataframe;
mod session;
mod utils;

use dataframe::{PyDataFrame, PyGroupedData};
use session::{PyDataFrameReader, PySparkSession, PySparkSessionBuilder};

/// PyRust Python module initialization.
///
/// This function is called by Python when the module is imported.
/// It registers all Python classes and functions provided by PyRust.
///
/// # Exported Classes
///
/// - [`PySparkSession`] - Main entry point for Spark functionality
/// - [`PySparkSessionBuilder`] - Builder pattern for creating sessions
/// - [`PyDataFrameReader`] - Reads data from various sources
/// - [`PyDataFrame`] - Distributed collection of data
/// - [`PyGroupedData`] - Grouped data for aggregation operations
#[pymodule]
fn _pyrust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySparkSession>()?;
    m.add_class::<PySparkSessionBuilder>()?;
    m.add_class::<PyDataFrameReader>()?;
    m.add_class::<PyDataFrame>()?;
    m.add_class::<PyGroupedData>()?;
    Ok(())
}
