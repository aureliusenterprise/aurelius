from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..term_relationship_status import TermRelationshipStatus


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelatedTermHeaderBase(DataClassJsonMixin):

    term_guid: str

# END RelatedTermHeaderBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelatedTermHeaderDefaultsBase(DataClassJsonMixin):

    description: Optional[str] = None
    display_text: Optional[str] = None
    expression: Optional[str] = None
    relation_guid: Optional[str] = None
    source: Optional[str] = None
    status: Optional[TermRelationshipStatus] = None
    steward: Optional[str] = None

# END RelatedTermHeaderDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelatedTermHeader(RelatedTermHeaderDefaultsBase, RelatedTermHeaderBase):

    pass

# END RelatedTermHeader
