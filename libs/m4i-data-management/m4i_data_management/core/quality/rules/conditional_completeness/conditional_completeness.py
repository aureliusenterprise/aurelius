from typing import Iterable

from pandas import DataFrame, Series

from ..completeness import completeness


def conditional_completeness(data: DataFrame, key_column: str, value_column: str, values: Iterable[str]) -> Series:
    """
    Checks whether or not the values in the given `value_column` are `None` or `NaN`.

    Before applying the metric, filter out all rows where the value in the given `key_column` is not a substring of the given `values`.

    This metric is derived from the `completeness` metric.

    If there is a value, assign a score of 1.
    Otherwise, assign a score of 0.
    """

    def filter(key: str):
        return any(value in key for value in values)
    # END FILTER

    # Values can also be substrings of the values in the rows to check
    row_matches_values = data[key_column].apply(filter)
    rows_to_check = data[row_matches_values]

    if len(rows_to_check) == 0:
        return Series()
    # END IF

    return completeness(rows_to_check, value_column)
# END conditional_completeness
