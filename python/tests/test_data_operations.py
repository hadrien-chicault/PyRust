"""
Tests for data operations: distinct, dropDuplicates, union, intersect, except.
"""

import pytest
from pyrust import SparkSession


@pytest.fixture
def spark():
    """Create a SparkSession for tests."""
    return SparkSession.builder.appName("DataOperationsTests").getOrCreate()


@pytest.fixture
def sample_df(spark, tmp_path):
    """Create a sample DataFrame with duplicates for testing."""
    csv_file = tmp_path / "sample.csv"
    content = """name,age,city
Alice,25,NYC
Bob,30,LA
Alice,25,NYC
Charlie,35,SF
Bob,30,LA
David,28,NYC
"""
    csv_file.write_text(content)
    return spark.read.csv(str(csv_file), header=True)


@pytest.fixture
def df1(spark, tmp_path):
    """Create first DataFrame for set operations."""
    csv_file = tmp_path / "df1.csv"
    content = """id,name
1,Alice
2,Bob
3,Charlie
"""
    csv_file.write_text(content)
    return spark.read.csv(str(csv_file), header=True)


@pytest.fixture
def df2(spark, tmp_path):
    """Create second DataFrame for set operations."""
    csv_file = tmp_path / "df2.csv"
    content = """id,name
2,Bob
3,Charlie
4,David
"""
    csv_file.write_text(content)
    return spark.read.csv(str(csv_file), header=True)


class TestDistinct:
    """Tests for distinct() operation."""

    def test_distinct_removes_duplicates(self, sample_df):
        """Test that distinct removes duplicate rows."""
        result = sample_df.distinct()

        # Original has 6 rows, with 2 duplicate Alice and 2 duplicate Bob
        assert result.count() == 4  # Should have 4 unique rows

    def test_distinct_all_unique(self, df1):
        """Test distinct on DataFrame with no duplicates."""
        result = df1.distinct()

        # Should have same count as original
        assert result.count() == df1.count()

    def test_distinct_chaining(self, sample_df):
        """Test distinct can be chained with other operations."""
        result = sample_df.filter("age > 25").distinct()

        # Should work without errors
        assert result.count() > 0


class TestDropDuplicates:
    """Tests for dropDuplicates() operation."""

    def test_drop_duplicates_no_subset(self, sample_df):
        """Test dropDuplicates without subset (same as distinct)."""
        result = sample_df.dropDuplicates()

        assert result.count() == 4  # Same as distinct

    def test_drop_duplicates_single_column(self, sample_df):
        """Test dropDuplicates on single column."""
        result = sample_df.dropDuplicates(["name"])

        # Should have 4 unique names: Alice, Bob, Charlie, David
        assert result.count() == 4

    def test_drop_duplicates_multiple_columns(self, sample_df):
        """Test dropDuplicates on multiple columns."""
        result = sample_df.dropDuplicates(["name", "age"])

        # Should remove rows with same name AND age
        assert result.count() == 4

    def test_drop_duplicates_alias(self, sample_df):
        """Test drop_duplicates() alias works."""
        result = sample_df.drop_duplicates(["name"])

        assert result.count() == 4

    def test_drop_duplicates_invalid_column(self, sample_df):
        """Test dropDuplicates with invalid column raises error."""
        with pytest.raises(ValueError, match="Column 'invalid' does not exist"):
            sample_df.dropDuplicates(["invalid"])


class TestUnion:
    """Tests for union() and unionAll() operations."""

    def test_union_basic(self, df1, df2):
        """Test basic union of two DataFrames."""
        result = df1.union(df2)

        # df1 has 3 rows, df2 has 3 rows = 6 total
        assert result.count() == 6

    def test_union_keeps_duplicates(self, df1, df2):
        """Test that union keeps duplicate rows."""
        result = df1.union(df2)

        # Bob and Charlie appear in both, so we should have them twice
        result_distinct = result.distinct()
        assert result_distinct.count() == 4  # Alice, Bob, Charlie, David

    def test_union_all_same_as_union(self, df1, df2):
        """Test that unionAll behaves same as union."""
        union_result = df1.union(df2)
        union_all_result = df1.unionAll(df2)

        assert union_result.count() == union_all_result.count()

    def test_union_with_self(self, df1):
        """Test union of DataFrame with itself."""
        result = df1.union(df1)

        # Should double the rows
        assert result.count() == df1.count() * 2

    def test_union_then_distinct(self, df1, df2):
        """Test union followed by distinct."""
        result = df1.union(df2).distinct()

        # Should have 4 unique rows: Alice, Bob, Charlie, David
        assert result.count() == 4


