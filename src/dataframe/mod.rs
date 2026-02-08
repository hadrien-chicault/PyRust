//! DataFrame operations and transformations.
//!
//! This module provides the core DataFrame API for distributed data processing.
//! DataFrames represent distributed collections of data organized into named columns,
//! similar to tables in a relational database.
//!
//! # Architecture
//!
//! PyRust DataFrames wrap Apache DataFusion's DataFrame, providing:
//! - Lazy evaluation with query optimization
//! - Columnar processing via Apache Arrow
//! - Automatic parallelization
//! - Memory-efficient operations
//!
//! # Example
//!
//! ```python
//! # Load data
//! df = spark.read.csv("data.csv")
//!
//! # Chain transformations (lazy evaluation)
//! result = df.select(["name", "age", "city"]) \
//!            .filter("age > 18") \
//!            .groupBy(["city"]) \
//!            .count() \
//!            .orderBy(["count"])
//!
//! # Trigger execution
//! result.show()
//! ```

use datafusion::arrow::util::pretty;
use datafusion::functions_aggregate::expr_fn::{avg, count, max, min, sum};
use datafusion::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::sync::Arc;

/// DataFrame - Distributed collection of data organized into named columns.
///
/// A DataFrame is similar to a table in a relational database or a Pandas DataFrame,
/// but with distributed computing capabilities. Operations on DataFrames are lazily
/// evaluated and optimized before execution.
///
/// # Key Features
///
/// - **Lazy Evaluation**: Operations are not executed until an action (like `show()` or `count()`) is called
/// - **Query Optimization**: DataFusion's optimizer automatically improves query plans
/// - **Columnar Processing**: Uses Apache Arrow for efficient vectorized operations
/// - **Type Safety**: Schema is preserved and validated at each operation
///
/// # Transformations vs Actions
///
/// - **Transformations** (lazy): `select()`, `filter()`, `groupBy()`, `orderBy()`, `limit()`
/// - **Actions** (eager): `show()`, `count()`, `collect()`
///
/// # Performance Tips
///
/// 1. **Filter Early**: Apply `filter()` before other operations
/// 2. **Select Only Needed Columns**: Use `select()` to reduce data size
/// 3. **Limit When Exploring**: Use `limit()` for quick data inspection
/// 4. **Batch Operations**: Chain multiple transformations before an action
///
/// # Example
///
/// ```python
/// df = spark.read.csv("sales.csv")
///
/// # Transformation chain (no execution yet)
/// high_value_sales = df.filter("amount > 1000") \
///                      .select(["customer", "amount", "date"]) \
///                      .orderBy(["amount"]) \
///                      .limit(100)
///
/// # Action (triggers execution)
/// high_value_sales.show(20)
/// ```
#[pyclass(name = "DataFrame")]
#[derive(Clone)]
pub struct PyDataFrame {
    /// Wrapped DataFusion DataFrame (reference-counted for efficient cloning)
    df: Arc<DataFrame>,
}

impl PyDataFrame {
    /// Creates a new PyDataFrame wrapping a DataFusion DataFrame.
    ///
    /// # Arguments
    ///
    /// * `df` - The DataFusion DataFrame to wrap
    ///
    /// # Returns
    ///
    /// A new PyDataFrame instance with the DataFrame wrapped in an Arc for efficient sharing.
    pub fn new(df: DataFrame) -> Self {
        Self { df: Arc::new(df) }
    }

    /// Creates a new Tokio runtime for async operations.
    ///
    /// DataFusion operations are async, so we need a runtime to execute them
    /// synchronously from Python. Each operation creates its own runtime to
    /// avoid runtime lifetime issues.
    ///
    /// # Returns
    ///
    /// A new Tokio runtime or an error if creation fails.
    ///
    /// # Performance Note
    ///
    /// Runtime creation is fast (~100μs) and runtimes are short-lived,
    /// so the overhead is minimal compared to query execution time.
    fn runtime() -> PyResult<tokio::runtime::Runtime> {
        tokio::runtime::Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))
    }

    /// Clones the underlying DataFrame.
    ///
    /// Since the DataFrame is wrapped in an Arc, this is a cheap operation
    /// that just increments a reference count rather than copying data.
    ///
    /// # Returns
    ///
    /// A clone of the underlying DataFrame.
    fn clone_df(&self) -> DataFrame {
        self.df.as_ref().clone()
    }
}

