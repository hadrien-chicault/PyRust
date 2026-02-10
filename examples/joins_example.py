"""
Join Operations Examples for PyRust

This example demonstrates all join types:
- Inner join
- Left join
- Right join
- Full outer join
- Semi join
- Anti join
"""

from pyrust import SparkSession

# Create a SparkSession
spark = SparkSession.builder.appName("JoinsExample").getOrCreate()

print("=" * 80)
print("PREPARING SAMPLE DATA")
print("=" * 80)

# Load users data
users_df = spark.read.csv("examples/data/users.csv", header=True)
print("\nUsers DataFrame:")
users_df.show()

# For demonstration, let's create a subset for orders
# In practice, you'd load from another CSV
print("\n" + "=" * 80)
print("INNER JOIN (DEFAULT)")
print("=" * 80)

print("\n1. Simple inner join:")
print("Join users with themselves to demonstrate (normally different DataFrames)")
# Select subset for left side
df_left = users_df.select("name", "city").limit(3)
print("Left DataFrame:")
df_left.show()

# Select subset for right side
df_right = users_df.select("name", "age").filter("age > 25")
print("Right DataFrame:")
df_right.show()

print("\nInner join on 'name':")
result = df_left.join(df_right, on="name")
print(f"Result has {result.count()} rows (only names in both)")
result.show()

print("\n2. Inner join - explicit:")
result = df_left.join(df_right, on="name", how="inner")
result.show()

print("\n" + "=" * 80)
print("LEFT JOIN (LEFT OUTER)")
print("=" * 80)

print("\n3. Left join - keeps all left rows:")
result = df_left.join(df_right, on="name", how="left")
print(f"Result has {result.count()} rows (all from left)")
result.show()

print("\n" + "=" * 80)
print("RIGHT JOIN (RIGHT OUTER)")
print("=" * 80)

print("\n4. Right join - keeps all right rows:")
result = df_left.join(df_right, on="name", how="right")
print(f"Result has {result.count()} rows (all from right)")
result.show()

print("\n" + "=" * 80)
print("FULL OUTER JOIN")
print("=" * 80)

print("\n5. Full outer join - keeps all rows from both:")
result = df_left.join(df_right, on="name", how="outer")
print(f"Result has {result.count()} rows (all from both)")
result.show()

print("\n6. Using 'full' alias:")
result = df_left.join(df_right, on="name", how="full")
print(f"Same result: {result.count()} rows")

print("\n" + "=" * 80)
print("SEMI JOIN (FILTER)")
print("=" * 80)

print("\n7. Semi join - left rows where match exists:")
result = df_left.join(df_right, on="name", how="semi")
print(f"Result has {result.count()} rows")
print("Only left columns, filtered by existence in right")
result.show()

print("\n" + "=" * 80)
print("ANTI JOIN (FILTER)")
print("=" * 80)

print("\n8. Anti join - left rows where NO match:")
result = df_left.join(df_right, on="name", how="anti")
print(f"Result has {result.count()} rows")
print("Only left columns, where name not in right")
result.show()

print("\n" + "=" * 80)
print("MULTI-COLUMN JOINS")
print("=" * 80)

print("\n9. Join on multiple columns:")
# Create test data with multiple join keys
left = users_df.select("name", "city", "age").limit(3)
right = users_df.select("name", "city", "salary").filter("age > 25")

print("Left:")
left.show()
print("Right:")
right.show()

result = left.join(right, on=["name", "city"])
print(f"\nJoined on both 'name' AND 'city': {result.count()} rows")
result.show()

print("\n" + "=" * 80)
print("STRING VS LIST SYNTAX")
print("=" * 80)

print("\n10. Single column - can use string:")
result = df_left.join(df_right, on="name")
print(f"Using on='name': {result.count()} rows")

print("\n11. Multiple columns - must use list:")
result = left.join(right, on=["name", "city"])
print(f"Using on=['name', 'city']: {result.count()} rows")

print("\n" + "=" * 80)
print("CHAINING OPERATIONS")
print("=" * 80)

print("\n12. Filter before join (efficient):")
filtered = users_df.filter("age > 28")
result = users_df.join(filtered, on="name", how="semi")
print(f"Users older than 28: {result.count()}")
result.show()

print("\n13. Join then filter:")
result = df_left.join(df_right, on="name").filter("age > 28")
print(f"Joined then filtered: {result.count()} rows")
result.show()

print("\n14. Join then select:")
result = df_left.join(df_right, on="name").select("name", "city")
print("Selected columns after join:")
result.show()

print("\n15. Join then aggregate:")
result = users_df.join(users_df.select("name", "salary"), on="name").groupBy("city").count()
print("Count by city after self-join:")
result.show()

print("\n" + "=" * 80)
print("PRACTICAL USE CASES")
print("=" * 80)

print("\n16. Enriching data with left join:")
base = users_df.select("name", "city")
details = users_df.select("name", "salary", "age")
enriched = base.join(details, on="name", how="left")
print("Base data enriched with details:")
enriched.show()

print("\n17. Finding missing records with anti join:")
all_users = users_df.select("name")
active_users = users_df.filter("age > 30").select("name")
inactive = all_users.join(active_users, on="name", how="anti")
print(f"Users aged 30 or less: {inactive.count()}")
inactive.show()

print("\n18. Data validation with semi join:")
expected = users_df.select("name", "city")
actual = users_df.filter("salary > 60000").select("name", "city")
valid = expected.join(actual, on=["name", "city"], how="semi")
print("Expected records that exist in actual:")
valid.show()

print("\n" + "=" * 80)
print("COLUMN DEDUPLICATION")
print("=" * 80)

print("\n19. Join keys appear only once:")
result = df_left.join(df_right, on="name")
print("Join key 'name' appears only once in result:")
result.printSchema()

print("\n" + "=" * 80)
print("HANDLING NAME CONFLICTS")
print("=" * 80)

print("\n20. Rename before join to avoid conflicts:")
# Both DataFrames have 'city' column
left_renamed = users_df.withColumnRenamed("city", "home_city").select("name", "home_city")
right_renamed = users_df.withColumnRenamed("city", "work_city").select("name", "work_city")

print("Left (home_city):")
left_renamed.show(3)
print("Right (work_city):")
right_renamed.show(3)

result = left_renamed.join(right_renamed, on="name")
print("No conflicts after renaming:")
result.show(3)

print("\n" + "=" * 80)
print("Examples completed successfully!")
print("=" * 80)

# Stop the session
spark.stop()
