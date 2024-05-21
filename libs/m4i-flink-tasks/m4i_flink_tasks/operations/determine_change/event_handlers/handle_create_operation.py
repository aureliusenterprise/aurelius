
from flink_tasks import (
    AtlasChangeMessageWithPreviousVersion,
    EntityMessage,
    EntityMessageType,
)


def handle_create_operation(
    change_message: AtlasChangeMessageWithPreviousVersion,
) -> list[EntityMessage]:
    """
    Identify the changes when an entity is created.

    This function takes a change message that includes details of a newly created entity
    and constructs an `EntityMessage` that contains a summary of the attributes and
    relationships that have been inserted as part of the entity creation process.

    Parameters
    ----------
    change_message : AtlasChangeMessageWithPreviousVersion
        An object that encapsulates the change message received, which includes the
        entity details along with its previous version information.

    Returns
    -------
    list[EntityMessage]
        A list containing a single `EntityMessage` object that represents the changes
        associated with the entity creation event.

    Raises
    ------
    ValueError
        If the entity attribute of the change message is None, indicating that the
        necessary details to construct the `EntityMessage` are missing.
    """
    entity = change_message.message.entity

    if entity is None:
        msg = "Entity is None"
        raise ValueError(msg)

    attributes_dict = entity.attributes.to_dict()

    if "unmappedAttributes" in attributes_dict:
        del attributes_dict["unmappedAttributes"]

    inserted_attributes = list(attributes_dict.keys())

    entity_message = EntityMessage.from_change_message(
        change_message=change_message,
        event_type=EntityMessageType.ENTITY_CREATED,
    )

    entity_message.inserted_attributes = inserted_attributes
    entity_message.inserted_relationships = entity.relationship_attributes
    entity_message.new_value = entity

    return [entity_message]