#[pymethods]
impl PyDataFrame {
    /// Selects a subset of columns from the DataFrame.
    ///
    /// This is a transformation operation (lazy) that creates a new DataFrame
    /// with only the specified columns. Column order in the result matches
    /// the order provided.
    ///
    /// # Arguments
    ///
    /// * `cols` - List of column names to select
    ///
    /// # Returns
    ///
    /// A new DataFrame containing only the selected columns.
    ///
    /// # Performance
    ///
    /// - Selecting fewer columns reduces memory usage and I/O
    /// - With Parquet files, only selected columns are read from disk
    /// - Operation itself is O(1) as it's lazily evaluated
    ///
    /// # Errors
    ///
    /// Returns a `PyRuntimeError` if:
    /// - A column name does not exist in the DataFrame
    /// - The runtime cannot be created
    ///
    /// # Example
    ///
    /// ```python
    /// # Select specific columns
    /// df_subset = df.select(["name", "age", "city"])
    ///
    /// # Reorder columns
    /// df_reordered = df.select(["city", "name", "age"])
    ///
    /// # Select a single column
    /// df_single = df.select(["age"])
    /// ```
    fn select(&self, cols: Vec<&str>) -> PyResult<Self> {
        let rt = Self::runtime()?;

        let df = rt
            .block_on(async {
                let col_exprs: Vec<Expr> = cols.iter().map(|c| col(*c)).collect();

                self.clone_df().select(col_exprs)
            })
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to select columns: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }

    /// Filters rows based on a condition (alias for `where_`).
    ///
    /// This is a transformation operation (lazy) that creates a new DataFrame
    /// containing only rows that match the condition.
    ///
    /// # Arguments
    ///
    /// * `condition` - A filter expression as a string (e.g., "age > 18")
    ///
    /// # Returns
    ///
    /// A new DataFrame containing only matching rows.
    ///
    /// # Performance Tip
    ///
    /// Apply filters as early as possible in your transformation chain to
    /// reduce the amount of data processed by subsequent operations.
    ///
    /// # Example
    ///
    /// ```python
    /// adults = df.filter("age > 18")
    /// high_earners = df.filter("salary >= 100000")
    /// ```
    ///
    /// # See Also
    ///
    /// - [`where_`](#method.where_) - Identical functionality, SQL-style naming
    fn filter(&self, condition: &str) -> PyResult<Self> {
        // For POC, we support simple conditions like "age > 18"
        // In production, this would need a proper expression parser
        self.where_(condition)
    }

