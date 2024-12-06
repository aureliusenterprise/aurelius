from typing import Any, Iterable

from pandas import DataFrame, Series


def validity(data: DataFrame, column_name: str, values: Iterable[Any]) -> Series:
    """
    Checks whether or not the values in the column with the given `column_name` exist in the given list of `values`.

    If the value exists in the given list of `values`, assign a score of 1.
    Otherwise, assign a score of 0.
    """

    def check(value):
        return 0 if not value in values else 1
    # END check

    return data[column_name].apply(check)
# END validity
