from pandas import DataFrame


def find_different_rows(a: DataFrame, b: DataFrame) -> DataFrame:
    difference = a.index.difference(b.index)
    is_not_in_b = a.index.isin(difference)

    result = a[is_not_in_b].copy()  # type: ignore[union-attr]

    return result  # type: ignore[return-value]


# END find_different_rows
