class PseudoEnum:
    @classmethod
    def getAll(cls):
        """
        Returns a list of tuples representing all entries for this
        PseudoEnum along the dimensions key x value. This is useful
        when you need to iterate over the enum.

        :returns: A list of all PseudoEnum entries
        :rtype: list of tuple
        """

        return [
            (i, getattr(cls, i)) for i in dir(cls) if not i.startswith("__") and not callable(getattr(cls, i))
        ]

    # END getAll


# END PseudoEnum
