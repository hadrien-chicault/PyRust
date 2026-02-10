# SQL Queries

PyRust provides full SQL query support through DataFusion's SQL engine. You can execute standard SQL queries on your DataFrames using temporary views.

## Quick Start

```python
from pyrust import SparkSession

# Create a SparkSession
spark = SparkSession.builder.appName("SQLExample").getOrCreate()

# Load data
df = spark.read.csv("users.csv", header=True)

# Register as temporary view
df.createOrReplaceTempView("users")

# Execute SQL query
result = spark.sql("SELECT name, age FROM users WHERE age > 25")
result.show()
```

## Creating Temporary Views

Before you can query a DataFrame with SQL, you need to register it as a temporary view:

```python
# Register DataFrame as a view
df.createOrReplaceTempView("users")

# Now you can reference it in SQL queries
result = spark.sql("SELECT * FROM users")
```

### Replacing Views

The `createOrReplaceTempView()` method will replace any existing view with the same name:

```python
# Create initial view
df.createOrReplaceTempView("my_data")

# Later, replace it with a filtered version
filtered_df = df.filter("age > 30")
filtered_df.createOrReplaceTempView("my_data")  # Replaces the old view
```

## Basic SQL Queries

### SELECT

Select specific columns:

```python
result = spark.sql("SELECT name, age, city FROM users")
```

Select all columns:

```python
result = spark.sql("SELECT * FROM users")
```

### WHERE Clause

Filter rows based on conditions:

```python
result = spark.sql("SELECT * FROM users WHERE age > 25")
result = spark.sql("SELECT * FROM users WHERE city = 'New York'")
result = spark.sql("SELECT * FROM users WHERE age > 25 AND salary > 70000")
```

### ORDER BY

Sort results:

```python
# Ascending order (default)
result = spark.sql("SELECT * FROM users ORDER BY age")

# Descending order
result = spark.sql("SELECT * FROM users ORDER BY salary DESC")

# Multiple columns
result = spark.sql("SELECT * FROM users ORDER BY city, age DESC")
```

### LIMIT

Limit the number of rows:

```python
result = spark.sql("SELECT * FROM users LIMIT 10")
```

## Aggregations

### COUNT

Count rows:

```python
result = spark.sql("SELECT COUNT(*) as total FROM users")
```

### GROUP BY

Group and aggregate:

```python
result = spark.sql("""
    SELECT city, COUNT(*) as count
    FROM users
    GROUP BY city
""")
```

### Multiple Aggregations

Use multiple aggregate functions:

```python
result = spark.sql("""
    SELECT
        city,
        COUNT(*) as total,
        AVG(age) as avg_age,
        MIN(salary) as min_salary,
        MAX(salary) as max_salary,
        SUM(salary) as total_salary
    FROM users
    GROUP BY city
""")
```

### HAVING Clause

Filter groups after aggregation:

```python
result = spark.sql("""
    SELECT city, COUNT(*) as count
    FROM users
    GROUP BY city
    HAVING COUNT(*) > 5
""")
```

## Joins

You can perform joins using SQL syntax:

### INNER JOIN

```python
# Register both DataFrames
employees.createOrReplaceTempView("employees")
departments.createOrReplaceTempView("departments")

# Join them
result = spark.sql("""
    SELECT e.name, e.age, d.dept_name
    FROM employees e
    INNER JOIN departments d ON e.dept_id = d.dept_id
""")
```

### LEFT JOIN

```python
result = spark.sql("""
    SELECT e.name, d.dept_name
    FROM employees e
    LEFT JOIN departments d ON e.dept_id = d.dept_id
""")
```

### Other Join Types

PyRust supports all standard SQL join types:
- `INNER JOIN`
- `LEFT JOIN` (or `LEFT OUTER JOIN`)
- `RIGHT JOIN` (or `RIGHT OUTER JOIN`)
- `FULL OUTER JOIN`

## Subqueries

### Subquery in WHERE

Filter based on a subquery result:

```python
result = spark.sql("""
    SELECT name, age
    FROM users
    WHERE age > (SELECT AVG(age) FROM users)
""")
```

### Subquery in FROM

Use a subquery as a data source:

