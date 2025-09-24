from pandas import DataFrame, Series, isna


def starts_with(data: DataFrame, column_name: str, *prefixes: str) -> Series:
    """
    Checks whether or not the values in the column with the given `column_name` start with any of the given `prefixes`.

    This only works for textual values.
    If a value is not a string, it is converted to a string before comparison.

    If the value starts with any of the given `prefixes`, or if the value is empty, assign a score of 1.
    Otherwise, assign a score of 0.
    """

    def check(value):

        if isna(value):
            return 1

        str_value = str(value)

        return 1 if str_value.startswith(prefixes) else 0
    
    if column_name not in data.columns:
        return Series([0] * len(data), index=data.index)

    return data[column_name].apply(check)
