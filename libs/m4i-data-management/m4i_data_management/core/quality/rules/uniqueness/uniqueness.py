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

    records_per_value = defaultdict(set)

    for index, row in data.iterrows():
        value = row[column_name]

        if isna(value):
            continue
        # END IF

        records_per_value[str(value)].add(str(index))
    # END LOOP

    def check(value):
        if isna(value):
            return 1
        # END IF

        occurrences = records_per_value[str(value)]

        return 1 if len(occurrences) == 1 else 0
    # END check

    return data[column_name].apply(check)
# END uniqueness
