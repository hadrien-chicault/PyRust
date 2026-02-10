"""
Tests for SQL query support.
"""

import pytest
from pyrust import SparkSession


@pytest.fixture
def spark():
    """Create a SparkSession for tests."""
    return SparkSession.builder.appName("SQLTests").getOrCreate()


@pytest.fixture
def users_df(spark):
    """Create a users DataFrame for testing."""
    return spark.read.csv("examples/data/users.csv", header=True)


class TestBasicSQL:
    """Tests for basic SQL queries."""

    def test_simple_select(self, spark, users_df):
        """Test simple SELECT query."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("SELECT * FROM users")

        assert result.count() == users_df.count()

    def test_select_specific_columns(self, spark, users_df):
        """Test SELECT with specific columns."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("SELECT name, age FROM users")

        assert result.count() == users_df.count()

    def test_select_with_where(self, spark, users_df):
        """Test SELECT with WHERE clause."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("SELECT * FROM users WHERE age > 25")

        assert result.count() > 0
        assert result.count() <= users_df.count()


class TestAggregationSQL:
    """Tests for SQL aggregation queries."""

    def test_count_aggregate(self, spark, users_df):
        """Test COUNT aggregate function."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("SELECT COUNT(*) as count FROM users")

        assert result.count() == 1

    def test_group_by(self, spark, users_df):
        """Test GROUP BY clause."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("SELECT city, COUNT(*) as count FROM users GROUP BY city")

        assert result.count() > 0

    def test_multiple_aggregates(self, spark, users_df):
        """Test multiple aggregate functions."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("""
            SELECT
                city,
                COUNT(*) as count,
                AVG(age) as avg_age,
                MAX(salary) as max_salary
            FROM users
            GROUP BY city
        """)

        assert result.count() > 0


class TestOrderBySQL:
    """Tests for ORDER BY in SQL."""

    def test_order_by_single(self, spark, users_df):
        """Test ORDER BY single column."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("SELECT * FROM users ORDER BY age")

        assert result.count() == users_df.count()

    def test_order_by_desc(self, spark, users_df):
        """Test ORDER BY with DESC."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("SELECT * FROM users ORDER BY age DESC")

        assert result.count() == users_df.count()

    def test_order_by_multiple(self, spark, users_df):
        """Test ORDER BY multiple columns."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("SELECT * FROM users ORDER BY city, age")

        assert result.count() == users_df.count()


class TestComplexSQL:
    """Tests for complex SQL queries."""

    def test_having_clause(self, spark, users_df):
        """Test HAVING clause with GROUP BY."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("""
            SELECT city, COUNT(*) as count
            FROM users
            GROUP BY city
            HAVING count > 1
        """)

        # Should execute without error
        result.count()

    def test_limit_clause(self, spark, users_df):
        """Test LIMIT clause."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("SELECT * FROM users LIMIT 5")

        assert result.count() <= 5

    def test_case_when(self, spark, users_df):
        """Test CASE WHEN expression."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("""
            SELECT
                name,
                age,
                CASE
                    WHEN age < 25 THEN 'young'
                    WHEN age < 35 THEN 'mid'
                    ELSE 'senior'
                END as age_group
            FROM users
        """)

        assert result.count() == users_df.count()


class TestJoinsViaSQL:
    """Tests for joins using SQL syntax."""

    def test_inner_join_sql(self, spark, tmp_path):
        """Test INNER JOIN via SQL."""
        # Create two DataFrames
        df1_csv = tmp_path / "employees.csv"
        df1_content = """id,name,dept_id
1,Alice,10
2,Bob,20
3,Charlie,10
"""
        df1_csv.write_text(df1_content)

        df2_csv = tmp_path / "departments.csv"
        df2_content = """dept_id,dept_name
10,Engineering
20,Sales
30,Marketing
"""
        df2_csv.write_text(df2_content)

        df1 = spark.read.csv(str(df1_csv), header=True)
        df2 = spark.read.csv(str(df2_csv), header=True)

        df1.createOrReplaceTempView("employees")
        df2.createOrReplaceTempView("departments")

        result = spark.sql("""
            SELECT e.name, d.dept_name
            FROM employees e
            INNER JOIN departments d ON e.dept_id = d.dept_id
        """)

        assert result.count() == 3

    def test_left_join_sql(self, spark, tmp_path):
        """Test LEFT JOIN via SQL."""
        df1_csv = tmp_path / "employees.csv"
        df1_content = """id,name,dept_id
