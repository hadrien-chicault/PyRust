# Basic Operations

This guide covers the fundamental operations you'll use in PyRust.

## Reading Data

### CSV Files

```python
# Basic CSV read
df = spark.read.csv("data.csv")

# With options
df = spark.read.csv(
    "data.csv",
    header=True,        # First row contains column names
    infer_schema=True   # Automatically detect column types
)
```

**CSV Options:**
- `header` (bool): Whether first row is header (default: `True`)
- `infer_schema` (bool): Automatically detect types (default: `True`)

### Parquet Files

```python
# Read Parquet file
df = spark.read.parquet("data.parquet")

# Read directory of Parquet files
df = spark.read.parquet("data_dir/")
```

**Why Parquet?**
- 5-10x smaller file size
- 10-100x faster reads for selective queries
- Schema preserved (no inference needed)
- Built-in compression and encoding

## Inspecting Data

### View Schema

```python
# Print schema in tree format
df.printSchema()

# Get schema as string
schema_str = df.schema()
print(schema_str)
```

### Display Rows

```python
# Show first 20 rows (default)
df.show()

# Show specific number of rows
df.show(5)
df.show(100)

# Count total rows
total = df.count()
print(f"Total rows: {total}")
```

## Selecting Columns

### Select Specific Columns

```python
# Select single column
names = df.select(["name"])

# Select multiple columns
subset = df.select(["name", "age", "city"])

# Reorder columns
reordered = df.select(["city", "name", "age"])
```

### Column Operations

```python
# Select all columns (rarely needed)
all_cols = df.select(df.columns)  # TODO: Not yet implemented

# Drop columns
# TODO: Not yet implemented in current version
```

## Filtering Rows

### Simple Filters

```python
# Single condition
adults = df.filter("age >= 18")
seniors = df.filter("age >= 65")

# Numeric comparisons
high_earners = df.filter("salary > 100000")
young_adults = df.filter("age > 18")
```

### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `>` | Greater than | `age > 18` |
| `<` | Less than | `age < 65` |
| `>=` | Greater or equal | `salary >= 50000` |
| `<=` | Less or equal | `age <= 30` |
| `==` | Equal | `status == 'active'` |
| `!=` | Not equal | `city != 'Unknown'` |

### String Filters

```python
# String equality (with quotes)
vip_customers = df.filter("status == 'VIP'")
ny_users = df.filter("city == 'New York'")

# String inequality
active = df.filter("status != 'inactive'")
```

## Sorting Data

### Sort Ascending

```python
# Sort by single column
sorted_df = df.orderBy(["age"])

# Sort by multiple columns (priority: left to right)
sorted_df = df.orderBy(["country", "city", "name"])

# Alternative: sort() method (identical)
sorted_df = df.sort(["age"])
```

### Sorting Tips

- Nulls are sorted first by default
- Descending sort not yet implemented (future feature)
- Combine with `limit()` for "top N" queries

## Limiting Results

### Limit Rows

```python
# First 10 rows
preview = df.limit(10)

# Top 5 after sorting
top_5 = df.orderBy(["sales"]).limit(5)

# Sample for testing
test_df = df.limit(1000)
```

**Use Cases:**
- Quick data preview
- Top N queries
- Testing transformations on small subset
- Reducing output size

## Grouping and Aggregation

### Simple Count

```python
# Count by single column
city_counts = df.groupBy(["city"]).count()
city_counts.show()
```

### Multiple Aggregations

```python
# Aggregate functions: count, sum, avg, min, max
stats = df.groupBy(["department"]).agg([
    ("salary", "avg"),
    ("salary", "min"),
    ("salary", "max"),
    ("employee_id", "count")
])
stats.show()
```

### Group by Multiple Columns

```python
# Multi-level grouping
summary = df.groupBy(["country", "city"]).agg([
    ("population", "sum"),
    ("age", "avg")
])
summary.show()
```

### Available Aggregation Functions

| Function | Description | Example |
|----------|-------------|---------|
| `count` | Count rows | `("id", "count")` |
| `sum` | Sum values | `("amount", "sum")` |
| `avg` / `mean` | Average | `("age", "avg")` |
| `min` | Minimum | `("salary", "min")` |
| `max` | Maximum | `("salary", "max")` |

## Chaining Operations

### Transformation Chain

Operations can be chained for complex workflows:

```python
result = df.select(["name", "age", "city", "salary"]) \
           .filter("age > 25") \
           .filter("salary > 50000") \
           .orderBy(["salary"]) \
           .limit(100)
```

### Lazy Evaluation

Transformations are **lazy** - they don't execute until an action is called:

```python
# These are lazy (just build query plan)
filtered = df.filter("age > 18")
selected = filtered.select(["name", "city"])
sorted_df = selected.orderBy(["name"])

# This triggers execution
sorted_df.show()  # Action!
```

**Actions that trigger execution:**
- `show()` - Display rows
- `count()` - Count rows
- `collect()` - Future: return all data to Python

## Complete Examples

### Example 1: Data Cleaning

```python
# Remove invalid rows and select relevant columns
clean_df = df.filter("age > 0") \
             .filter("age < 120") \
             .select(["name", "age", "email"]) \
             .orderBy(["age"])

print(f"Valid records: {clean_df.count()}")
clean_df.show(10)
```

### Example 2: Sales Analysis

```python
# Analyze sales by region
sales_summary = df.filter("amount > 0") \
                  .groupBy(["region"]) \
                  .agg([
                      ("amount", "sum"),
                      ("amount", "avg"),
                      ("transaction_id", "count")
                  ]) \
                  .orderBy(["sum(amount)"])

print("Sales Summary by Region:")
sales_summary.show()
```

### Example 3: User Segmentation

```python
# Find active users in top cities
active_users = df.filter("last_login_days < 30") \
                 .filter("age >= 18") \
                 .groupBy(["city"]) \
                 .count() \
                 .orderBy(["count"]) \
                 .limit(10)

print("Top 10 Cities by Active Users:")
active_users.show()
```

## Best Practices

### 1. Filter Early
```python
# Good
df.filter("age > 18").select(["name", "city"]).groupBy(["city"]).count()

# Less efficient
df.groupBy(["city"]).count().filter("count > 100")
```

### 2. Select Only Needed Columns
```python
# Good
df.select(["name", "age"]).filter("age > 18")

# Less efficient (processes all columns)
df.filter("age > 18")
```

### 3. Use Limit for Exploration
```python
# Quick preview
df.limit(100).show()

# Test on subset
df.limit(10000).filter("age > 18").groupBy(["city"]).count().show()
```

### 4. Chain Related Operations
```python
# Good - clear intent
result = df.filter("valid == true") \
           .select(["id", "value"]) \
           .orderBy(["value"]) \
           .limit(100)

# Avoid - unnecessary intermediate variables
filtered = df.filter("valid == true")
selected = filtered.select(["id", "value"])
sorted_df = selected.orderBy(["value"])
result = sorted_df.limit(100)
```

## Next Steps

- [DataFrame API Guide](../user-guide/dataframe.md) - Advanced DataFrame operations
- [Performance Tips](../user-guide/performance.md) - Optimize your queries
- [API Reference](../api/dataframe.md) - Complete method documentation