class TestIntersect:
    """Tests for intersect() operation."""

    def test_intersect_basic(self, df1, df2):
        """Test basic intersect of two DataFrames."""
        result = df1.intersect(df2)

        # Bob and Charlie appear in both
        assert result.count() == 2

    def test_intersect_no_common_rows(self, spark, tmp_path):
        """Test intersect with no common rows."""
        csv1 = tmp_path / "a.csv"
        csv1.write_text("id,name\n1,Alice\n")

        csv2 = tmp_path / "b.csv"
        csv2.write_text("id,name\n2,Bob\n")

        df_a = spark.read.csv(str(csv1), header=True)
        df_b = spark.read.csv(str(csv2), header=True)

        result = df_a.intersect(df_b)
        assert result.count() == 0

    def test_intersect_with_self(self, df1):
        """Test intersect of DataFrame with itself."""
        result = df1.intersect(df1)

        # Should have same rows (duplicates removed)
        assert result.count() == df1.count()

    def test_intersect_with_distinct(self, spark, tmp_path):
        """Test using distinct() after intersect for unique rows."""
        csv1 = tmp_path / "c.csv"
        csv1.write_text("id,name\n1,Alice\n1,Alice\n2,Bob\n")

        csv2 = tmp_path / "d.csv"
        csv2.write_text("id,name\n1,Alice\n")

        df_c = spark.read.csv(str(csv1), header=True)
        df_d = spark.read.csv(str(csv2), header=True)

        result = df_c.intersect(df_d).distinct()
        # After distinct, should have only 1 Alice row
        assert result.count() == 1


class TestExcept:
    """Tests for exceptAll() operation."""

    def test_except_basic(self, df1, df2):
        """Test basic except operation."""
        result = df1.exceptAll(df2)

        # df1 has Alice, Bob, Charlie
        # df2 has Bob, Charlie, David
        # Result should have only Alice
        assert result.count() == 1

    def test_except_reverse(self, df1, df2):
        """Test except in reverse order."""
        result = df2.exceptAll(df1)

        # df2 has Bob, Charlie, David
        # df1 has Alice, Bob, Charlie
        # Result should have only David
        assert result.count() == 1

    def test_except_no_difference(self, df1):
        """Test except with same DataFrame."""
        result = df1.exceptAll(df1)

        # Should have 0 rows
        assert result.count() == 0

    def test_except_all_different(self, spark, tmp_path):
        """Test except where all rows are different."""
        csv1 = tmp_path / "e.csv"
        csv1.write_text("id,name\n1,Alice\n2,Bob\n")

        csv2 = tmp_path / "f.csv"
        csv2.write_text("id,name\n3,Charlie\n4,David\n")

        df_e = spark.read.csv(str(csv1), header=True)
        df_f = spark.read.csv(str(csv2), header=True)

        result = df_e.exceptAll(df_f)
        # Should have all rows from df_e
        assert result.count() == 2

    def test_subtract_alias(self, df1, df2):
        """Test that subtract() is an alias for exceptAll()."""
        except_result = df1.exceptAll(df2)
        subtract_result = df1.subtract(df2)

        assert except_result.count() == subtract_result.count()


class TestChainedOperations:
    """Tests for chaining multiple data operations."""

    def test_filter_then_distinct(self, sample_df):
        """Test filter followed by distinct."""
        result = sample_df.filter("age > 25").distinct()

        assert result.count() > 0

    def test_union_then_filter(self, df1, df2):
        """Test union followed by filter."""
        result = df1.union(df2).filter("id > 2")

        assert result.count() > 0

    def test_distinct_then_orderby(self, sample_df):
        """Test distinct followed by orderBy."""
        result = sample_df.distinct().orderBy("name")

        assert result.count() == 4

    def test_complex_chain(self, df1, df2):
        """Test complex chain of operations."""
        result = df1.union(df2).distinct().filter("id > 1").orderBy("id").limit(2)

        assert result.count() == 2


class TestPerformance:
    """Performance-related tests."""

    def test_distinct_on_large_duplicates(self, spark, tmp_path):
        """Test distinct on DataFrame with many duplicates."""
        csv_file = tmp_path / "large_dup.csv"
        # Create DataFrame with lots of duplicates
        content = "id,value\n"
        for i in range(100):
            content += f"{i % 10},value_{i % 10}\n"
        csv_file.write_text(content)

        df = spark.read.csv(str(csv_file), header=True)
        result = df.distinct()

        # Should have only 10 unique rows
        assert result.count() == 10

    def test_union_multiple(self, df1):
        """Test union of multiple DataFrames."""
        result = df1.union(df1).union(df1)

        assert result.count() == df1.count() * 3
