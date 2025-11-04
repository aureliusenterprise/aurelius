from pandas import DataFrame, Series

from ..get_quality_functions import get_quality_functions
from ..validate_function_string import validate_function_string


def run_quality_rule_expression(data: DataFrame, rule_expression: str) -> Series:
    """
    Runs the given quality `rule_expression` on the given `data`.
    Returns a Pandas `Series` containing the quality score per row (between 0 and 1).
    """
    if '|' in rule_expression:
        # Split the expression by logical OR operator
        # Evaluate each part separately and combine the results
        return DataFrame([
            run_quality_rule_expression(data, expression.strip())
            for expression in rule_expression.split(' | ')
        ]).any(axis=0)

    # Index all available quality functions
    quality_functions = get_quality_functions()

    # Validate the function string
    validate_function_string(rule_expression, quality_functions)

    # Find the index at which the function arguments start
    args_start = rule_expression.index('(') + 1

    # Adds `data` as the first argument of the function string
    # The resulting string looks like `function_name(data, args)`
    function_string = f"{rule_expression[:args_start]}data, {rule_expression[args_start:]}"

    # Run the function.
    # Reduce security risks by restricting the global execution context.
    # Make the data variable and quality functions available in the local execution context.
    return eval(
        function_string,
        {"__builtins__": {}},
        {"data": data, **quality_functions}
    )

# END run_quality_rule_expression
