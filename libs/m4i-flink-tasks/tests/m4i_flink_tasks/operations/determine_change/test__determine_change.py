"""Tests for the DetermineChangeFunction class."""

from typing import Any, Dict, Union

from m4i_flink_tasks import AtlasChangeMessageWithPreviousVersion, EntityMessage

from m4i_flink_tasks.operations.determine_change.determine_change import DetermineChangeFunction


def create_mock_change_message(
    operation_type: str, previous: Union[Dict[str, Any], None], current: Union[Dict[str, Any], None]
) -> AtlasChangeMessageWithPreviousVersion:
    """Create a mock change message for testing purposes."""
    change_message = {
        "msg_compression_kind": "none",
        "msg_split_idx": 0,
        "msg_split_count": 1,
        "msg_created_by": "user",
        "msg_creation_time": 162392394,
        "message": {
            "event_time": 162392394,
            "operation_type": operation_type,
            "type": "ENTITY_NOTIFICATION_V2",
            "entity": current,
        },
        "version": {"version": "1.0", "version_parts": [1, 0]},
        "msg_source_ip": "192.168.1.1",
        "previous_version": previous,
        "spooled": False,
        "source": {},
    }

    return AtlasChangeMessageWithPreviousVersion.from_dict(change_message)


def test__determine_change_handle_valid_input_event() -> None:
    """Test valid ENTITY_UPDATE event produces two EntityMessage objects."""
    previous = {
        "type_name": "SampleEntity",
        "attributes": {"attr1": "test"},
        "relationship_attributes": {
            "relation1": [{"guid": "12345", "relationship_guid": "12345", "type_name": "RelatedEntity"}]
        },
    }

    current = {
        "type_name": "SampleEntity",
        "attributes": {"attr1": "new_value", "attr2": "value"},
        "relationship_attributes": {
            "relation1": [{"guid": "23456", "relationship_guid": "23456", "type_name": "RelatedEntity"}]
        },
    }

    change_message = create_mock_change_message("ENTITY_UPDATE", previous, current)

    func = DetermineChangeFunction()
    output = func.map(change_message)

    assert len(output) == 2
    assert all(isinstance(message, EntityMessage) for message in output)


def test__determine_change_handle_unsupported_operation_type() -> None:
    """Test unsupported operation type returns NotImplementedError."""
    change_message = create_mock_change_message("CLASSIFICATION_ADD", {"guid": "12345"}, {"guid": "23456"})

    func = DetermineChangeFunction()
    output = func.map(change_message)

    assert len(output) == 1

    error = output[0]

    assert isinstance(error, NotImplementedError)
    assert str(error) == "Unknown event type: EntityAuditAction.CLASSIFICATION_ADD"


def test__determine_change_handle_processing_error() -> None:
    """Test processing error (missing current entity) returns ValueError."""
    change_message = create_mock_change_message("ENTITY_UPDATE", {"guid": "12345"}, None)

    func = DetermineChangeFunction()
    output = func.map(change_message)

    assert len(output) == 1

    error = output[0]

    assert isinstance(error, ValueError)
