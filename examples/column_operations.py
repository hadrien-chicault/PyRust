"""
Column Operations Examples for PyRust

This example demonstrates column manipulation operations:
- withColumnRenamed() - Rename columns
- Chaining renames with other operations
"""

from pyrust import SparkSession

# Create a SparkSession
spark = SparkSession.builder.appName("ColumnOperationsExample").getOrCreate()

print("=" * 80)
print("COLUMN RENAMING - withColumnRenamed()")
print("=" * 80)

# Load sample data
df = spark.read.csv("examples/data/users.csv", header=True)

print("\n1. Original DataFrame:")
df.printSchema()
df.show()

print("\n" + "=" * 80)
print("SINGLE COLUMN RENAME")
print("=" * 80)

print("\n2. Rename 'name' to 'full_name':")
renamed_df = df.withColumnRenamed("name", "full_name")
renamed_df.printSchema()
renamed_df.show()

print("\n" + "=" * 80)
print("CHAINED RENAMING")
print("=" * 80)

print("\n3. Rename multiple columns:")
multi_renamed = (
    df.withColumnRenamed("name", "full_name")
    .withColumnRenamed("age", "user_age")
    .withColumnRenamed("city", "location")
)
multi_renamed.printSchema()
multi_renamed.show()

print("\n" + "=" * 80)
print("RENAME WITH OTHER OPERATIONS")
print("=" * 80)

print("\n4. Rename then filter:")
result = df.withColumnRenamed("age", "user_age").filter("user_age > 25")
print(f"Users with age > 25: {result.count()} rows")
result.show()

print("\n5. Rename then select specific columns:")
result = df.withColumnRenamed("name", "full_name").select("full_name", "salary")
result.show()

print("\n6. Rename then sort:")
result = df.withColumnRenamed("salary", "annual_salary").orderBy("annual_salary")
result.show()

print("\n" + "=" * 80)
print("RENAME WITH AGGREGATIONS")
print("=" * 80)

print("\n7. Rename then group by:")
result = df.withColumnRenamed("city", "location").groupBy("location").count()
print("Count by location:")
result.show()

print("\n8. Chain rename with aggregation:")
result = (
    df.withColumnRenamed("city", "location")
    .withColumnRenamed("salary", "pay")
    .groupBy("location")
    .agg(("pay", "avg"))
)
print("Average pay by location:")
result.show()

print("\n" + "=" * 80)
print("SNAKE_CASE ALIAS")
print("=" * 80)

print("\n9. Using with_column_renamed() (snake_case):")
result = df.with_column_renamed("name", "full_name")
result.printSchema()

print("\n" + "=" * 80)
print("PRACTICAL USE CASES")
print("=" * 80)

print("\n10. Standardizing column names:")
# Make column names more descriptive
cleaned_df = (
    df.withColumnRenamed("name", "employee_name")
    .withColumnRenamed("age", "employee_age")
    .withColumnRenamed("city", "work_location")
    .withColumnRenamed("salary", "annual_salary")
)
print("Standardized column names:")
cleaned_df.printSchema()
cleaned_df.show()

print("\n11. Preparing for join (avoid name conflicts):")
# Rename columns before join to avoid conflicts
users = df.withColumnRenamed("age", "user_age").withColumnRenamed("city", "user_city")
users.printSchema()

print("\n12. Quick column name fix:")
# Fix a typo in column name
fixed_df = df.withColumnRenamed("name", "Name")  # Capitalize
fixed_df.printSchema()

print("\n" + "=" * 80)
print("ERROR HANDLING")
print("=" * 80)

print("\n13. Attempting to rename non-existent column:")
try:
    df.withColumnRenamed("nonexistent", "new_name")
except RuntimeError as e:
    print(f"Error (expected): {e}")

print("\n14. Attempting to rename to existing name:")
try:
    df.withColumnRenamed("name", "age")  # age already exists
except RuntimeError as e:
    print(f"Error (expected): {e}")

print("\n" + "=" * 80)
print("Examples completed successfully!")
print("=" * 80)

# Stop the session
spark.stop()
