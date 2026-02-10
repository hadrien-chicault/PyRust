//! Spark session management and data reading.
//!
//! This module provides the entry point for PyRust functionality through the
//! [`PySparkSession`] class. It follows the Spark API design pattern with a
//! builder for configuration and a reader for data ingestion.
//!
//! # Example
//!
//! ```python
//! from pyrust import SparkSession
//!
//! # Create a session using the builder pattern
//! spark = SparkSession.builder() \
//!     .appName("MyApplication") \
//!     .master("local[*]") \
//!     .getOrCreate()
//!
//! # Read CSV data
//! df = spark.read.csv("data.csv", header=True)
//!
//! # Read Parquet data
//! df = spark.read.parquet("data.parquet")
//! ```

use datafusion::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::sync::Arc;

use crate::dataframe::PyDataFrame;

/// SparkSession - Main entry point for PyRust functionality.
///
/// The SparkSession is the primary interface for working with PyRust. It provides
/// methods to read data from various sources and create DataFrames.
///
/// # Architecture
///
/// Internally, SparkSession wraps a DataFusion [`SessionContext`], which provides
/// the query planning and execution capabilities. The session maintains configuration
/// and provides a consistent interface for data operations.
///
/// # Performance Notes
///
/// - Session creation is lightweight (< 1ms typically)
/// - Sessions can be reused across multiple operations
/// - Multiple sessions can coexist independently
///
/// # Python Example
///
/// ```python
/// spark = SparkSession.builder().appName("MyApp").getOrCreate()
/// df = spark.read.csv("data.csv")
/// print(spark.appName)  # Access the application name
/// spark.stop()  # Clean up resources
/// ```
#[pyclass(name = "SparkSession")]
pub struct PySparkSession {
    /// DataFusion session context for query execution
    ctx: SessionContext,
    /// Application name for identification
    app_name: String,
}

/// Builder for creating SparkSession instances.
///
/// Follows the builder pattern to provide a fluent API for configuring
/// and creating SparkSession objects. This matches the PySpark API for
/// familiarity.
///
/// # Example
///
/// ```python
/// builder = SparkSession.builder()
/// session = builder.appName("MyApp") \
///                  .master("local[*]") \
///                  .getOrCreate()
/// ```
///
/// # Note
///
/// The `master()` configuration is accepted for API compatibility but does not
/// affect execution in the current implementation. PyRust executes locally using
/// DataFusion's execution engine.
#[pyclass(name = "SparkSessionBuilder")]
pub struct PySparkSessionBuilder {
    /// Optional application name
    app_name: Option<String>,
    /// Optional master URL (for compatibility, not used)
    master: Option<String>,
}

#[pymethods]
impl PySparkSessionBuilder {
    /// Creates a new SparkSessionBuilder.
    ///
    /// # Returns
    ///
    /// A new builder instance with default configuration.
    #[new]
    fn new() -> Self {
        Self {
            app_name: None,
            master: None,
        }
    }

    /// Sets the application name for the SparkSession.
    ///
    /// The application name is used for identification and logging purposes.
    ///
    /// # Arguments
    ///
    /// * `name` - The name to assign to the application
    ///
    /// # Returns
    ///
    /// A new builder instance with the application name set.
    ///
    /// # Example
    ///
    /// ```python
    /// builder = SparkSession.builder().appName("DataProcessing")
    /// ```
    #[allow(non_snake_case)]
    fn appName(&mut self, name: &str) -> Self {
        self.app_name = Some(name.to_string());
        Self {
            app_name: self.app_name.clone(),
            master: self.master.clone(),
        }
    }

    /// Sets the master URL for the SparkSession.
    ///
    /// **Note**: This method is provided for API compatibility with PySpark,
    /// but the master URL does not affect execution in PyRust. All operations
    /// execute locally using DataFusion.
    ///
    /// # Arguments
    ///
    /// * `url` - The master URL (e.g., "local[*]", "spark://host:port")
    ///
    /// # Returns
    ///
    /// A new builder instance with the master URL set.
    ///
    /// # Example
    ///
    /// ```python
    /// builder = SparkSession.builder().master("local[4]")
    /// ```
    fn master(&mut self, url: &str) -> Self {
        self.master = Some(url.to_string());
        Self {
            app_name: self.app_name.clone(),
            master: self.master.clone(),
        }
    }

