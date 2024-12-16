import pytest
from pandas import DataFrame

from .annotate_results_with_metdata import annotate_results_with_metadata


@pytest.fixture
def rules():
    return DataFrame([
        {
            "id": 1,
            "data_field_qualified_name": "a",
            "expression_version": "1",
            "expression": "completeness('abc')",
            "active": 1
        }
    ])
# END get_rules


@pytest.fixture
def metadata():
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


def test__annotate_results_with_metadata_with_correct_input(rules: DataFrame, metadata: DataFrame):
    annotated = annotate_results_with_metadata(rules, metadata)

    assert "data_field_qualified_name" in annotated and "data_field_name" in annotated
# END test__annotate_results_with_metadata_with_correct_input
