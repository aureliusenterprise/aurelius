from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..term_relationship_status import TermRelationshipStatus


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TermCategorizationHeaderBase(DataClassJsonMixin):

    category_guid: str
    relationship_guid: str

# END TermCategorizationHeaderBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TermCategorizationHeaderDefaultsBase(DataClassJsonMixin):

    description: Optional[str] = None
    display_text: Optional[str] = None
    status: Optional[TermRelationshipStatus] = None

# END TermCategorizationHeaderDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TermCategorizationHeader(TermCategorizationHeaderDefaultsBase, TermCategorizationHeaderBase):

    pass

# END TermCategorizationHeader
