from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Dict, List, Union

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import AtlasChangeMessage, Entity, EntityAuditAction, ObjectId


class EntityMessageType(Enum):
    """Different types of entity messages."""

    ENTITY_ATTRIBUTE_AUDIT = "EntityAttributeAudit"
    ENTITY_CREATED = "EntityCreated"
    ENTITY_DELETED = "EntityDeleted"
    ENTITY_RELATIONSHIP_AUDIT = "EntityRelationshipAudit"


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass
class EntityMessage(DataClassJsonMixin):
    """Captures changes to entity attributes and relationships."""

    type_name: str
    guid: str
    original_event_type: EntityAuditAction
    event_type: EntityMessageType

    inserted_attributes: List[str] = field(default_factory=list)
    changed_attributes: List[str] = field(default_factory=list)
    deleted_attributes: List[str] = field(default_factory=list)

    inserted_relationships: Union[Dict[str, List[ObjectId]], None] = field(
        default_factory=dict,
    )
    changed_relationships: Union[Dict[str, List[ObjectId]], None] = field(default_factory=dict)
    deleted_relationships: Union[Dict[str, List[ObjectId]], None] = field(default_factory=dict)

    direct_change: bool = True
    msg_creation_time: float = field(default_factory=time)
    old_value: Union[Entity, None] = None
    new_value: Union[Entity, None] = None

    @classmethod
    def from_change_message(
        cls,
        change_message: AtlasChangeMessage,
        event_type: EntityMessageType,
    ) -> "EntityMessage":
        """
        Create an `EntityMessage` instance from an `AtlasChangeMessage`.

        The method extracts necessary details from the `AtlasChangeMessage`, such as entity GUID and
        type name, and maps the original event type to a more specific `EntityMessageType`.

        Parameters
        ----------
        change_message : AtlasChangeMessage
            The original change message containing details about the entity and the event.
        event_type : EntityMessageType
            The specific type of entity message event being represented.

        Returns
        -------
        EntityMessage
            An instantiated `EntityMessage` reflecting the entity changes and event context.

        Raises
        ------
        ValueError
            If the entity within the change message is None, indicating an invalid state.
        """
        entity = change_message.message.entity

        if entity is None:
            msg = "Entity is None"
            raise ValueError(msg)

        return cls(
            event_type=event_type,
            guid=entity.guid,
            original_event_type=change_message.message.operation_type,
            type_name=entity.type_name,
        )
