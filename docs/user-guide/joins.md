# Joins

PyRust provides comprehensive support for joining DataFrames using various join strategies. This guide covers all join types and best practices.

## Overview

Joins combine rows from two DataFrames based on a common column (or columns). PyRust supports all standard SQL join types.

## Join Types

### Inner Join (default)

Returns only rows that have matching values in both DataFrames:

```python
# Inner join on single column
result = df1.join(df2, on="user_id")

# Explicit inner join
result = df1.join(df2, on="user_id", how="inner")

# Join on multiple columns
result = df1.join(df2, on=["country", "city"])
```

**When to use:**
- You only want rows that exist in both DataFrames
- Finding matching records between two datasets
- Most common join type

### Left Join (Left Outer)

Returns all rows from the left DataFrame, with matching rows from the right (nulls where no match):

```python
result = df1.join(df2, on="user_id", how="left")
```

**When to use:**
- Keep all records from the primary DataFrame
- Add optional information from another DataFrame
- Find which left records have no match (nulls in right columns)

### Right Join (Right Outer)

Returns all rows from the right DataFrame, with matching rows from the left (nulls where no match):

```python
result = df1.join(df2, on="user_id", how="right")
```

**When to use:**
- Keep all records from the secondary DataFrame
- Less common (can usually be rewritten as left join by swapping DataFrames)

### Full Outer Join

Returns all rows from both DataFrames, with nulls where there's no match:

```python
result = df1.join(df2, on="user_id", how="outer")

# 'full' is an alias for 'outer'
result = df1.join(df2, on="user_id", how="full")
```

**When to use:**
- Find all records from both DataFrames
- Identify records unique to each DataFrame
- Data reconciliation and comparison

### Semi Join

Returns rows from the left DataFrame where there's a match in the right (only left columns):

```python
result = df1.join(df2, on="user_id", how="semi")
```

**When to use:**
- Filter left DataFrame based on existence in right
- More efficient than inner join when you don't need right columns
- "WHERE EXISTS" style queries

### Anti Join

Returns rows from the left DataFrame where there's NO match in the right:

```python
result = df1.join(df2, on="user_id", how="anti")
```

**When to use:**
- Find records that don't have a match
- Data validation (find missing records)
- "WHERE NOT EXISTS" style queries

## Basic Examples

### Simple Join

```python
from pyrust import SparkSession

spark = SparkSession.builder.appName("JoinExample").getOrCreate()

# Load datasets
users = spark.read.csv("users.csv", header=True)
orders = spark.read.csv("orders.csv", header=True)

# Join on user_id
result = users.join(orders, on="user_id")
result.show()
```

### Multi-Column Join

```python
# Join on multiple columns
df1 = spark.read.csv("sales_2023.csv", header=True)
df2 = spark.read.csv("sales_2024.csv", header=True)

# Join on both country and city
result = df1.join(df2, on=["country", "city"])
```

### String vs List

```python
# Single column - can use string
result = df1.join(df2, on="id")

# Multiple columns - use list
result = df1.join(df2, on=["country", "city"])
```

## Join Patterns

### Enriching Data

```python
# Add customer details to orders
orders = spark.read.csv("orders.csv", header=True)
customers = spark.read.csv("customers.csv", header=True)

enriched = orders.join(customers, on="customer_id", how="left")
enriched.show()
```

### Finding Missing Records

```python
# Find orders without shipping info
orders = spark.read.csv("orders.csv", header=True)
shipments = spark.read.csv("shipments.csv", header=True)

missing_shipments = orders.join(shipments, on="order_id", how="anti")
print(f"Orders not yet shipped: {missing_shipments.count()}")
```

### Data Validation

```python
# Find records in both datasets (validation)
expected = spark.read.csv("expected.csv", header=True)
actual = spark.read.csv("actual.csv", header=True)

# Records in both
correct = expected.join(actual, on="id", how="inner")

# Records only in expected (missing from actual)
missing = expected.join(actual, on="id", how="anti")

# Records only in actual (extra data)
extra = actual.join(expected, on="id", how="anti")
```

### Combining with Filters

```python
# Join then filter
result = users.join(orders, on="user_id") \
              .filter("order_amount > 100")

# Filter before join (more efficient)
high_value_orders = orders.filter("amount > 100")
result = users.join(high_value_orders, on="user_id")
```

### Chaining Joins

```python
# Join multiple DataFrames
users = spark.read.csv("users.csv", header=True)
orders = spark.read.csv("orders.csv", header=True)
products = spark.read.csv("products.csv", header=True)

result = users.join(orders, on="user_id") \
              .join(products, on="product_id")
```

## Column Deduplication

PyRust automatically deduplicates join key columns:

