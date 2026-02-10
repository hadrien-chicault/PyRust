# Current Limitations

PyRust is under active development. While it provides core DataFrame functionality, some features are not yet implemented.

## Overview

This page documents known limitations and provides workarounds. For a complete roadmap of planned features, see [ROADMAP.md](https://github.com/hadrien-chicault/PyRust/blob/main/ROADMAP.md).

## Major Limitations

### 1. Column Expressions Not Supported

**What's missing:**
- Cannot use expressions in `select()`
- No column arithmetic or transformations
- No function calls on columns

**Examples that DON'T work:**
```python
from pyrust.functions import col, mean  # Module doesn't exist yet

# This will fail
df.select(col("price") * col("quantity"))

# This will fail
df.select(mean("amount").alias("avg_amount"))

# This will fail
df.select(col("name").upper())
```

**Workaround - Use SQL:**
```python
# Instead, use SQL
df.createOrReplaceTempView("data")
result = spark.sql("SELECT price * quantity as total FROM data")

# Or for aggregations
result = spark.sql("SELECT AVG(amount) as avg_amount FROM data")
```

**Workaround - Use groupBy for aggregations:**
```python
# For simple aggregations
df.groupBy().agg(("amount", "avg"))
```

### 2. No withColumn()

**What's missing:**
- Cannot add new columns with expressions
- Cannot modify existing columns with transformations

**Examples that DON'T work:**
```python
# This will fail
df = df.withColumn("total", col("price") * col("quantity"))

# This will fail
df = df.withColumn("upper_name", col("name").upper())
```

**Workaround - Use SQL:**
```python
df.createOrReplaceTempView("sales")
result = spark.sql("SELECT *, price * quantity as total FROM sales")
```

**Workaround - Use withColumnRenamed for simple cases:**
```python
# If you just need to rename
df = df.withColumnRenamed("old_name", "new_name")
```

### 3. No Window Functions

**What's missing:**
- No `Window.partitionBy()` or `Window.orderBy()`
- No ranking functions: `row_number()`, `rank()`, `dense_rank()`
- No offset functions: `lag()`, `lead()`
- No cumulative aggregations

**Examples that DON'T work:**
```python
from pyrust.window import Window  # Doesn't exist

# This will fail
window = Window.partitionBy("category").orderBy("date")
df = df.select("*", row_number().over(window).alias("row_num"))
```

**Workaround - Use SQL:**
```python
df.createOrReplaceTempView("orders")
result = spark.sql("""
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) as row_num,
           LAG(amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date) as prev_amount
    FROM orders
""")
```

### 4. No Type Casting

**What's missing:**
- No `cast()` function
- Cannot change column data types
- Schema is determined at read time only

**Examples that DON'T work:**
```python
# This will fail
df.select(col("age").cast("string"))
```

**Workaround - Use SQL:**
```python
df.createOrReplaceTempView("data")
result = spark.sql("SELECT CAST(age AS STRING) as age_str FROM data")
```

### 5. Limited Aggregation Functions

**What's available:**
- ✅ count, sum, avg, min, max

**What's missing:**
- stddev, variance
- percentile, median
- first, last
- collect_list, collect_set

**Workaround - Use SQL:**
```python
result = spark.sql("""
    SELECT category,
           STDDEV(price) as price_stddev,
           PERCENTILE(price, 0.5) as price_median
    FROM products
    GROUP BY category
""")
```

### 6. No String/Date Functions

**What's missing:**
- String: `upper()`, `lower()`, `substring()`, `concat()`, `trim()`
- Date: `year()`, `month()`, `day()`, `date_format()`
- Math: `round()`, `ceil()`, `floor()`, `abs()`

**Workaround - Use SQL:**
```python
result = spark.sql("""
    SELECT UPPER(name) as name_upper,
           SUBSTRING(description, 1, 10) as desc_short,
           YEAR(date) as year
    FROM data
""")
```

### 7. No Write Operations

**What's missing:**
- Cannot save DataFrames to files
- No `df.write.csv()` or `df.write.parquet()`

**Workaround:**
```python
# Collect to Python and save manually
import csv

data = []
# Note: Collecting large datasets not recommended
# This is just for small results
result.show()  # Display instead
```

### 8. No Caching/Persistence

**What's missing:**
- No `cache()` or `persist()`
- DataFrames are recomputed each time

**Workaround:**
- Keep queries simple
- Avoid reusing expensive computations
- Consider using SQL CTEs for complex queries

### 9. No Complex Join Conditions

**What's available:**
- ✅ Equality joins on column names

**What's missing:**
- Non-equality joins
- Complex join expressions

**Examples that DON'T work:**
```python
# This will fail
df1.join(df2, df1["price"] > df2["min_price"])
```

**Workaround - Use SQL:**
```python
df1.createOrReplaceTempView("products")
df2.createOrReplaceTempView("ranges")
result = spark.sql("""
    SELECT p.*, r.category
    FROM products p
    JOIN ranges r ON p.price > r.min_price AND p.price <= r.max_price
""")
```

### 10. Select Only Accepts Strings

**What's available:**
```python
# This works
df.select("name", "age", "city")
```

**What doesn't work:**
```python
# This fails
df.select(col("name"), col("age"))

# This fails
df.select([col("price") * col("qty")])
```

**Workaround:**
```python
# Use SQL for transformations
df.createOrReplaceTempView("data")
result = spark.sql("SELECT name, age, price * qty as total FROM data")

# Or use separate operations
df.select("name", "age").show()
```

## General Workaround: Use SQL

For most limitations, SQL provides a powerful workaround:

```python
from pyrust import SparkSession

spark = SparkSession.builder.appName("SQLWorkaround").getOrCreate()

# Load data
df = spark.read.csv("data.csv", header=True)

# Register as temp view
df.createOrReplaceTempView("mydata")

# Use SQL for complex operations
result = spark.sql("""
    SELECT
        customer_id,
        UPPER(name) as name_upper,
        price * quantity as total,
        AVG(price) OVER (PARTITION BY category ORDER BY date) as running_avg,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY date DESC) as recent_order
    FROM mydata
    WHERE price > 100
""")

result.show()
```

## Feature Priorities

See [ROADMAP.md](https://github.com/hadrien-chicault/PyRust/blob/main/ROADMAP.md) for:
- Complete list of planned features
- Timeline estimates
- How to contribute

**High Priority:**
1. Expression system (`col()`, `lit()`, operators)
2. `withColumn()` for column transformations
3. Type casting (`cast()`)
4. Basic column functions (string, math, date)

**Medium Priority:**
5. Window functions
6. Write operations
7. Advanced aggregations (pivot, rollup)
8. UDFs

## Contributing

Want to help implement these features? See [CONTRIBUTING.md](development/contributing.md).

## Questions?

- Check existing [Issues](https://github.com/hadrien-chicault/PyRust/issues)
- Start a [Discussion](https://github.com/hadrien-chicault/PyRust/discussions)
- Read the [User Guide](user-guide/dataframe.md)
