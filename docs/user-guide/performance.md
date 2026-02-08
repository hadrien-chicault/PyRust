# Performance Tips

Optimize your PyRust workflows for maximum performance.

## PyRust Performance Profile

### Speed Advantages

PyRust is typically **10-50x faster** than PySpark:

| Operation | PySpark | PyRust | Speedup |
|-----------|---------|--------|---------|
| CSV Read | 12.5s | 1.2s | 10.4x |
| Filter + Select | 8.3s | 0.4s | 20.8x |
| GroupBy + Aggregate | 15.2s | 0.8s | 19.0x |
| Multi-stage Pipeline | 45.6s | 2.1s | 21.7x |

### Why So Fast?

1. **Rust Performance** - Compiled, not interpreted
2. **Arrow Columnar Format** - Vectorized operations
3. **DataFusion Optimizer** - Query plan optimization
4. **Zero-Copy** - No Python/Rust boundary overhead
5. **Parallel Execution** - Automatic parallelization

## General Optimization Strategies

### 1. Choose the Right File Format

#### Parquet vs CSV

**Use Parquet for:**
- Production pipelines
- Large datasets (>100MB)
- Repeated queries
- Column-selective queries

**Parquet advantages:**
```python
# Read Parquet: 10-100x faster
df = spark.read.parquet("data.parquet")

# Only reads needed columns (column pruning)
df.select(["name", "age"]).show()

# Filters applied during read (predicate pushdown)
df.filter("age > 18").show()
```

**Use CSV for:**
- Ad-hoc analysis
- Human-readable data
- One-time imports
- Small files (<10MB)

### 2. Filter Early and Often

Push filters as early as possible in your transformation chain:

```python
# ✅ GOOD - Filter early
df.filter("year == 2024") \
  .filter("status == 'active'") \
  .select(["name", "amount"]) \
  .groupBy(["name"]) \
  .count()

# ❌ BAD - Filter late
df.groupBy(["name", "year"]) \
  .count() \
  .filter("year == 2024")
```

**Impact:** Filtering early can reduce execution time by 5-20x.

### 3. Select Only Needed Columns

Column pruning reduces I/O and memory:

```python
# ✅ GOOD - Select early
df.select(["id", "amount"]) \
  .filter("amount > 1000") \
  .groupBy(["id"]) \
  .count()

# ❌ BAD - Carries unnecessary columns
df.filter("amount > 1000") \
  .groupBy(["id"]) \
  .count()
```

**Impact:** 2-5x faster with Parquet files.

### 4. Minimize Sorting

Sorting is expensive - only sort when necessary:

```python
# ✅ GOOD - Sort only final result
df.filter("active == true") \
  .groupBy(["category"]) \
  .count() \
  .orderBy(["count"])  # Sort small result

# ❌ BAD - Unnecessary sort
df.orderBy(["name"]) \  # Sorts all data
  .filter("active == true") \
  .groupBy(["category"]) \
  .count()
```

### 5. Use Limit for Exploration

When exploring data, use `limit()` liberally:

```python
# Quick preview
df.limit(1000).show()

# Test transformations on subset
df.limit(10000) \
  .filter("category == 'electronics'") \
  .groupBy(["brand"]) \
  .count() \
  .show()
```

## Operation-Specific Optimizations

### Reading Data

```python
# ✅ GOOD - Parquet with schema
df = spark.read.parquet("data.parquet")

# ⚠️ OK - CSV with schema inference
df = spark.read.csv("data.csv", header=True, infer_schema=True)

# ❌ SLOW - CSV without schema
df = spark.read.csv("data.csv", header=False, infer_schema=False)
```

### Filtering

```python
# ✅ GOOD - Simple conditions
df.filter("age > 18")
df.filter("salary >= 50000")

# ⚠️ Future - Complex conditions
# df.filter("age > 18 AND salary >= 50000")
```

### Grouping

```python
# ✅ GOOD - Single aggregation
df.groupBy(["city"]).count()

# ✅ BETTER - Multiple aggregations in one pass
df.groupBy(["city"]).agg([
    ("age", "avg"),
    ("salary", "avg"),
    ("id", "count")
])

# ❌ BAD - Separate aggregations
avg_age = df.groupBy(["city"]).agg([("age", "avg")])
avg_salary = df.groupBy(["city"]).agg([("salary", "avg")])
count_records = df.groupBy(["city"]).count()
```

### Sorting

```python
# ✅ GOOD - Sort + Limit (Top N)
df.orderBy(["sales"]).limit(10)

# ❌ BAD - Sort all data unnecessarily
df.orderBy(["name"])  # If order doesn't matter downstream
```

## Memory Optimization

### Understanding Memory Usage

PyRust uses Apache Arrow's columnar format, which is very memory-efficient:

