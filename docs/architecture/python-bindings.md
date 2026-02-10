# Python Bindings

How PyRust bridges Python and Rust using PyO3.

## PyO3 Framework

PyRust uses [PyO3](https://pyo3.rs/) for Python bindings:

- Zero-cost abstractions
- Type-safe conversions
- Automatic reference counting
- Native Python types

## Type Conversions

### Rust → Python

```rust
// String
let s: String = "hello".to_string();
// Becomes Python str

// Numbers
let n: i64 = 42;
// Becomes Python int

// DataFrame
let df: PyDataFrame = ...;
// Becomes Python object
```

### Python → Rust

```rust
fn select(&self, cols: Vec<&str>) -> PyResult<Self>
//              ↑ Python list → Rust Vec<&str>
```

## Class Wrapping

### Rust Struct

```rust
#[pyclass]
pub struct PyDataFrame {
    df: Arc<DataFrame>,
}
```

### Python Class

```python
# In Python, this becomes:
df = DataFrame(...)
```

## Method Binding

### Rust Methods

```rust
#[pymethods]
impl PyDataFrame {
    fn count(&self) -> PyResult<i64> {
        // Implementation
    }
}
```

### Python Methods

```python
# Callable from Python as:
total = df.count()
```

## Error Handling

### Rust Error Types

```rust
PyResult<T>  // Result that can cross Python boundary
PyErr        // Python exception
```

### Example

```rust
fn operation(&self) -> PyResult<DataFrame> {
    self.df.do_something()
        .map_err(|e| PyRuntimeError::new_err(
            format!("Operation failed: {}", e)
        ))
}
```

### In Python

```python
try:
    df.operation()
except RuntimeError as e:
    print(f"Error: {e}")
```

## Memory Management

### Reference Counting

PyO3 uses Python's reference counting:

```rust
#[pyclass]
struct PyDataFrame {
    df: Arc<DataFrame>,  // Shared ownership in Rust
}
```

When Python GC collects, Rust's Arc<> decrements.

### Zero-Copy Arrow

Arrow arrays shared without copying:

```rust
// Arrow batch created in Rust
let batch: RecordBatch = ...;

// Sent to Python via Arrow C API
// No data copying!
```

## Performance

### Function Call Overhead

- PyO3 calls: ~10-50ns
- Negligible for DataFrame operations
- Dominated by actual computation

### Data Transfer

- Column data: Zero-copy via Arrow
- Metadata: Small overhead
- Overall: Very efficient

## See Also

- [Architecture Overview](overview.md)
- [Rust Core](rust-core.md)