```python
result = spark.sql("""
    SELECT city, avg_salary
    FROM (
        SELECT city, AVG(salary) as avg_salary
        FROM users
        GROUP BY city
    ) AS city_stats
    WHERE avg_salary > 70000
""")
```

## SQL Functions

### String Functions

```python
result = spark.sql("""
    SELECT
        name,
        UPPER(name) as upper_name,
        LOWER(city) as lower_city
    FROM users
""")
```

Common string functions:
- `UPPER(col)` - Convert to uppercase
- `LOWER(col)` - Convert to lowercase
- `LENGTH(col)` - Get string length
- `TRIM(col)` - Remove whitespace

### Math Functions

```python
result = spark.sql("""
    SELECT
        age,
        age * 2 as double_age,
        age + 10 as age_plus_10
    FROM users
""")
```

### CASE Expressions

Conditional logic in SQL:

```python
result = spark.sql("""
    SELECT
        name,
        age,
        CASE
            WHEN age < 25 THEN 'Young'
            WHEN age < 35 THEN 'Middle'
            ELSE 'Senior'
        END as age_category
    FROM users
""")
```

## Mixing SQL and DataFrame Operations

You can seamlessly mix SQL queries with DataFrame operations:

### SQL → DataFrame Operations

```python
# Start with SQL
result = spark.sql("SELECT * FROM users WHERE age > 25")

# Continue with DataFrame operations
result = result.filter("salary > 70000") \
               .orderBy("salary") \
               .limit(10)
```

### DataFrame Operations → SQL

```python
# Start with DataFrame operations
filtered = df.filter("age > 25")

# Register and query with SQL
filtered.createOrReplaceTempView("filtered_users")
result = spark.sql("SELECT city, COUNT(*) FROM filtered_users GROUP BY city")
```

## Error Handling

PyRust raises `RuntimeError` for SQL errors:

```python
try:
    result = spark.sql("SELECT * FROM nonexistent_table")
except RuntimeError as e:
    print(f"SQL error: {e}")
```

Common errors:
- **Table not found**: Make sure you've called `createOrReplaceTempView()` first
- **Column not found**: Check column names in your query
- **Syntax error**: Verify your SQL syntax is correct

## Performance Tips

1. **Filter early**: Use WHERE clauses to reduce data before joins
   ```python
   # Good
   spark.sql("SELECT * FROM users WHERE age > 25")

   # Less efficient for large datasets
   spark.sql("SELECT * FROM users").filter("age > 25")
   ```

2. **Use column selection**: Select only needed columns
   ```python
   # Good
   spark.sql("SELECT name, age FROM users")

   # Unnecessary if you only need two columns
   spark.sql("SELECT * FROM users")
   ```

3. **Aggregate before joining**: Reduce data size before expensive operations
   ```python
   spark.sql("""
       SELECT u.city, s.avg_salary
       FROM users u
       JOIN (
           SELECT city, AVG(salary) as avg_salary
           FROM salaries
           GROUP BY city
       ) s ON u.city = s.city
   """)
   ```

## Examples

See the complete SQL examples in `examples/sql_queries.py`:

```bash
python examples/sql_queries.py
```

This example demonstrates:
- Basic queries (SELECT, WHERE, ORDER BY)
- Aggregations (GROUP BY, HAVING)
- CASE expressions
- Subqueries
- String and math functions
- Mixing SQL with DataFrame operations
- Replacing temporary views

## Supported SQL Features

PyRust leverages DataFusion's SQL engine, which supports:

- ✅ SELECT, WHERE, ORDER BY, LIMIT
- ✅ GROUP BY, HAVING
- ✅ Aggregations: COUNT, SUM, AVG, MIN, MAX
- ✅ Joins: INNER, LEFT, RIGHT, FULL OUTER
- ✅ Subqueries in SELECT, FROM, and WHERE
- ✅ CASE expressions
- ✅ String functions: UPPER, LOWER, TRIM, LENGTH
- ✅ Math operators: +, -, *, /
- ✅ Comparison operators: =, !=, <, >, <=, >=
- ✅ Logical operators: AND, OR, NOT
- ✅ Common SQL functions

For advanced SQL features, refer to [DataFusion's SQL documentation](https://arrow.apache.org/datafusion/user-guide/sql/index.html).