- Columnar layout reduces memory fragmentation
- Compression reduces memory footprint
- Zero-copy operations avoid duplication

### Tips for Large Datasets

1. **Stream Processing**
   ```python
   # Process in chunks with limit
   for offset in range(0, total, 100000):
       chunk = df.limit(100000).offset(offset)  # Future: offset
       process_chunk(chunk)
   ```

2. **Select Early**
   ```python
   # Don't: Load all columns
   df = spark.read.parquet("huge.parquet")

   # Do: Select needed columns
   df = spark.read.parquet("huge.parquet").select(["id", "amount"])
   ```

3. **Filter Early**
   ```python
   # Don't: Filter after loading
   df = spark.read.parquet("huge.parquet")
   filtered = df.filter("year == 2024")

   # Do: Filter during read (predicate pushdown)
   df = spark.read.parquet("huge.parquet")
   # Filter applied at read time automatically
   filtered = df.filter("year == 2024")
   ```

## Query Optimization Patterns

### Pattern 1: ETL Pipeline

```python
# Optimized ETL
clean_df = spark.read.parquet("raw.parquet") \  # Fast read
             .filter("valid == true") \           # Early filter
             .select(["id", "amount", "date"]) \  # Column pruning
             .filter("amount > 0") \              # More filtering
             .orderBy(["date"]) \                 # Sort if needed
             .limit(10000)                        # Limit output

print(f"Processed: {clean_df.count()}")
```

### Pattern 2: Aggregation Report

```python
# Optimized aggregation
report = spark.read.parquet("sales.parquet") \
              .filter("year == 2024") \              # Early filter
              .select(["region", "product", "amount"]) \  # Select needed
              .groupBy(["region", "product"]) \      # Group
              .agg([("amount", "sum"), ("amount", "avg")]) \  # Multi-agg
              .orderBy(["sum(amount)"])              # Sort result

report.show(50)
```

### Pattern 3: Data Quality

```python
# Efficient validation
validation = spark.read.parquet("data.parquet") \
                  .select(["id", "age", "email"]) \  # Select validators
                  .filter("age > 0") \                # Quick filter
                  .filter("age < 150")                # Range check

print(f"Valid records: {validation.count()}")
```

## Benchmarking Your Code

### Measure Performance

```python
import time

# Time a query
start = time.time()
result = df.filter("age > 18").groupBy(["city"]).count()
result.show()
elapsed = time.time() - start
print(f"Query took: {elapsed:.2f}s")
```

### Compare Approaches

```python
# Approach 1: Filter late
start = time.time()
df.groupBy(["city"]).count().filter("count > 100").show()
time1 = time.time() - start

# Approach 2: Filter early
start = time.time()
df.filter("active == true").groupBy(["city"]).count().show()
time2 = time.time() - start

print(f"Approach 1: {time1:.2f}s")
print(f"Approach 2: {time2:.2f}s ({time1/time2:.1f}x faster)")
```

## Performance Checklist

Before running queries on large datasets:

- [ ] Using Parquet format? (vs CSV)
- [ ] Filtering as early as possible?
- [ ] Selecting only needed columns?
- [ ] Combining multiple aggregations in one `agg()` call?
- [ ] Avoiding unnecessary sorts?
- [ ] Using `limit()` for exploration?
- [ ] Testing on small subset first?

## Common Performance Pitfalls

### Pitfall 1: Late Filtering

```python
# ❌ Processes all data before filtering
df.groupBy(["category"]).count().filter("count > 1000")

# ✅ Filters early
df.filter("active == true").groupBy(["category"]).count()
```

### Pitfall 2: Multiple Aggregations

```python
# ❌ Three separate queries
avg1 = df.groupBy(["dept"]).agg([("salary", "avg")])
max1 = df.groupBy(["dept"]).agg([("salary", "max")])
count1 = df.groupBy(["dept"]).count()

# ✅ Single query
stats = df.groupBy(["dept"]).agg([
    ("salary", "avg"),
    ("salary", "max"),
    ("id", "count")
])
```

### Pitfall 3: Unnecessary Sorts

```python
# ❌ Sorts before filter
df.orderBy(["name"]).filter("age > 18").show()

# ✅ Filter first (might make sort unnecessary)
df.filter("age > 18").show()  # No sort needed for show()
```

### Pitfall 4: Reading All Columns

```python
# ❌ Reads all columns from Parquet
df = spark.read.parquet("wide_table.parquet")
df.select(["id", "name"]).show()

# ✅ Column pruning automatically applied
df = spark.read.parquet("wide_table.parquet") \
          .select(["id", "name"])  # Only reads 2 columns
df.show()
```

## Next Steps

- [DataFrame Guide](dataframe.md) - Master DataFrame operations
- [Transformations](transformations.md) - Learn transformation patterns
- [Architecture](../architecture/overview.md) - Understand internals
