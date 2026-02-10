"""
DataFrame implementation - Python wrapper around Rust backend.
"""


class DataFrame:
    """
    A distributed collection of data organized into named columns.

    Examples
    --------
    >>> df = spark.read.csv("data.csv")
    >>> df.select("name", "age").show()
    >>> df.filter("age > 18").count()
    """

    def __init__(self, rust_dataframe):
        self._rust_df = rust_dataframe

    def select(self, *cols: str) -> "DataFrame":
        """
        Select columns from the DataFrame.

        Parameters
        ----------
        *cols : str
            Column names to select

        Returns
        -------
        DataFrame
            A new DataFrame with selected columns

        Examples
        --------
        >>> df.select("name", "age")
        """
        rust_df = self._rust_df.select(list(cols))
        return DataFrame(rust_df)

    def filter(self, condition: str) -> "DataFrame":
        """
        Filter rows based on a condition.

        Parameters
        ----------
        condition : str
            Filter condition (e.g., "age > 18")

        Returns
        -------
        DataFrame
            A new DataFrame with filtered rows

        Examples
        --------
        >>> df.filter("age > 18")
        >>> df.filter("name == 'Alice'")
        """
        rust_df = self._rust_df.filter(condition)
        return DataFrame(rust_df)

    def where(self, condition: str) -> "DataFrame":
        """Alias for filter()."""
        return self.filter(condition)

    def groupBy(self, *cols: str) -> "GroupedData":
        """
        Group the DataFrame by specified columns.

        Parameters
        ----------
        *cols : str
            Column names to group by

        Returns
        -------
        GroupedData
            A GroupedData object for aggregation

        Examples
        --------
        >>> df.groupBy("city").count()
        >>> df.groupBy("city", "country").agg([("age", "avg")])
        """
        rust_grouped = self._rust_df.groupBy(list(cols))
        return GroupedData(rust_grouped)

    def orderBy(self, *cols: str) -> "DataFrame":
        """
        Sort the DataFrame by specified columns.

        Parameters
        ----------
        *cols : str
            Column names to sort by

        Returns
        -------
        DataFrame
            A new sorted DataFrame

        Examples
        --------
        >>> df.orderBy("age")
        >>> df.orderBy("age", "name")
        """
        rust_df = self._rust_df.orderBy(list(cols))
        return DataFrame(rust_df)

    def sort(self, *cols: str) -> "DataFrame":
        """Alias for orderBy()."""
        return self.orderBy(*cols)

    def join(self, other: "DataFrame", on=None, how: str = "inner") -> "DataFrame":
        """
        Join this DataFrame with another DataFrame.

        Parameters
        ----------
        other : DataFrame
            The right DataFrame to join with
        on : str, list of str, optional
            Column name(s) to join on. Can be a single column name or list of column names.
            Both DataFrames must have these columns.
        how : str, optional
            Type of join to perform (default: "inner")
            Supported types:
            - "inner": Inner join (default)
            - "left": Left outer join
            - "right": Right outer join
            - "outer" or "full": Full outer join
            - "semi": Left semi join (only left columns where match exists)
            - "anti": Left anti join (only left columns where NO match exists)

        Returns
        -------
        DataFrame
            A new DataFrame containing the joined result

        Examples
        --------
        >>> # Inner join on single column
        >>> result = df1.join(df2, on="user_id")

        >>> # Left join on single column
        >>> result = df1.join(df2, on="user_id", how="left")

        >>> # Join on multiple columns
        >>> result = df1.join(df2, on=["country", "city"])

        >>> # Semi join (filtering)
        >>> result = df1.join(df2, on="user_id", how="semi")

        Notes
        -----
        - For best performance, filter DataFrames before joining
        - Semi and anti joins are more efficient than full joins for filtering operations
        - The join columns must exist in both DataFrames
        """
        # Convert single string to list
        if isinstance(on, str):
            on = [on]

        rust_df = self._rust_df.join(other._rust_df, on=on, how=how)
        return DataFrame(rust_df)

    def limit(self, n: int) -> "DataFrame":
        """
        Limit the number of rows.

        Parameters
        ----------
        n : int
            Number of rows to return

        Returns
        -------
        DataFrame
            A new DataFrame with at most n rows

        Examples
        --------
        >>> df.limit(10)
        """
        rust_df = self._rust_df.limit(n)
        return DataFrame(rust_df)

    def count(self) -> int:
        """
        Count the number of rows.

        Returns
        -------
        int
            Number of rows in the DataFrame

        Examples
        --------
        >>> df.count()
        100
        """
        return self._rust_df.count()

    def show(self, n: int = 20, truncate: bool = True):
        """
        Display the first n rows.

        Parameters
        ----------
        n : int, optional
            Number of rows to display (default: 20)
        truncate : bool, optional
            Whether to truncate long values (default: True)

        Examples
        --------
        >>> df.show()
        >>> df.show(5)
        """
        self._rust_df.show(n, truncate)

    def printSchema(self):
        """
        Print the schema of the DataFrame.

        Examples
        --------
        >>> df.printSchema()
        root
         |-- name: Utf8 (nullable = true)
         |-- age: Int64 (nullable = true)
        """
        self._rust_df.printSchema()

    def schema(self) -> str:
        """Get the schema as a string."""
        return self._rust_df.schema()

    def __repr__(self):
        return repr(self._rust_df)


class GroupedData:
    """
    A grouped DataFrame for aggregation operations.

    Examples
    --------
    >>> grouped = df.groupBy("city")
    >>> grouped.count()
    >>> grouped.agg([("age", "avg"), ("salary", "sum")])
    """

    def __init__(self, rust_grouped):
        self._rust_grouped = rust_grouped

    def count(self) -> DataFrame:
        """
        Count rows in each group.

        Returns
        -------
        DataFrame
            A DataFrame with group keys and counts

        Examples
        --------
        >>> df.groupBy("city").count()
        """
        rust_df = self._rust_grouped.count()
        return DataFrame(rust_df)

    def agg(self, *exprs) -> DataFrame:
        """
        Perform aggregations on grouped data.

        Parameters
        ----------
        *exprs : tuple
            Tuples of (column_name, aggregation_function)
            Supported functions: count, sum, avg, min, max

        Returns
        -------
        DataFrame
            A DataFrame with aggregation results

        Examples
        --------
        >>> df.groupBy("city").agg(("age", "avg"), ("salary", "sum"))
        """
        # Convert to list of tuples
        expr_list = []
        for expr in exprs:
            if isinstance(expr, tuple) and len(expr) == 2:
                expr_list.append(expr)
            else:
                raise ValueError(f"Expected tuple of (column, function), got {expr}")

        rust_df = self._rust_grouped.agg(expr_list)
        return DataFrame(rust_df)

    def sum(self, *cols: str) -> DataFrame:
        """Compute sum for specified columns."""
        exprs = [(col, "sum") for col in cols]
        return self.agg(*exprs)

    def avg(self, *cols: str) -> DataFrame:
        """Compute average for specified columns."""
        exprs = [(col, "avg") for col in cols]
        return self.agg(*exprs)

    def mean(self, *cols: str) -> DataFrame:
        """Alias for avg()."""
        return self.avg(*cols)

    def min(self, *cols: str) -> DataFrame:
        """Compute minimum for specified columns."""
        exprs = [(col, "min") for col in cols]
        return self.agg(*exprs)

    def max(self, *cols: str) -> DataFrame:
        """Compute maximum for specified columns."""
        exprs = [(col, "max") for col in cols]
        return self.agg(*exprs)
