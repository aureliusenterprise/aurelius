from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from dataclasses_json import (DataClassJsonMixin, LetterCase, config,
                              dataclass_json)

from ..entity import Entity
from ..relationship import Relationship
from ..entity_audit_event import EntityAuditAction

class EntityNotificationType(Enum):
    ENTITY_NOTIFICATION_V1 = "ENTITY_NOTIFICATION_V1"
    ENTITY_NOTIFICATION_V2 = "ENTITY_NOTIFICATION_V2"
# END EntityNotificationType

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AtlasChangeMessageVersion(DataClassJsonMixin):

    version: str
    version_parts: List[int]    
    
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AtlasChangeMessageBody(DataClassJsonMixin):
    event_time: int
    operation_type: EntityAuditAction
    type: EntityNotificationType
    entity: Optional[Entity] = None
    relationship: Optional[Relationship] = None 

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AtlasChangeMessage(DataClassJsonMixin):

    version: AtlasChangeMessageVersion
    msg_compression_kind: str
    msg_split_idx: int
    msg_split_count: int
    msg_source_ip: str=field(metadata=config(field_name="msgSourceIP"))
    msg_created_by: str
    msg_creation_time: int
    message: AtlasChangeMessageBody
    spooled: bool
