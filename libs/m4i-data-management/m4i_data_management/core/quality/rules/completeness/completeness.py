from pandas import DataFrame, Series, isna


def completeness(data: DataFrame, column_name: str) -> Series:
    """
    Checks whether the values in the column with the given `column_name` are None or NaN. 
    
    If there is no value, assigns a score of 0. 
    If there is a value, assigns a score of 1.
    """

    def check(value):
        return 0 if isna(value) else 1
    # END check

    return data[column_name].apply(check)
# END completeness
