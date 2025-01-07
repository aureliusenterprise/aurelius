def validate_function_string(function_string: str, valid_function_names: dict) -> bool:
    """
    Compiles the given `function_string` to code, but does not run the code.
    Instead, check whether any of the names used in the code are not valid quality functions.
    If any invalid names are found, raise an error.
    This helps improve security when running arbitrary code, and gives feedback to the user.
    """

    if len(function_string) == 0:
        raise ValueError("Quality expression should not be empty")
    # END IF

    code = compile(function_string, "<string>", "eval")

    if len(code.co_names) == 0:
        raise NameError(f"{function_string} is not a quality function")
    # END IF

    for name in code.co_names:
        if name not in valid_function_names:
            raise NameError(f"{name} is not a quality function")
       # END IF
    # END LOOP
# END validate_function_string
