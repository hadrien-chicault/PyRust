"""
Column implementation - Placeholder for future column expressions.
"""


class Column:
    """
    A column in a DataFrame.

    Note: This is a placeholder for the POC. Full column expression support
    will be added in future versions.

    Examples
    --------
    >>> from pyrust import Column
    >>> col("age") > 18  # Future functionality
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Column<'{self.name}'>"

    # Placeholder methods for future implementation
    def __gt__(self, other):
        raise NotImplementedError("Column expressions not yet supported in POC")

    def __lt__(self, other):
        raise NotImplementedError("Column expressions not yet supported in POC")

    def __eq__(self, other):
        raise NotImplementedError("Column expressions not yet supported in POC")


def col(name: str) -> Column:
    """
    Create a Column reference.

    Parameters
    ----------
    name : str
        Column name

    Returns
    -------
    Column
        A Column object

    Note: This is a placeholder for the POC.
    """
    return Column(name)
