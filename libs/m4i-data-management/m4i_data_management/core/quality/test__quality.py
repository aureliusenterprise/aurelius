import pytest
from pandas import DataFrame

from .quality import Quality


def get_data():
    return DataFrame([
        {
            "id": 1,
            "abc": "def",
            "ghi": "jkl"
        }
    ]).set_index("id")
# END get_data


def get_rules():
    return DataFrame([
        {
            "id": 1,
            "data_field_qualified_name": "a",
            "data_quality_rule_description": "description",
            "data_quality_rule_dimension": "dimension",
            "expression_version": "1",
            "expression": "completeness('abc')",
            "active": 1
        }
    ])
# END get_rules


def get_metadata():
    return DataFrame([
        {
            "data_field_qualified_name": "a",
            "data_field_name": "a",
            "data_attribute_qualified_name": "b",
            "data_attribute_name": "b",
            "data_entity_qualified_name": "c",
            "data_entity_name": "c",
            "data_domain_qualified_name": "d",
            "data_domain_name": "d"
        }
    ]).set_index("data_field_qualified_name")
# END get_metadata


def propagate(data: DataFrame, compliant: DataFrame, non_compliant: DataFrame):
    pass
# END _propagate


@pytest.fixture
def quality():
    return Quality(
        get_data=get_data,
        get_rules=get_rules,
        get_metadata=get_metadata,
        propagate=propagate
    )
# END quality
