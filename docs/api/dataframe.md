# DataFrame API Reference

Complete API reference for PyRust DataFrame operations.

## Core Methods

### Creation & Loading

DataFrames are typically created through `SparkSession.read`:

```python
df = spark.read.csv("data.csv", header=True)
df = spark.read.parquet("data.parquet")
```

---

### select(*cols)

Select columns from the DataFrame.

**Parameters:**
- `*cols` (str): Column names to select

**Returns:** DataFrame

**Example:**
```python
df.select("name", "age", "city")
```

---

### filter(condition) / where(condition)

Filter rows based on a condition.

**Parameters:**
- `condition` (str): SQL-like filter expression

**Returns:** DataFrame

**Example:**
```python
df.filter("age > 18")
df.where("salary >= 50000")
```

---

### groupBy(*cols)

Group DataFrame by specified columns.

**Parameters:**
- `*cols` (str): Column names to group by

**Returns:** GroupedData

**Example:**
```python
df.groupBy("city").count()
df.groupBy("department", "year").agg(("salary", "avg"))
```

---

### join(other, on, how="inner")

Join with another DataFrame.

**Parameters:**
- `other` (DataFrame): DataFrame to join with
- `on` (str or list): Column name(s) to join on
- `how` (str): Join type - "inner", "left", "right", "outer", "semi", "anti"

**Returns:** DataFrame

**Example:**
```python
df1.join(df2, on="user_id")
df1.join(df2, on=["country", "city"], how="left")
```

See [Joins Guide](../user-guide/joins.md) for detailed documentation.

---

### orderBy(*cols) / sort(*cols)

Sort DataFrame by specified columns.

**Parameters:**
- `*cols` (str): Column names to sort by

**Returns:** DataFrame

**Example:**
```python
df.orderBy("age")
df.sort("department", "salary")
```

---

### distinct()

Remove duplicate rows.

**Returns:** DataFrame

**Example:**
```python
df.distinct()
```

---

### dropDuplicates(subset=None)

Remove duplicates based on specified columns.

**Parameters:**
- `subset` (list, optional): Column names to consider. If None, uses all columns.

**Returns:** DataFrame

**Aliases:** `drop_duplicates()`

**Example:**
```python
df.dropDuplicates(["user_id"])
df.drop_duplicates(["email"])
```

---

### union(other) / unionAll(other)

Combine DataFrames vertically (append rows).

**Parameters:**
- `other` (DataFrame): DataFrame to union with

**Returns:** DataFrame

**Example:**
```python
df1.union(df2)
df1.unionAll(df2)  # Same as union()
```

---

### intersect(other)

Return rows that exist in both DataFrames.

**Parameters:**
- `other` (DataFrame): DataFrame to intersect with

**Returns:** DataFrame

**Example:**
```python
df1.intersect(df2)
```

---

### exceptAll(other) / subtract(other)

Return rows in this DataFrame but not in other.

**Parameters:**
- `other` (DataFrame): DataFrame to subtract

**Returns:** DataFrame

**Example:**
```python
df1.exceptAll(df2)
df1.subtract(df2)  # Alias
```

---

### withColumnRenamed(existing, new)

Rename a column.

**Parameters:**
- `existing` (str): Current column name
- `new` (str): New column name

**Returns:** DataFrame

**Aliases:** `with_column_renamed()`

**Example:**
```python
df.withColumnRenamed("old_name", "new_name")
```

---

### limit(n)

Limit number of rows returned.

**Parameters:**
- `n` (int): Maximum number of rows

**Returns:** DataFrame

**Example:**
```python
df.limit(10)
```

---

### count()

Count total number of rows.

**Returns:** int

**Example:**
```python
total = df.count()
```

---

### show(n=20, truncate=True)

Display DataFrame contents.

**Parameters:**
- `n` (int): Number of rows to show
- `truncate` (bool): Whether to truncate long strings

**Returns:** None

**Example:**
```python
df.show()
df.show(5)
```

---

### printSchema()

Print DataFrame schema.

**Returns:** None

**Example:**
```python
df.printSchema()
```

---

### createOrReplaceTempView(name)

Register DataFrame as a temporary SQL view.

**Parameters:**
- `name` (str): View name

**Returns:** None

**Example:**
```python
df.createOrReplaceTempView("users")
spark.sql("SELECT * FROM users WHERE age > 18")
```

---

## GroupedData Methods

Returned by `groupBy()`.

### count()

Count rows in each group.

**Returns:** DataFrame

**Example:**
```python
df.groupBy("city").count()
```

---

### agg(*exprs)

Perform aggregations on grouped data.

**Parameters:**
- `*exprs` (tuple): Tuples of (column, function) - "sum", "avg", "min", "max", "count"

**Returns:** DataFrame

**Example:**
```python
df.groupBy("department").agg(("salary", "avg"), ("age", "max"))
```

---

### sum(*cols)

Sum of specified columns per group.

**Parameters:**
- `*cols` (str): Column names

**Returns:** DataFrame

**Example:**
```python
df.groupBy("category").sum("price", "quantity")
```

---

### avg(*cols)

Average of specified columns per group.

**Parameters:**
- `*cols` (str): Column names

**Returns:** DataFrame

**Example:**
```python
df.groupBy("department").avg("salary")
```

---

### min(*cols)

Minimum of specified columns per group.

**Parameters:**
- `*cols` (str): Column names

**Returns:** DataFrame

---

### max(*cols)

Maximum of specified columns per group.

**Parameters:**
- `*cols` (str): Column names

**Returns:** DataFrame

---

## See Also

- [User Guide - DataFrame](../user-guide/dataframe.md)
- [User Guide - Joins](../user-guide/joins.md)
- [User Guide - Data Operations](../user-guide/set-operations.md)
- [Limitations](../limitations.md)
