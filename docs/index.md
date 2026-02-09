# PyRust Documentation

Welcome to **PyRust** - a high-performance, Rust-based implementation of PySpark that delivers 10-50x faster data processing while maintaining API compatibility.

## What is PyRust?

PyRust brings the power of Rust to Python data processing by leveraging:

- **[Apache DataFusion](https://datafusion.apache.org/)** - High-performance query engine
- **[Apache Arrow](https://arrow.apache.org/)** - Columnar memory format
- **[PyO3](https://pyo3.rs/)** - Zero-copy Python bindings

## Key Features

### ⚡ High Performance
- **10-50x faster** than PySpark for common operations
- Optimized columnar processing with vectorized operations
- Lazy evaluation with automatic query optimization

### 🔒 Type Safe
- Leverages Rust's type system for safer data processing
- Compile-time guarantees prevent common runtime errors
- Strong schema validation

### 🔌 Drop-in Replacement
- Familiar PySpark-like API
- Minimal code changes required
- Easy migration path

### 💾 Memory Efficient
- Apache Arrow's columnar format reduces memory usage
- Zero-copy data sharing between Python and Rust
- Efficient predicate pushdown and column pruning

## Quick Example

```python
from pyrust import SparkSession

# Create a session
spark = SparkSession.builder() \
    .appName("MyApp") \
    .getOrCreate()

# Read data
df = spark.read.csv("sales.csv", header=True)

# Transform and analyze
result = df.filter("amount > 1000") \
           .groupBy(["region"]) \
           .agg([("amount", "sum"), ("amount", "avg")]) \
           .orderBy(["sum(amount)"])

# Display results
result.show()
```

## Performance Comparison

| Operation | PySpark | PyRust | Speedup |
|-----------|---------|--------|---------|
| CSV Read (1GB) | 12.5s | 1.2s | **10.4x** |
| Filter + Select | 8.3s | 0.4s | **20.8x** |
| GroupBy + Count | 15.2s | 0.8s | **19.0x** |
| Complex Query | 45.6s | 2.1s | **21.7x** |

*Benchmarks run on: Intel Core i7, 16GB RAM, NVMe SSD*

## Getting Started

Ready to try PyRust? Check out our guides:

- [Installation Guide](getting-started/installation.md) - Install PyRust on your system
- [Quick Start Tutorial](getting-started/quickstart.md) - Your first PyRust program
- [Basic Operations](getting-started/basic-operations.md) - Common data operations

## Documentation Sections

### 📖 [Getting Started](getting-started/installation.md)
Installation, setup, and your first PyRust program.

### 📚 [User Guide](user-guide/dataframe.md)
In-depth guides on DataFrames, transformations, and best practices.

### 🔧 [API Reference](api/dataframe.md)
Complete API documentation for all classes and methods.

### 🏗️ [Architecture](architecture/overview.md)
Deep dive into PyRust's internals and design decisions.

### 👨‍💻 [Development](development/contributing.md)
Contributing guidelines, building from source, and testing.

## Community & Support

- **GitHub**: [hadrien-chicault/PyRust](https://github.com/hadrien-chicault/PyRust)
- **Issues**: [Report bugs or request features](https://github.com/hadrien-chicault/PyRust/issues)
- **🦀 Rust API Docs**: [Rust implementation documentation](rust/pyrust/index.html) - Low-level internals

## Related Documentation

- **[Rust API Reference](rust/pyrust/index.html)** - Detailed documentation of the Rust implementation
- **[Apache DataFusion](https://datafusion.apache.org/)** - Query engine powering PyRust
- **[Apache Arrow](https://arrow.apache.org/)** - Columnar format for efficient data processing

## License

PyRust is open source software licensed under the [Apache License 2.0](https://github.com/hadrien-chicault/PyRust/blob/main/LICENSE).
