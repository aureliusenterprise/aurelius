import re

from pandas import DataFrame, Series, isna


def formatting(data: DataFrame, column_name: str, pattern: str) -> Series:
    """
    Checks whether or not the values in the column with the given `column_name` match the given `pattern`.

    This only works for textual values.
    If a value is not a string, it is converted to a string before comparison.

    If the value matches the given `pattern`, or if the value is empty, assign a score of 1.
    Otherwise, assign a score of 0.
    """

    regex = re.compile(pattern)

    def check(value):

        if isna(value):
            return 0
        # END IF

        return 1 if regex.match(str(value)) else 0
    # END check

    return data[column_name].apply(check)
# END formatting
