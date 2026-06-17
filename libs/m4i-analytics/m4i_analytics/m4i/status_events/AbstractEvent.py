from enum import Enum


class EventStatus(Enum):
    CRITICAL = 3
    WARNING = 2
    OK = 1
    UNKNOWN = 0


# END EventStatus


class AbstractEvent:
    pass


# END AbstractEvent