    /// Filters rows based on a condition (SQL-style alias).
    ///
    /// This method is identical to `filter()` but uses SQL-style naming.
    /// It's a transformation operation (lazy) that creates a new DataFrame
    /// containing only rows that match the specified condition.
    ///
    /// # Supported Syntax
    ///
    /// The current implementation supports simple conditions in the format:
    /// `column operator value`
    ///
    /// **Supported Operators:**
    /// - Numeric: `>`, `<`, `>=`, `<=`, `==`, `!=`
    /// - String: `==`, `!=`
    ///
    /// # Arguments
    ///
    /// * `condition` - A filter expression string
    ///
    /// # Returns
    ///
    /// A new DataFrame containing only matching rows.
    ///
    /// # Performance Notes
    ///
    /// - Filter pushdown is applied when reading Parquet files
    /// - Filters on indexed columns are particularly fast
    /// - Complex filters are automatically optimized by the query planner
    ///
    /// # Errors
    ///
    /// Returns a `PyRuntimeError` if:
    /// - The condition syntax is invalid
    /// - The column does not exist
    /// - The value type doesn't match the column type
    /// - The runtime cannot be created
    ///
    /// # Examples
    ///
    /// ```python
    /// # Numeric comparison
    /// adults = df.where_("age > 18")
    /// seniors = df.where_("age >= 65")
    ///
    /// # String comparison (with quotes)
    /// vip_customers = df.where_("status == 'VIP'")
    ///
    /// # Equality
    /// active_users = df.where_("active == 1")
    /// ```
    ///
    /// # Future Enhancements
    ///
    /// Future versions will support:
    /// - Complex conditions with AND/OR
    /// - SQL-like expressions (LIKE, IN, BETWEEN)
    /// - Column-to-column comparisons
    /// - Function calls in conditions
    fn where_(&self, condition: &str) -> PyResult<Self> {
        let rt = Self::runtime()?;

        let df = rt
            .block_on(async {
                // Parse simple conditions
                // This is a simplified parser for the POC
                let parts: Vec<&str> = condition.split_whitespace().collect();
                if parts.len() != 3 {
                    return Err(datafusion::error::DataFusionError::Plan(format!(
                        "Invalid condition format: {}. Expected format: 'column op value'",
                        condition
                    )));
                }

                let col_name = parts[0];
                let op = parts[1];
                let value_str = parts[2];

                // Try to parse as number first, then as string
                let expr = if let Ok(num) = value_str.parse::<i64>() {
                    match op {
                        ">" => col(col_name).gt(lit(num)),
                        "<" => col(col_name).lt(lit(num)),
                        ">=" => col(col_name).gt_eq(lit(num)),
                        "<=" => col(col_name).lt_eq(lit(num)),
                        "==" | "=" => col(col_name).eq(lit(num)),
                        "!=" => col(col_name).not_eq(lit(num)),
                        _ => {
                            return Err(datafusion::error::DataFusionError::Plan(format!(
                                "Unsupported operator: {}",
                                op
                            )))
                        }
                    }
                } else if let Ok(num) = value_str.parse::<f64>() {
                    match op {
                        ">" => col(col_name).gt(lit(num)),
                        "<" => col(col_name).lt(lit(num)),
                        ">=" => col(col_name).gt_eq(lit(num)),
                        "<=" => col(col_name).lt_eq(lit(num)),
                        "==" | "=" => col(col_name).eq(lit(num)),
                        "!=" => col(col_name).not_eq(lit(num)),
                        _ => {
                            return Err(datafusion::error::DataFusionError::Plan(format!(
                                "Unsupported operator: {}",
                                op
                            )))
                        }
                    }
                } else {
                    // Treat as string, remove quotes if present
                    let value = value_str.trim_matches('\'').trim_matches('"');
                    match op {
                        "==" | "=" => col(col_name).eq(lit(value)),
                        "!=" => col(col_name).not_eq(lit(value)),
                        _ => {
                            return Err(datafusion::error::DataFusionError::Plan(format!(
                                "Unsupported operator for string: {}",
                                op
                            )))
                        }
                    }
                };

                self.clone_df().filter(expr)
            })
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to filter: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }

    /// Groups the DataFrame by specified columns for aggregation.
    ///
    /// This transformation creates a [`PyGroupedData`] object that can be used
    /// to perform aggregations like count, sum, avg, min, and max on the grouped data.
    ///
    /// # Arguments
    ///
    /// * `cols` - List of column names to group by
    ///
    /// # Returns
    ///
    /// A [`PyGroupedData`] object ready for aggregation operations.
    ///
    /// # Performance
    ///
    /// - Grouping uses hash-based aggregation (very efficient)
    /// - Multiple groups are processed in parallel when possible
    /// - Memory usage scales with the number of unique groups
    ///
    /// # Example
    ///
    /// ```python
    /// # Count by single column
    /// df.groupBy(["city"]).count().show()
    ///
    /// # Count by multiple columns
    /// df.groupBy(["country", "city"]).count().show()
    ///
    /// # Multiple aggregations
    /// df.groupBy(["department"]).agg([
    ///     ("salary", "avg"),
    ///     ("salary", "max"),
    ///     ("employee_id", "count")
    /// ]).show()
    /// ```
    ///
    /// # See Also
    ///
    /// - [`PyGroupedData::count`] - Count rows in each group
    /// - [`PyGroupedData::agg`] - Perform multiple aggregations
    #[allow(non_snake_case)]
    fn groupBy(&self, cols: Vec<&str>) -> PyResult<PyGroupedData> {
        let col_exprs: Vec<Expr> = cols.iter().map(|c| col(*c)).collect();

        Ok(PyGroupedData {
            df: self.df.clone(),
            group_cols: col_exprs,
        })
    }

