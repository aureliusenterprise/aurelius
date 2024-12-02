from typing import TypeVar

T = TypeVar('T')


def identity(arg: T) -> T:
    """
    Takes a single argument and returns it unchanged.
    """
    return arg
# END identity