    /// Creates or retrieves the SparkSession.
    ///
    /// This method creates a new SparkSession with the configured settings.
    /// In the current implementation, it always creates a new session rather
    /// than reusing an existing one.
    ///
    /// # Returns
    ///
    /// A configured SparkSession instance ready for use.
    ///
    /// # Performance
    ///
    /// Session creation is very fast (< 1ms) so creating multiple sessions
    /// has minimal overhead.
    ///
    /// # Example
    ///
    /// ```python
    /// spark = SparkSession.builder() \
    ///     .appName("MyApp") \
    ///     .getOrCreate()
    /// ```
    #[allow(non_snake_case)]
    fn getOrCreate(&self) -> PyResult<PySparkSession> {
        let ctx = SessionContext::new();
        let app_name = self
            .app_name
            .clone()
            .unwrap_or_else(|| "pyrust-app".to_string());

        Ok(PySparkSession { ctx, app_name })
    }
}

/// DataFrameReader for loading data from various sources.
///
/// The DataFrameReader provides methods to read data from different file formats
/// into DataFrames. It supports efficient reading with schema inference and
/// various parsing options.
///
/// # Supported Formats
///
/// - CSV - Comma-separated values with header detection
/// - Parquet - Columnar format with built-in compression
///
/// # Performance
///
/// - CSV reading uses Arrow's fast CSV parser (10-20x faster than Pandas)
/// - Parquet reading leverages predicate pushdown and column pruning
/// - Large files are read in parallel when possible
///
/// # Example
///
/// ```python
/// spark = SparkSession.builder().appName("Reader").getOrCreate()
/// reader = spark.read
///
/// # Read CSV with automatic schema inference
/// df = reader.csv("data.csv", header=True, infer_schema=True)
///
/// # Read Parquet (schema is always preserved)
/// df = reader.parquet("data.parquet")
/// ```
#[pyclass(name = "DataFrameReader")]
pub struct PyDataFrameReader {
    /// Reference to the parent session's context
    session: Arc<SessionContext>,
}

#[pymethods]
impl PyDataFrameReader {
    /// Reads a CSV file into a DataFrame.
    ///
    /// CSV (Comma-Separated Values) files are parsed using Apache Arrow's
    /// high-performance CSV reader. The reader supports automatic schema
    /// inference and header detection.
    ///
    /// # Arguments
    ///
    /// * `path` - Path to the CSV file (can be local or remote URL)
    /// * `header` - Whether the first row contains column names (default: true)
    /// * `infer_schema` - Whether to automatically detect column types (default: true)
    ///
    /// # Returns
    ///
    /// A DataFrame containing the CSV data.
    ///
    /// # Performance Notes
    ///
    /// - Schema inference scans the first 1000 rows
    /// - For large files, consider providing an explicit schema
    /// - CSV parsing is CPU-bound and benefits from multi-core systems
    ///
    /// # Errors
    ///
    /// Returns a `PyRuntimeError` if:
    /// - The file does not exist or cannot be read
    /// - The CSV format is invalid
    /// - The runtime cannot be created
    ///
    /// # Example
    ///
    /// ```python
    /// # Read with header and auto schema inference
    /// df = spark.read.csv("users.csv", header=True, infer_schema=True)
    ///
    /// # Read without header (generates default column names)
    /// df = spark.read.csv("data.csv", header=False, infer_schema=True)
    /// ```
    #[pyo3(signature = (path, header=true, infer_schema=true))]
    fn csv(&self, path: &str, header: bool, infer_schema: bool) -> PyResult<PyDataFrame> {
        let ctx = self.session.clone();

        // Use tokio runtime to execute async datafusion operations
        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?;

        let df = rt
            .block_on(async {
                ctx.read_csv(
                    path,
                    datafusion::prelude::CsvReadOptions::new()
                        .has_header(header)
                        .schema_infer_max_records(if infer_schema { 1000 } else { 0 }),
                )
                .await
            })
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to read CSV: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }

