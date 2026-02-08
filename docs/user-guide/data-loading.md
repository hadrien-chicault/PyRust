# Data Loading Guide

Learn how to efficiently load data into PyRust DataFrames.

## Supported Formats

PyRust currently supports:
- **CSV** - Comma-separated values
- **Parquet** - Columnar format (recommended)

## CSV Files

### Basic CSV Loading

```python
# Simple read
df = spark.read.csv("data.csv")

# With header
df = spark.read.csv("data.csv", header=True)

# With schema inference
df = spark.read.csv("data.csv", header=True, infer_schema=True)
```

### CSV Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `header` | bool | `True` | First row contains column names |
| `infer_schema` | bool | `True` | Automatically detect column types |

### Schema Inference

When `infer_schema=True`, PyRust samples the first 1000 rows to detect types:

```python
df = spark.read.csv("data.csv", header=True, infer_schema=True)
df.printSchema()
# Output:
# root
#  |-- name: Utf8
#  |-- age: Int64
#  |-- salary: Float64
```

**Inference Rules:**
- Pure integers → `Int64`
- Numbers with decimals → `Float64`
- Text → `Utf8` (string)
- Dates (future) → `Date` or `Timestamp`

### Performance Tips for CSV

1. **Use Schema Inference Carefully**
   ```python
   # Fast: skip inference for known schema
   df = spark.read.csv("data.csv", header=True, infer_schema=False)
   ```

2. **Convert to Parquet**
   ```python
   # Read CSV once
   df = spark.read.csv("large_file.csv", header=True)

   # TODO: Write to Parquet (not yet implemented)
   # df.write.parquet("large_file.parquet")

   # Future reads will be much faster
   # df = spark.read.parquet("large_file.parquet")
   ```

## Parquet Files

### Basic Parquet Loading

```python
# Read single file
df = spark.read.parquet("data.parquet")

# Read directory of Parquet files
df = spark.read.parquet("data_dir/")
```

### Why Parquet?

**Advantages over CSV:**
- **10-100x faster** for selective queries
- **5-10x smaller** file size
- **Schema preserved** - no inference needed
- **Columnar format** - only read needed columns
- **Built-in compression** - automatic
- **Predicate pushdown** - filters applied during read

**Comparison Example:**

| Metric | CSV (1GB) | Parquet (200MB) |
|--------|-----------|-----------------|
| File Size | 1.0 GB | 0.2 GB (5x smaller) |
| Full Read | 12.5s | 1.2s (10x faster) |
| Select 2 cols | 11.8s | 0.3s (39x faster) |
| Filter + Select | 8.3s | 0.2s (41x faster) |

### Parquet Partitioning

Parquet files can be partitioned for even better performance:

```
data_dir/
  year=2023/
    month=01/
      data.parquet
    month=02/
      data.parquet
  year=2024/
    month=01/
      data.parquet
```

```python
# Read all partitions
df = spark.read.parquet("data_dir/")

# Filter automatically uses partitions
# Only reads data from 2024
df_2024 = df.filter("year == 2024")
```

## File Path Patterns

### Local Files

```python
# Absolute path
df = spark.read.csv("/home/user/data.csv")

# Relative path
df = spark.read.csv("./data/input.csv")
df = spark.read.csv("data.csv")
```

### Multiple Files (Future)

```python
# Future: Read multiple files
# df = spark.read.csv("data/*.csv")
# df = spark.read.csv(["file1.csv", "file2.csv"])
```

## Data Sources Best Practices

### 1. Choose the Right Format

| Use Case | Recommended Format |
|----------|-------------------|
| Ad-hoc analysis | CSV (easy to create/view) |
| Production pipelines | Parquet (fast, compressed) |
| One-time import | CSV (then convert to Parquet) |
| Archival storage | Parquet (compressed) |
| Human-readable | CSV |
| Machine-only | Parquet |

### 2. Optimize CSV Reading

```python
# For large CSVs, consider:
# 1. Enable schema inference
df = spark.read.csv("large.csv", header=True, infer_schema=True)

# 2. Save to Parquet for future use
# df.write.parquet("large.parquet")  # TODO
```

### 3. Leverage Parquet Features

```python
# Parquet automatically optimizes these operations:

# Only reads 'name' and 'age' columns
df = spark.read.parquet("data.parquet").select(["name", "age"])

# Filter is pushed down to file read
df = spark.read.parquet("data.parquet").filter("age > 18")

# Combines both optimizations
df = spark.read.parquet("data.parquet") \
       .select(["name", "age"]) \
       .filter("age > 18")
```

## Common Issues

### Issue 1: File Not Found

```python
# Error: file doesn't exist
df = spark.read.csv("missing.csv")
# RuntimeError: Failed to read CSV: ...

# Solution: Check path
import os
print(os.path.exists("data.csv"))  # True
df = spark.read.csv("data.csv")
```

### Issue 2: Encoding Problems

```python
# CSV with special characters may fail
# Future: add encoding parameter
# df = spark.read.csv("data.csv", encoding="utf-8")
```

### Issue 3: Large File Memory

```python
# If file is too large, filter early
df = spark.read.csv("huge.csv", header=True)
subset = df.limit(1000)  # Work with subset first
subset.show()
```

## Next Steps

- [DataFrame Guide](dataframe.md) - Working with loaded data
- [Performance Tips](performance.md) - Optimize data loading
- [API Reference](../api/dataframe.md) - Complete API documentation
