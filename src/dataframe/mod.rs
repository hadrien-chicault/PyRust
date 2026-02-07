use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use datafusion::prelude::*;
use datafusion::arrow::util::pretty;
use datafusion::functions_aggregate::expr_fn::{count, sum, avg, min, max};
use std::sync::Arc;

/// DataFrame Rust implementation wrapping DataFusion DataFrame
#[pyclass(name = "DataFrame")]
#[derive(Clone)]
pub struct PyDataFrame {
    df: Arc<DataFrame>,
}

impl PyDataFrame {
    pub fn new(df: DataFrame) -> Self {
        Self {
            df: Arc::new(df),
        }
    }

    fn runtime() -> PyResult<tokio::runtime::Runtime> {
        tokio::runtime::Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))
    }

    fn clone_df(&self) -> DataFrame {
        self.df.as_ref().clone()
    }
}

#[pymethods]
impl PyDataFrame {
    /// Select columns
    fn select(&self, cols: Vec<&str>) -> PyResult<Self> {
        let rt = Self::runtime()?;

        let df = rt.block_on(async {
            let col_exprs: Vec<Expr> = cols.iter()
                .map(|c| col(*c))
                .collect();

            self.clone_df().select(col_exprs)
        })
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to select columns: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }

    /// Filter rows (alias: where)
    fn filter(&self, condition: &str) -> PyResult<Self> {
        // For POC, we support simple conditions like "age > 18"
        // In production, this would need a proper expression parser
        self.where_(condition)
    }

    /// Filter rows
    fn where_(&self, condition: &str) -> PyResult<Self> {
        let rt = Self::runtime()?;

        let df = rt.block_on(async {
            // Parse simple conditions
            // This is a simplified parser for the POC
            let parts: Vec<&str> = condition.split_whitespace().collect();
            if parts.len() != 3 {
                return Err(datafusion::error::DataFusionError::Plan(
                    format!("Invalid condition format: {}. Expected format: 'column op value'", condition)
                ));
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
                    _ => return Err(datafusion::error::DataFusionError::Plan(
                        format!("Unsupported operator: {}", op)
                    )),
                }
            } else if let Ok(num) = value_str.parse::<f64>() {
                match op {
                    ">" => col(col_name).gt(lit(num)),
                    "<" => col(col_name).lt(lit(num)),
                    ">=" => col(col_name).gt_eq(lit(num)),
                    "<=" => col(col_name).lt_eq(lit(num)),
                    "==" | "=" => col(col_name).eq(lit(num)),
                    "!=" => col(col_name).not_eq(lit(num)),
                    _ => return Err(datafusion::error::DataFusionError::Plan(
                        format!("Unsupported operator: {}", op)
                    )),
                }
            } else {
                // Treat as string, remove quotes if present
                let value = value_str.trim_matches('\'').trim_matches('"');
                match op {
                    "==" | "=" => col(col_name).eq(lit(value)),
                    "!=" => col(col_name).not_eq(lit(value)),
                    _ => return Err(datafusion::error::DataFusionError::Plan(
                        format!("Unsupported operator for string: {}", op)
                    )),
                }
            };

            self.clone_df().filter(expr)
        })
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to filter: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }

    /// Group by columns
    fn groupBy(&self, cols: Vec<&str>) -> PyResult<PyGroupedData> {
        let col_exprs: Vec<Expr> = cols.iter().map(|c| col(*c)).collect();

        Ok(PyGroupedData {
            df: self.df.clone(),
            group_cols: col_exprs,
        })
    }

    /// Order by columns
    fn orderBy(&self, cols: Vec<&str>) -> PyResult<Self> {
        self.sort(cols)
    }

    /// Sort by columns
    fn sort(&self, cols: Vec<&str>) -> PyResult<Self> {
        let rt = Self::runtime()?;

        let df = rt.block_on(async {
            let sort_exprs = cols.iter()
                .map(|c| col(*c).sort(true, true))  // ascending, nulls first
                .collect();

            self.clone_df().sort(sort_exprs)
        })
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to sort: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }

    /// Limit rows
    fn limit(&self, n: usize) -> PyResult<Self> {
        let rt = Self::runtime()?;

        let df = rt.block_on(async {
            self.clone_df().limit(0, Some(n))
        })
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to limit: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }

    /// Count rows
    fn count(&self) -> PyResult<i64> {
        let rt = Self::runtime()?;

        let count = rt.block_on(async {
            let batches = self.clone_df().collect().await?;
            let total: usize = batches.iter().map(|b| b.num_rows()).sum();
            Ok::<i64, datafusion::error::DataFusionError>(total as i64)
        })
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to count: {}", e)))?;

        Ok(count)
    }

    /// Show rows
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

    /// Get schema
    fn schema(&self) -> PyResult<String> {
        let schema = self.df.schema();
        Ok(format!("{:?}", schema))
    }

    /// Print schema
    fn printSchema(&self) -> PyResult<()> {
        let schema = self.df.schema();
        println!("root");
        for field in schema.fields() {
            println!(" |-- {}: {} (nullable = {})",
                     field.name(),
                     field.data_type(),
                     field.is_nullable());
        }
        Ok(())
    }

    fn __repr__(&self) -> String {
        format!("<DataFrame[{}]>",
                self.df.schema().fields()
                    .iter()
                    .map(|f| format!("{}: {}", f.name(), f.data_type()))
                    .collect::<Vec<_>>()
                    .join(", "))
    }
}

/// Grouped data for aggregations
#[pyclass(name = "GroupedData")]
pub struct PyGroupedData {
    df: Arc<DataFrame>,
    group_cols: Vec<Expr>,
}

#[pymethods]
impl PyGroupedData {
    /// Count aggregation
    fn count(&self) -> PyResult<PyDataFrame> {
        let rt = PyDataFrame::runtime()?;

        let df = rt.block_on(async {
            self.df.as_ref().clone()
                .aggregate(self.group_cols.clone(), vec![count(lit(1)).alias("count")])
        })
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to aggregate: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }

    /// General aggregation
    fn agg(&self, exprs: Vec<(&str, &str)>) -> PyResult<PyDataFrame> {
        let rt = PyDataFrame::runtime()?;

        let agg_exprs: Vec<Expr> = exprs.iter().map(|(col_name, func)| {
            match *func {
                "count" => count(col(*col_name)).alias(&format!("count({})", col_name)),
                "sum" => sum(col(*col_name)).alias(&format!("sum({})", col_name)),
                "avg" | "mean" => avg(col(*col_name)).alias(&format!("avg({})", col_name)),
                "min" => min(col(*col_name)).alias(&format!("min({})", col_name)),
                "max" => max(col(*col_name)).alias(&format!("max({})", col_name)),
                _ => count(col(*col_name)).alias("count"),  // fallback
            }
        }).collect();

        let df = rt.block_on(async {
            self.df.as_ref().clone().aggregate(self.group_cols.clone(), agg_exprs)
        })
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to aggregate: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }
}
