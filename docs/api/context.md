# SparkSession API Reference

API reference for SparkSession (context) operations.

## SparkSession

Main entry point for PyRust applications.

### Creating a Session

#### builder

Create a new SparkSession builder.

**Returns:** SparkSession.Builder

**Example:**
```python
from pyrust import SparkSession

spark = SparkSession.builder \
    .appName("MyApp") \
    .getOrCreate()
```

---

### Builder Methods

#### appName(name)

Set application name.

**Parameters:**
- `name` (str): Application name

**Returns:** Builder

**Example:**
```python
builder.appName("DataProcessing")
```

---

#### master(master_url)

Set master URL (for future distributed support).

**Parameters:**
- `master_url` (str): Master URL

**Returns:** Builder

**Example:**
```python
builder.master("local[*]")
```

---

#### getOrCreate()

Get existing session or create new one.

**Returns:** SparkSession

**Example:**
```python
spark = SparkSession.builder.appName("App").getOrCreate()
```

---

## Reading Data

### read

Access DataFrameReader for loading data.

**Returns:** DataFrameReader

**Example:**
```python
df = spark.read.csv("data.csv", header=True)
```

---

### DataFrameReader Methods

#### csv(path, header=False)

Read CSV file.

**Parameters:**
- `path` (str): File path
- `header` (bool): Whether first row is header

**Returns:** DataFrame

**Example:**
```python
df = spark.read.csv("users.csv", header=True)
```

---

#### parquet(path)

Read Parquet file.

**Parameters:**
- `path` (str): File path

**Returns:** DataFrame

**Example:**
```python
df = spark.read.parquet("data.parquet")
```

---

## SQL Operations

### sql(query)

Execute SQL query.

**Parameters:**
- `query` (str): SQL query string

**Returns:** DataFrame

**Example:**
```python
result = spark.sql("SELECT * FROM users WHERE age > 18")
```

---

### register_temp_view(df, name)

Register DataFrame as temporary view (internal method).

**Parameters:**
- `df` (DataFrame): DataFrame to register
- `name` (str): View name

**Returns:** None

---

## Session Management

### stop()

Stop the SparkSession.

**Returns:** None

**Example:**
```python
spark.stop()
```

---

## Complete Example

```python
from pyrust import SparkSession

# Create session
spark = SparkSession.builder \
    .appName("DataAnalysis") \
    .getOrCreate()

# Read data
df = spark.read.csv("sales.csv", header=True)

# Register for SQL
df.createOrReplaceTempView("sales")

# Execute SQL
result = spark.sql("""
    SELECT product, SUM(amount) as total
    FROM sales
    GROUP BY product
""")

result.show()

# Clean up
spark.stop()
```

---

## See Also

- [User Guide - Data Loading](../user-guide/data-loading.md)
- [User Guide - SQL Queries](../user-guide/sql-queries.md)
- [DataFrame API](dataframe.md)
