from typing import Any, Iterable

from pandas import DataFrame, Series

from ..validity import validity


def invalidity(data: DataFrame, column_name: str, values: Iterable[Any]) -> Series:
    """
    Checks whether or not the values in the column with the given `column_name` does not exist in the given list of `values`.

    This metric is the inverse of the `validity` metric.

    If the value does not exist in the given list of `values`, assign a score of 1.
    Otherwise, assign a score of 0.
    """

    return 1 - validity(data, column_name, values)
# END invalidity
