# DataFrame Guide

A comprehensive guide to working with PyRust DataFrames.

## What is a DataFrame?

A DataFrame is a distributed collection of data organized into named columns. It's conceptually similar to:
- A table in a relational database
- A Pandas DataFrame (but distributed)
- A spreadsheet with named columns

## Creating DataFrames

### From Files

```python
# CSV
df = spark.read.csv("data.csv", header=True, infer_schema=True)

# Parquet
df = spark.read.parquet("data.parquet")
```

### From Memory (Future Feature)

```python
# Not yet implemented
data = [["Alice", 25], ["Bob", 30]]
df = spark.createDataFrame(data, ["name", "age"])
```

## DataFrame Properties

### Schema

Every DataFrame has a schema defining column names and types:

```python
# View schema
df.printSchema()

# Output:
# root
#  |-- name: Utf8 (nullable = true)
#  |-- age: Int64 (nullable = true)
#  |-- salary: Float64 (nullable = true)
```

**Supported Types:**
- `Utf8` - String/text
- `Int64` - 64-bit integer
- `Float64` - 64-bit float
- `Boolean` - true/false
- `Date`, `Timestamp` - Date/time values

### Row Count

```python
count = df.count()  # Triggers execution
print(f"Total rows: {count}")
```

## Transformations

Transformations are **lazy** - they build a query plan but don't execute until an action is called.

### Select

Project specific columns:

```python
# Select columns
df.select(["name", "age"])

# Reorder columns
df.select(["age", "name", "city"])

# Select single column
df.select(["name"])
```

### Filter / Where

Keep rows matching a condition:

```python
# Numeric filters
df.filter("age > 18")
df.filter("salary >= 50000")
df.filter("score < 100")

# String filters
df.filter("city == 'New York'")
df.filter("status != 'inactive'")

# where() is an alias for filter()
df.where("age > 18")
```

**Limitation:** Currently only supports simple conditions (`column op value`). Complex conditions with AND/OR coming in future versions.

### Sort / OrderBy

Sort rows by column values:

```python
# Sort by single column
df.orderBy(["age"])

# Sort by multiple columns
df.orderBy(["country", "city", "name"])

# sort() is an alias for orderBy()
df.sort(["age"])
```

**Note:** Currently only ascending order supported. Descending order coming in future versions.

### Limit

Restrict number of rows:

```python
# First 10 rows
df.limit(10)

# Top 5 after sorting
df.orderBy(["sales"]).limit(5)
```

### GroupBy

Group rows for aggregation:

```python
# Count by group
df.groupBy(["city"]).count()

# Multiple aggregations
df.groupBy(["department"]).agg([
    ("salary", "avg"),
    ("salary", "max"),
    ("age", "min")
])

# Multi-level grouping
df.groupBy(["country", "city"]).count()
```

## Actions

Actions trigger execution and return results to Python.

### Show

Display rows in formatted table:

```python
# Default: 20 rows
df.show()

# Custom number
df.show(5)
df.show(100)
```

### Count

Return row count:

```python
total = df.count()
filtered_count = df.filter("age > 18").count()
```

### Collect (Future)

Return all data to Python (not yet implemented):

```python
# Future feature
rows = df.collect()  # Returns list of rows
```

## Complex Workflows

### Example 1: ETL Pipeline

```python
# Extract
raw_df = spark.read.csv("raw_data.csv", header=True)

# Transform
clean_df = raw_df.filter("valid == true") \
                 .select(["id", "name", "amount", "date"]) \
                 .filter("amount > 0") \
                 .orderBy(["date"])

# Load (Future: write to Parquet)
print(f"Processed {clean_df.count()} records")
clean_df.show(10)
```

### Example 2: Aggregation Report

```python
# Load data
sales = spark.read.parquet("sales.parquet")

# Multi-level aggregation
report = sales.filter("year == 2024") \
              .groupBy(["region", "product"]) \
              .agg([
                  ("amount", "sum"),
                  ("amount", "avg"),
                  ("transaction_id", "count")
              ]) \
              .orderBy(["region", "sum(amount)"])

# Display
print("2024 Sales Report:")
report.show(50)
```

