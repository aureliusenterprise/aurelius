from collections import defaultdict

from pandas import DataFrame, Series, isna


def uniqueness(data: DataFrame, column_name: str) -> Series:
    """
    Checks whether the values in the column with the given `column_name` are unique (duplicate value check). 

    This only works for textual values.
    If a value is not a string, it is converted to a string before comparison.

    If a value is unique, or if the value is empty, assigns a score of 1. 
    Otherwise, assigns a score of 0.
    """

    if column_name not in data.columns:
        return Series([0] * len(data), index=data.index)

    records_per_value = defaultdict(set)

    for index, row in data.iterrows():
        value = row[column_name]

        if isna(value):
            continue

        records_per_value[str(value)].add(str(index))

    def check(value):
        if isna(value):
            return 1

        occurrences = records_per_value[str(value)]

        return 1 if len(occurrences) == 1 else 0
    


    return data[column_name].apply(check)