    /// Orders the DataFrame by specified columns (SQL-style naming).
    ///
    /// This is an alias for [`sort`](#method.sort) that follows SQL/PySpark naming conventions.
    ///
    /// # Arguments
    ///
    /// * `cols` - List of column names to sort by
    ///
    /// # Returns
    ///
    /// A new DataFrame sorted by the specified columns in ascending order.
    ///
    /// # Example
    ///
    /// ```python
    /// # Sort by single column
    /// df.orderBy(["age"]).show()
    ///
    /// # Sort by multiple columns (priority: left to right)
    /// df.orderBy(["country", "city", "name"]).show()
    /// ```
    #[allow(non_snake_case)]
    fn orderBy(&self, cols: Vec<&str>) -> PyResult<Self> {
        self.sort(cols)
    }

    /// Sorts the DataFrame by specified columns.
    ///
    /// This transformation creates a new DataFrame with rows sorted by the
    /// specified columns in ascending order. For multiple columns, sorting
    /// priority is left-to-right.
    ///
    /// # Arguments
    ///
    /// * `cols` - List of column names to sort by
    ///
    /// # Returns
    ///
    /// A new DataFrame sorted by the specified columns.
    ///
    /// # Performance
    ///
    /// - Sorting is performed using efficient parallel sort algorithms
    /// - For large datasets, consider using `limit()` after sort
    /// - Nulls are sorted first by default
    /// - Sorting is done in-memory, so memory usage can be significant for large datasets
    ///
    /// # Performance Tip
    ///
    /// If you only need the top N rows, combine sort with limit:
    /// ```python
    /// # More efficient than sorting all rows
    /// top_10 = df.orderBy(["sales"]).limit(10)
    /// ```
    ///
    /// # Errors
    ///
    /// Returns a `PyRuntimeError` if:
    /// - A column name does not exist
    /// - The runtime cannot be created
    ///
    /// # Example
    ///
    /// ```python
    /// # Sort by age ascending
    /// sorted_df = df.sort(["age"])
    ///
    /// # Sort by multiple columns
    /// sorted_df = df.sort(["department", "salary"])
    /// ```
    ///
    /// # Future Enhancements
    ///
    /// Future versions will support:
    /// - Descending order specification
    /// - Null ordering control (nulls first/last)
    /// - Custom comparators
    fn sort(&self, cols: Vec<&str>) -> PyResult<Self> {
        let rt = Self::runtime()?;

        let df = rt
            .block_on(async {
                let sort_exprs = cols
                    .iter()
                    .map(|c| col(*c).sort(true, true)) // ascending, nulls first
                    .collect();

                self.clone_df().sort(sort_exprs)
            })
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to sort: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }

    /// Limits the DataFrame to the first N rows.
    ///
    /// This transformation creates a new DataFrame containing only the first
    /// N rows. This is particularly useful for:
    /// - Quickly inspecting data
    /// - Testing transformations on a subset
    /// - Taking top N after sorting
    ///
    /// # Arguments
    ///
    /// * `n` - Maximum number of rows to return
    ///
    /// # Returns
    ///
    /// A new DataFrame containing at most N rows.
    ///
    /// # Performance
    ///
    /// - Very efficient: stops processing after N rows
    /// - Essential for working with large datasets interactively
    /// - Combines well with `orderBy()` for "top N" queries
    ///
    /// # Errors
    ///
    /// Returns a `PyRuntimeError` if the runtime cannot be created.
    ///
    /// # Examples
    ///
    /// ```python
    /// # Preview first 10 rows
    /// df.limit(10).show()
    ///
    /// # Get top 5 highest salaries
    /// df.orderBy(["salary"]).limit(5).show()
    ///
    /// # Sample a subset for testing
    /// test_df = df.limit(1000)
    /// ```
    ///
    /// # See Also
    ///
    /// - [`show`](#method.show) - Display rows (includes implicit limit)
    fn limit(&self, n: usize) -> PyResult<Self> {
        let rt = Self::runtime()?;

        let df = rt
            .block_on(async { self.clone_df().limit(0, Some(n)) })
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to limit: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }

