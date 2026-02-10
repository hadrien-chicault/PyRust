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

    def __init__(self, rust_dataframe, session=None):
        self._rust_df = rust_dataframe
        self._session = session  # Optional reference to SparkSession for temp views

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
        return DataFrame(rust_df, session=self._session)

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
        return DataFrame(rust_df, session=self._session)

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
        return GroupedData(rust_grouped, session=self._session)

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
        return DataFrame(rust_df, session=self._session)

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
        return DataFrame(rust_df, session=self._session)

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
        return DataFrame(rust_df, session=self._session)

    def distinct(self) -> "DataFrame":
        """
        Remove duplicate rows from the DataFrame.

        Returns a new DataFrame with only unique rows. All columns are
        considered when determining duplicates.

        Returns
        -------
        DataFrame
            A new DataFrame containing only distinct rows

        Examples
        --------
        >>> df.distinct()

        Notes
        -----
        - The order of rows in the result is not guaranteed
        - Use dropDuplicates() if you want to check uniqueness on specific columns only
        """
        rust_df = self._rust_df.distinct()
        return DataFrame(rust_df, session=self._session)

    def dropDuplicates(self, subset=None) -> "DataFrame":
        """
        Remove duplicate rows based on specified columns.

        Parameters
        ----------
        subset : list of str, optional
            Column names to consider for identifying duplicates.
            If None, all columns are used (equivalent to distinct()).

        Returns
        -------
        DataFrame
            A new DataFrame with duplicates removed

        Examples
        --------
        >>> # Remove duplicates based on all columns
        >>> df.dropDuplicates()

        >>> # Remove duplicates based on 'name' column only
        >>> df.dropDuplicates(['name'])

        >>> # Remove duplicates based on multiple columns
        >>> df.dropDuplicates(['name', 'city'])

        Notes
        -----
        - More efficient than distinct() when only checking a subset of columns
        - The first occurrence of each unique combination is kept
        """
        if subset is None:
            rust_df = self._rust_df.dropDuplicates(None)
        else:
            rust_df = self._rust_df.dropDuplicates(subset)
        return DataFrame(rust_df, session=self._session)

    def drop_duplicates(self, subset=None) -> "DataFrame":
        """Alias for dropDuplicates()."""
        return self.dropDuplicates(subset)

    def union(self, other: "DataFrame") -> "DataFrame":
        """
        Combine two DataFrames vertically (union).

        Returns a new DataFrame containing all rows from both DataFrames.
        Duplicates are kept (equivalent to SQL UNION ALL).

        Parameters
        ----------
        other : DataFrame
            The DataFrame to union with this one

        Returns
        -------
        DataFrame
            A new DataFrame with rows from both DataFrames

        Examples
        --------
        >>> df1 = spark.read.csv("data1.csv")
        >>> df2 = spark.read.csv("data2.csv")
        >>> combined = df1.union(df2)

        Notes
        -----
        - Both DataFrames must have the same schema (column names and types)
        - Column order must match
        - Duplicates are NOT removed (use distinct() after union if needed)
        """
        rust_df = self._rust_df.union(other._rust_df)
        return DataFrame(rust_df, session=self._session)

    def unionAll(self, other: "DataFrame") -> "DataFrame":
        """
        Combine two DataFrames vertically, keeping duplicates.

        This is an alias for union(). In PySpark, both union() and unionAll()
        keep duplicates (they are equivalent).

        Parameters
        ----------
        other : DataFrame
            The DataFrame to union with this one

        Returns
        -------
        DataFrame
            A new DataFrame with rows from both DataFrames

        Examples
        --------
        >>> combined = df1.unionAll(df2)
        """
        rust_df = self._rust_df.unionAll(other._rust_df)
        return DataFrame(rust_df, session=self._session)

    def intersect(self, other: "DataFrame") -> "DataFrame":
        """
        Return rows that exist in both DataFrames (intersection).

        Returns a new DataFrame containing only rows that appear in both
        this DataFrame and the other DataFrame. Duplicates are automatically
        removed from the result.

        Parameters
        ----------
        other : DataFrame
            The DataFrame to intersect with

        Returns
        -------
        DataFrame
            A new DataFrame with rows common to both DataFrames

        Examples
        --------
        >>> df1 = spark.read.csv("data1.csv")
        >>> df2 = spark.read.csv("data2.csv")
        >>> common = df1.intersect(df2)

        Notes
        -----
        - Both DataFrames must have compatible schemas
        - Duplicates are automatically removed
        - This is equivalent to SQL INTERSECT
        """
        rust_df = self._rust_df.intersect(other._rust_df)
        return DataFrame(rust_df, session=self._session)

    def exceptAll(self, other: "DataFrame") -> "DataFrame":
        """
        Return rows in this DataFrame but not in the other (difference).

        Returns a new DataFrame containing rows that exist in this DataFrame
        but not in the other DataFrame. Duplicates are automatically removed.

        Parameters
        ----------
        other : DataFrame
            The DataFrame whose rows should be excluded

        Returns
        -------
        DataFrame
            A new DataFrame with rows from this DataFrame not in other

        Examples
        --------
        >>> df1 = spark.read.csv("data1.csv")
        >>> df2 = spark.read.csv("data2.csv")
        >>> difference = df1.exceptAll(df2)

        Notes
        -----
        - Both DataFrames must have compatible schemas
        - Duplicates are automatically removed
        - This is equivalent to SQL EXCEPT
        - Named exceptAll() instead of except() because except is a Python keyword
        """
        rust_df = self._rust_df.except_(other._rust_df)
        return DataFrame(rust_df, session=self._session)

    def subtract(self, other: "DataFrame") -> "DataFrame":
        """Alias for exceptAll()."""
        return self.exceptAll(other)

    def withColumnRenamed(self, existing: str, new: str) -> "DataFrame":
        """
        Rename a column in the DataFrame.

        Returns a new DataFrame with one column renamed. All other columns
        remain unchanged.

        Parameters
        ----------
        existing : str
            The current name of the column to rename
        new : str
            The new name for the column

        Returns
        -------
        DataFrame
            A new DataFrame with the column renamed

        Examples
        --------
        >>> # Rename a single column
        >>> df = df.withColumnRenamed("old_name", "new_name")

        >>> # Chain multiple renames
        >>> df = df.withColumnRenamed("col1", "column_one") \\
        ...        .withColumnRenamed("col2", "column_two")

        >>> # Make column name more descriptive
        >>> df = df.withColumnRenamed("age", "user_age")

        Notes
        -----
        - Raises an error if the existing column doesn't exist
        - Raises an error if the new name already exists
        - Use select() to rename multiple columns at once
        """
        rust_df = self._rust_df.withColumnRenamed(existing, new)
        return DataFrame(rust_df, session=self._session)

    def with_column_renamed(self, existing: str, new: str) -> "DataFrame":
        """Snake_case alias for withColumnRenamed()."""
        return self.withColumnRenamed(existing, new)

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

    def createOrReplaceTempView(self, name: str):
        """
        Register this DataFrame as a temporary view.

        The view is session-scoped and can be referenced in SQL queries.

        Parameters
        ----------
        name : str
            Name of the temporary view

        Examples
        --------
        >>> df = spark.read.csv("users.csv")
        >>> df.createOrReplaceTempView("users")
        >>> result = spark.sql("SELECT * FROM users WHERE age > 18")

        Notes
        -----
        Requires a session reference. If the DataFrame was created without
        a session reference, this method will raise an error.
        """
        if self._session is None:
            raise RuntimeError(
                "Cannot create temp view: DataFrame has no session reference. "
                "This can happen if the DataFrame was created directly instead of "
                "through SparkSession methods."
            )
        self._session.register_temp_view(self, name)

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

    def __init__(self, rust_grouped, session=None):
        self._rust_grouped = rust_grouped
        self._session = session

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
        return DataFrame(rust_df, session=self._session)

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
        return DataFrame(rust_df, session=self._session)

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
