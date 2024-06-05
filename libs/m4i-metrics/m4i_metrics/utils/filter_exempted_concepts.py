from typing import Sequence

from pandas import DataFrame


def filter_exempted_concepts(
    violations: DataFrame,
    id_column: str,
    exempted_ids: Sequence[str] = []
) -> (DataFrame, DataFrame):
    """
    Splits the given violations dataframe into two dataframes. One dataframe contains the actual violations, 
    and the other contains the elements that are exempted based on the given list of exemptions.

    :return: A tuple of dataframes with non-exempted and exempted elements
    :rtype: (pandas.Dataframe, pandas.Dataframe)
    """

    # By default, return an empty dataframe for the exempted elements and all violations as non-exempted
    exempted = DataFrame(columns=violations.columns)
    non_exempted = violations

    # Continue only if the given `id_column` is in the violations dataframe
    # This also handles the case where the value of `id_column` is `None`
    if id_column in violations.columns:

        # Split the `violations` dataframe into exempted and non-exempted elements,
        # based on whether or not the id column value is included in the list of `exempted_ids`
        is_exempted = violations[id_column].isin(exempted_ids)

        exempted = violations[is_exempted]
        non_exempted = violations[~is_exempted]
    # END IF

    return non_exempted, exempted
# END filter_exempted_concepts
