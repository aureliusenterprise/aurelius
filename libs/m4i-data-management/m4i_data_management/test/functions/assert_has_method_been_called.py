class assert_has_method_been_called():
    """
    Asserts whether or not the method with the given `method_name` has been called on the given `obj`.
    """

    method_called = False

    def __init__(self, obj, method_name):
        self.obj = obj
        self.method_name = method_name
    # END __init__

    def called(self, *args, **kwargs):
        self.method_called = True
        return self.orig_method(*args, **kwargs)
    # END called

    def __enter__(self):
        self.orig_method = getattr(self.obj, self.method_name)
        setattr(self.obj, self.method_name, self.called)
        self.method_called = False
    # END __enter__

    def __exit__(self, exc_type, exc_value, traceback):
        has_been_modified = getattr(self.obj, self.method_name) != self.called
        assert not has_been_modified, f"method {self.method_name} was modified during assert_has_method_been_called"

        setattr(self.obj, self.method_name, self.orig_method)

        # If an exception was thrown within the block, we've already failed.
        if traceback is None:
            assert self.method_called, f"method {self.method_name} of {self.obj} was not called"
        # END IF
    # END __exit__
# END assert_has_method_been_called
