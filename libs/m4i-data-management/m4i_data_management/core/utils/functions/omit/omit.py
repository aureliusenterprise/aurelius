def omit(source: dict, *keys: str) -> dict:
    """
    Returns a new `dict` that is a copy of `source` but excludes the given `keys`.
    """
    return {
        key: source[key]
        for key in source
        if key not in keys
    }
# END omit
