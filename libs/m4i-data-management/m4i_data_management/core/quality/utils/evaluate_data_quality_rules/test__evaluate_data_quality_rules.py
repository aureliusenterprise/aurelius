from datetime import datetime

import pytest
from pandas import DataFrame

from .evaluate_data_quality_rules import evaluate_data_quality_rules


@pytest.fixture
def data():
    return DataFrame([
        {
            "id": 1,
            "abc": "def",
            "ghi": "jkl"
        }
    ]).set_index("id")
# END data


@pytest.fixture
def rules():
    return DataFrame([
        {
            "id": 1,
            "data_field_qualified_name": "a",
            "data_quality_rule_description": "description",
            "data_quality_rule_dimension": "dimension",
            "expression_version": "1",
            "expression": "completeness('abc')",
            "active": 1
        },
        {
            "id": 2,
            "data_field_qualified_name": "a",
            "data_quality_rule_description": "description",
            "data_quality_rule_dimension": "dimension",
            "expression_version": "1",
            "expression": "completeness('abc')",
            "active": 0
        }
    ])
# END rules


def test__evaluate_data_quality_rules_skips_inactive(data: DataFrame, rules: DataFrame):
    results, _, _ = evaluate_data_quality_rules(data, rules)

    assert len(results.index) == 1
# END test__evaluate_data_quality_rules_skips_inactive


def test__evaluate_data_quality_rules_must_annotate_results_with_metadata(data: DataFrame, rules: DataFrame):
    results, compliant, non_compliant = evaluate_data_quality_rules(
        data=data,
        rules=rules
    )

    metadata_columns = {"run_id", "run_date"}

    assert (
        metadata_columns.issubset(results)
        and metadata_columns.issubset(compliant)
        and metadata_columns.issubset(non_compliant)
    )
# END test__evaluate_data_quality_rules_must_annotate_results_with_metadata


def test__evaluate_data_quality_rules_run_date_must_be_iso_format(data: DataFrame, rules: DataFrame):
    result, _, _ = evaluate_data_quality_rules(data, rules)

    # Try to convert the time strings. If the dates are not in iso format, this will raise an exception.
    result['run_date'].apply(datetime.fromisoformat)
# END test__evaluate_data_quality_rules_run_date_must_be_iso_format