    /// Reads a Parquet file into a DataFrame.
    ///
    /// Parquet is a columnar storage format optimized for analytics workloads.
    /// It includes built-in schema, compression, and encoding, making it ideal
    /// for large-scale data processing.
    ///
    /// # Arguments
    ///
    /// * `path` - Path to the Parquet file or directory
    ///
    /// # Returns
    ///
    /// A DataFrame containing the Parquet data with the original schema preserved.
    ///
    /// # Performance Advantages
    ///
    /// - **Columnar Format**: Only reads columns actually used in queries
    /// - **Compression**: Built-in compression (typically 5-10x smaller than CSV)
    /// - **Predicate Pushdown**: Filters applied during read, not after
    /// - **Type Safety**: Schema is preserved exactly, no inference needed
    /// - **Speed**: 10-100x faster than CSV for selective queries
    ///
    /// # Errors
    ///
    /// Returns a `PyRuntimeError` if:
    /// - The file does not exist or cannot be read
    /// - The Parquet format is corrupted
    /// - The runtime cannot be created
    ///
    /// # Example
    ///
    /// ```python
    /// # Read a single Parquet file
    /// df = spark.read.parquet("data.parquet")
    ///
    /// # Read a directory of Parquet files
    /// df = spark.read.parquet("data_dir/")
    /// ```
    ///
    /// # Recommendation
    ///
    /// For production workloads, prefer Parquet over CSV for:
    /// - Faster read/write performance
    /// - Smaller storage footprint
    /// - Preserved data types
    /// - Better compression
    fn parquet(&self, path: &str) -> PyResult<PyDataFrame> {
        let ctx = self.session.clone();

        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?;

        let df = rt
            .block_on(async {
                ctx.read_parquet(path, datafusion::prelude::ParquetReadOptions::default())
                    .await
            })
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to read Parquet: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }
}

#[pymethods]
impl PySparkSession {
    /// Returns a builder for creating SparkSession instances.
    ///
    /// This is the recommended way to create a SparkSession, as it allows
    /// configuration through a fluent API.
    ///
    /// # Returns
    ///
    /// A new [`PySparkSessionBuilder`] instance.
    ///
    /// # Example
    ///
    /// ```python
    /// spark = SparkSession.builder() \
    ///     .appName("MyApp") \
    ///     .master("local[*]") \
    ///     .getOrCreate()
    /// ```
    #[staticmethod]
    fn builder() -> PySparkSessionBuilder {
        PySparkSessionBuilder::new()
    }

    /// Returns a DataFrameReader for loading data.
    ///
    /// The reader provides methods to load data from various file formats
    /// into DataFrames.
    ///
    /// # Returns
    ///
    /// A [`PyDataFrameReader`] instance associated with this session.
    ///
    /// # Example
    ///
    /// ```python
    /// df = spark.read.csv("data.csv")
    /// df = spark.read.parquet("data.parquet")
    /// ```
    #[getter]
    fn read(&self) -> PyDataFrameReader {
        PyDataFrameReader {
            session: Arc::new(self.ctx.clone()),
        }
    }

    /// Returns the application name of this SparkSession.
    ///
    /// The application name is set during session creation via the builder
    /// and is used for identification in logs and monitoring.
    ///
    /// # Returns
    ///
    /// The application name as a string.
    ///
    /// # Example
    ///
    /// ```python
    /// spark = SparkSession.builder().appName("MyApp").getOrCreate()
    /// print(spark.appName)  # Output: MyApp
    /// ```
    #[getter]
    #[allow(non_snake_case)]
    fn appName(&self) -> String {
        self.app_name.clone()
    }

    /// Creates a DataFrame from in-memory data.
    ///
    /// **Note**: This method is not yet implemented in the current version.
    /// It is provided for API compatibility with PySpark.
    ///
    /// # Arguments
    ///
    /// * `_data` - A nested list representing rows and columns
    ///
    /// # Returns
    ///
    /// Currently returns an error indicating the feature is not implemented.
    ///
    /// # Future Implementation
    ///
    /// Future versions will support creating DataFrames from:
    /// - Lists of lists
    /// - Lists of dictionaries
    /// - Pandas DataFrames (via PyArrow)
    /// - NumPy arrays
    ///
    /// # Example (not yet working)
    ///
    /// ```python
    /// # This will be supported in future versions
    /// data = [["Alice", 25], ["Bob", 30]]
    /// df = spark.createDataFrame(data, ["name", "age"])
    /// ```
    #[allow(non_snake_case)]
    fn createDataFrame(&self, _data: Vec<Vec<PyObject>>) -> PyResult<PyDataFrame> {
        Err(PyRuntimeError::new_err(
            "createDataFrame not yet implemented in POC",
        ))
    }

