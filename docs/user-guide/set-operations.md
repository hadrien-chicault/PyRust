# Data Operations

PyRust provides comprehensive data manipulation operations for working with DataFrames. This guide covers operations for removing duplicates, combining DataFrames, and performing set operations.

## Removing Duplicates

### distinct()

Remove all duplicate rows from a DataFrame:

```python
# Remove duplicate rows (considers all columns)
unique_df = df.distinct()
```

The `distinct()` method:
- Compares all columns when determining duplicates
- Returns a new DataFrame with only unique rows
- Order of rows is not guaranteed

### dropDuplicates()

Remove duplicates based on specific columns:

```python
# Remove duplicates based on specific columns
df.dropDuplicates(['name'])           # By single column
df.dropDuplicates(['name', 'city'])   # By multiple columns
df.dropDuplicates()                   # All columns (same as distinct)
```

**Alias**: You can also use `drop_duplicates()` (snake_case) for compatibility.

**Parameters**:
- `subset`: List of column names to consider for deduplication
- If `None` or empty, all columns are used

**Examples**:

```python
from pyrust import SparkSession

spark = SparkSession.builder.appName("DedupeExample").getOrCreate()

# Sample data with duplicates
df = spark.read.csv("users.csv", header=True)

# Keep only one row per unique name
unique_names = df.dropDuplicates(['name'])

# Keep only one row per unique (name, city) combination
unique_pairs = df.dropDuplicates(['name', 'city'])

# Remove all duplicate rows
completely_unique = df.dropDuplicates()
```

## Combining DataFrames

### union() / unionAll()

Combine two DataFrames vertically (stack rows):

```python
# Combine DataFrames (keeps all rows including duplicates)
combined = df1.union(df2)

# unionAll() is an alias for union()
combined = df1.unionAll(df2)
```

**Requirements**:
- Both DataFrames must have the same schema (column names and types)
- Column order must match

**Behavior**:
- All rows from both DataFrames are included
- Duplicates are kept (equivalent to SQL `UNION ALL`)
- To remove duplicates after union, use `.distinct()`

**Examples**:

```python
# Combine two datasets
df1 = spark.read.csv("data_2023.csv", header=True)
df2 = spark.read.csv("data_2024.csv", header=True)

# Combine keeping all rows
all_data = df1.union(df2)
print(f"Total rows: {all_data.count()}")

# Combine and remove duplicates
unique_data = df1.union(df2).distinct()
print(f"Unique rows: {unique_data.count()}")
```

## Set Operations

### intersect()

Find rows that exist in both DataFrames:

```python
# Get rows common to both DataFrames
common_rows = df1.intersect(df2)
```

**Behavior**:
- Returns rows that appear in both DataFrames
- Similar to SQL `INTERSECT`
- May keep some duplicates (use `.distinct()` for truly unique results)

**Examples**:

```python
# Find common users between two datasets
users_2023 = spark.read.csv("users_2023.csv", header=True)
users_2024 = spark.read.csv("users_2024.csv", header=True)

# Users in both years
returning_users = users_2023.intersect(users_2024)
returning_users.show()

# Ensure unique results
unique_returning = users_2023.intersect(users_2024).distinct()
```

### exceptAll() / subtract()

Find rows in the first DataFrame that don't exist in the second:

```python
# Get rows in df1 but not in df2
difference = df1.exceptAll(df2)

# subtract() is an alias
difference = df1.subtract(df2)
```

**Behavior**:
- Returns rows from the first DataFrame that don't appear in the second
- Equivalent to SQL `EXCEPT`
- Duplicates are removed from the result

**Examples**:

```python
# Find users who left
all_users = spark.read.csv("all_users.csv", header=True)
active_users = spark.read.csv("active_users.csv", header=True)

# Users who are no longer active
inactive_users = all_users.exceptAll(active_users)
inactive_users.show()

# Also works with subtract()
inactive_users = all_users.subtract(active_users)
```

## Chaining Operations

All operations can be chained together:

```python
# Complex chain of operations
result = (
    df1.union(df2)           # Combine DataFrames
    .distinct()               # Remove duplicates
    .filter("age > 25")       # Filter rows
    .orderBy("name")          # Sort
    .limit(100)               # Limit results
)

# Another example: data comparison
high_earners = df.filter("salary > 100000")
long_tenure = df.filter("years_employed > 5")

# People with high salary but short tenure
new_high_earners = high_earners.exceptAll(long_tenure)

# People with both high salary and long tenure
senior_high_earners = high_earners.intersect(long_tenure).distinct()
```

