from pandas import DataFrame, Series, isna


def range(data: DataFrame, column_name: str, lower_bound: int = 0, upper_bound: int = 1) -> Series:
    """
    Checks whether or not the values in the column with the given `column_name` are:

    - Greater than or equal to the given `lower_bound`.
    - Less than or equal to the given `upper_bound`.

    This only works for numeric values.
    If a value is not a number, it is converted to a number before comparison.

    If the value is within the given `lower_bound` and `upper_bound`, assign a score of 1.
    Otherwise, assign a score of 0.
    """

    def check(value):
        is_in_range = (
            not isna(value)
            and int(value) >= lower_bound
            and int(value) <= upper_bound
        )

        return 1 if is_in_range else 0
    # END check

    return data[column_name].apply(check)
# END range