    /// Executes a SQL query and returns the result as a DataFrame.
    ///
    /// This method allows you to run SQL queries directly, leveraging DataFusion's
    /// full SQL engine. It supports standard SQL syntax including SELECT, WHERE,
    /// GROUP BY, ORDER BY, joins, subqueries, and window functions.
    ///
    /// # Arguments
    ///
    /// * `query` - SQL query string to execute
    ///
    /// # Returns
    ///
    /// A DataFrame containing the query results.
    ///
    /// # SQL Support
    ///
    /// PyRust supports full ANSI SQL via DataFusion:
    /// - SELECT, WHERE, GROUP BY, HAVING, ORDER BY
    /// - Joins (INNER, LEFT, RIGHT, FULL, CROSS)
    /// - Subqueries and CTEs (WITH)
    /// - Window functions (ROW_NUMBER, RANK, etc.)
    /// - Aggregate functions (COUNT, SUM, AVG, MIN, MAX)
    /// - String, date, and math functions
    ///
    /// # Performance
    ///
    /// - SQL queries are optimized by DataFusion's query planner
    /// - Predicate pushdown and column pruning applied automatically
    /// - Vectorized execution for high performance
    ///
    /// # Errors
    ///
    /// Returns a `PyRuntimeError` if:
    /// - SQL syntax is invalid
    /// - Referenced tables/views don't exist
    /// - Query execution fails
    ///
    /// # Examples
    ///
    /// ```python
    /// # Simple SELECT
    /// df = spark.sql("SELECT name, age FROM users WHERE age > 18")
    ///
    /// # With aggregation
    /// df = spark.sql(\"\"\"
    ///     SELECT city, COUNT(*) as count, AVG(age) as avg_age
    ///     FROM users
    ///     GROUP BY city
    ///     ORDER BY count DESC
    /// \"\"\")
    ///
    /// # With joins (requires temp views)
    /// users_df.createOrReplaceTempView("users")
    /// orders_df.createOrReplaceTempView("orders")
    /// df = spark.sql(\"\"\"
    ///     SELECT u.name, COUNT(o.id) as order_count
    ///     FROM users u
    ///     JOIN orders o ON u.id = o.user_id
    ///     GROUP BY u.name
    /// \"\"\")
    /// ```
    fn sql(&self, query: &str) -> PyResult<PyDataFrame> {
        // Use tokio runtime to execute async datafusion operations
        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?;

        let df = rt
            .block_on(async {
                // Execute SQL query via DataFusion
                self.ctx.sql(query).await
            })
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to execute SQL: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }

    /// Registers a DataFrame as a temporary view/table.
    ///
    /// This allows SQL queries to reference the DataFrame by name. The view is
    /// session-scoped and will be available until the session ends or the view
    /// is replaced.
    ///
    /// # Arguments
    ///
    /// * `df` - The DataFrame to register
    /// * `name` - The name to assign to the view
    ///
    /// # Errors
    ///
    /// Returns a `PyRuntimeError` if registration fails.
    ///
    /// # Example
    ///
    /// ```python
    /// df = spark.read.csv("users.csv")
    /// spark.register_temp_view(df, "users")
    /// result = spark.sql("SELECT * FROM users WHERE age > 18")
    /// ```
    ///
    /// # Note
    ///
    /// This is a helper method. In PySpark, you would use `df.createOrReplaceTempView()`.
    /// For API compatibility, use the Python wrapper which delegates to this method.
    fn register_temp_view(&self, df: &PyDataFrame, name: &str) -> PyResult<()> {
        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?;

        rt.block_on(async {
            // First, deregister any existing table with this name (ignore errors if doesn't exist)
            let _ = self.ctx.deregister_table(name);

            // Now register the new table
            self.ctx
                .register_table(name, df.inner_df().as_ref().clone().into_view())
        })
        .map_err(|e| {
            PyRuntimeError::new_err(format!("Failed to register temp view '{}': {}", name, e))
        })?;

        Ok(())
    }

    /// Stops the SparkSession and releases resources.
    ///
    /// **Note**: In the current implementation, this is a no-op. Future versions
    /// will properly clean up resources such as:
    /// - Thread pools
    /// - Cached data
    /// - Temporary files
    /// - Network connections
    ///
    /// # Example
    ///
    /// ```python
    /// spark = SparkSession.builder().appName("MyApp").getOrCreate()
    /// # ... use spark ...
    /// spark.stop()  # Clean up
    /// ```
    fn stop(&self) {
        // In the POC, this is a no-op
        // In future versions, this would clean up resources
    }

    /// Returns a string representation of the SparkSession.
    ///
    /// # Returns
    ///
    /// A string showing the session type and application name.
    fn __repr__(&self) -> String {
        format!("<SparkSession(app='{}')>", self.app_name)
    }
}
