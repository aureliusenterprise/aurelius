from pandas import DataFrame, Series, isna


def completeness(data: DataFrame, column_name: str) -> Series:
    """
    Checks whether the values in the column with the given `column_name` are None or NaN. 
    
    If there is no value, assigns a score of 0. 
    If there is a value, assigns a score of 1.
    If the column does not exist, assigns a score of 0 to all rows.
    """

    def check(value):
        return 0 if isna(value) else 1

    if column_name not in data.columns:
        return Series([0] * len(data), index=data.index)

    return data[column_name].apply(check)
