from dataclasses import dataclass
from typing import Optional

from dataclasses_json import LetterCase, dataclass_json

from ..attributes import Attributes
from ..object_id import ObjectId, ObjectIdBase, ObjectIdDefaultsBase
from ..status import Status


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelatedObjectIdBase(ObjectIdBase):

    relationship_guid: str
    relationship_type: str

# END RelatedObjectIdBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelatedObjectIdDefaultsBase(ObjectIdDefaultsBase):

    display_text: Optional[str] = None
    entity_status: Optional[Status] = None
    relationship_attributes: Optional[Attributes] = None
    relationship_status: Optional[Status] = None

# END RelatedObjectIdDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelatedObjectId(ObjectId, RelatedObjectIdDefaultsBase, RelatedObjectIdBase):

    pass

# END RelatedObjectId
