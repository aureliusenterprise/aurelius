from inspect import getmembers, isfunction

from ... import rules


def get_quality_functions() -> dict:
    """
    Returns the quality rules from the `rules` package as a dictionary of name and function.
    """
    return {key: value for key, value in getmembers(rules, isfunction)}
# END get_valid_function_names
