"""
SQL Query Examples for PyRust

This example demonstrates SQL query capabilities including:
- Basic SELECT queries with WHERE, ORDER BY, GROUP BY
- Aggregation functions (COUNT, AVG, MAX, MIN, SUM)
- Joins using SQL syntax
- Subqueries
- CASE expressions
- Temporary views
"""

from pyrust import SparkSession

# Create a SparkSession
spark = SparkSession.builder.appName("SQLExample").getOrCreate()

# Load the users dataset
users_df = spark.read.csv("examples/data/users.csv", header=True)

print("=" * 80)
print("BASIC SQL QUERIES")
print("=" * 80)

# Register DataFrame as a temporary view
users_df.createOrReplaceTempView("users")

print("\n1. Simple SELECT with WHERE clause:")
print("-" * 40)
result = spark.sql("SELECT name, age, city FROM users WHERE age > 25")
result.show()

print("\n2. SELECT with ORDER BY:")
print("-" * 40)
result = spark.sql("SELECT name, age, salary FROM users ORDER BY salary DESC LIMIT 5")
result.show()

print("\n3. GROUP BY with aggregation:")
print("-" * 40)
result = spark.sql("""
    SELECT city, COUNT(*) as count, AVG(age) as avg_age
    FROM users
    GROUP BY city
    ORDER BY count DESC
""")
result.show()

print("\n" + "=" * 80)
print("ADVANCED AGGREGATIONS")
print("=" * 80)

print("\n4. Multiple aggregations per group:")
print("-" * 40)
result = spark.sql("""
    SELECT
        city,
        COUNT(*) as total_users,
        AVG(age) as avg_age,
        MIN(salary) as min_salary,
        MAX(salary) as max_salary,
        SUM(salary) as total_salary
    FROM users
    GROUP BY city
""")
result.show()

print("\n5. HAVING clause (filter after grouping):")
print("-" * 40)
result = spark.sql("""
    SELECT city, COUNT(*) as user_count
    FROM users
    GROUP BY city
    HAVING COUNT(*) > 1
    ORDER BY user_count DESC
""")
result.show()

print("\n" + "=" * 80)
print("CASE EXPRESSIONS")
print("=" * 80)

print("\n6. CASE WHEN for conditional logic:")
print("-" * 40)
result = spark.sql("""
    SELECT
        name,
        age,
        CASE
            WHEN age < 25 THEN 'Young'
            WHEN age < 35 THEN 'Middle'
            ELSE 'Senior'
        END as age_category,
        salary,
        CASE
            WHEN salary < 60000 THEN 'Low'
            WHEN salary < 80000 THEN 'Medium'
            ELSE 'High'
        END as salary_bracket
    FROM users
    ORDER BY age
""")
result.show()

print("\n" + "=" * 80)
print("SUBQUERIES")
print("=" * 80)

print("\n7. Subquery in WHERE clause (users above average age):")
print("-" * 40)
result = spark.sql("""
    SELECT name, age, city
    FROM users
    WHERE age > (SELECT AVG(age) FROM users)
    ORDER BY age DESC
""")
result.show()

print("\n8. Subquery in FROM clause:")
print("-" * 40)
result = spark.sql("""
    SELECT city, avg_salary
    FROM (
        SELECT city, AVG(salary) as avg_salary
        FROM users
        GROUP BY city
    ) AS city_stats
    WHERE avg_salary > 70000
    ORDER BY avg_salary DESC
""")
result.show()

print("\n" + "=" * 80)
print("SQL FUNCTIONS")
print("=" * 80)

print("\n9. String functions (UPPER, LOWER, CONCAT):")
print("-" * 40)
result = spark.sql("""
    SELECT
        name,
        UPPER(name) as upper_name,
        LOWER(city) as lower_city
    FROM users
    LIMIT 5
""")
result.show()

print("\n10. Math functions:")
print("-" * 40)
result = spark.sql("""
    SELECT
        name,
        age,
        age * 2 as double_age,
        age + 10 as age_plus_10,
        salary,
        salary * 1.1 as salary_with_raise
    FROM users
    LIMIT 5
""")
result.show()

print("\n" + "=" * 80)
print("MIXING SQL AND DATAFRAME OPERATIONS")
print("=" * 80)

print("\n11. SQL query followed by DataFrame operations:")
print("-" * 40)
result = (
    spark.sql("SELECT * FROM users WHERE age > 25")
    .filter("salary > 70000")
    .orderBy("salary")
    .limit(5)
)
result.show()

print("\n12. DataFrame operations followed by SQL:")
print("-" * 40)
# Create a filtered DataFrame
high_earners = users_df.filter("salary > 70000")
high_earners.createOrReplaceTempView("high_earners")

# Now query it with SQL
result = spark.sql("""
    SELECT city, COUNT(*) as count, AVG(age) as avg_age
    FROM high_earners
    GROUP BY city
    ORDER BY count DESC
""")
result.show()

print("\n" + "=" * 80)
print("REPLACING TEMP VIEWS")
print("=" * 80)

print("\n13. createOrReplaceTempView example:")
print("-" * 40)
# Create initial view
users_df.createOrReplaceTempView("my_view")
print("Initial view - all users:")
spark.sql("SELECT COUNT(*) as total FROM my_view").show()

# Replace with filtered DataFrame
filtered = users_df.filter("age > 30")
filtered.createOrReplaceTempView("my_view")  # Replaces the existing view
print("After replace - only users over 30:")
spark.sql("SELECT COUNT(*) as total FROM my_view").show()

print("\n" + "=" * 80)
print("Examples completed successfully!")
print("=" * 80)

# Stop the session
spark.stop()
