from collections import defaultdict
from typing import Generic, Mapping, Set, TypeVar

T = TypeVar('T')


class MultiMap(Generic[T], defaultdict):

    def __init__(self):
        super(MultiMap, self).__init__(set)
    # END __init__()

    def add(self, key: str, *values: T):
        self[key].update(values)
    # END add

    def delete(self, key: str):
        self[key].clear()
    # END delete

    def remove(self, key: str, value: T):
        self[key].discard(value)
    # END remove
# END MultiMap
