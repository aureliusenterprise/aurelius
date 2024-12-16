import json
from os import path
from pathlib import Path
from typing import List

from ..model import GovQualityRuleDefinition

DEFINITIONS_PATH = Path(__file__).parent.parent.joinpath("definitions")


def get_rules_for_type(type_name: str) -> List[GovQualityRuleDefinition]:
    """
    Returns all governance quality rules applicable for the given `type_name`.
    The `type_name` corresponds to the type of the entity for which you want to run a check.

    Retrieves the rules from the definition file corresponding to the given `type_name`.

    :param type_name: The name of the entity type for which to retrieve the governance quality rules.
    :type type_name: str

    :return: A list of all governance quality rules applicable for the given `type_name`.
    :rtype: List[GovQualityRuleDefinition]
    """

    rules_path = path.join(DEFINITIONS_PATH, f"{type_name}.json")

    with open(rules_path) as file:
        rules_json = json.load(file)
    # END WITH file

    return GovQualityRuleDefinition.schema().load(rules_json, many=True)
# END get_rules_for_type
