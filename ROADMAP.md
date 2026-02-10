# PyRust Roadmap

This document tracks PyRust's current status, known limitations, and planned features.

## Current Status (v0.3.0)

### ✅ Fully Implemented

**Core Operations:**
- DataFrame creation from CSV/Parquet
- Column selection (`select()`)
- Row filtering (`filter()`, `where()`)
- Sorting (`orderBy()`, `sort()`)
- Limiting results (`limit()`)
- Counting rows (`count()`)
- Display operations (`show()`, `printSchema()`)

**Aggregations:**
- Group by operations (`groupBy()`)
- Aggregate functions: `count()`, `sum()`, `avg()`, `min()`, `max()`
- Multiple aggregations with `agg()`

**Joins (All Types):**
- Inner join
- Left outer join
- Right outer join
- Full outer join
- Semi join (filtering)
- Anti join (filtering)
- Multi-column joins
- Automatic column deduplication

**Data Operations:**
- Remove duplicates (`distinct()`, `dropDuplicates()`)
- Union DataFrames (`union()`, `unionAll()`)
- Intersection (`intersect()`)
- Set difference (`exceptAll()`, `subtract()`)

**Column Operations:**
- Rename columns (`withColumnRenamed()`)

**SQL Support:**
- Execute SQL queries (`spark.sql()`)
- Temporary views (`createOrReplaceTempView()`)
- Full SQL query support

### ⚠️ Known Limitations

**1. Column Expressions**
- `select()` only accepts column names (strings), not expressions
- Cannot do: `df.select(col("price") * col("quantity"))`
- Cannot do: `df.select(mean("amount").alias("avg_amount"))`
- Workaround: Use SQL queries for complex expressions

**2. Column Manipulation**
- No `withColumn()` - cannot add/modify columns with expressions
- Cannot do: `df.withColumn("total", col("a") + col("b"))`
- Workaround: Use `withColumnRenamed()` for simple renames, SQL for complex operations

**3. Column Data Types**
- No `cast()` function for type conversion
- Schema inference only at read time
- Workaround: Use SQL CAST expressions

**4. Aggregation Functions**
- Limited to: count, sum, avg, min, max
- Missing: stddev, variance, percentile, etc.
- Workaround: Use SQL for advanced aggregations

**5. String/Date Functions**
- No built-in functions module (`pyrust.functions`)
- Cannot do: `upper(col("name"))`, `substring()`, `date_format()`
- Workaround: Use SQL string/date functions

**6. Window Functions**
- No window operations support
- Cannot do: `row_number().over(Window.partitionBy("category"))`
- Missing: rank, dense_rank, lag, lead, cumulative sums
- Workaround: Use SQL window functions

**7. Join Limitations**
- Only equality joins on column names
- No complex join conditions: `df1.join(df2, df1.col1 > df2.col2)`
- No broadcast joins optimization (yet)

**8. Write Operations**
- No DataFrame.write() support yet
- Cannot save results to CSV/Parquet from DataFrame API
- Workaround: Collect results and write manually

**9. Partitioning**
- No `repartition()` or `coalesce()`
- No control over data partitioning

**10. Caching**
- No `cache()` or `persist()`
- No optimization for reused DataFrames

## Planned Features

### 🎯 High Priority (Next Release)

**1. Expression System (Foundation)**
- Create `pyrust.functions` module
- Implement `col()`, `lit()` for column references
- Support expressions in `select()`: `df.select(col("a") + col("b"))`
- Add `alias()` for renaming expressions

**2. withColumn()**
- Add/modify columns with expressions
- `df.withColumn("total", col("price") * col("quantity"))`
- Enable column transformations

**3. Type Casting**
- `cast()` function for type conversion
- `df.select(col("age").cast("string"))`
- Proper type handling

**4. Basic Column Functions**
- String: `upper()`, `lower()`, `substring()`, `concat()`
- Math: `round()`, `ceil()`, `floor()`, `abs()`
- Date: `year()`, `month()`, `day()`, `current_date()`

### 🎯 Medium Priority