1,Alice,10
2,Bob,20
3,Charlie,99
"""
        df1_csv.write_text(df1_content)

        df2_csv = tmp_path / "departments.csv"
        df2_content = """dept_id,dept_name
10,Engineering
20,Sales
"""
        df2_csv.write_text(df2_content)

        df1 = spark.read.csv(str(df1_csv), header=True)
        df2 = spark.read.csv(str(df2_csv), header=True)

        df1.createOrReplaceTempView("employees")
        df2.createOrReplaceTempView("departments")

        result = spark.sql("""
            SELECT e.name, d.dept_name
            FROM employees e
            LEFT JOIN departments d ON e.dept_id = d.dept_id
        """)

        # All employees should be in result
        assert result.count() == 3


class TestSubqueriesSQL:
    """Tests for subqueries in SQL."""

    def test_subquery_in_where(self, spark, users_df):
        """Test subquery in WHERE clause."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("""
            SELECT * FROM users
            WHERE age > (SELECT AVG(age) FROM users)
        """)

        # Should have some results
        assert result.count() > 0

    def test_subquery_in_from(self, spark, users_df):
        """Test subquery in FROM clause."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("""
            SELECT city, avg_age
            FROM (
                SELECT city, AVG(age) as avg_age
                FROM users
                GROUP BY city
            ) AS city_stats
            WHERE avg_age > 25
        """)

        # Should execute without error
        result.count()


class TestSQLFunctions:
    """Tests for SQL functions."""

    def test_string_functions(self, spark, users_df):
        """Test string functions like UPPER, LOWER."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("""
            SELECT UPPER(name) as upper_name, LOWER(city) as lower_city
            FROM users
        """)

        assert result.count() == users_df.count()

    def test_math_functions(self, spark, users_df):
        """Test math functions."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("""
            SELECT name, age, age * 2 as double_age, age + 10 as age_plus_10
            FROM users
        """)

        assert result.count() == users_df.count()


class TestTempViews:
    """Tests for temporary view management."""

    def test_create_temp_view(self, spark, users_df):
        """Test creating a temp view."""
        users_df.createOrReplaceTempView("test_view")

        result = spark.sql("SELECT * FROM test_view")
        assert result.count() == users_df.count()

    def test_replace_temp_view(self, spark, users_df):
        """Test replacing an existing temp view."""
        users_df.createOrReplaceTempView("test_view")
        result1 = spark.sql("SELECT * FROM test_view")
        count1 = result1.count()

        # Replace with filtered DataFrame
        filtered = users_df.filter("age > 25")
        filtered.createOrReplaceTempView("test_view")

        result2 = spark.sql("SELECT * FROM test_view")
        count2 = result2.count()

        # Second query should have fewer results
        assert count2 <= count1


class TestSQLErrors:
    """Tests for SQL error handling."""

    def test_invalid_sql_syntax(self, spark):
        """Test that invalid SQL raises error."""
        with pytest.raises(RuntimeError, match="Failed to execute SQL"):
            spark.sql("SELCT * FROM users")  # Typo

    def test_nonexistent_table(self, spark):
        """Test querying non-existent table raises error."""
        with pytest.raises(RuntimeError, match="Failed to execute SQL"):
            spark.sql("SELECT * FROM nonexistent_table")

    def test_invalid_column(self, spark, users_df):
        """Test querying invalid column raises error."""
        users_df.createOrReplaceTempView("users")

        with pytest.raises(RuntimeError, match="Failed to execute SQL"):
            spark.sql("SELECT nonexistent_column FROM users")


class TestSQLChaining:
    """Tests for chaining SQL with DataFrame operations."""

    def test_sql_then_dataframe_ops(self, spark, users_df):
        """Test using DataFrame operations on SQL results."""
        users_df.createOrReplaceTempView("users")

        result = spark.sql("SELECT * FROM users WHERE age > 25").filter("salary > 70000").limit(5)

        assert result.count() <= 5

    def test_dataframe_then_sql(self, spark, users_df):
        """Test SQL on DataFrame that was created from operations."""
        filtered = users_df.filter("age > 25")
        filtered.createOrReplaceTempView("filtered_users")

        result = spark.sql("SELECT city, COUNT(*) FROM filtered_users GROUP BY city")

        assert result.count() > 0
