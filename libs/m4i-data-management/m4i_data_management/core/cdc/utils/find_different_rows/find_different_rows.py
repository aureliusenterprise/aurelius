from pandas import DataFrame


def find_different_rows(a: DataFrame, b: DataFrame) -> DataFrame:
    difference = a.index.difference(b.index)
    is_not_in_b = a.index.isin(difference)

    return a[is_not_in_b].copy()
# END find_different_rows
