# Testing Guide

Guide for writing and running tests in PyRust.

## Test Structure

```
python/tests/
├── test_dataframe.py       # Core DataFrame tests
├── test_joins.py           # Join operation tests
├── test_data_operations.py # Distinct, union, etc.
├── test_column_operations.py # Column manipulation
├── test_sql.py             # SQL query tests
└── test_compatibility.py   # PySpark compatibility
```

## Running Tests

### All Tests

```bash
pytest python/tests/ -v
```

### Specific File

```bash
pytest python/tests/test_dataframe.py -v
```

### Specific Test

```bash
pytest python/tests/test_dataframe.py::TestDataFrameOperations::test_filter_numeric -v
```

### With Coverage

```bash
pytest python/tests/ --cov=pyrust --cov-report=html
```

## Writing Tests

### Test Structure

```python
import pytest
from pyrust import SparkSession

@pytest.fixture
def spark():
    """Create SparkSession for tests."""
    return SparkSession.builder.appName("Test").getOrCreate()

@pytest.fixture
def sample_df(spark, tmp_path):
    """Create sample DataFrame."""
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,age\nAlice,25\nBob,30\n")
    return spark.read.csv(str(csv_file), header=True)

class TestFeature:
    """Tests for feature X."""

    def test_basic_case(self, sample_df):
        """Test basic functionality."""
        result = sample_df.operation()
        assert result.count() == 2

    def test_edge_case(self, sample_df):
        """Test edge case."""
        # Test implementation
```

### Test Fixtures

Common fixtures:
- `spark` - SparkSession instance
- `tmp_path` - Temporary directory (pytest built-in)
- Sample DataFrames created in fixtures

### Assertions

```python
# Count checks
assert df.count() == 10

# Content checks (use show for debugging)
result.show()
assert "expected_value" in str(result)

# Error checks
with pytest.raises(RuntimeError, match="error message"):
    df.invalid_operation()
```

## Test Categories

### Unit Tests

Test individual operations:

```python
def test_select(self, sample_df):
    result = sample_df.select("name")
    assert result.count() == sample_df.count()
```

### Integration Tests

Test multiple operations:

```python
def test_filter_and_aggregate(self, sample_df):
    result = sample_df.filter("age > 25") \
                     .groupBy("city") \
                     .count()
    assert result.count() > 0
```

### Compatibility Tests

Verify PySpark compatibility:

```python
def test_api_compatibility(self):
    """Test that API matches PySpark."""
    # Verify methods exist and have correct signatures
```

## Best Practices

### 1. Use Fixtures

```python
@pytest.fixture
def users_df(spark, tmp_path):
    csv_file = tmp_path / "users.csv"
    csv_file.write_text("name,age\nAlice,25\n")
    return spark.read.csv(str(csv_file), header=True)
```

### 2. Test Edge Cases

```python
def test_empty_dataframe(self, spark):
    """Test operations on empty DataFrame."""
    # Create empty DataFrame
    # Verify behavior
```

### 3. Test Error Conditions

```python
def test_invalid_column_raises_error(self, sample_df):
    with pytest.raises(ValueError):
        sample_df.select("nonexistent_column")
```

### 4. Keep Tests Fast

- Use small datasets
- Avoid unnecessary I/O
- Use tmp_path for temp files

### 5. Test Names Should Be Descriptive

```python
def test_join_on_single_column_returns_matching_rows(self):
    # Clear what's being tested
```

## CI/CD

Tests run automatically on:
- Every push to GitHub
- Every pull request

See `.github/workflows/ci.yml` for CI configuration.

## See Also

- [Building Guide](building.md)
- [Contributing Guide](contributing.md)
- [Local CI](local-ci.md)
