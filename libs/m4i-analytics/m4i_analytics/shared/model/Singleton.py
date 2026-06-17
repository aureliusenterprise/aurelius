class Singleton:
    """
    Classes inheriting from Singleton can only be instantiated once.
    Subsequent instantiations will return the original instance.
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    # END __new__


# END Singleton
