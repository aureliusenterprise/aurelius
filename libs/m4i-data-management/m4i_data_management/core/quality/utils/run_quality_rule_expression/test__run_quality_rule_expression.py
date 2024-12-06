import pytest
from numpy import NaN
from pandas import DataFrame

from .run_quality_rule_expression import run_quality_rule_expression


@pytest.fixture
def data() -> DataFrame:
    return DataFrame([
        {"abc": "def"},
        {"abc": NaN}
    ])
# END data


def test__run_quality_rule_expression_with_valid_function_string(data: DataFrame):
    expression = "completeness('abc')"

    run_quality_rule_expression(data, expression)
# END test__run_quality_rule_expression_with_valid_function_string


def test__run_quality_rule_expression_with_typo_in_function_string(data: DataFrame):
    expression = "completenes('abc')"

    with pytest.raises(NameError):
        run_quality_rule_expression(data, expression)
    # END WITH
# END test__run_quality_rule_expression_with_typo_in_function_string


def test__run_quality_rule_expression_with_arbitrary_code(data: DataFrame):
    expression = "print('abc')"

    with pytest.raises(NameError):
        run_quality_rule_expression(data, expression)
    # END WITH
# END test__run_quality_rule_expression_with_arbitrary_code


def test__run_quality_rule_expression_with_undefined_variable(data: DataFrame):
    expression = "completeness(abc)"

    with pytest.raises(NameError):
        run_quality_rule_expression(data, expression)
    # END WITH
# END test__run_quality_rule_expression_with_undefined_variable


def test__run_quality_rule_expression_with_syntax_error(data: DataFrame):
    expression = "completeness('abc'"

    with pytest.raises(SyntaxError):
        run_quality_rule_expression(data, expression)
    # END WITH
# END test__run_quality_rule_expression_with_syntax_error


def test__run_quality_rule_expression_with_empty_expression(data: DataFrame):
    expression = ""

    with pytest.raises(ValueError):
        run_quality_rule_expression(data, expression)
    # END WITH
# END test__run_quality_rule_expression_with_empty_expression


def test__run_quality_rule_expression_without_function(data: DataFrame):
    expression = "'abc'"

    with pytest.raises(NameError):
        run_quality_rule_expression(data, expression)
    # END WITH
# END test__run_quality_rule_expression_without_function
