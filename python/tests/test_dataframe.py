"""
Unit tests for PyRust DataFrame operations.
"""

import os
import sys

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pyrust import SparkSession


@pytest.fixture
def spark():
    """Create a SparkSession for testing."""
    session = SparkSession.builder.appName("PyRust Tests").getOrCreate()
    yield session
    session.stop()


@pytest.fixture
def sample_df(spark):
    """Create a sample DataFrame for testing."""
    # Use the example CSV file
    csv_path = "examples/data/users.csv"
    if not os.path.exists(csv_path):
        pytest.skip(f"Sample data file not found: {csv_path}")
    return spark.read.csv(csv_path, header=True)


class TestSparkSession:
    """Test SparkSession functionality."""

    def test_create_session(self):
        """Test creating a SparkSession."""
        spark = SparkSession.builder.appName("Test").getOrCreate()
        assert spark is not None
        spark.stop()

    def test_session_with_master(self):
        """Test creating a SparkSession with master URL."""
        spark = SparkSession.builder.appName("Test").master("local[*]").getOrCreate()
        assert spark is not None
        spark.stop()


class TestDataFrameReading:
    """Test DataFrame reading operations."""

    def test_read_csv(self, spark):
        """Test reading CSV file."""
        df = spark.read.csv("examples/data/users.csv", header=True)
        assert df is not None
        count = df.count()
        assert count > 0

    def test_read_csv_no_header(self, spark):
        """Test reading CSV without header."""
        df = spark.read.csv("examples/data/users.csv", header=False)
        assert df is not None


class TestDataFrameOperations:
    """Test DataFrame operations."""

    def test_count(self, sample_df):
        """Test counting rows."""
        count = sample_df.count()
        assert count == 10  # users.csv has 10 rows

    def test_select(self, sample_df):
        """Test selecting columns."""
        df = sample_df.select("name", "age")
        assert df is not None
        # Verify it executes without error
        count = df.count()
        assert count == 10

    def test_filter_numeric(self, sample_df):
        """Test filtering with numeric condition."""
        df = sample_df.filter("age > 28")
        count = df.count()
        assert count > 0
        assert count < 10

    def test_filter_equals(self, sample_df):
        """Test filtering with equals condition."""
        df = sample_df.filter("age == 25")
        count = df.count()
        assert count >= 0

    def test_where_alias(self, sample_df):
        """Test that where() is an alias for filter()."""
        df1 = sample_df.filter("age > 28")
        df2 = sample_df.where("age > 28")
        assert df1.count() == df2.count()

    def test_limit(self, sample_df):
        """Test limiting rows."""
        df = sample_df.limit(5)
        count = df.count()
        assert count == 5

    def test_orderby(self, sample_df):
        """Test ordering."""
        df = sample_df.orderBy("age")
        assert df is not None
        count = df.count()
        assert count == 10

    def test_sort_alias(self, sample_df):
        """Test that sort() is an alias for orderBy()."""
        df1 = sample_df.orderBy("age")
        df2 = sample_df.sort("age")
        assert df1.count() == df2.count()

    def test_chaining(self, sample_df):
        """Test chaining multiple operations."""
        df = sample_df.filter("age > 26").select("name", "city").limit(5)
        count = df.count()
        assert count <= 5


class TestGroupedData:
    """Test grouped data operations."""

    def test_groupby_count(self, sample_df):
        """Test grouping and counting."""
        df = sample_df.groupBy("city").count()
        assert df is not None
        count = df.count()
        assert count > 0  # Should have multiple cities

    def test_groupby_agg(self, sample_df):
        """Test grouping with aggregations."""
        df = sample_df.groupBy("city").agg(("age", "avg"))
        assert df is not None
        count = df.count()
        assert count > 0

    def test_groupby_multiple_aggs(self, sample_df):
        """Test grouping with multiple aggregations."""
        df = sample_df.groupBy("city").agg(("age", "avg"), ("salary", "sum"))
        assert df is not None
        count = df.count()
        assert count > 0


class TestDataFrameDisplay:
    """Test DataFrame display operations."""

    def test_show(self, sample_df, capsys):
        """Test show() method."""
        sample_df.show()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_show_with_limit(self, sample_df, capsys):
        """Test show() with custom limit."""
        sample_df.show(5)
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_print_schema(self, sample_df, capsys):
        """Test printSchema() method."""
        sample_df.printSchema()
        captured = capsys.readouterr()
        assert "root" in captured.out
        assert "name" in captured.out or "age" in captured.out

    def test_schema(self, sample_df):
        """Test schema() method."""
        schema = sample_df.schema()
        assert schema is not None
        assert len(schema) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
