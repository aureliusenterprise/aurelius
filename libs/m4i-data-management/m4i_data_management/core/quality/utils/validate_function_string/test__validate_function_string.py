import pytest

from ..get_quality_functions import get_quality_functions
from .validate_function_string import validate_function_string


@pytest.fixture
def quality_functions() -> dict:
    return get_quality_functions()
# END quality_functions


def test__validate_function_string_with_valid_function_string(quality_functions: dict):
    expression = "completeness('abc')"

    validate_function_string(expression, quality_functions)
# END test__validate_function_string_with_valid_function_string


def test__validate_function_string_with_typo_in_function_string(quality_functions: dict):
    expression = "completenes('abc')"

    with pytest.raises(NameError):
        validate_function_string(expression, quality_functions)
    # END WITH
# END test__validate_function_string_with_typo_in_function_string


def test__validate_function_string_with_arbitrary_code(quality_functions: dict):
    expression = "print('abc')"

    with pytest.raises(NameError):
        validate_function_string(expression, quality_functions)
    # END WITH
# END test__validate_function_string_with_arbitrary_code


def test__validate_function_string_with_undefined_variable(quality_functions: dict):
    expression = "completeness(abc)"

    with pytest.raises(NameError):
        validate_function_string(expression, quality_functions)
    # END WITH
# END test__validate_function_string_with_undefined_variable


def test__validate_function_string_with_syntax_error(quality_functions: dict):
    expression = "completeness('abc'"

    with pytest.raises(SyntaxError):
        validate_function_string(expression, quality_functions)
    # END WITH
# END test__validate_function_string_with_syntax_error


def test__validate_function_string_with_empty_expression(quality_functions: dict):
    expression = ""

    with pytest.raises(ValueError):
        validate_function_string(expression, quality_functions)
    # END WITH
# END test__validate_function_string_with_empty_expression


def test__validate_function_string_without_function(quality_functions: dict):
    expression = "'abc'"

    with pytest.raises(NameError):
        validate_function_string(expression, quality_functions)
    # END WITH
# END test__validate_function_string_without_function
