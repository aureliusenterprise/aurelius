from m4i_atlas_core import Attributes, ObjectId

from flink_tasks import (
    AtlasChangeMessageWithPreviousVersion,
    EntityMessageType,
)

from .handle_update_operation import handle_update_operation


def create_mock_change_message(
    previous: dict,
    current: dict,
) -> AtlasChangeMessageWithPreviousVersion:
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
            "operation_type": "ENTITY_UPDATE",
            "type": "ENTITY_NOTIFICATION_V2",
            "entity": current,
        },
        "version": {
            "version": "1.0",
            "version_parts": [1, 0],
        },
        "msg_source_ip": "192.168.1.1",
        "previous_version": previous,
        "spooled": False,
    }

    return AtlasChangeMessageWithPreviousVersion.from_dict(change_message)


def test_handle_update_operation_no_changes() -> None:
    """
    Verify update operation with no changes in entity attributes or relationships.

    Asserts:
    - No messages are produced when there are no changes in the entity's state.
    """
    current = {
        "type_name": "SampleEntity",
        "attributes": {"attr1": "test"},
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

    change_message = create_mock_change_message(current, current)

    messages = handle_update_operation(change_message)

    assert not any(messages)


def test_handle_update_operation_attribute_changes_only() -> None:
    """
    Verify update operation with changes only in entity attributes.

    Asserts:
    - One message is produced.
    - The message type is ENTITY_ATTRIBUTE_AUDIT.
    - The correct attributes are marked as inserted and changed.
    - No attributes are marked as deleted.
    """
    previous = {
        "type_name": "SampleEntity",
        "attributes": {"attr1": "test"},
        "relationship_attributes": {},
    }

    current = {
        "type_name": "SampleEntity",
        "attributes": {"attr1": "new_value", "attr2": "value"},
        "relationship_attributes": {},
    }

    change_message = create_mock_change_message(previous, current)

    messages = handle_update_operation(change_message)

    assert len(messages) == 1
    assert messages[0].event_type == EntityMessageType.ENTITY_ATTRIBUTE_AUDIT
    assert messages[0].inserted_attributes == ["attr2"]
    assert messages[0].deleted_attributes == []
    assert messages[0].changed_attributes == ["attr1"]


def test_handle_update_operation_relationship_changes_only() -> None:
    """
    Verify update operation with changes only in entity relationships.

    Asserts:
    - One message is produced.
    - The message type is ENTITY_RELATIONSHIP_AUDIT.
    - The correct relationships are marked as inserted.
    - No relationships are marked as deleted.
    """
    previous = {
        "type_name": "SampleEntity",
        "relationship_attributes": {
            "relation1": [
                {
                    "guid": "12345",
                    "relationship_guid": "12345",
                    "type_name": "RelatedEntity",
                },
            ],
        },
    }

    current = {
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

    change_message = create_mock_change_message(previous, current)

    messages = handle_update_operation(change_message)

    assert len(messages) == 1
    assert messages[0].event_type == EntityMessageType.ENTITY_RELATIONSHIP_AUDIT
    assert messages[0].inserted_relationships == {
        "relation1": [
            ObjectId(type_name="RelatedEntity", guid="23456", unique_attributes=Attributes()),
        ],
    }
    assert messages[0].deleted_relationships == {"relation1": []}


def test_handle_update_operation_both_attribute_and_relationship_changes() -> None:
    """
    Verify update operation with changes in both attributes and relationships.

    Asserts:
    - Two messages are produced, one for attribute audit and one for relationship audit.
    - The correct attributes and relationships are marked as inserted, deleted, and changed.
    """
    previous = {
        "type_name": "SampleEntity",
        "attributes": {"attr1": "test"},
        "relationship_attributes": {
            "relation1": [
                {
                    "guid": "12345",
                    "relationship_guid": "12345",
                    "type_name": "RelatedEntity",
                },
            ],
        },
    }

    current = {
        "type_name": "SampleEntity",
        "attributes": {"attr1": "new_value", "attr2": "value"},
        "relationship_attributes": {
            "relation1": [
                {
                    "guid": "23456",
                    "relationship_guid": "23456",
                    "type_name": "RelatedEntity",
                },
            ],
        },
    }

    change_message = create_mock_change_message(previous, current)

    messages = handle_update_operation(change_message)

    assert len(messages) == 2

    attribute_audit_message = messages[0]

    assert attribute_audit_message.inserted_attributes == ["attr2"]
    assert attribute_audit_message.deleted_attributes == []
    assert attribute_audit_message.changed_attributes == ["attr1"]

    relationship_audit_message = messages[1]

    assert relationship_audit_message.inserted_relationships == {
        "relation1": [
            ObjectId(type_name="RelatedEntity", guid="23456", unique_attributes=Attributes()),
        ],
    }
    assert relationship_audit_message.deleted_relationships == {
        "relation1": [
            ObjectId(type_name="RelatedEntity", guid="12345", unique_attributes=Attributes()),
        ],
    }