## Performance Tips

1. **Use distinct() early**: Apply deduplication before expensive operations
   ```python
   # Good
   df.distinct().filter("complex_condition").join(other)

   # Less efficient
   df.filter("complex_condition").join(other).distinct()
   ```

2. **Use dropDuplicates() with specific columns**: More efficient than distinct()
   ```python
   # More efficient if you only care about name uniqueness
   df.dropDuplicates(['name'])

   # Less efficient - checks all columns
   df.distinct()
   ```

3. **Union with distinct only when needed**: union() is cheap, distinct() is expensive
   ```python
   # If you know there are no duplicates
   df1.union(df2)  # Fast

   # Only if you need unique rows
   df1.union(df2).distinct()  # Slower
   ```

4. **Order matters for except()**: `df1.exceptAll(df2)` ≠ `df2.exceptAll(df1)`
   ```python
   # Rows in A but not in B
   a_only = df_a.exceptAll(df_b)

   # Rows in B but not in A
   b_only = df_b.exceptAll(df_a)
   ```

## Common Patterns

### Deduplication

```python
# Keep first occurrence based on timestamp
df.orderBy("timestamp").dropDuplicates(['user_id'])

# Remove exact duplicate rows
df.distinct()

# Remove duplicates by key columns only
df.dropDuplicates(['id', 'date'])
```

### Combining Multiple Sources

```python
# Combine data from multiple files
df_list = [
    spark.read.csv("data_jan.csv", header=True),
    spark.read.csv("data_feb.csv", header=True),
    spark.read.csv("data_mar.csv", header=True),
]

# Union all
from functools import reduce
combined = reduce(lambda a, b: a.union(b), df_list)

# Remove any duplicates across sources
final = combined.distinct()
```

### Set Analysis

```python
# Venn diagram analysis
set_a = df.filter("category = 'A'").select("user_id")
set_b = df.filter("category = 'B'").select("user_id")

# Only in A
a_only = set_a.exceptAll(set_b)

# Only in B
b_only = set_b.exceptAll(set_a)

# In both A and B
both = set_a.intersect(set_b).distinct()

# In A or B (or both)
either = set_a.union(set_b).distinct()
```

### Data Quality Checks

```python
# Find duplicate IDs (should be unique)
df.groupBy("id").count().filter("count > 1")

# Compare two datasets for differences
expected = spark.read.csv("expected.csv", header=True)
actual = spark.read.csv("actual.csv", header=True)

# Rows in expected but not in actual (missing data)
missing = expected.exceptAll(actual)

# Rows in actual but not in expected (extra data)
extra = actual.exceptAll(expected)

# Rows in both (correct data)
correct = expected.intersect(actual)
```

## Examples

See the complete examples in `examples/data_operations.py`:

```bash
python examples/data_operations.py
```

This example demonstrates:
- Removing duplicates with distinct() and dropDuplicates()
- Combining DataFrames with union()
- Finding common rows with intersect()
- Finding differences with exceptAll()
- Chaining multiple operations
- Practical use cases

## Method Summary

| Method | Description | Removes Duplicates |
|--------|-------------|-------------------|
| `distinct()` | Remove duplicate rows (all columns) | Yes |
| `dropDuplicates(cols)` | Remove duplicates by columns | Yes |
| `union(other)` | Combine DataFrames vertically | No |
| `unionAll(other)` | Alias for union() | No |
| `intersect(other)` | Rows in both DataFrames | Partial* |
| `exceptAll(other)` | Rows in first but not second | Yes |
| `subtract(other)` | Alias for exceptAll() | Yes |

*Note: `intersect()` may keep some duplicates. Use `.distinct()` after for fully unique results.

## API Aliases

For compatibility, several methods have snake_case aliases:

```python
df.dropDuplicates(['name'])  # camelCase
df.drop_duplicates(['name'])  # snake_case (alias)

df.unionAll(other)    # camelCase
# (snake_case alias not provided as union() is already simple)

df.exceptAll(other)   # camelCase
df.subtract(other)    # alternative name
```
