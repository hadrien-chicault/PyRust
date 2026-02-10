"""
Tests for DataFrame join operations.
"""

import pytest
from pyrust import SparkSession


@pytest.fixture
def spark():
    """Create a SparkSession for tests."""
    return SparkSession.builder.appName("JoinTests").getOrCreate()


@pytest.fixture
def users_df(spark):
    """Create a users DataFrame for testing."""
    # Use the existing users CSV
    return spark.read.csv("examples/data/users.csv", header=True)


@pytest.fixture
def departments_csv(tmp_path):
    """Create a temporary departments CSV file."""
    csv_file = tmp_path / "departments.csv"
    csv_content = """dept_id,dept_name,budget
1,Engineering,500000
2,Sales,300000
3,Marketing,200000
4,HR,150000
"""
    csv_file.write_text(csv_content)
    return str(csv_file)


@pytest.fixture
def salaries_csv(tmp_path):
    """Create a temporary salaries CSV file."""
    csv_file = tmp_path / "salaries.csv"
    csv_content = """name,base_salary,bonus
Alice,60000,10000
Bob,75000,10000
Charlie,80000,10000
Diana,65000,10000
Frank,45000,5000
"""
    csv_file.write_text(csv_content)
    return str(csv_file)


class TestInnerJoin:
    """Tests for inner join operations."""

    def test_inner_join_single_column(self, spark, users_df, salaries_csv):
        """Test inner join on a single column."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result = users_df.join(salaries_df, on=["name"])

        # Check that result contains data
        count = result.count()
        assert count > 0

        # Inner join should only have rows where names match
        assert count <= users_df.count()
        assert count <= salaries_df.count()

    def test_inner_join_implicit(self, spark, users_df, salaries_csv):
        """Test that inner join is the default."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result1 = users_df.join(salaries_df, on=["name"])
        result2 = users_df.join(salaries_df, on=["name"], how="inner")

        assert result1.count() == result2.count()


class TestLeftJoin:
    """Tests for left outer join operations."""

    def test_left_join(self, spark, users_df, salaries_csv):
        """Test left outer join."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result = users_df.join(salaries_df, on=["name"], how="left")

        # Left join should have all rows from left DataFrame
        assert result.count() == users_df.count()


class TestRightJoin:
    """Tests for right outer join operations."""

    def test_right_join(self, spark, users_df, salaries_csv):
        """Test right outer join."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result = users_df.join(salaries_df, on=["name"], how="right")

        # Right join should have all rows from right DataFrame
        assert result.count() == salaries_df.count()


class TestFullOuterJoin:
    """Tests for full outer join operations."""

    def test_full_outer_join(self, spark, users_df, salaries_csv):
        """Test full outer join."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result = users_df.join(salaries_df, on=["name"], how="outer")

        # Full outer join should have at least as many rows as the larger DataFrame
        assert result.count() >= max(users_df.count(), salaries_df.count())

    def test_full_alias(self, spark, users_df, salaries_csv):
        """Test that 'full' is an alias for 'outer'."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result1 = users_df.join(salaries_df, on=["name"], how="outer")
        result2 = users_df.join(salaries_df, on=["name"], how="full")

        assert result1.count() == result2.count()


class TestSemiJoin:
    """Tests for left semi join operations."""

    def test_semi_join(self, spark, users_df, salaries_csv):
        """Test left semi join."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result = users_df.join(salaries_df, on=["name"], how="semi")

        # Semi join should only have matching rows from left
        assert result.count() <= users_df.count()
        assert result.count() > 0


class TestAntiJoin:
    """Tests for left anti join operations."""

    def test_anti_join(self, spark, users_df, salaries_csv):
        """Test left anti join."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result = users_df.join(salaries_df, on=["name"], how="anti")

        # Anti join should have rows from left that don't match right
        assert result.count() <= users_df.count()


class TestMultiColumnJoin:
    """Tests for joins on multiple columns."""

    def test_multi_column_join(self, spark, tmp_path):
        """Test join on multiple columns."""
        # Create two DataFrames with multiple join keys
        df1_csv = tmp_path / "df1.csv"
        df1_content = """country,city,population
USA,New York,8000000
USA,Los Angeles,4000000
UK,London,9000000
France,Paris,2000000
"""
        df1_csv.write_text(df1_content)

        df2_csv = tmp_path / "df2.csv"
        df2_content = """country,city,gdp
USA,New York,1500000
USA,Los Angeles,900000
UK,London,800000
Germany,Berlin,600000
"""
        df2_csv.write_text(df2_content)

        df1 = spark.read.csv(str(df1_csv), header=True)
        df2 = spark.read.csv(str(df2_csv), header=True)

        result = df1.join(df2, on=["country", "city"])

        # Should only have rows where both country AND city match
        assert result.count() == 3  # USA/NY, USA/LA, UK/London


class TestJoinParameters:
    """Tests for join parameter handling."""

    def test_single_column_string(self, spark, users_df, salaries_csv):
        """Test that a single column can be passed as string."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        # Should work with string
        result = users_df.join(salaries_df, on="name")
        assert result.count() > 0

    def test_invalid_join_type(self, spark, users_df, salaries_csv):
        """Test that invalid join type raises error."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        with pytest.raises(RuntimeError, match="Invalid join type"):
            users_df.join(salaries_df, on=["name"], how="invalid")

    def test_missing_join_keys(self, spark, users_df, salaries_csv):
        """Test that missing join keys raises error."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        with pytest.raises(RuntimeError, match="Join keys required"):
            users_df.join(salaries_df, on=None)


class TestJoinChaining:
    """Tests for chaining joins with other operations."""

    def test_filter_before_join(self, spark, users_df, salaries_csv):
        """Test filtering before join."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result = users_df.filter("age > 25").join(salaries_df, on=["name"])

        assert result.count() > 0
        assert result.count() <= users_df.filter("age > 25").count()

    def test_join_then_select(self, spark, users_df, salaries_csv):
        """Test selecting after join."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result = users_df.join(salaries_df, on=["name"]).select(["name", "age"])

        # Should execute without error
        assert result.count() > 0

    def test_join_then_aggregate(self, spark, users_df, salaries_csv):
        """Test aggregating after join."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result = users_df.join(salaries_df, on=["name"]).groupBy(["city"]).count()

        assert result.count() > 0


class TestJoinDisplay:
    """Tests for displaying joined DataFrames."""

    def test_show_after_join(self, spark, users_df, salaries_csv):
        """Test that show() works after join."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result = users_df.join(salaries_df, on=["name"])

        # Should not raise an error
        result.show(5)

    def test_print_schema_after_join(self, spark, users_df, salaries_csv):
        """Test that printSchema() works after join."""
        salaries_df = spark.read.csv(salaries_csv, header=True)

        result = users_df.join(salaries_df, on=["name"])

        # Should not raise an error
        result.printSchema()
