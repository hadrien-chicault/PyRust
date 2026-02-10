"""
Tests for column operations: withColumnRenamed, etc.
"""

import pytest
from pyrust import SparkSession


@pytest.fixture
def spark():
    """Create a SparkSession for tests."""
    return SparkSession.builder.appName("ColumnOperationsTests").getOrCreate()


@pytest.fixture
def sample_df(spark, tmp_path):
    """Create a sample DataFrame for testing."""
    csv_file = tmp_path / "sample.csv"
    content = """name,age,city,salary
Alice,25,NYC,60000
Bob,30,LA,75000
Charlie,35,SF,80000
"""
    csv_file.write_text(content)
    return spark.read.csv(str(csv_file), header=True)


class TestWithColumnRenamed:
    """Tests for withColumnRenamed() operation."""

    def test_rename_single_column(self, sample_df):
        """Test renaming a single column."""
        result = sample_df.withColumnRenamed("name", "full_name")

        # Check that the column was renamed
        schema_str = str(result)
        assert "full_name" in schema_str
        assert "name" not in schema_str or "full_name" in schema_str

        # Check that data is preserved
        assert result.count() == sample_df.count()

    def test_rename_multiple_columns_chained(self, sample_df):
        """Test chaining multiple renames."""
        result = (
            sample_df.withColumnRenamed("name", "full_name")
            .withColumnRenamed("age", "user_age")
            .withColumnRenamed("city", "location")
        )

        schema_str = str(result)
        assert "full_name" in schema_str
        assert "user_age" in schema_str
        assert "location" in schema_str

        # Original count preserved
        assert result.count() == sample_df.count()

    def test_rename_preserves_data(self, sample_df):
        """Test that renaming preserves data integrity."""
        result = sample_df.withColumnRenamed("salary", "annual_salary")

        # Count should be the same
        assert result.count() == sample_df.count()

        # Should be able to select the renamed column
        selected = result.select("annual_salary")
        assert selected.count() == sample_df.count()

    def test_rename_nonexistent_column_raises_error(self, sample_df):
        """Test that renaming a non-existent column raises an error."""
        with pytest.raises(RuntimeError, match="does not exist"):
            sample_df.withColumnRenamed("nonexistent", "new_name")

    def test_rename_to_existing_name_raises_error(self, sample_df):
        """Test that renaming to an existing name raises an error."""
        with pytest.raises(RuntimeError, match="already exists"):
            sample_df.withColumnRenamed("name", "age")

    def test_snake_case_alias(self, sample_df):
        """Test that with_column_renamed() alias works."""
        result = sample_df.with_column_renamed("name", "full_name")

        schema_str = str(result)
        assert "full_name" in schema_str
        assert result.count() == sample_df.count()

    def test_rename_then_select(self, sample_df):
        """Test selecting after renaming."""
        result = sample_df.withColumnRenamed("name", "full_name").select("full_name", "age")

        assert result.count() == sample_df.count()

    def test_rename_then_filter(self, sample_df):
        """Test filtering after renaming."""
        result = sample_df.withColumnRenamed("age", "user_age").filter("user_age > 25")

        # Should have 2 rows (Bob and Charlie)
        assert result.count() == 2

    def test_rename_then_orderby(self, sample_df):
        """Test ordering after renaming."""
        result = sample_df.withColumnRenamed("salary", "pay").orderBy("pay")

        # Should work without error
        assert result.count() == sample_df.count()

    def test_rename_in_aggregation(self, sample_df):
        """Test using renamed column in aggregation."""
        result = sample_df.withColumnRenamed("city", "location").groupBy("location").count()

        # Should have 3 groups (NYC, LA, SF)
        assert result.count() == 3
