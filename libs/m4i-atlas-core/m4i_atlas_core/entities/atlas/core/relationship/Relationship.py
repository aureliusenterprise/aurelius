from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..classification import Classification
from ..object_id import ObjectId
from ..propagate_tags import PropagateTags
from ..status import Status
from ..struct import Struct, StructBase, StructDefaultsBase
from ..utils import create_placehoder_guid


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipBase(StructBase):

    end1: ObjectId
    end2: ObjectId

# END RelationshipBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipDefaultsBase(StructDefaultsBase):

    blocked_propagated_classifications: List[Classification] = field(
        default_factory=list
    )
    create_time: Optional[int] = None
    created_by: Optional[str] = None
    guid: str = field(default_factory=create_placehoder_guid)
    home_id: Optional[str] = None
    label: Optional[str] = None
    propagate_tags: PropagateTags = PropagateTags.ONE_TO_TWO
    propagated_classifications: List[Classification] = field(
        default_factory=list
    )
    provenance_type: Optional[int] = None
    status: Optional[Status] = None
    update_time: Optional[int] = None
    updated_by: Optional[str] = None
    version: Optional[int] = None

# END RelationshipDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Relationship(Struct, RelationshipDefaultsBase, RelationshipBase):

    pass

# END Relationship
