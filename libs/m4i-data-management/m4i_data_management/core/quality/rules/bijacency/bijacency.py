from pandas import DataFrame, Series

from .....core.utils import BidirectionalMutliMap


def bijacency(data: DataFrame, column_a: str, column_b: str) -> Series:
    """
    Checks whether or not the values in the given `column_a` and `column_b` only occur as a unique combination.

    This only works for textual values.
    If a value is not a string, it is converted to a string before comparison.

    If the values occur as a unique combination, assign a score of 1.
    Otherwise, assign a score of 0.
    """

    def get_values(row: Series):
        return str(row[column_a]), str(row[column_b])
    # END get_values

    combinations = BidirectionalMutliMap()

    for _, row in data.iterrows():
        a, b = get_values(row)
        combinations.add(a, b)
    # END LOOP

    def check(row: Series):
        a, b = get_values(row)

        unique = len(combinations[a]) <= 1
        inverse_unique = len(combinations.inverse[b]) <= 1

        return 1 if unique and inverse_unique else 0
    # END check

    return data[[column_a, column_b]].apply(check, axis='columns')
# END bijacency
