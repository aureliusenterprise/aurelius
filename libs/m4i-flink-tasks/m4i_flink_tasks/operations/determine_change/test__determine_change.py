import pytest
from pyflink.datastream import StreamExecutionEnvironment

from m4i_flink_tasks import AtlasChangeMessageWithPreviousVersion, EntityMessage

from .determine_change import DetermineChange


def create_mock_change_message(
    operation_type: str,
    previous: dict | None,
    current: dict | None,
) -> AtlasChangeMessageWithPreviousVersion:
    """
    Create a mock change message for testing purposes.

    This function constructs a mock `AtlasChangeMessageWithPreviousVersion` object from a provided
    dictionary, simulating the kind of message that would be received in an actual operation.

    Parameters
    ----------
    operation_type : str
        The operation type of the change message.

    previous : dict | None
        A dictionary representing the previous entity that will be included in the change message.

    current : dict | None
        A dictionary representing the current entity that will be included in the change message.

    Returns
    -------
    AtlasChangeMessageWithPreviousVersion
        A mock `AtlasChangeMessageWithPreviousVersion` object populated with the provided entities
        and operation type.

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
            "operation_type": operation_type,
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


@pytest.fixture()
def environment() -> StreamExecutionEnvironment:
    """
    Provide a StreamExecutionEnvironment for testing.

    This fixture initializes a Flink StreamExecutionEnvironment
    with a parallelism of 1 for consistent testing.
    """
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    return env


def test__determine_change_handle_valid_input_event(
    environment: StreamExecutionEnvironment,
) -> None:
    """
    Test if `DetermineChange` correctly processes a valid entity update event.

    Asserts
    -------
    - The output should have a length of 2.
    - Each message in the output is an instance of `EntityMessage`.
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

    change_message = create_mock_change_message("ENTITY_UPDATE", previous, current)

    data_stream = environment.from_collection([change_message])

    determine_change = DetermineChange(
        data_stream=data_stream,
    )

    output = list(determine_change.main.execute_and_collect())

    assert len(output) == 2
    assert all(isinstance(message, EntityMessage) for message in output)


def test__determine_change_handle_unsupported_operation_type(
    environment: StreamExecutionEnvironment,
) -> None:
    """
    Verify `DetermineChange`'s behavior when encountering an unsupported operation type.

    Asserts
    -------
    - The output should have a length of 1.
    - The single output item is an instance of `NotImplementedError`.
    - The exception message matches "Unknown event type: EntityAuditAction.CLASSIFICATION_ADD".
    """
    change_message = create_mock_change_message(
        "CLASSIFICATION_ADD",
        {"guid": "12345"},
        {"guid": "23456"},
    )

    data_stream = environment.from_collection([change_message])

    determine_change = DetermineChange(
        data_stream=data_stream,
    )

    output = list(determine_change.main.execute_and_collect())

    assert len(output) == 1

    error = output[0]

    assert isinstance(error, NotImplementedError)
    assert str(error) == "Unknown event type: EntityAuditAction.CLASSIFICATION_ADD"


def test__determine_change_handle_processing_error(
    environment: StreamExecutionEnvironment,
) -> None:
    """
    Test error handling in `DetermineChange` when a processing error occurs.

    Asserts
    -------
    - The output should have a length of 1.
    - The single output item is an instance of `ValueError`.
    """
    change_message = create_mock_change_message(
        "ENTITY_UPDATE",
        {"guid": "12345"},
        None,
    )

    data_stream = environment.from_collection([change_message])

    determine_change = DetermineChange(
        data_stream=data_stream,
    )

    output = list(determine_change.main.execute_and_collect())

    assert len(output) == 1

    error = output[0]

    assert isinstance(error, ValueError)
