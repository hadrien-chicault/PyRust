use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use datafusion::prelude::*;
use std::sync::Arc;

use crate::dataframe::PyDataFrame;

/// SparkSession Rust implementation
#[pyclass(name = "SparkSession")]
pub struct PySparkSession {
    ctx: SessionContext,
    app_name: String,
}

/// Builder for SparkSession
#[pyclass(name = "SparkSessionBuilder")]
pub struct PySparkSessionBuilder {
    app_name: Option<String>,
    master: Option<String>,
}

#[pymethods]
impl PySparkSessionBuilder {
    #[new]
    fn new() -> Self {
        Self {
            app_name: None,
            master: None,
        }
    }

    /// Set application name
    fn appName(&mut self, name: &str) -> Self {
        self.app_name = Some(name.to_string());
        Self {
            app_name: self.app_name.clone(),
            master: self.master.clone(),
        }
    }

    /// Set master URL (for compatibility, not used in POC)
    fn master(&mut self, url: &str) -> Self {
        self.master = Some(url.to_string());
        Self {
            app_name: self.app_name.clone(),
            master: self.master.clone(),
        }
    }

    /// Create or get SparkSession
    fn getOrCreate(&self) -> PyResult<PySparkSession> {
        let ctx = SessionContext::new();
        let app_name = self.app_name.clone().unwrap_or_else(|| "pyrust-app".to_string());

        Ok(PySparkSession {
            ctx,
            app_name,
        })
    }
}

/// DataFrameReader for reading data
#[pyclass(name = "DataFrameReader")]
pub struct PyDataFrameReader {
    session: Arc<SessionContext>,
}

#[pymethods]
impl PyDataFrameReader {
    /// Read CSV file
    #[pyo3(signature = (path, header=true, infer_schema=true))]
    fn csv(&self, path: &str, header: bool, infer_schema: bool) -> PyResult<PyDataFrame> {
        let ctx = self.session.clone();

        // Use tokio runtime to execute async datafusion operations
        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?;

        let df = rt.block_on(async {
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

    /// Read Parquet file
    fn parquet(&self, path: &str) -> PyResult<PyDataFrame> {
        let ctx = self.session.clone();

        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?;

        let df = rt.block_on(async {
            ctx.read_parquet(path, datafusion::prelude::ParquetReadOptions::default())
                .await
        })
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to read Parquet: {}", e)))?;

        Ok(PyDataFrame::new(df))
    }
}

#[pymethods]
impl PySparkSession {
    /// Get the builder
    #[staticmethod]
    fn builder() -> PySparkSessionBuilder {
        PySparkSessionBuilder::new()
    }

    /// Get DataFrameReader
    #[getter]
    fn read(&self) -> PyDataFrameReader {
        PyDataFrameReader {
            session: Arc::new(self.ctx.clone()),
        }
    }

    /// Get application name
    #[getter]
    fn appName(&self) -> String {
        self.app_name.clone()
    }

    /// Create DataFrame from data (placeholder for now)
    fn createDataFrame(&self, _data: Vec<Vec<PyObject>>) -> PyResult<PyDataFrame> {
        Err(PyRuntimeError::new_err("createDataFrame not yet implemented in POC"))
    }

    /// Stop the session
    fn stop(&self) {
        // In the POC, this is a no-op
        // In future versions, this would clean up resources
    }

    fn __repr__(&self) -> String {
        format!("<SparkSession(app='{}')>", self.app_name)
    }
}
