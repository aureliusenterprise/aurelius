from typing import Iterable, Mapping, Union
from pandas import DataFrame, Series, isna


def conditional_value(
    data: DataFrame,
    key_column: str,
    value_column: str,
    value_mapping: Mapping[str, Union[str, Iterable[str]]]
) -> Series:
    """
    Checks whether the values in the given `value_column` match (one of) the expected value(s) for a given key in the `key_column`. 

    If the `value_column` contains an expected value, assign a score of 1.
    Otherwise, assign a score of 0.
    """

    def check(row):

        key = row[key_column]

        if isna(key):
            return 0
        # END IF

        expected_value = value_mapping[key]

        if isinstance(expected_value, (list, set)):
            has_valid_value = row[value_column] in expected_value
        else:
            has_valid_value = row[value_column] == expected_value
        # END IF

        return 1 if has_valid_value else 0
    # END check

    # Limit the sample to rows containing a value we want to check for
    rows_to_check = data[data[key_column].isin(value_mapping)]

    if len(rows_to_check) == 0:
        return Series()
    # END IF

    return rows_to_check[[value_column, key_column]].apply(check, axis=1)
# END conditional_value
