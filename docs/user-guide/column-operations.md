# Column Operations

PyRust provides operations for manipulating DataFrame columns, including renaming columns and type casting. This guide covers column-level transformations.

## Renaming Columns

### withColumnRenamed()

Rename a single column in the DataFrame:

```python
# Rename a single column
df = df.withColumnRenamed("old_name", "new_name")

# Chain multiple renames
df = df.withColumnRenamed("col1", "column_one") \
       .withColumnRenamed("col2", "column_two")
```

**Alias**: You can also use `with_column_renamed()` (snake_case) for compatibility.

**Parameters**:
- `existing`: Current column name (must exist)
- `new`: New name for the column (must not already exist)

**Returns**: A new DataFrame with the column renamed

**Behavior**:
- All data is preserved
- Only affects the specified column
- Other columns remain unchanged
- Can be chained with other operations

**Examples**:

```python
from pyrust import SparkSession

spark = SparkSession.builder.appName("ColumnOps").getOrCreate()

# Load data
df = spark.read.csv("users.csv", header=True)

# Make column names more descriptive
df = df.withColumnRenamed("name", "employee_name") \
       .withColumnRenamed("age", "employee_age")

# Rename before aggregation
result = df.withColumnRenamed("city", "location") \
           .groupBy("location") \
           .count()
```

## Common Patterns

### Standardizing Column Names

```python
# Convert to standard naming convention
standardized = (
    df.withColumnRenamed("FirstName", "first_name")
      .withColumnRenamed("LastName", "last_name")
      .withColumnRenamed("EmailAddr", "email_address")
)
```

### Preparing for Joins

```python
# Rename columns to avoid conflicts in joins
users = df.withColumnRenamed("id", "user_id") \
          .withColumnRenamed("name", "user_name")

orders = orders_df.withColumnRenamed("id", "order_id")

# Now join without column name conflicts
result = users.join(orders, on=["user_id"])
```

### Making Names More Descriptive

```python
# Add context to generic names
improved = (
    df.withColumnRenamed("date", "purchase_date")
      .withColumnRenamed("amount", "total_amount")
      .withColumnRenamed("status", "order_status")
)
```

### Fixing Typos or Case

```python
# Fix column name issues
fixed = df.withColumnRenamed("adress", "address")  # Fix typo
fixed = df.withColumnRenamed("Name", "name")        # Normalize case
```

## Integration with Other Operations

### With Filtering

```python
# Rename then filter
result = df.withColumnRenamed("age", "user_age") \
           .filter("user_age > 25")
```

### With Selection

```python
# Rename then select specific columns
result = df.withColumnRenamed("name", "full_name") \
           .select("full_name", "email")
```

### With Sorting

```python
# Rename then sort
result = df.withColumnRenamed("salary", "annual_salary") \
           .orderBy("annual_salary")
```

### With Aggregation

```python
# Rename before grouping
result = df.withColumnRenamed("city", "location") \
           .groupBy("location") \
           .agg(("salary", "avg"))
```

### With Joins

```python
# Rename before join to avoid ambiguity
df1 = df1.withColumnRenamed("name", "user_name")
df2 = df2.withColumnRenamed("name", "product_name")

result = df1.join(df2, on=["id"])
# Result has both user_name and product_name clearly distinguished
```

## Error Handling

### Column Doesn't Exist

```python
try:
    df.withColumnRenamed("nonexistent", "new_name")
except RuntimeError:
    print("Column 'nonexistent' does not exist")
```

### Target Name Already Exists

```python
try:
    # age already exists
    df.withColumnRenamed("name", "age")
except RuntimeError:
    print("Column 'age' already exists")
```

## Performance Tips

1. **Chain efficiently**: Multiple renames can be chained together
   ```python
   # Good - single pass through data
   df.withColumnRenamed("a", "col_a") \
     .withColumnRenamed("b", "col_b") \
     .withColumnRenamed("c", "col_c")
   ```

2. **Rename early**: If you only need renamed columns, rename before filtering
   ```python
   # Better - rename affects fewer columns after select
   df.select("name", "age") \
     .withColumnRenamed("name", "full_name")

   # vs renaming before select
   df.withColumnRenamed("name", "full_name") \
     .select("full_name", "age")
   ```

3. **Rename for clarity**: Use descriptive names to make code more readable
   ```python
   # Clear and self-documenting
   df.withColumnRenamed("ts", "timestamp") \
     .withColumnRenamed("qty", "quantity") \
     .withColumnRenamed("amt", "amount")
   ```

## Method Summary

| Method | Description | Returns |
|--------|-------------|---------|
| `withColumnRenamed(existing, new)` | Rename a column | New DataFrame |
| `with_column_renamed(existing, new)` | Snake_case alias | New DataFrame |

## API Aliases

For compatibility, PyRust provides both naming conventions:

```python
df.withColumnRenamed("old", "new")  # camelCase (PySpark style)
df.with_column_renamed("old", "new")  # snake_case (Python style)
```

## Future Enhancements

Future versions will support:
- `withColumn()` - Add or replace columns with expressions
- `cast()` - Change column data types
- `alias()` - Column aliases in select expressions
- `drop()` - Remove columns from DataFrame

## Examples

See the complete examples in `examples/column_operations.py`:

```bash
python examples/column_operations.py
```

This example demonstrates:
- Basic column renaming
- Chaining multiple renames
- Renaming with filters, joins, and aggregations
- Error handling
- Practical use cases
