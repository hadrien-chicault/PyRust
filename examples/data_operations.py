"""
Data Operations Examples for PyRust

This example demonstrates data manipulation operations including:
- distinct() - Remove duplicate rows
- dropDuplicates() - Remove duplicates based on specific columns
- union() / unionAll() - Combine DataFrames vertically
- intersect() - Find common rows between DataFrames
- exceptAll() - Find difference between DataFrames
"""

from pyrust import SparkSession

# Create a SparkSession
spark = SparkSession.builder.appName("DataOperationsExample").getOrCreate()

print("=" * 80)
print("DISTINCT - REMOVE DUPLICATES")
print("=" * 80)

# Load dataset with duplicates
users_df = spark.read.csv("examples/data/users.csv", header=True)

print("\n1. Original DataFrame:")
print(f"Total rows: {users_df.count()}")
users_df.show()

print("\n2. After distinct() - remove all duplicate rows:")
distinct_df = users_df.distinct()
print(f"Total rows: {distinct_df.count()}")
distinct_df.show()

print("\n" + "=" * 80)
print("DROP DUPLICATES - BASED ON SPECIFIC COLUMNS")
print("=" * 80)

print("\n3. Drop duplicates based on 'city' column:")
by_city = users_df.dropDuplicates(["city"])
print(f"Total rows: {by_city.count()}")
by_city.show()

print("\n4. Drop duplicates based on 'name' and 'age':")
by_name_age = users_df.dropDuplicates(["name", "age"])
print(f"Total rows: {by_name_age.count()}")
by_name_age.show()

print("\n5. Using drop_duplicates() alias:")
alias_result = users_df.drop_duplicates(["city"])
print(f"Total rows: {alias_result.count()}")

print("\n" + "=" * 80)
print("UNION - COMBINE DATAFRAMES")
print("=" * 80)

# Create two sample DataFrames for union operations
# Note: In a real scenario, these would be different datasets
df1 = users_df.filter("age > 30").select("name", "age", "city")
df2 = users_df.filter("salary > 75000").select("name", "age", "city")

print("\n6. First DataFrame:")
print(f"Total rows: {df1.count()}")
df1.show()

print("\n7. Second DataFrame:")
print(f"Total rows: {df2.count()}")
df2.show()

print("\n8. Union of both DataFrames (keeps duplicates):")
union_df = df1.union(df2)
print(f"Total rows: {union_df.count()}")
union_df.show()

print("\n9. Union followed by distinct (removes duplicates):")
union_distinct = df1.union(df2).distinct()
print(f"Total rows: {union_distinct.count()}")
union_distinct.show()

print("\n10. unionAll() - same as union():")
union_all_df = df1.unionAll(df2)
print(f"Total rows: {union_all_df.count()}")

print("\n" + "=" * 80)
print("INTERSECT - FIND COMMON ROWS")
print("=" * 80)

print("\n11. Intersect - rows that exist in both DataFrames:")
intersect_df = df1.intersect(df2)
print(f"Total rows: {intersect_df.count()}")
intersect_df.show()

print("\n12. Intersect with distinct for unique common rows:")
intersect_distinct = df1.intersect(df2).distinct()
print(f"Total rows: {intersect_distinct.count()}")

print("\n" + "=" * 80)
print("EXCEPT - FIND DIFFERENCES")
print("=" * 80)

print("\n13. Except - rows in df1 but not in df2:")
except_df = df1.exceptAll(df2)
print(f"Total rows: {except_df.count()}")
except_df.show()

print("\n14. Except in reverse - rows in df2 but not in df1:")
except_reverse = df2.exceptAll(df1)
print(f"Total rows: {except_reverse.count()}")
except_reverse.show()

print("\n15. Using subtract() alias:")
subtract_df = df1.subtract(df2)
print(f"Total rows: {subtract_df.count()}")

print("\n" + "=" * 80)
print("CHAINING OPERATIONS")
print("=" * 80)

print("\n16. Complex chain: union, distinct, filter, orderBy:")
complex_result = df1.union(df2).distinct().filter("age > 25").orderBy("age").limit(5)
print(f"Total rows: {complex_result.count()}")
complex_result.show()

print("\n17. Filter, distinct, then orderBy:")
chained_result = users_df.filter("salary > 60000").distinct().orderBy("salary")
print(f"Total rows: {chained_result.count()}")
chained_result.show()

print("\n" + "=" * 80)
print("PRACTICAL EXAMPLES")
print("=" * 80)

print("\n18. Finding unique cities:")
unique_cities = users_df.select("city").distinct().orderBy("city")
print("Unique cities in dataset:")
unique_cities.show()

print("\n19. Combining multiple sources and removing duplicates:")
# Simulate combining data from multiple sources
source1 = users_df.filter("age < 30")
source2 = users_df.filter("age >= 30")
combined = source1.union(source2).distinct()
print(f"Combined unique rows: {combined.count()}")

print("\n20. Set operations for data comparison:")
# Find users unique to each dataset
high_age = users_df.filter("age > 28").select("name", "age")
high_salary = users_df.filter("salary > 70000").select("name", "age")

print("\nHigh age but not high salary:")
age_only = high_age.exceptAll(high_salary)
age_only.show()

print("\nHigh salary but not high age:")
salary_only = high_salary.exceptAll(high_age)
salary_only.show()

print("\nBoth high age AND high salary:")
both = high_age.intersect(high_salary)
both.show()

print("\n" + "=" * 80)
print("Examples completed successfully!")
print("=" * 80)

# Stop the session
spark.stop()
