# Transformations Guide

Master PyRust's transformation operations for powerful data manipulation.

## Understanding Transformations

### Lazy Evaluation

Transformations don't execute immediately - they build a query plan:

```python
# None of these execute yet
df1 = df.filter("age > 18")        # Lazy
df2 = df1.select(["name", "city"]) # Lazy
df3 = df2.orderBy(["name"])        # Lazy

# This triggers execution
df3.show()  # Action! Executes entire chain
```

**Benefits:**
- Query optimization
- Efficient execution planning
- Reduced memory usage

### Transformations vs Actions

| Transformations (Lazy) | Actions (Eager) |
|------------------------|-----------------|
| `select()` | `show()` |
| `filter()` / `where_()` | `count()` |
| `orderBy()` / `sort()` | `collect()` (future) |
| `limit()` | |
| `groupBy()` | |

## Column Operations

### Selecting Columns

```python
# Select specific columns
df.select(["name", "age"])

# Reorder columns
df.select(["age", "name", "city"])

# Select all except (future feature)
# df.select(df.columns.except(["id"]))
```

### Renaming Columns (Future)

```python
# Future: Column renaming
# df.withColumnRenamed("old_name", "new_name")
```

### Adding Columns (Future)

```python
# Future: Computed columns
# df.withColumn("age_plus_10", col("age") + 10)
```

## Row Operations

### Filtering

#### Simple Conditions

```python
# Numeric comparisons
df.filter("age > 18")
df.filter("salary >= 50000")
df.filter("score < 100")

# String equality
df.filter("city == 'New York'")
df.filter("status == 'active'")

# String inequality
df.filter("country != 'USA'")
```

#### Multiple Filters

```python
# Chain filters (implicit AND)
df.filter("age > 18") \
  .filter("age < 65") \
  .filter("salary > 30000")

# Future: Combined conditions
# df.filter("age > 18 AND salary > 30000")
# df.filter("city == 'NYC' OR city == 'LA'")
```

### Sorting

```python
# Sort ascending
df.orderBy(["age"])

# Multiple columns (priority: left to right)
df.orderBy(["country", "city", "name"])

# Future: Descending order
# df.orderBy(col("age").desc())
```

### Limiting

```python
# First N rows
df.limit(10)

# Top N (combine with sort)
df.orderBy(["sales"]).limit(5)
```

### Deduplication (Future)

```python
# Future: Remove duplicates
# df.distinct()
# df.dropDuplicates(["email"])
```

## Aggregations

### Simple Count

```python
# Count by group
df.groupBy(["city"]).count()

# Multiple group columns
df.groupBy(["country", "city"]).count()
```

### Multiple Aggregations

```python
# Various aggregate functions
df.groupBy(["department"]).agg([
    ("salary", "sum"),
    ("salary", "avg"),
    ("salary", "min"),
    ("salary", "max"),
    ("employee_id", "count")
])
```

### Aggregation Functions

| Function | Description | Example Output Column |
|----------|-------------|----------------------|
| `count` | Count rows | `count(column)` |
| `sum` | Sum values | `sum(column)` |
| `avg` | Average | `avg(column)` |
| `mean` | Average (alias) | `avg(column)` |
| `min` | Minimum | `min(column)` |
| `max` | Maximum | `max(column)` |

## Transformation Patterns

### Pattern 1: Filter-Select-Sort

```python
# Extract specific data
result = df.filter("status == 'active'") \
           .select(["name", "email", "signup_date"]) \
           .orderBy(["signup_date"])
result.show()
```

### Pattern 2: Aggregate-Filter

```python
# Group and filter groups
summary = df.groupBy(["product"]) \
            .agg([("quantity", "sum")]) \
            .filter("sum(quantity) > 1000")
summary.show()
```

### Pattern 3: Multiple Groupings

```python
# Hierarchical aggregation
by_region = df.groupBy(["region"]).agg([("sales", "sum")])
by_city = df.groupBy(["region", "city"]).agg([("sales", "sum")])
by_store = df.groupBy(["region", "city", "store"]).agg([("sales", "sum")])
```

### Pattern 4: Top N per Group

```python
# Top 5 highest sales
top_sales = df.orderBy(["amount"]) \
              .limit(5)

# Future: Top N per category
# window = Window.partitionBy("category").orderBy(col("sales").desc())
# df.withColumn("rank", row_number().over(window)) \
#   .filter("rank <= 5")
```

## Optimization Strategies

### 1. Filter Pushdown

Push filters as early as possible:

```python
# Good - filter early
df.filter("year == 2024") \
  .select(["name", "amount"]) \
  .groupBy(["name"]) \
  .agg([("amount", "sum")])

# Less efficient - filter late
df.groupBy(["name", "year"]) \
  .agg([("amount", "sum")]) \
  .filter("year == 2024")
```

### 2. Column Pruning

Select only needed columns early:

```python
# Good - select early
df.select(["id", "amount", "date"]) \
  .filter("amount > 1000") \
  .groupBy(["date"]) \
  .agg([("amount", "sum")])

# Less efficient - all columns carried through
df.filter("amount > 1000") \
  .groupBy(["date"]) \
  .agg([("amount", "sum")])
```

### 3. Minimize Sorts

Sorting is expensive - only sort when necessary:

```python
# Good - sort only final result
df.filter("age > 18") \
  .groupBy(["city"]) \
  .count() \
  .orderBy(["count"])

# Less efficient - unnecessary intermediate sort
df.orderBy(["name"]) \
  .filter("age > 18") \
  .groupBy(["city"]) \
  .count()
```

### 4. Limit Early for Exploration

```python
# Quick exploration
df.limit(1000) \
  .filter("category == 'electronics'") \
  .groupBy(["brand"]) \
  .count() \
  .show()
```

## Advanced Patterns

### Conditional Aggregation (Future)

```python
# Future: Conditional sums
# df.groupBy(["product"]).agg(
#     sum(when(col("status") == "sold", col("amount"))).alias("sold_amount"),
#     sum(when(col("status") == "returned", col("amount"))).alias("returned_amount")
# )
```

### Window Functions (Future)

```python
# Future: Running totals, rankings
# window = Window.orderBy("date")
# df.withColumn("running_total", sum("amount").over(window))
```

### Joins (Future)

```python
# Future: Join DataFrames
# df1.join(df2, on="user_id", how="inner")
# df1.join(df2, df1.id == df2.user_id, how="left")
```

## Best Practices

1. **Filter Early, Often**
   - Apply filters before expensive operations
   - Reduces data volume throughout pipeline

2. **Select Only Needed Columns**
   - Reduces memory usage and I/O
   - Especially important with wide tables

3. **Understand Lazy Evaluation**
   - Transformations build a plan
   - Actions trigger execution
   - Multiple actions re-execute the plan

4. **Use Appropriate Aggregations**
   - `count()` for counting
   - `sum()` for totals
   - `avg()` for means
   - Combine multiple in single `agg()` call

5. **Test on Subsets**
   - Use `limit()` for quick validation
   - Test transformations on small data first

## Next Steps

- [Performance Guide](performance.md) - Optimize transformations
- [DataFrame API](dataframe.md) - Complete DataFrame guide
- [API Reference](../api/dataframe.md) - Method documentation
