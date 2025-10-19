from pandas import DataFrame, Series


def logical_or(left_series: Series, right_series: Series) -> Series:
    """
    Returns a Series with logical OR operation between two Series.
    If either value is 1 (True), the result is 1, otherwise 0.
    """
    # Handle different series lengths by aligning indices
    result = left_series.copy()
    
    for idx in result.index:
        left_val = left_series.get(idx, 0)
        right_val = right_series.get(idx, 0) if idx in right_series.index else 0
        result[idx] = 1 if (left_val == 1 or right_val == 1) else 0
    
    return result