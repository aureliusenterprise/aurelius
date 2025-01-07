from typing import Iterable

from pandas import DataFrame, Series

from ..unallowed_text import unallowed_text

def conditional_unallowed_text(data: DataFrame, key_column: str, value_column: str, values: Iterable[str], text: str) -> Series:
    """
    Checks if values in the column with the given `value_column` contain a specific unallowed `text`. 

    Before applying the metric, filter out all rows where the value in the given `key_column` is not a substring of the given `values`.

    This metric is derived from the `unallowed_text` metric.

    If there is no unallowed value, assign a score of 1.
    Otherwise, assign a score of 0.
    """

    # Values can also be substrings of the values in the rows to check
    def filter(key: str):
        return any(value in key for value in values)
    # END FILTER

    row_matches_values = data[key_column].apply(filter)
    rows_to_check = data[row_matches_values]

    if len(rows_to_check) == 0:
        return Series()
    # END IF

    return unallowed_text(rows_to_check, value_column, text)
# END conditional_unallowed_text
