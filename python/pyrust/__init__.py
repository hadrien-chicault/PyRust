"""
PyRust - A Rust-based implementation of PySpark for high-performance distributed computing.

This module provides a PySpark-compatible API backed by a high-performance Rust engine
using Apache DataFusion and Arrow.
"""

__version__ = "0.1.0"

# Import the compiled Rust module
try:
    from pyrust._pyrust import DataFrame as _RustDataFrame
    from pyrust._pyrust import SparkSession as _RustSparkSession
except ImportError as e:
    raise ImportError(
        "Failed to import PyRust native module. "
        "Make sure you have built the Rust extension with 'maturin develop' or 'pip install -e .'"
    ) from e

# Re-export main classes
from .column import Column
from .dataframe import DataFrame
from .session import SparkSession

__all__ = [
    "SparkSession",
    "DataFrame",
    "Column",
    "__version__",
]
