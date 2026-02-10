"""
SparkSession implementation - Python wrapper around Rust backend.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyrust._pyrust import SparkSession as _RustSparkSession

if TYPE_CHECKING:
    from pyrust.dataframe import DataFrame


class SparkSession:
    """
    Main entry point for PyRust functionality.

    A SparkSession can be used to create DataFrames, register DataFrames as tables,
    execute SQL over tables, and more.

    Examples
    --------
    >>> spark = SparkSession.builder.appName("MyApp").getOrCreate()
    >>> df = spark.read.csv("data.csv", header=True)
    >>> df.show()
    """

    def __init__(self, rust_session: _RustSparkSession):
        self._rust_session = rust_session

    @property
    def builder(self):
        """Get a builder for SparkSession."""
        return SparkSessionBuilder()

    @property
    def read(self):
        """Get DataFrameReader for reading data."""
        return DataFrameReader(self._rust_session.read, spark_session=self)

    @property
    def appName(self):
        """Get the application name."""
        return self._rust_session.appName

    def sql(self, query: str) -> DataFrame:
        """
        Execute a SQL query and return the result as a DataFrame.

        Parameters
        ----------
        query : str
            SQL query string to execute

        Returns
        -------
        DataFrame
            The query result as a DataFrame

        Examples
        --------
        >>> df = spark.sql("SELECT name, age FROM users WHERE age > 18")
        >>> df = spark.sql("SELECT city, COUNT(*) FROM users GROUP BY city")
        """
        from .dataframe import DataFrame

        rust_df = self._rust_session.sql(query)
        return DataFrame(rust_df, session=self)

    def register_temp_view(self, df: DataFrame, name: str):
        """
        Register a DataFrame as a temporary view (internal method).

        This is used by DataFrame.createOrReplaceTempView().
        """
        self._rust_session.register_temp_view(df._rust_df, name)

    def stop(self):
        """Stop the SparkSession."""
        self._rust_session.stop()

    def __repr__(self):
        return repr(self._rust_session)


class SparkSessionBuilder:
    """
    Builder for SparkSession.

    Examples
    --------
    >>> spark = SparkSession.builder \\
    ...     .appName("MyApp") \\
    ...     .master("local[*]") \\
    ...     .getOrCreate()
    """

    def __init__(self):
        from pyrust._pyrust import SparkSessionBuilder as _RustBuilder

        self._rust_builder = _RustBuilder()

    def appName(self, name: str) -> SparkSessionBuilder:
        """Set application name."""
        self._rust_builder = self._rust_builder.appName(name)
        return self

    def master(self, master: str) -> SparkSessionBuilder:
        """Set master URL (for compatibility, not used in POC)."""
        self._rust_builder = self._rust_builder.master(master)
        return self

    def getOrCreate(self) -> SparkSession:
        """Get or create a SparkSession."""
        rust_session = self._rust_builder.getOrCreate()
        return SparkSession(rust_session)


# Make builder accessible as class attribute
SparkSession.builder = SparkSessionBuilder()


class DataFrameReader:
    """
    Interface for reading data into DataFrames.

    Examples
    --------
    >>> spark.read.csv("data.csv", header=True)
    >>> spark.read.parquet("data.parquet")
    """

    def __init__(self, rust_reader, spark_session=None):
        self._rust_reader = rust_reader
        self._spark_session = spark_session

    def csv(self, path: str, header: bool = True, inferSchema: bool = True):
        """
        Read a CSV file into a DataFrame.

        Parameters
        ----------
        path : str
            Path to the CSV file
        header : bool, optional
            Whether the CSV has a header row (default: True)
        inferSchema : bool, optional
            Whether to infer the schema (default: True)

        Returns
        -------
        DataFrame
            The loaded DataFrame
        """
        from .dataframe import DataFrame

        rust_df = self._rust_reader.csv(path, header=header, infer_schema=inferSchema)
        return DataFrame(rust_df, session=self._spark_session)

    def parquet(self, path: str):
        """
        Read a Parquet file into a DataFrame.

        Parameters
        ----------
        path : str
            Path to the Parquet file

        Returns
        -------
        DataFrame
            The loaded DataFrame
        """
        from .dataframe import DataFrame

        rust_df = self._rust_reader.parquet(path)
        return DataFrame(rust_df, session=self._spark_session)
