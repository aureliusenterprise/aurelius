from enum import Enum

from m4i_analytics.shared.model.BaseModel import BaseModel


class ChangeEnum(Enum):
    UNCHANGED = "unchanged"
    ADDED = "added"
    DELETED = "deleted"
    MODIFIED = "modified"


# EMD ChangeEnum


class TypeEnum(Enum):
    NODES = "nodes"
    RELATIONS = "relations"
    VIEWS = "views"


# END TypeEnum


class ModelQueryDifResultConflictList(BaseModel):
    _fields = [
        ("left", str, False),
        ("leftChange", str, False),
        ("right", str, False),
        ("rightChange", str, False),
        ("type", str, False),
    ]


# END ModelQueryDifResultConflictList
