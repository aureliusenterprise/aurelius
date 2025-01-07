from pandas import DataFrame, Series, isna


def length(data: DataFrame, column_name: str, required_length: int) -> Series:
    """
    Checks if the number of characters of the values in the column with the given `column_name` are equal to the `required_length`.

    This function only works for array-like values such as strings or lists.

    If the length of a value is equal or greater than the `required_length`, assigns a score of 1.
    Otherwise, or if the value is empty, assigns a score of 0.
    """

    def check(value):

        if not isinstance(value, list) and isna(value):
            return 0
        # END IF

        has_required_length = (
            required_length <= len(value)
        )

        return 1 if has_required_length else 0
    # END check

    return data[column_name].apply(check)
# END length
