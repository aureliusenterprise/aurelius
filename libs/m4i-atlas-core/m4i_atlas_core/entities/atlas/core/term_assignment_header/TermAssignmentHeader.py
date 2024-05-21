from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..term_assignment_status import TermAssignmentStatus


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TermAssignmentHeaderBase(DataClassJsonMixin):

    relation_guid: str
    term_guid: str

# END TermAssignmentHeaderBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TermAssignmentHeaderDefaultsBase(DataClassJsonMixin):

    created_by: Optional[str] = None
    confidence: Optional[int] = None
    description: Optional[str] = None
    display_text: Optional[str] = None
    expression: Optional[str] = None
    source: Optional[str] = None
    status: Optional[TermAssignmentStatus] = None
    steward: Optional[str] = None

# END TermAssignmentHeaderDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TermAssignmentHeader(TermAssignmentHeaderDefaultsBase, TermAssignmentHeaderBase):

    pass

# END TermAssignmentHeader
