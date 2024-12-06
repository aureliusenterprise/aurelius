from typing import List

from m4i_atlas_core import BusinessReferenceable
from m4i_data_management.core.quality.utils import run_quality_rule_expression
from pandas import DataFrame



from m4i_governance_data_quality.rules import GovQualityRuleDefinition


def calculate_gov_quality(*entities: BusinessReferenceable, rules: List[GovQualityRuleDefinition]) -> DataFrame:
    """
    Calculates data governance quality for the given set of `entities` and `rules`.

    :param entities: One or more entities for which to check the data governance quality.
    :type entities: BusinessReferenceable

    :param rules: The data governance quality rules to apply to the given `entities`.
    :type rules: List[GovQualityRuleDefinition]

    :return:
        A pandas `DataFrame` of the data governance quality results for every entity per given rule.
        The rows correspond to the given `rules`, while the columns correspond to the given `entities`.
        A value of `1` indicates compliance, while a value of `0` indicates non-compliance.
    :rtype: DataFrame
    """

    index = [entity.guid for entity in entities]

    data = {
        "attribute": DataFrame((entity.attributes for entity in entities), index=index),
        "relationship": DataFrame((entity.relationship_attributes for entity in entities), index=index)
    }

    results = DataFrame(
        run_quality_rule_expression(data[rule.type], rule.expression)
        for rule in rules
    )

    return results
# END calculate_gov_quality
