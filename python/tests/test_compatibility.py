"""
Compatibility tests - Ensure API matches PySpark where implemented.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyrust import SparkSession


@pytest.fixture
def spark():
    """Create a SparkSession."""
    session = SparkSession.builder \
        .appName("Compatibility Tests") \
        .getOrCreate()
    yield session
    session.stop()


def test_builder_pattern(spark):
    """Test that builder pattern works like PySpark."""
    # This should work just like PySpark
    spark2 = SparkSession.builder \
        .appName("Test App") \
        .master("local[*]") \
        .getOrCreate()
    assert spark2 is not None
    spark2.stop()


def test_dataframe_api(spark):
    """Test that DataFrame API matches PySpark."""
    if not os.path.exists("examples/data/users.csv"):
        pytest.skip("Sample data not found")

    df = spark.read.csv("examples/data/users.csv", header=True)

    # These methods should all exist and work like PySpark
    assert hasattr(df, 'select')
    assert hasattr(df, 'filter')
    assert hasattr(df, 'where')
    assert hasattr(df, 'groupBy')
    assert hasattr(df, 'orderBy')
    assert hasattr(df, 'sort')
    assert hasattr(df, 'limit')
    assert hasattr(df, 'count')
    assert hasattr(df, 'show')
    assert hasattr(df, 'printSchema')

    # Test method chaining (PySpark style)
    result = df.select("name", "age") \
        .filter("age > 25") \
        .orderBy("age") \
        .limit(5)

    assert result is not None
    assert result.count() <= 5


def test_reader_api(spark):
    """Test that DataFrameReader API matches PySpark."""
    reader = spark.read

    # These methods should exist
    assert hasattr(reader, 'csv')
    assert hasattr(reader, 'parquet')

    # Test parameters match PySpark
    if os.path.exists("examples/data/users.csv"):
        # Should accept header and inferSchema like PySpark
        df = reader.csv("examples/data/users.csv", header=True, inferSchema=True)
        assert df is not None


def test_grouped_data_api(spark):
    """Test that GroupedData API matches PySpark."""
    if not os.path.exists("examples/data/users.csv"):
        pytest.skip("Sample data not found")

    df = spark.read.csv("examples/data/users.csv", header=True)
    grouped = df.groupBy("city")

    # These methods should exist
    assert hasattr(grouped, 'count')
    assert hasattr(grouped, 'agg')

    # Test they work
    result = grouped.count()
    assert result is not None
    assert result.count() > 0
