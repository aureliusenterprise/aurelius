from m4i_atlas_core import Attributes, ObjectId

from m4i_flink_tasks import (
    AtlasChangeMessageWithPreviousVersion,
    EntityMessageType,
)

from .handle_delete_operation import handle_delete_operation


def create_mock_change_message(entity: dict) -> AtlasChangeMessageWithPreviousVersion:
    """
    Create a mock change message for testing purposes.

    This function constructs a mock `AtlasChangeMessageWithPreviousVersion` object from a provided
    dictionary, simulating the kind of message that would be received in an actual operation.

    Parameters
    ----------
    entity : dict
        A dictionary representing the entity that will be included in the change message.

    Returns
    -------
    AtlasChangeMessageWithPreviousVersion
        A mock `AtlasChangeMessageWithPreviousVersion` object populated with the provided entity.

    Examples
    --------
    >>> entity_dict = {"type_name": "SampleEntity", "attributes": {}}
    >>> mock_message = create_mock_change_message(entity_dict)
    """
    change_message = {
        "msg_compression_kind": "none",
        "msg_split_idx": 0,
        "msg_split_count": 1,
        "msg_created_by": "user",
        "msg_creation_time": 162392394,
        "message": {
            "event_time": 162392394,
            "operation_type": "ENTITY_DELETE",
            "type": "ENTITY_NOTIFICATION_V2",
            "entity": entity,
        },
        "version": {
            "version": "1.0",
            "version_parts": [1, 0],
        },
        "msg_source_ip": "192.168.1.1",
        "previous_version": entity,
        "spooled": False,
    }

    return AtlasChangeMessageWithPreviousVersion.from_dict(change_message)


def test_handle_delete_operation_no_attributes_relationships() -> None:
    """
    Test the handling of a delete operation where the entity has no attributes or relationships.

    The test verifies that:
    - The output message list has a length of one.
    - The event type in the message is 'ENTITY_DELETED'.
    - The list of deleted attributes is empty.
    - The dictionary of deleted relationships is empty.
    """
    entity = {
        "type_name": "SampleEntity",
        "relationship_attributes": {},
    }

    change_message = create_mock_change_message(entity)

    messages = handle_delete_operation(change_message)

    assert len(messages) == 1
    assert messages[0].event_type == EntityMessageType.ENTITY_DELETED
    assert messages[0].deleted_attributes == []
    assert messages[0].deleted_relationships == {}


def test_handle_delete_operation_attributes_only() -> None:
    """
    Test the handling of a delete operation where the entity has attributes but no relationships.

    The test verifies that:
    - The output message list has a length of one.
    - The event type in the message is 'ENTITY_DELETED'.
    - The list of deleted attributes contains the correct attribute keys.
    - The dictionary of deleted relationships is empty.
    """
    entity = {
        "type_name": "SampleEntity",
        "attributes": {"attr1": "test"},
        "relationship_attributes": {},
    }

    change_message = create_mock_change_message(entity)

    messages = handle_delete_operation(change_message)

    assert len(messages) == 1
    assert messages[0].event_type == EntityMessageType.ENTITY_DELETED
    assert messages[0].deleted_attributes == ["attr1"]
    assert messages[0].deleted_relationships == {}


def test_handle_delete_operation_relationships_only() -> None:
    """
    Test the handling of a delete operation where the entity has relationships but no attributes.

    The test verifies that:
    - The output message list has a length of one.
    - The event type in the message is 'ENTITY_DELETED'.
    - The list of deleted attributes is empty.
    - The dictionary of deleted relationships contains the correct relationship data.
    """
    entity = {
        "type_name": "SampleEntity",
        "relationship_attributes": {
            "relation1": [
                {
                    "guid": "12345",
                    "relationship_guid": "12345",
                    "type_name": "RelatedEntity",
                },
                {
                    "guid": "23456",
                    "relationship_guid": "23456",
                    "type_name": "RelatedEntity",
                },
            ],
        },
    }

    change_message = create_mock_change_message(entity)

    messages = handle_delete_operation(change_message)

    assert len(messages) == 1
    assert messages[0].event_type == EntityMessageType.ENTITY_DELETED
    assert messages[0].deleted_attributes == []
    assert messages[0].deleted_relationships == {
        "relation1": [
            ObjectId(type_name="RelatedEntity", guid="12345", unique_attributes=Attributes()),
            ObjectId(type_name="RelatedEntity", guid="23456", unique_attributes=Attributes()),
        ],
    }


def test_handle_delete_operation_both_attributes_relationships() -> None:
    """
    Test the delete operation handling when the entity has both attributes and relationships.

    The test verifies that:
    - The output message list has a length of one.
    - The event type in the message is 'ENTITY_DELETED'.
    - The list of deleted attributes contains all attribute keys.
    - The dictionary of deleted relationships contains the correct relationship data.
    """
    entity = {
        "type_name": "SampleEntity",
        "attributes": {"attr1": "test", "attr2": "value"},
        "relationship_attributes": {
            "relation1": [
                {
                    "guid": "12345",
                    "relationship_guid": "12345",
                    "type_name": "RelatedEntity",
                },
                {
                    "guid": "23456",
                    "relationship_guid": "23456",
                    "type_name": "RelatedEntity",
                },
            ],
        },
    }

    change_message = create_mock_change_message(entity)

    messages = handle_delete_operation(change_message)

    assert len(messages) == 1
    assert messages[0].event_type == EntityMessageType.ENTITY_DELETED
    assert messages[0].deleted_attributes == ["attr1", "attr2"]
    assert messages[0].deleted_relationships == {
        "relation1": [
            ObjectId(type_name="RelatedEntity", guid="12345", unique_attributes=Attributes()),
            ObjectId(type_name="RelatedEntity", guid="23456", unique_attributes=Attributes()),
        ],
    }
