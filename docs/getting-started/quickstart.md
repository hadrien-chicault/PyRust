# Quick Start Tutorial

This tutorial will get you started with PyRust in 5 minutes.

## Your First PyRust Program

Let's create a simple data analysis program:

```python
from pyrust import SparkSession

# 1. Create a SparkSession
spark = SparkSession.builder() \
    .appName("MyFirstApp") \
    .getOrCreate()

# 2. Read a CSV file
df = spark.read.csv("data.csv", header=True, infer_schema=True)

# 3. Inspect the data
df.printSchema()
df.show(5)

# 4. Perform transformations
result = df.select(["name", "age", "city"]) \
           .filter("age > 18") \
           .orderBy(["age"])

# 5. Display results
result.show()
```

## Step-by-Step Breakdown

### Step 1: Create a SparkSession

The `SparkSession` is your entry point to PyRust:

```python
spark = SparkSession.builder() \
    .appName("MyFirstApp") \
    .getOrCreate()
```

- **`builder()`** - Returns a builder for configuration
- **`appName()`** - Sets your application name
- **`getOrCreate()`** - Creates or retrieves the session

### Step 2: Read Data

Load data from various sources:

```python
# CSV with header
df = spark.read.csv("data.csv", header=True, infer_schema=True)

# Parquet (faster for large files)
df = spark.read.parquet("data.parquet")
```

**Supported formats:**
- CSV - Comma-separated values
- Parquet - Columnar format (recommended for production)

### Step 3: Inspect Data

Understand your data structure:

```python
# Print schema (column types)
df.printSchema()
# Output:
# root
#  |-- name: Utf8 (nullable = true)
#  |-- age: Int64 (nullable = true)
#  |-- city: Utf8 (nullable = true)

# Show first rows
df.show(5)  # Show 5 rows

# Count total rows
print(f"Total rows: {df.count()}")
```

### Step 4: Transform Data

Chain operations to transform your data:

```python
# Select specific columns
subset = df.select(["name", "age"])

# Filter rows
adults = df.filter("age >= 18")

# Sort data
sorted_df = df.orderBy(["age"])

# Limit results
top_10 = df.limit(10)

# Chain operations (lazy evaluation)
result = df.select(["name", "age"]) \
           .filter("age > 18") \
           .orderBy(["age"]) \
           .limit(100)
```

### Step 5: Aggregations

Compute statistics on grouped data:

```python
# Count by group
city_counts = df.groupBy(["city"]).count()
city_counts.show()

# Multiple aggregations
stats = df.groupBy(["city"]).agg([
    ("age", "avg"),
    ("age", "min"),
    ("age", "max")
])
stats.show()
```

## Complete Example

Here's a complete data analysis workflow:

```python
from pyrust import SparkSession

# Initialize
spark = SparkSession.builder().appName("Analysis").getOrCreate()

# Load sales data
sales = spark.read.csv("sales.csv", header=True, infer_schema=True)

# Analyze high-value sales by region
analysis = sales.filter("amount > 1000") \
                .select(["region", "amount", "product"]) \
                .groupBy(["region"]) \
                .agg([
                    ("amount", "sum"),
                    ("amount", "avg"),
                    ("product", "count")
                ]) \
                .orderBy(["sum(amount)"])

# Display results
print("High-Value Sales Analysis:")
analysis.show()

# Get summary statistics
print(f"\nTotal high-value transactions: {sales.filter('amount > 1000').count()}")
```

## Performance Tips

### 1. Filter Early
Apply filters before other operations:

```python
# Good - filter first
df.filter("age > 18").select(["name", "city"]).groupBy(["city"]).count()

# Less efficient - filter last
df.select(["name", "city"]).groupBy(["city"]).count().filter("count > 100")
```

### 2. Select Only Needed Columns
Reduce data size by selecting only required columns:

```python
# Good - select only needed columns
df.select(["name", "age"]).filter("age > 18")

# Less efficient - process all columns
df.filter("age > 18")  # Still carries all columns
```

### 3. Use Parquet for Large Files
Parquet is much faster than CSV:

```python
# Save as Parquet for future use
df.write.parquet("data.parquet")  # TODO: Not yet implemented

# Read Parquet (10-100x faster than CSV)
df = spark.read.parquet("data.parquet")
```

### 4. Limit When Exploring
Use `limit()` for quick data exploration:

```python
# Fast preview
df.limit(1000).show()

# Analyze small subset first
df.limit(10000).groupBy(["category"]).count().show()
```

## Common Patterns

### Pattern 1: Filter and Aggregate

```python
# Count adult users by city
adult_by_city = df.filter("age >= 18") \
                  .groupBy(["city"]) \
                  .count() \
                  .orderBy(["count"])
adult_by_city.show()
```

### Pattern 2: Top N Analysis

```python
# Top 10 highest sales
top_sales = df.orderBy(["amount"]) \
              .limit(10) \
              .select(["customer", "amount", "date"])
top_sales.show()
```

### Pattern 3: Multi-Column Grouping

```python
# Sales by country and product
summary = df.groupBy(["country", "product"]) \
            .agg([("amount", "sum"), ("order_id", "count")])
summary.show()
```

## Next Steps

You're now ready to use PyRust! Continue learning:

- [Basic Operations](basic-operations.md) - More detailed operation guides
- [DataFrame API](../user-guide/dataframe.md) - Complete DataFrame guide
- [Performance Tips](../user-guide/performance.md) - Optimize your queries
- [API Reference](../api/dataframe.md) - Full API documentation

## Sample Data

Need sample data to practice? Create a test CSV file:

```csv
name,age,city,salary
Alice,25,New York,75000
Bob,30,London,85000
Charlie,35,New York,95000
Diana,28,Paris,80000
Eve,42,London,110000
Frank,19,Paris,45000
Grace,55,New York,125000
Henry,31,London,88000
```

Save this as `test.csv` and try the examples above!
