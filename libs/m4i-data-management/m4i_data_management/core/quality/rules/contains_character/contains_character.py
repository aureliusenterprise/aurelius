from pandas import DataFrame, Series, isna


def contains_character(data: DataFrame, column_name: str, substring: str, expected_count: int = 1) -> Series:
    """
    Checks how many times the values in the column with the given `column_name` contain a specific character. 

    This only works for textual values.
    If a value is not a string, it is converted to a string before comparison.

    If the number of occurrences is at least the `expected_count`, or if the value is empty, assign a score of 1.
    Otherwise, assigns a score of 1.
    """

    def check(value):
        if isna(value):
            return 1
        # END IF

        return 1 if str(value).count(substring) >= expected_count else 0
    # END check

    return data[column_name].apply(check)
# END contains_character
