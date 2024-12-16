from pandas import Series


def calculate_quality_score(scores_per_row: Series) -> float:
    """
    Given the data quality `scores_per_row`, calculates the overall data quality score.
    """
    return scores_per_row.mean()
# END calculate_quality_score
