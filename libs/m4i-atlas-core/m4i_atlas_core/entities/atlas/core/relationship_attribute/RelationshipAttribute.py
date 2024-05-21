from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import (DataClassJsonMixin, LetterCase,
                              dataclass_json)

from ..attributes import Attributes
from ..status import Status
from ..utils import create_placehoder_guid


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipAttributeBase(DataClassJsonMixin):
    pass
# END RelationshipAttributeBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipAttributeDefaultsBase(DataClassJsonMixin):
    display_text: Optional[str] = None
    entity_status: Optional[Status] = None
    guid: str = field(default_factory=create_placehoder_guid)
    relationship_attributes: Optional[Attributes] = None
    relationship_guid: str = field(default_factory=create_placehoder_guid)
    relationship_status: Optional[Status] = None
    relationship_type: Optional[str] = None
    type_name: Optional[str] = None
# END RelationshipAttributeDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipAttribute(
    RelationshipAttributeDefaultsBase,
    RelationshipAttributeBase
):
    pass
# END RelationshipAttribute
