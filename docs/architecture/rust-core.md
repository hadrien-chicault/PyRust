# Rust Core

Implementation details of PyRust's Rust core.

## Module Structure

```
src/
├── lib.rs              # PyO3 module definition
├── dataframe/
│   └── mod.rs         # DataFrame implementation
└── session/
    └── mod.rs         # SparkSession implementation
```

## Key Types

### PyDataFrame

Main DataFrame wrapper around DataFusion's DataFrame.

```rust
#[pyclass]
pub struct PyDataFrame {
    df: Arc<DataFrame>,  // Shared reference to DataFusion DataFrame
}
```

**Why Arc?**
- Cheap cloning for transformations
- Thread-safe sharing
- Immutability

### PySparkSession

Session management and DataFrame creation.

```rust
#[pyclass]
pub struct PySparkSession {
    ctx: Arc<SessionContext>,  // DataFusion context
}
```

## DataFusion Integration

PyRust uses Apache DataFusion for query execution:

```rust
use datafusion::prelude::*;
use datafusion::arrow::util::pretty;
```

### Query Execution Pattern

```rust
fn filter(&self, condition: &str) -> PyResult<Self> {
    let rt = Self::runtime()?;  // Tokio runtime

    let df = rt.block_on(async {
        self.clone_df()
            .filter(parse_condition(condition))?
            .await
    })?;

    Ok(PyDataFrame::new(df))
}
```

## Async Runtime

DataFusion is async, PyRust bridges to sync Python:

```rust
fn runtime() -> PyResult<Runtime> {
    Runtime::new()
        .map_err(|e| PyRuntimeError::new_err(
            format!("Failed to create runtime: {}", e)
        ))
}
```

**Pattern:**
1. Create Tokio runtime
2. `block_on()` async DataFusion calls
3. Return result to Python

## Error Handling

Rust errors → Python exceptions:

```rust
.map_err(|e| PyRuntimeError::new_err(
    format!("Failed to execute: {}", e)
))?
```

## PyO3 Bindings

### Method Decoration

```rust
#[pymethods]
impl PyDataFrame {
    fn select(&self, cols: Vec<&str>) -> PyResult<Self> {
        // Implementation
    }
}
```

### Python Module

```rust
#[pymodule]
fn pyrust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyDataFrame>()?;
    m.add_class::<PySparkSession>()?;
    Ok(())
}
```

## See Also

- [Architecture Overview](overview.md)
- [Python Bindings](python-bindings.md)
