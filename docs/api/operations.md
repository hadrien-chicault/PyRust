# Operations Reference

Quick reference for common DataFrame operations.

## Transformations (Lazy)

Transformations create new DataFrames without executing immediately.

| Operation | Method | Example |
|-----------|--------|---------|
| Select columns | `select()` | `df.select("name", "age")` |
| Filter rows | `filter()`, `where()` | `df.filter("age > 18")` |
| Sort | `orderBy()`, `sort()` | `df.orderBy("name")` |
| Limit rows | `limit()` | `df.limit(10)` |
| Remove duplicates | `distinct()` | `df.distinct()` |
| Drop duplicates by cols | `dropDuplicates()` | `df.dropDuplicates(["id"])` |
| Rename column | `withColumnRenamed()` | `df.withColumnRenamed("old", "new")` |

## Actions (Eager)

Actions trigger execution and return results.

| Operation | Method | Returns | Example |
|-----------|--------|---------|---------|
| Count rows | `count()` | int | `df.count()` |
| Display data | `show()` | None | `df.show(10)` |
| Show schema | `printSchema()` | None | `df.printSchema()` |

## Aggregations

Group and aggregate data.

| Operation | Method | Example |
|-----------|--------|---------|
| Group by | `groupBy()` | `df.groupBy("city")` |
| Count per group | `.count()` | `df.groupBy("city").count()` |
| Multiple aggs | `.agg()` | `df.groupBy("dept").agg(("salary", "avg"))` |
| Sum | `.sum()` | `df.groupBy("category").sum("amount")` |
| Average | `.avg()` | `df.groupBy("dept").avg("salary")` |
| Min/Max | `.min()`, `.max()` | `df.groupBy("product").max("price")` |

## Joins

Combine DataFrames.

| Join Type | Method | Example |
|-----------|--------|---------|
| Inner | `join()` | `df1.join(df2, on="id")` |
| Left outer | `join(how="left")` | `df1.join(df2, on="id", how="left")` |
| Right outer | `join(how="right")` | `df1.join(df2, on="id", how="right")` |
| Full outer | `join(how="outer")` | `df1.join(df2, on="id", how="outer")` |
| Semi | `join(how="semi")` | `df1.join(df2, on="id", how="semi")` |
| Anti | `join(how="anti")` | `df1.join(df2, on="id", how="anti")` |

## Set Operations

Combine DataFrames as sets.

| Operation | Method | Example |
|-----------|--------|---------|
| Union | `union()`, `unionAll()` | `df1.union(df2)` |
| Intersection | `intersect()` | `df1.intersect(df2)` |
| Difference | `exceptAll()`, `subtract()` | `df1.exceptAll(df2)` |

## SQL Operations

Execute SQL queries.

| Operation | Method | Example |
|-----------|--------|---------|
| Register view | `createOrReplaceTempView()` | `df.createOrReplaceTempView("users")` |
| Execute SQL | `spark.sql()` | `spark.sql("SELECT * FROM users")` |

## Common Patterns

### Filter and Aggregate

```python
df.filter("age > 25") \
  .groupBy("city") \
  .agg(("salary", "avg")) \
  .orderBy("city")
```

### Join and Select

```python
df1.join(df2, on="user_id") \
   .select("name", "age", "order_total")
```

### Complex Chain

```python
df.filter("status = 'active'") \
  .join(details, on="id", how="left") \
  .groupBy("category") \
  .count() \
  .orderBy("count") \
  .limit(10) \
  .show()
```

### Union and Deduplicate

```python
df1.union(df2) \
   .distinct() \
   .orderBy("date")
```

## See Also

- [DataFrame API](dataframe.md) - Detailed API reference
- [SparkSession API](context.md) - Session and reader methods
- [User Guide](../user-guide/dataframe.md) - Complete tutorials
