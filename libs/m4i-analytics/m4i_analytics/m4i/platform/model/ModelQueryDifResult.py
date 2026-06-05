from enum import Enum

from m4i_analytics.m4i.platform.model.ModelQueryDifResultConflictList import (
    ModelQueryDifResultConflictList,
)
from m4i_analytics.shared.model.BaseModel import BaseModel


class StateEnum(Enum):
    COMMITTED = "COMMITTED"
    FAILURE = "FAILURE"
    CONFLICT = "CONFLICT"
    LOCKED = "LOCKED"
    UNDEFINED = "UNDEFINED"


# END StateEnum


class ModelQueryDifResult(BaseModel):
    _fields = [
        ("state", str, False),
        ("timestamp", int, False),
        ("conflictList", ModelQueryDifResultConflictList, True),
        ("addListLeft", str, True),
        ("deleteListLeft", str, True),
        ("addListRight", str, True),
        ("deleteListRight", str, True),
    ]


# END ModelQueryDifResult