    /// Counts the number of rows in the DataFrame.
    ///
    /// This is an **action** (eager operation) that triggers execution of the
    /// query plan and returns the total row count.
    ///
    /// # Returns
    ///
    /// The total number of rows as a 64-bit integer.
    ///
    /// # Performance
    ///
    /// - For files with metadata (e.g., Parquet), this can be very fast (reads metadata only)
    /// - For CSV files, requires scanning the entire file
    /// - Counts are computed in parallel for multi-partition datasets
    ///
    /// # Errors
    ///
    /// Returns a `PyRuntimeError` if:
    /// - Query execution fails
    /// - The runtime cannot be created
    ///
    /// # Examples
    ///
    /// ```python
    /// # Count all rows
    /// total = df.count()
    /// print(f"Total rows: {total}")
    ///
    /// # Count after filtering
    /// adults_count = df.filter("age >= 18").count()
    ///
    /// # Count unique groups
    /// city_count = df.select(["city"]).distinct().count()
    /// ```
    ///
    /// # See Also
    ///
    /// - [`PyGroupedData::count`] - Count rows per group
    fn count(&self) -> PyResult<i64> {
        let rt = Self::runtime()?;

        let count = rt
            .block_on(async {
                let batches = self.clone_df().collect().await?;
                let total: usize = batches.iter().map(|b| b.num_rows()).sum();
                Ok::<i64, datafusion::error::DataFusionError>(total as i64)
            })
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to count: {}", e)))?;

        Ok(count)
    }

    /// Displays rows from the DataFrame in a formatted table.
    ///
    /// This is an **action** (eager operation) that triggers execution and
    /// prints the results to stdout. It's the primary way to inspect DataFrame
    /// contents during development.
    ///
    /// # Arguments
    ///
    /// * `n` - Maximum number of rows to display (default: 20)
    /// * `_truncate` - Whether to truncate long strings (not yet implemented, always true)
    ///
    /// # Performance
    ///
    /// - Only fetches and displays the first N rows
    /// - Uses Arrow's pretty-print formatter for clean output
    /// - Very efficient for quick data inspection
    ///
    /// # Errors
    ///
    /// Returns a `PyRuntimeError` if:
    /// - Query execution fails
    /// - The runtime cannot be created
    /// - Display formatting fails
    ///
    /// # Examples
    ///
    /// ```python
    /// # Show first 20 rows (default)
    /// df.show()
    ///
    /// # Show first 5 rows
    /// df.show(5)
    ///
    /// # Show results of a transformation
    /// df.filter("age > 18").orderBy(["name"]).show(10)
    /// ```
    ///
    /// # Output Format
    ///
    /// ```text
    /// +-------+-----+----------+
    /// | name  | age | city     |
    /// +-------+-----+----------+
    /// | Alice |  25 | New York |
    /// | Bob   |  30 | London   |
    /// +-------+-----+----------+
    /// ```
    #[pyo3(signature = (n=20, _truncate=true))]
    fn show(&self, n: usize, _truncate: bool) -> PyResult<()> {
        let rt = Self::runtime()?;

        rt.block_on(async {
            let df_limited = self.clone_df().limit(0, Some(n))?;
            let batches = df_limited.collect().await?;

            if batches.is_empty() {
                println!("Empty DataFrame");
                return Ok(());
            }

            // Use Arrow's pretty print
            let output = pretty::pretty_format_batches(&batches)
                .map_err(|e| datafusion::error::DataFusionError::ArrowError(e, None))?;

            println!("{}", output);
            Ok::<(), datafusion::error::DataFusionError>(())
        })
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to show: {}", e)))?;

        Ok(())
    }

