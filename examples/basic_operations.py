"""
Basic PyRust Operations Example

This example demonstrates the core functionality of PyRust,
showing how it provides a PySpark-compatible API with Rust performance.
"""

from pyrust import SparkSession


def main():
    print("=" * 60)
    print("PyRust - Basic Operations Demo")
    print("=" * 60)
    print()

    # Create SparkSession
    print("1. Creating SparkSession...")
    spark = SparkSession.builder \
        .appName("PyRust Basic Demo") \
        .getOrCreate()
    print(f"   Created: {spark}")
    print()

    # Read CSV file
    print("2. Reading CSV file...")
    df = spark.read.csv("examples/data/users.csv", header=True)
    print(f"   Loaded DataFrame: {df}")
    print()

    # Show data
    print("3. Showing all data:")
    df.show()
    print()

    # Print schema
    print("4. Schema information:")
    df.printSchema()
    print()

    # Select specific columns
    print("5. Selecting columns (name, age):")
    df.select("name", "age").show()
    print()

    # Filter data
    print("6. Filtering (age > 28):")
    df.filter("age > 28").show()
    print()

    # Multiple operations
    print("7. Complex query (age > 27, select name and city):")
    df.filter("age > 27") \
        .select("name", "city") \
        .show()
    print()

    # Group by and count
    print("8. Group by city and count:")
    df.groupBy("city").count().show()
    print()

    # Group by with aggregations
    print("9. Group by city with avg(age) and avg(salary):")
    df.groupBy("city") \
        .agg(("age", "avg"), ("salary", "avg")) \
        .show()
    print()

    # Order by
    print("10. Order by salary (descending order not yet supported in POC):")
    df.orderBy("salary").show()
    print()

    # Limit
    print("11. Limit to 3 rows:")
    df.limit(3).show()
    print()

    # Count
    print("12. Total row count:")
    count = df.count()
    print(f"   Total rows: {count}")
    print()

    # Complex chain
    print("13. Complex chain: filter age > 26, group by city, count, order by city:")
    df.filter("age > 26") \
        .groupBy("city") \
        .count() \
        .orderBy("city") \
        .show()
    print()

    # Stop session
    print("14. Stopping SparkSession...")
    spark.stop()
    print("   Done!")
    print()

    print("=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
