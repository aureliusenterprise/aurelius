from pandas import DataFrame, merge

join = {
    "how": "left",
    "left_on": "data_field_qualified_name",
    "right_index": True
}


def annotate_results_with_metadata(results: DataFrame, metadata: DataFrame):
    """
    Joins the test results with metadata from the data dictionary
    """

    return merge(left=results, right=metadata, **join)
# END annotate_results_with_metadata