### Example 3: Data Quality Check

```python
# Load data
df = spark.read.csv("user_data.csv", header=True)

# Check for data issues
print("=== Data Quality Report ===\n")

# Total records
print(f"Total records: {df.count()}")

# Age validation
invalid_age = df.filter("age < 0")
print(f"Invalid ages: {invalid_age.count()}")

# Missing cities (assuming empty strings)
missing_city = df.filter("city == ''")
print(f"Missing cities: {missing_city.count()}")

# Show problematic records
print("\nProblematic Records:")
df.filter("age < 0").show(10)
```

## Performance Optimization

### Filter Pushdown

Apply filters early to reduce data volume:

```python
# Good - filter early
df.filter("year == 2024") \
  .filter("valid == true") \
  .select(["name", "amount"]) \
  .groupBy(["name"]) \
  .count()

# Less efficient - filter late
df.groupBy(["name", "year"]) \
  .count() \
  .filter("year == 2024")
```

### Column Pruning

Select only needed columns:

```python
# Good - select early
df.select(["id", "amount"]) \
  .filter("amount > 1000") \
  .orderBy(["amount"])

# Less efficient - carries all columns
df.filter("amount > 1000") \
  .orderBy(["amount"])
```

### Limit for Exploration

Use limit() when exploring large datasets:

```python
# Fast preview
df.limit(1000).show()

# Test transformations on subset
df.limit(10000) \
  .filter("category == 'electronics'") \
  .groupBy(["brand"]) \
  .count() \
  .show()
```

## Common Patterns

### Top N Query

```python
# Top 10 highest values
top_10 = df.orderBy(["sales"]) \
           .limit(10) \
           .select(["product", "sales"])
top_10.show()
```

### Distinct Count

```python
# Count unique cities
unique_cities = df.select(["city"]) \
                  .distinct() \  # TODO: Not yet implemented
                  .count()
```

### Summary Statistics

```python
# Statistics by group
stats = df.groupBy(["category"]).agg([
    ("price", "min"),
    ("price", "max"),
    ("price", "avg"),
    ("product_id", "count")
])
stats.show()
```

## Working with Nulls

### Handling Nulls

```python
# Filter out nulls (future feature)
# df.filter("age IS NOT NULL")

# For now, use value checks
df.filter("age > 0")  # Assuming positive ages are valid
```

## Best Practices

### 1. Cache Intermediate Results (Future)

```python
# Future feature
# expensive_df = df.filter(...).select(...)
# expensive_df.cache()  # Reuse in memory
```

### 2. Understand Lazy Evaluation

```python
# These DON'T execute immediately
filtered = df.filter("age > 18")  # Lazy
selected = filtered.select(["name"])  # Lazy
sorted_df = selected.orderBy(["name"])  # Lazy

# This triggers execution of entire chain
sorted_df.show()  # Action!
```

### 3. Avoid Repeated Actions

```python
# Bad - counts twice (executes query twice)
count1 = df.filter("age > 18").count()
count2 = df.filter("age > 18").count()

# Good - store result
filtered = df.filter("age > 18")
count = filtered.count()
```

### 4. Use Parquet for Production

```python
# CSV: Good for ad-hoc analysis
df = spark.read.csv("data.csv")

# Parquet: Better for production (faster, smaller)
df = spark.read.parquet("data.parquet")
```

## Debugging

### View Query Plan (Future)

```python
# Future feature: df.explain()
```

### Print Intermediate Results

```python
# Check data at each step
step1 = df.filter("age > 18")
print(f"After filter: {step1.count()}")

step2 = step1.select(["name", "city"])
step2.show(5)

step3 = step2.groupBy(["city"]).count()
step3.show()
```

## Next Steps

- [Data Loading Guide](data-loading.md) - More on reading data
- [Performance Tips](performance.md) - Optimize your queries
- [API Reference](../api/dataframe.md) - Complete DataFrame API
