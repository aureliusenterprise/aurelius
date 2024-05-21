from enum import Enum


class TermAssignmentStatus(Enum):
    DISCOVERED="DISCOVERED"
    PROPOSED="PROPOSED"
    IMPORTED="IMPORTED"
    VALIDATED="VALIDATED"
    DEPRECATED="DEPRECATED"
    OBSOLETE="OBSOLETE"
    OTHER="OTHER"
# END TermAssignmentStatus