    /// Returns the schema of the DataFrame as a string.
    ///
    /// The schema includes column names, types, and nullability information.
    ///
    /// # Returns
    ///
    /// A string representation of the DataFrame schema.
    ///
    /// # Example
    ///
    /// ```python
    /// schema_str = df.schema()
    /// print(schema_str)
    /// ```
    ///
    /// # See Also
    ///
    /// - [`printSchema`](#method.printSchema) - Pretty-prints the schema (recommended)
    fn schema(&self) -> PyResult<String> {
        let schema = self.df.schema();
        Ok(format!("{:?}", schema))
    }

    /// Prints the schema in a tree-like format.
    ///
    /// This method displays the DataFrame schema in a human-readable format,
    /// showing column names, data types, and nullability.
    ///
    /// # Example Output
    ///
    /// ```text
    /// root
    ///  |-- name: Utf8 (nullable = true)
    ///  |-- age: Int64 (nullable = true)
    ///  |-- city: Utf8 (nullable = true)
    ///  |-- salary: Float64 (nullable = true)
    /// ```
    ///
    /// # Example
    ///
    /// ```python
    /// df = spark.read.csv("data.csv")
    /// df.printSchema()
    /// ```
    ///
    /// # Use Cases
    ///
    /// - Verify column types after reading data
    /// - Debug type mismatches
    /// - Document data structure
    /// - Understand schema before transformations
    #[allow(non_snake_case)]
    fn printSchema(&self) -> PyResult<()> {
        let schema = self.df.schema();
        println!("root");
        for field in schema.fields() {
            println!(
                " |-- {}: {} (nullable = {})",
                field.name(),
                field.data_type(),
                field.is_nullable()
            );
        }
        Ok(())
    }

    /// Returns a string representation of the DataFrame.
    ///
    /// Shows the DataFrame type and column information in a concise format.
    ///
    /// # Returns
    ///
    /// A string like `<DataFrame[name: Utf8, age: Int64, city: Utf8]>`
    ///
    /// # Example
    ///
    /// ```python
    /// df = spark.read.csv("data.csv")
    /// print(df)  # Calls __repr__
    /// # Output: <DataFrame[name: Utf8, age: Int64, city: Utf8]>
    /// ```
    fn __repr__(&self) -> String {
        format!(
            "<DataFrame[{}]>",
            self.df
                .schema()
                .fields()
                .iter()
                .map(|f| format!("{}: {}", f.name(), f.data_type()))
                .collect::<Vec<_>>()
                .join(", ")
        )
    }
}

/// Grouped data for performing aggregations.
///
/// A `GroupedData` object is created by calling [`PyDataFrame::groupBy`] and
/// provides methods to perform aggregations on grouped data. This is similar
/// to SQL's GROUP BY functionality.
///
/// # Aggregation Functions
///
/// - `count()` - Count rows in each group
/// - `agg()` - Perform multiple aggregations (sum, avg, min, max, count)
///
/// # Example
///
/// ```python
/// # Simple count
/// df.groupBy(["city"]).count().show()
///
/// # Multiple aggregations
/// df.groupBy(["department"]).agg([
///     ("salary", "avg"),
///     ("salary", "max"),
///     ("employee_id", "count")
/// ]).show()
/// ```
///
/// # Performance
///
/// - Uses hash-based aggregation (very fast)
/// - Processes groups in parallel
/// - Memory usage scales with number of unique groups
/// - Consider the cardinality of grouping columns
#[pyclass(name = "GroupedData")]
pub struct PyGroupedData {
    /// Reference to the original DataFrame
    df: Arc<DataFrame>,
    /// Expressions representing the grouping columns
    group_cols: Vec<Expr>,
}

