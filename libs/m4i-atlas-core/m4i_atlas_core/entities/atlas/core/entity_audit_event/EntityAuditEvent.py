from dataclasses import dataclass
from enum import Enum
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..entity import Entity


class EntityAuditAction(Enum):
    ENTITY_CREATE = "ENTITY_CREATE"
    ENTITY_UPDATE = "ENTITY_UPDATE"
    ENTITY_DELETE = "ENTITY_DELETE"
    ENTITY_IMPORT_CREATE = "ENTITY_IMPORT_CREATE"
    ENTITY_IMPORT_UPDATE = "ENTITY_IMPORT_UPDATE"
    ENTITY_IMPORT_DELETE = "ENTITY_IMPORT_DELETE"
    CLASSIFICATION_ADD = "CLASSIFICATION_ADD"
    CLASSIFICATION_DELETE = "CLASSIFICATION_DELETE"
    CLASSIFICATION_UPDATE = "CLASSIFICATION_UPDATE"
    PROPAGATED_CLASSIFICATION_ADD = "PROPAGATED_CLASSIFICATION_ADD"
    PROPAGATED_CLASSIFICATION_DELETE = "PROPAGATED_CLASSIFICATION_DELETE"
    PROPAGATED_CLASSIFICATION_UPDATE = "PROPAGATED_CLASSIFICATON_UPDATE"
    TERM_ADD = "TERM_ADD"
    TERM_DELETE = "TERM_DELETE"
    LABEL_ADD = "LABEL_ADD"
    LABEL_DELETE = "LABEL_DELETE"
    ENTITY_PURGE = "ENTITY_PURGE"
    BUSINESS_ATTRIBUTE_UPDATE = "BUSINESS_ATTRIBUTE_UPDATE"

    RELATIONSHIP_CREATE = "RELATIONSHIP_CREATE"
    RELATIONSHIP_UPDATE = "RELATIONSHIP_UPDATE"
    RELATIONSHIP_DELETE = "RELATIONSHIP_DELETE"
# END EntityAuditAction


class EntityAuditType(Enum):
    ENTITY_AUDIT_V1 = "ENTITY_AUDIT_V1"
    ENTITY_AUDIT_V2 = "ENTITY_AUDIT_V2"
# END EntityAuditType


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EntityAuditEventBase(DataClassJsonMixin):

    action: EntityAuditAction
    entity_id: str
    event_key: str
    timestamp: int
    user: str

# END EntityAuditEventBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EntityAuditEventDefaultsBase(DataClassJsonMixin):

    details: Optional[str] = None
    entity: Optional[Entity] = None
    type: EntityAuditType = EntityAuditType.ENTITY_AUDIT_V2

# END EntityAuditEventDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EntityAuditEvent(EntityAuditEventDefaultsBase, EntityAuditEventBase):

    pass

# END EntityAuditEvent