**5. Window Functions**
- `Window.partitionBy()`, `Window.orderBy()`
- Ranking: `row_number()`, `rank()`, `dense_rank()`
- Offset: `lag()`, `lead()`
- Aggregate windows: running sum, moving average

**6. Advanced Aggregations**
- `pivot()` for pivoting data
- `rollup()` and `cube()` for multi-dimensional aggregations
- More aggregate functions: `stddev()`, `variance()`, `percentile()`

**7. Write Operations**
- `df.write.csv()` to save as CSV
- `df.write.parquet()` to save as Parquet
- Write options (compression, partitioning)

**8. UDFs (User Defined Functions)**
- Python functions as UDFs
- `@udf` decorator
- Register and use custom functions

### 🎯 Lower Priority

**9. Broadcast Joins**
- Optimize joins for small tables
- Automatic broadcast for small DataFrames

**10. Caching & Persistence**
- `cache()` to cache DataFrames in memory
- `persist()` with storage levels
- `unpersist()` to free memory

**11. Partitioning Control**
- `repartition(n)` to change partition count
- `coalesce(n)` to reduce partitions
- `partitionBy()` for write operations

**12. Advanced Join Conditions**
- Non-equality joins
- Complex join expressions
- Join hints and optimizations

**13. Array/Map Operations**
- Array functions: `explode()`, `array_contains()`
- Map functions: `map_keys()`, `map_values()`
- Nested data structure support

**14. Null Handling**
- `fillna()`, `dropna()` for null values
- `isNull()`, `isNotNull()` functions
- `na.fill()`, `na.drop()` DataFrame methods

**15. Performance Optimizations**
- Predicate pushdown improvements
- Column pruning optimization
- Join reordering
- Cost-based optimization

## How to Contribute

See [CONTRIBUTING.md](development/contributing.md) for guidelines.

Priority areas for contribution:
1. **Expression System** - Most impactful for user experience
2. **Column Functions** - High user demand
3. **Window Functions** - Common use case
4. **Write Operations** - Complete the data pipeline

## Workarounds for Current Limitations

### Using SQL for Complex Operations

Many limitations can be worked around using SQL:

```python
# Instead of: df.select(col("price") * col("quantity").alias("total"))
# Use SQL:
df.createOrReplaceTempView("sales")
result = spark.sql("SELECT *, price * quantity as total FROM sales")

# Instead of: df.withColumn("total", col("a") + col("b"))
# Use SQL:
df.createOrReplaceTempView("data")
result = spark.sql("SELECT *, a + b as total FROM data")

# Window functions via SQL:
df.createOrReplaceTempView("orders")
result = spark.sql("""
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) as row_num
    FROM orders
""")
```

### Chaining Operations

Many complex operations can be achieved by chaining existing methods:

```python
# Calculate average by group
df.groupBy("category").agg(("price", "avg"))

# Filter, join, aggregate
df.filter("age > 18") \
  .join(other_df, on="user_id") \
  .groupBy("city") \
  .count()
```

## Version History

### v0.3.0 (Current)
- ✅ Data operations (distinct, union, intersect, except)
- ✅ Complete join support (all 6 types)
- ✅ Column renaming (withColumnRenamed)
- ✅ Comprehensive documentation

### v0.2.0
- ✅ Basic DataFrame operations
- ✅ SQL query support
- ✅ Aggregations with groupBy

### v0.1.0 (Initial POC)
- ✅ Read CSV/Parquet
- ✅ Basic transformations (select, filter, orderBy)
- ✅ Show and schema operations

## Timeline Estimates

**Next 3 Months:**
- Expression system and basic functions
- withColumn() implementation
- Type casting

**6 Months:**
- Window functions
- Write operations
- Advanced aggregations

**12 Months:**
- Complete PySpark API compatibility (80%+)
- Performance optimizations
- Production-ready features

## Feedback

Feature requests and prioritization feedback welcome at:
- GitHub Issues: https://github.com/hadrien-chicault/PyRust/issues
- Discussions: https://github.com/hadrien-chicault/PyRust/discussions

---

Last updated: 2026-02-10
