from flink_tasks import (
    AtlasChangeMessageWithPreviousVersion,
    EntityMessage,
    EntityMessageType,
)


def handle_delete_operation(
    change_message: AtlasChangeMessageWithPreviousVersion,
) -> list[EntityMessage]:
    """
    Identify the changes when an entity is deleted.

    This function processes a deletion event by creating an `EntityMessage` that
    encapsulates the attributes and relationships that were deleted. It uses the
    incoming change message that contains the state of the entity before deletion.

    Parameters
    ----------
    change_message : AtlasChangeMessageWithPreviousVersion
        An object containing the change message with details of the entity prior to
        its deletion.

    Returns
    -------
    list[EntityMessage]
        A list containing a single `EntityMessage` object that represents the deletion
        event of the entity.

    Raises
    ------
    ValueError
        If the entity attribute of the change message is None, indicating that the
        entity details necessary to document the deletion are missing.
    """
    entity = change_message.message.entity

    if entity is None:
        msg = "Entity is None"
        raise ValueError(msg)

    attributes_dict = entity.attributes.to_dict()
    deleted_attributes = list(attributes_dict.keys())

    entity_message = EntityMessage.from_change_message(
        change_message=change_message,
        event_type=EntityMessageType.ENTITY_DELETED,
    )

    entity_message.deleted_attributes = deleted_attributes
    entity_message.deleted_relationships = entity.relationship_attributes
    entity_message.old_value = entity

    return [entity_message]
