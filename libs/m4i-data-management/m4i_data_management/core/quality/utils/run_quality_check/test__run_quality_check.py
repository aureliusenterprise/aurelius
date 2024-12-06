from datetime import datetime

import pytest
from numpy import NaN
from pandas import DataFrame
from pandas.core.series import Series

from .run_quality_check import run_quality_check


@pytest.fixture
def data():
    return DataFrame([
        {"id": 1, "abc": "def", "ghi": "jkl"},
        {"id": 2, "abc": NaN, "ghi": "mno"},
        {"id": 3, "abc": "pqr", "ghi": "stu"}
    ]).set_index("id")
# END data


@pytest.fixture
def rule_a():
    return Series({
        "id": 1,
        "data_field_qualified_name": "a",
        "data_quality_rule_description": "description",
        "data_quality_rule_dimension": "dimension",
        "expression_version": 1,
        "expression": "completeness('abc')"
    })
# END rule_a


@pytest.fixture
def rule_b():
    return Series({
        "id": 1,
        "data_field_qualified_name": "a",
        "data_quality_rule_description": "description",
        "data_quality_rule_dimension": "dimension",
        "expression_version": 1,
        "expression": "this_is_a_faulty_expression()"
    })
# END rule_b


def test__run_quality_check_must_have_unique_result_id(data: DataFrame, rule_a: Series):
    result_a, _, _ = run_quality_check(data, rule_a)
    result_b, _, _ = run_quality_check(data, rule_a)

    assert 'result_id' in result_a and result_a['result_id'] != result_b['result_id']
# END test__run_quality_check_must_have_unique_result_id


def test__run_quality_check_finished_must_have_success_status(data: DataFrame, rule_a: Series):
    result, _, _ = run_quality_check(data, rule_a)

    assert result['status'] == 'success'
# END test__run_quality_check_finished_must_have_success_status


def test__run_quality_check_unfinished_must_have_no_success_status(data: DataFrame, rule_b: Series):
    result, _, _ = run_quality_check(data, rule_b)

    assert result['status'] == 'no_success'
# END test__run_quality_check_unfinished_must_have_no_success_status


def test__run_quality_check_must_have_rule_id(data: DataFrame, rule_a: Series):
    result, _, _ = run_quality_check(data, rule_a)

    assert result['business_rule_id'] == rule_a['id']
# END test__run_quality_check_must_have_rule_id


def test__run_quality_check_must_have_expression_version(data: DataFrame, rule_a: Series):
    result, _, _ = run_quality_check(data, rule_a)

    assert result['expression_version'] == rule_a['expression_version']
# END test__run_quality_check_must_have_expression_version


def test__run_quality_check_must_have_expression(data: DataFrame, rule_a: Series):
    result, _, _ = run_quality_check(data, rule_a)

    assert result['expression'] == rule_a['expression']
# END test__run_quality_check_must_have_expression


def test__run_quality_check_test_date_must_be_iso_format(data: DataFrame, rule_a: Series):
    result, _, _ = run_quality_check(data, rule_a)

    # Try to convert the time string. If the date is not in iso format, this will raise an exception.
    datetime.fromisoformat(result['test_date'])
# END test__run_quality_check_test_date_must_be_iso_format


def test__run_quality_check_must_have_dq_score(data: DataFrame, rule_a: Series):
    result, _, _ = run_quality_check(data, rule_a)

    assert isinstance(result['dq_score'], float)
# END test__run_quality_check_must_have_dq_score


def test__run_quality_check_detailed_results_must_be_dataframe(data: DataFrame, rule_a: Series):
    _, compliant, non_compliant = run_quality_check(data, rule_a)

    assert (
        isinstance(compliant, DataFrame)
        and isinstance(non_compliant, DataFrame)
    )
# END test__run_quality_check_detailed_results_must_be_dataframe


def test__run_quality_check_must_annotate_results_with_metadata(data: DataFrame, rule_a: Series):
    result, compliant, non_compliant = run_quality_check(data, rule_a)

    metadata_columns = {
        "business_rule_id",
        "data_field_qualified_name",
        "data_quality_rule_description",
        "data_quality_rule_dimension",
        "result_id",
        "test_date"
    }

    assert (
        metadata_columns.issubset(result)
        and metadata_columns.issubset(compliant)
        and metadata_columns.issubset(non_compliant)

    )
# END test__run_quality_check_must_annotate_results_with_metadata