```python
df1 = spark.read.csv("users.csv", header=True)  # columns: id, name, age
df2 = spark.read.csv("details.csv", header=True)  # columns: id, email, phone

# Join on 'id' - the result will have 'id' only once
result = df1.join(df2, on="id")
# Result columns: id, name, age, email, phone
```

For joins, the join key appears only **once** in the result (from the left DataFrame).

## Handling Column Name Conflicts

If both DataFrames have columns with the same name (besides join keys), rename them first:

```python
# Both have 'status' column
orders = orders.withColumnRenamed("status", "order_status")
shipments = shipments.withColumnRenamed("status", "shipment_status")

# Now join without conflicts
result = orders.join(shipments, on="order_id")
```

## Performance Tips

### 1. Filter Before Joining

```python
# Good - reduce data before join
filtered_orders = orders.filter("amount > 100")
result = users.join(filtered_orders, on="user_id")

# Less efficient - filter after join
result = users.join(orders, on="user_id").filter("amount > 100")
```

### 2. Use Semi/Anti for Filtering

```python
# If you only need to filter (not add columns)
# Use semi join instead of inner join
active_users = users.join(recent_orders, on="user_id", how="semi")

# More efficient than
active_users = users.join(recent_orders, on="user_id") \
                    .select("user_id", "name", "email") \
                    .distinct()
```

### 3. Join on Specific Columns

```python
# Better - join on indexed/sorted columns
result = df1.join(df2, on="id")

# Less efficient - joining on multiple columns
result = df1.join(df2, on=["name", "email", "phone"])
```

### 4. Order Matters for Right Join

```python
# These are NOT equivalent
result1 = small_df.join(large_df, on="id", how="left")
result2 = large_df.join(small_df, on="id", how="right")

# But result1 ≈ result2 conceptually (column order differs)
```

## Common Patterns

### One-to-Many Join

```python
# One customer, many orders
customers = spark.read.csv("customers.csv", header=True)
orders = spark.read.csv("orders.csv", header=True)

result = customers.join(orders, on="customer_id")
# Each customer row is repeated for each order
```

### Many-to-Many Join

```python
# Students to courses (via enrollment table)
students = spark.read.csv("students.csv", header=True)
courses = spark.read.csv("courses.csv", header=True)
enrollments = spark.read.csv("enrollments.csv", header=True)

result = students.join(enrollments, on="student_id") \
                 .join(courses, on="course_id")
```

### Self Join

```python
# Find pairs of users from same city
users = spark.read.csv("users.csv", header=True)

# Rename columns to avoid conflicts
users1 = users.withColumnRenamed("name", "user1_name")
users2 = users.withColumnRenamed("name", "user2_name")

# Join on city
pairs = users1.join(users2, on="city")
```

### Lookup/Dimension Table

```python
# Enrich fact table with dimension data
fact_table = spark.read.csv("sales.csv", header=True)
dim_product = spark.read.csv("products.csv", header=True)
dim_customer = spark.read.csv("customers.csv", header=True)

enriched = fact_table.join(dim_product, on="product_id", how="left") \
                     .join(dim_customer, on="customer_id", how="left")
```

## Aggregations After Join

```python
# Join then aggregate
result = orders.join(customers, on="customer_id") \
               .groupBy("country") \
               .agg(("order_amount", "sum"))

# Show total sales by country
result.show()
```

## Error Handling

### Missing Join Keys

```python
try:
    result = df1.join(df2, on=None)
except RuntimeError:
    print("Join keys are required")
```

### Invalid Join Type

```python
try:
    result = df1.join(df2, on="id", how="invalid")
except RuntimeError:
    print("Invalid join type. Use: inner, left, right, outer, semi, anti")
```

## Comparison with PySpark

PyRust join API is compatible with PySpark:

```python
# These work the same in PyRust and PySpark
df1.join(df2, on="id")
df1.join(df2, on="id", how="left")
df1.join(df2, on=["col1", "col2"])
```

**Differences:**
- PyRust doesn't support join conditions (expressions) yet - only column names
- No broadcast joins yet (optimization for small tables)

## Method Summary

| Join Type | Method Call | Description |
|-----------|-------------|-------------|
| Inner | `df1.join(df2, on="id")` | Only matching rows |
| Left | `df1.join(df2, on="id", how="left")` | All left + matches |
| Right | `df1.join(df2, on="id", how="right")` | All right + matches |
| Outer/Full | `df1.join(df2, on="id", how="outer")` | All rows from both |
| Semi | `df1.join(df2, on="id", how="semi")` | Left where match exists |
| Anti | `df1.join(df2, on="id", how="anti")` | Left where no match |

## See Also

- [Set Operations](set-operations.md) - Union, intersect, except
- [SQL Queries](sql-queries.md) - SQL-based joins
- [Performance Tips](performance.md) - Join optimization strategies