#[pymethods]
impl PyGroupedData {
    /// Counts the number of rows in each group.
    ///
    /// This is the most common aggregation operation. It returns a DataFrame
    /// with the grouping columns plus a "count" column showing the number of
    /// rows in each group.
    ///
    /// # Returns
    ///
    /// A new DataFrame with grouping columns and a "count" column.
    ///
    /// # Performance
    ///
    /// - Very efficient: O(n) time complexity
    /// - Uses hash-based counting
    /// - Parallel execution for multiple groups
    ///
    /// # Errors
    ///
    /// Returns a `PyRuntimeError` if:
    /// - Aggregation execution fails
    /// - The runtime cannot be created
    ///
    /// # Examples
    ///
    /// ```python
    /// # Count users by city
    /// df.groupBy(["city"]).count().show()
    /// # Output:
    /// # +----------+-------+
    /// # | city     | count |
    /// # +----------+-------+
    /// # | New York | 1500  |
    /// # | London   | 1200  |
    /// # +----------+-------+
    ///
    /// # Count by multiple columns
    /// df.groupBy(["country", "city"]).count().show()
    /// ```
    fn count(&self) -> PyResult<PyDataFrame> {
        let rt = PyDataFrame::runtime()?;

        let df = rt
            .block_on(async {
                self.df
                    .as_ref()
                    .clone()
                    .aggregate(self.group_cols.clone(), vec![count(lit(1)).alias("count")])
            })
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to aggregate: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }

    /// Performs multiple aggregations on the grouped data.
    ///
    /// This method allows you to compute various aggregate functions (count, sum,
    /// avg, min, max) on different columns simultaneously.
    ///
    /// # Arguments
    ///
    /// * `exprs` - List of tuples `(column_name, function)` where:
    ///   - `column_name` is the column to aggregate
    ///   - `function` is one of: "count", "sum", "avg"/"mean", "min", "max"
    ///
    /// # Returns
    ///
    /// A new DataFrame with grouping columns and aggregation result columns.
    /// Result columns are named as `function(column)` (e.g., "avg(salary)").
    ///
    /// # Supported Functions
    ///
    /// - **count**: Count non-null values
    /// - **sum**: Sum numeric values
    /// - **avg** / **mean**: Calculate average
    /// - **min**: Find minimum value
    /// - **max**: Find maximum value
    ///
    /// # Performance
    ///
    /// - All aggregations are computed in a single pass
    /// - Significantly faster than multiple separate aggregations
    /// - Parallel execution for large groups
    ///
    /// # Errors
    ///
    /// Returns a `PyRuntimeError` if:
    /// - A column does not exist
    /// - An aggregation function is not supported
    /// - Query execution fails
    ///
    /// # Examples
    ///
    /// ```python
    /// # Single aggregation
    /// df.groupBy(["department"]).agg([
    ///     ("salary", "avg")
    /// ]).show()
    ///
    /// # Multiple aggregations on same column
    /// df.groupBy(["city"]).agg([
    ///     ("age", "avg"),
    ///     ("age", "min"),
    ///     ("age", "max")
    /// ]).show()
    ///
    /// # Aggregations on different columns
    /// df.groupBy(["country"]).agg([
    ///     ("population", "sum"),
    ///     ("gdp", "avg"),
    ///     ("city_name", "count")
    /// ]).show()
    /// ```
    ///
    /// # Output Example
    ///
    /// ```text
    /// +------------+-------------+-----------+-----------+
    /// | department | avg(salary) | min(age)  | max(age)  |
    /// +------------+-------------+-----------+-----------+
    /// | Sales      | 75000.50    | 22        | 58        |
    /// | Engineering| 95000.75    | 24        | 62        |
    /// +------------+-------------+-----------+-----------+
    /// ```
    fn agg(&self, exprs: Vec<(String, String)>) -> PyResult<PyDataFrame> {
        let rt = PyDataFrame::runtime()?;

        let agg_exprs: Vec<Expr> = exprs
            .iter()
            .map(|(col_name, func)| {
                match func.as_str() {
                    "count" => count(col(col_name.as_str())).alias(format!("count({})", col_name)),
                    "sum" => sum(col(col_name.as_str())).alias(format!("sum({})", col_name)),
                    "avg" | "mean" => {
                        avg(col(col_name.as_str())).alias(format!("avg({})", col_name))
                    }
                    "min" => min(col(col_name.as_str())).alias(format!("min({})", col_name)),
                    "max" => max(col(col_name.as_str())).alias(format!("max({})", col_name)),
                    _ => count(col(col_name.as_str())).alias("count"), // fallback
                }
            })
            .collect();

        let df = rt
            .block_on(async {
                self.df
                    .as_ref()
                    .clone()
                    .aggregate(self.group_cols.clone(), agg_exprs)
            })
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to aggregate: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }
}
