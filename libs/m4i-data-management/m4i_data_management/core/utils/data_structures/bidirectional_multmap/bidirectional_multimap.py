from collections import defaultdict


class BidirectionalMutliMap(defaultdict):
    """
    A data structure that maintains a set of values per key.
    It also maintains an `inverse` mapping with sets of keys per value.
    """

    inverse: defaultdict

    def __init__(self):
        super().__init__(set)
        self.inverse = defaultdict(set)
    # END __init__

    def add(self, key: str, *values: str):
        for value in values:
            self[key].add(value)
            self.inverse[value].add(key)
        # END LOOP
        return self
    # END add

# END BidirectionalMultiMap
