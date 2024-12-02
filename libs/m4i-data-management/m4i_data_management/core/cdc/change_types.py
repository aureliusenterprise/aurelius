from enum import Enum


class CDCChangeType(Enum):
    """
    All change type annotations that are applied by the CDC dataset comparison function.
    """
    ADDED = "added"
    CHANGED = "changed"
    REMOVED = "removed"
# END ChangeType
