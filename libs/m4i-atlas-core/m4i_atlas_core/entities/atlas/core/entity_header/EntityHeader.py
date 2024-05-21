from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..classification import Classification
from ..status import Status
from ..struct import Struct, StructBase, StructDefaultsBase
from ..term_assignment_header import TermAssignmentHeader


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EntityHeaderBase(StructBase):

    guid: str

# END EntityHeaderBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EntityHeaderDefaultsBase(StructDefaultsBase):

    classification_names: List[str] = field(default_factory=list)
    classifications: List[Classification] = field(default_factory=list)
    display_text: Optional[str] = None
    is_incomplete: Optional[bool] = None
    labels: List[str] = field(default_factory=list)
    meaning_names: List[str] = field(default_factory=list)
    meanings: List[TermAssignmentHeader] = field(default_factory=list)
    status: Optional[Status] = None

# END EntityHeaderDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EntityHeader(Struct, EntityHeaderDefaultsBase, EntityHeaderBase):

    pass

# END EntityHeader
