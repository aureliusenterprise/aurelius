from typing import Dict, List, Union
from m4i_atlas_core import Entity, ObjectId

from m4i_flink_tasks import (
    AtlasChangeMessageWithPreviousVersion,
    EntityMessage,
    EntityMessageType,
)


def handle_attribute_changes(
    change_message: AtlasChangeMessageWithPreviousVersion,
    previous: Entity,
    current: Entity,
) -> Union[EntityMessage, None]:
    """
    Identify and process changes in entity attributes between two versions of an entity.

    This function compares attributes of two entity versions and creates an `EntityMessage`
    capturing the inserted, deleted, and changed attributes.

    Parameters
    ----------
    change_message : AtlasChangeMessageWithPreviousVersion
        The change message object that contains the previous and current versions of the entity.
    previous : Entity
        The previous version of the entity before the update.
    current : Entity
        The current version of the entity after the update.

    Returns
    -------
    EntityMessage | None
        Returns an `EntityMessage` object containing details about the attribute changes if any
        changes are detected. Returns None if no changes are detected.
    """
    attributes_dict = current.attributes.to_dict()
    if "unmappedAttributes" in attributes_dict:
        del attributes_dict["unmappedAttributes"]

    previous_attributes_dict = previous.attributes.to_dict()

    if "unmappedAttributes" in  previous_attributes_dict:
        del previous_attributes_dict["unmappedAttributes"]

    inserted_attributes = [key for key in attributes_dict if key not in previous_attributes_dict]

    deleted_attributes = [key for key in previous_attributes_dict if key not in attributes_dict]

    changed_attributes = [
        key
        for key in attributes_dict
        if key in previous_attributes_dict and attributes_dict[key] != previous_attributes_dict[key]
    ]

    if not any(inserted_attributes) and not any(deleted_attributes) and not any(changed_attributes):
        return None

    entity_message = EntityMessage.from_change_message(
        change_message=change_message,
        event_type=EntityMessageType.ENTITY_ATTRIBUTE_AUDIT,
    )

    entity_message.old_value = previous
    entity_message.new_value = current

    entity_message.inserted_attributes = inserted_attributes
    entity_message.deleted_attributes = deleted_attributes
    entity_message.changed_attributes = changed_attributes

    return entity_message


def get_relationships_diff(a: Entity, b: Entity) -> Dict[str, List[ObjectId]]:
    """
    Compute the difference in relationships between two entity states.

    This function finds new relationships that have been added to 'b' that do not exist in 'a'.

    Parameters
    ----------
    a : Entity
        The first entity state to compare.
    b : Entity
        The second entity state to compare.

    Returns
    -------
    dict[str, list[ObjectId]]
        A dictionary where keys are attribute names and values are lists of `ObjectId` instances
        that represent new relationships in 'b'.
    """
    a_relationships = set()

    if a.relationship_attributes is not None:
        for relationships in a.relationship_attributes.values():
            if not relationships:
                continue

            a_relationships.update(relationship.guid for relationship in relationships)

    difference: dict[str, list[ObjectId]] = {}

    if b.relationship_attributes is None:
        return difference

    for attribute, relationships in b.relationship_attributes.items():
        if not relationships:
            continue

        difference[attribute] = [
            relationship for relationship in relationships if relationship.guid not in a_relationships
        ]

    return difference


def handle_relationship_changes(
    change_message: AtlasChangeMessageWithPreviousVersion,
    previous: Entity,
    current: Entity,
) -> Union[EntityMessage, None]:
    """
    Identify and process changes in entity relationships between two versions of an entity.

    This function compares relationships of two entity versions and creates an `EntityMessage`
    capturing the inserted and deleted relationships.

    Parameters
    ----------
    change_message : AtlasChangeMessageWithPreviousVersion
        The change message object that contains the old and current versions of the entity.
    previous : Entity
        The previous version of the entity before the update.
    current : Entity
        The current version of the entity after the update.

    Returns
    -------
    EntityMessage | None
        Returns an `EntityMessage` object containing details about the relationship changes if any
        changes are detected. Returns None if no changes are detected.
    """
    inserted_relationships = get_relationships_diff(previous, current)
    deleted_relationships = get_relationships_diff(current, previous)

    has_inserted_relationships = any(any(relationships) for relationships in inserted_relationships.values())

    has_deleted_relationships = any(any(relationships) for relationships in deleted_relationships.values())

    if not (has_inserted_relationships or has_deleted_relationships):
        return None

    entity_message = EntityMessage.from_change_message(
        change_message=change_message,
        event_type=EntityMessageType.ENTITY_RELATIONSHIP_AUDIT,
    )

    entity_message.old_value = previous
    entity_message.new_value = current

    entity_message.inserted_relationships = inserted_relationships
    entity_message.deleted_relationships = deleted_relationships

    return entity_message


def handle_update_operation(
    change_message: AtlasChangeMessageWithPreviousVersion,
) -> List[EntityMessage]:
    """
    Process the update operation on an entity to identify changes in attributes and relationships.

    This function checks for changes between the previous and current versions of an entity and
    generates `EntityMessage` objects if there are any changes in its attributes or relationships.
    It leverages the `handle_attribute_changes` and `handle_relationship_changes` functions to
    detect and process these changes.

    Parameters
    ----------
    change_message : AtlasChangeMessageWithPreviousVersion
        The change message object that contains the current and previous versions of the entity.

    Returns
    -------
    list[EntityMessage]
        A list of `EntityMessage` objects detailing the detected changes. The list may include
        messages for attribute changes, relationship changes, or both. If no changes are detected,
        the list will be empty.

    Raises
    ------
    ValueError
        If either the current entity or the previous entity version is None.
    """
    entity = change_message.message.entity
    previous_entity = change_message.previous_version

    if entity is None:
        msg = "Entity is None"
        raise ValueError(msg)

    if previous_entity is None:
        msg = "Previous entity is None"
        raise ValueError(msg)

    messages: list[EntityMessage] = []

    attribute_audit_message = handle_attribute_changes(
        change_message=change_message,
        previous=previous_entity,
        current=entity,
    )

    if attribute_audit_message is not None:
        messages.append(attribute_audit_message)

    relationship_audit_message = handle_relationship_changes(
        change_message=change_message,
        previous=previous_entity,
        current=entity,
    )

    if relationship_audit_message is not None:
        messages.append(relationship_audit_message)

    return messages
