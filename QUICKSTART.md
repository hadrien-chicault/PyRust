# PyRust Quick Start Guide

Welcome to PyRust! This guide will help you get started in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- Rust 1.70 or higher
- Linux/macOS (Windows via WSL)

## Installation

### 1. Clone and Setup

```bash
cd /root/pyrust

# Create virtual environment
uv venv  # or: python3 -m venv .venv

# Activate environment
source .venv/bin/activate

# Install dependencies
uv pip install maturin pyarrow pytest  # or use pip
```

### 2. Build PyRust

```bash
# Development build (faster compilation)
maturin develop

# Or release build (optimized, recommended)
maturin develop --release --uv
```

This will:
- Compile the Rust code
- Generate Python bindings
- Install PyRust in your virtual environment

**Note**: First build takes ~6 minutes. Subsequent builds are much faster.

## Your First PyRust Program

Create a file `hello_pyrust.py`:

```python
from pyrust import SparkSession

# Create session
spark = SparkSession.builder \
    .appName("Hello PyRust") \
    .getOrCreate()

# Create sample data (CSV file)
data_content = """name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,New York"""

with open("sample.csv", "w") as f:
    f.write(data_content)

# Load and process data
df = spark.read.csv("sample.csv", header=True)

print("Original Data:")
df.show()

print("\nFiltered (age > 26):")
df.filter("age > 26").show()

print("\nGroup by city:")
df.groupBy("city").count().show()

# Clean up
spark.stop()
```

Run it:
```bash
python hello_pyrust.py
```

## Run Examples

PyRust includes a comprehensive example:

```bash
python examples/basic_operations.py
```

This demonstrates:
- Reading CSV files
- Selecting columns
- Filtering rows
- Grouping and aggregation
- Sorting
- Method chaining

## Run Tests

```bash
# All tests
pytest python/tests/ -v

# Specific test file
pytest python/tests/test_dataframe.py -v

# Specific test
pytest python/tests/test_dataframe.py::TestDataFrameOperations::test_filter_numeric -v
```

## Common Operations

### Reading Data

```python
from pyrust import SparkSession

spark = SparkSession.builder.appName("My App").getOrCreate()

# Read CSV
df = spark.read.csv("data.csv", header=True, inferSchema=True)

# Read Parquet
df = spark.read.parquet("data.parquet")
```

### Selecting Columns

```python
# Select specific columns
df.select("name", "age").show()

# Select and rename (not yet implemented in POC)
# Coming in Phase 2
```

### Filtering

```python
# Numeric filter
df.filter("age > 25").show()

# Equality
df.filter("city == 'New York'").show()

# Multiple filters (chain them)
df.filter("age > 25").filter("city == 'New York'").show()
```

### Aggregations

```python
# Group by and count
df.groupBy("city").count().show()

# Group by with multiple aggregations
df.groupBy("city").agg(
    ("age", "avg"),
    ("salary", "sum")
).show()

# Using aggregation methods
df.groupBy("city").avg("age").show()
df.groupBy("city").sum("salary").show()
```

### Sorting

```python
# Sort by column
df.orderBy("age").show()

# Multiple columns
df.orderBy("city", "age").show()

# Alias: sort()
df.sort("age").show()
```

### Limiting

```python
# Get first N rows
df.limit(10).show()
```

### Chaining Operations

```python
# Combine multiple operations
result = df \
    .filter("age > 25") \
    .select("name", "city") \
    .groupBy("city") \
    .count() \
    .orderBy("city") \
    .limit(10)

result.show()
```

### Inspecting Data

```python
# Show first 20 rows
df.show()

# Show first N rows
df.show(10)

# Print schema
df.printSchema()

# Get row count
count = df.count()
print(f"Total rows: {count}")
```

## API Differences from PySpark

PyRust aims for PySpark compatibility, but the POC has some limitations:

### ✅ Supported (POC)
- Basic DataFrame operations
- CSV and Parquet reading
- Filtering with simple conditions
- Group by and aggregations
- Sorting and limiting

### 🚧 Coming Soon (Phase 2)
- Complex expressions (Column objects)
- Joins (inner, left, right, full)
- UDFs (User Defined Functions)
- Window functions
- SQL queries
- More data sources (JSON, ORC)

### 📋 Planned (Phase 3+)
- Distributed execution
- RDD API
- MLlib operations
- Streaming

## Troubleshooting

### Build Fails

```bash
# Clean build
cargo clean
rm -rf target/
maturin develop --release --uv
```

### Import Error

```bash
# Ensure you're in the virtual environment
source .venv/bin/activate

# Reinstall
maturin develop --uv
```

### Rust Not Found

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

### Module Not Found

```python
# Make sure you built the project first
# maturin develop --uv

# Verify installation
python -c "import pyrust; print(pyrust.__version__)"
```

## Performance Tips

1. **Use Release Build**: Always use `--release` for benchmarking
   ```bash
   maturin develop --release --uv
   ```

2. **Parquet Over CSV**: Parquet is much faster for large datasets
   ```python
   # Convert CSV to Parquet (using pandas temporarily)
   import pandas as pd
   pd.read_csv("data.csv").to_parquet("data.parquet")

   # Read with PyRust
   df = spark.read.parquet("data.parquet")
   ```

3. **Filter Early**: Apply filters before expensive operations
   ```python
   # Good: filter first
   df.filter("age > 25").groupBy("city").count()

   # Less efficient: filter after
   df.groupBy("city").count()  # processes all data
   ```

4. **Select Only Needed Columns**: Reduce data volume
   ```python
   # Only load columns you need
   df.select("name", "age").filter("age > 25")
   ```

## Next Steps

- Read [README.md](README.md) for project overview
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- See [POC_VALIDATION.md](POC_VALIDATION.md) for test results
- Review the [plan](/root/.claude/plans/dapper-jingling-knuth.md) for future roadmap

## Getting Help

- **Issues**: Report bugs or request features on GitHub
- **Questions**: Check documentation first, then ask on GitHub Discussions
- **Contributing**: See CONTRIBUTING.md (coming soon)

## What's Next?

Try these challenges:

1. **Load your own data**: Replace `sample.csv` with your dataset
2. **Complex queries**: Chain multiple operations together
3. **Performance test**: Compare speed with PySpark (coming in Phase 2)
4. **Explore examples**: Run and modify `examples/basic_operations.py`

Happy coding with PyRust! 🦀🐍
