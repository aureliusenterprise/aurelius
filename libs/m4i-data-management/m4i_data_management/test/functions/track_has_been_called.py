from typing import Callable


class track_has_been_called():
    """
    Wraps a function and keeps track of whether or not the function has been called.
    """

    func: Callable
    has_been_called: bool = False

    def __init__(self, func: Callable):
        self.func = func
    # END __init__

    def __call__(self, *args, **kwargs):
        self.has_been_called = True
        return self.func(*args, **kwargs)
    # END __call__
# END track_has_been_called
