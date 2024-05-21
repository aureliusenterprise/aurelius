from unittest.mock import Mock, PropertyMock, patch

import pytest
from aiohttp.web import HTTPError
from m4i_atlas_core import (
    AtlasChangeMessage,
    AtlasChangeMessageBody,
    AtlasChangeMessageVersion,
    Attributes,
    Entity,
    EntityAuditAction,
    EntityNotificationType,
)
from marshmallow import ValidationError
from pyflink.datastream import StreamExecutionEnvironment

from keycloak import KeycloakError, KeycloakOpenID

from .get_entity import GetEntity, KeycloakFactory


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


@pytest.fixture()
def entity() -> Entity:
    """
    Provide a sample Entity instance for testing.

    Returns a simple Entity object with a given guid and attributes.
    """
    return Entity(
        guid="1234",
        attributes=Attributes(unmapped_attributes={"hello": "world"}),
    )


@pytest.fixture()
def event() -> AtlasChangeMessage:
    """
    Provide a sample AtlasChangeMessage for testing.

    Returns a basic AtlasChangeMessage object with predefined values
    to simulate a typical change message event.
    """
    return AtlasChangeMessage(
        version=AtlasChangeMessageVersion(
            version="1",
            version_parts=[],
        ),
        msg_compression_kind="",
        msg_split_idx=1,
        msg_split_count=1,
        msg_source_ip="localhost",
        msg_created_by="test",
        msg_creation_time=1,
        spooled=False,
        message=AtlasChangeMessageBody(
            event_time=1,
            operation_type=EntityAuditAction.ENTITY_CREATE,
            type=EntityNotificationType.ENTITY_NOTIFICATION_V1,
            entity=Entity(guid="1234"),
            relationship=None,
        ),
    )


@pytest.fixture()
def keycloak_factory() -> KeycloakFactory:
    """
    Mock the Keycloak factory behavior.

    This fixture returns a mock object simulating the behavior
    of creating a Keycloak instance.

    The simulated Keycloak instance always returns the same access token.
    """

    def mock() -> KeycloakOpenID:
        mock_keycloak = Mock(spec=KeycloakOpenID)
        mock_keycloak.token.return_value = {"access_token": "1234", "expires_in": 3600}
        return mock_keycloak

    return mock


def test_get_entity_process_valid_input_event(
    environment: StreamExecutionEnvironment,
    entity: Entity,
    event: AtlasChangeMessage,
    keycloak_factory: KeycloakFactory,
) -> None:
    """
    Test the successful processing of a valid event by the GetEntity class.

    This test simulates a scenario where:
    - A data stream is created from a collection containing a sample valid event.
    - The GetEntity class processes this event.
    - The output is collected and verified to match the expected AtlasChangeMessage.
    """
    data_stream = environment.from_collection([event.to_json()])

    with patch(__package__ + ".get_entity.get_entity_by_guid", return_value=entity):
        get_entity = GetEntity(
            data_stream=data_stream,
            atlas_url="test",  # atlas_url is not used in the test
            keycloak_factory=keycloak_factory,
            credentials=("username", "password"),
        )

        expected = [
            AtlasChangeMessage(
                version=AtlasChangeMessageVersion(
                    version="1",
                    version_parts=[],
                ),
                msg_compression_kind="",
                msg_split_idx=1,
                msg_split_count=1,
                msg_source_ip="localhost",
                msg_created_by="test",
                msg_creation_time=1,
                spooled=False,
                message=AtlasChangeMessageBody(
                    event_time=1,
                    operation_type=EntityAuditAction.ENTITY_CREATE,
                    type=EntityNotificationType.ENTITY_NOTIFICATION_V1,
                    entity=entity,
                    relationship=None,
                ),
            ),
        ]

        output = list(get_entity.main.execute_and_collect())

        assert output == expected


def test_get_entity_handle_invalid_input_event(
    environment: StreamExecutionEnvironment,
    keycloak_factory: KeycloakFactory,
) -> None:
    """
    Test the GetEntity class's handling of an invalid event input.

    This test checks the behavior when:
    - A data stream is created with invalid event data.
    - The GetEntity class processes this stream.
    - The schema_errors stream is checked to ensure it reports the validation error.
    """
    data_stream = environment.from_collection(['{"hello": "world"}'])

    get_entity = GetEntity(
        data_stream=data_stream,
        atlas_url="test",  # atlas_url is not used in the test
        keycloak_factory=keycloak_factory,
        credentials=("username", "password"),
    )

    output = list(get_entity.main.execute_and_collect())

    assert len(output) == 1

    error = output[0]

    assert isinstance(error, ValidationError)


def test_get_entity_handle_event_without_entity(
    environment: StreamExecutionEnvironment,
    keycloak_factory: KeycloakFactory,
) -> None:
    """
    Test the GetEntity class's handling of an event without an entity.

    This test checks the behavior when:
    - A data stream is created with an event that lacks an entity.
    - The GetEntity class processes this stream.
    - The no_entity_errors stream is checked to ensure it reports the error.
    """
    event = AtlasChangeMessage(
        version=AtlasChangeMessageVersion(
            version="1",
            version_parts=[],
        ),
        msg_compression_kind="",
        msg_split_idx=1,
        msg_split_count=1,
        msg_source_ip="localhost",
        msg_created_by="test",
        msg_creation_time=1,
        spooled=False,
        message=AtlasChangeMessageBody(
            event_time=1,
            operation_type=EntityAuditAction.ENTITY_CREATE,
            type=EntityNotificationType.ENTITY_NOTIFICATION_V1,
            entity=None,
            relationship=None,
        ),
    )

    data_stream = environment.from_collection([event.to_json()])

    get_entity = GetEntity(
        data_stream=data_stream,
        atlas_url="test",  # atlas_url is not used in the test
        keycloak_factory=keycloak_factory,
        credentials=("username", "password"),
    )

    output = list(get_entity.main.execute_and_collect())

    assert len(output) == 1

    error = output[0]

    assert isinstance(error, ValueError)


def test_get_entity_handle_http_error_during_entity_lookup(
    environment: StreamExecutionEnvironment,
    event: AtlasChangeMessage,
    keycloak_factory: KeycloakFactory,
) -> None:
    """
    Test the GetEntity class's handling of HTTP errors during entity lookup.

    This test checks the behavior when:
    - A data stream is created with a valid event.
    - An HTTP error occurs during entity lookup.
    - The GetEntity class processes this stream.
    - The entity_lookup_errors stream is checked to ensure it reports the error.
    """
    data_stream = environment.from_collection([event.to_json()])

    with patch(__package__ + ".get_entity.get_entity_by_guid", new=Mock(side_effect=HTTPError())):
        get_entity = GetEntity(
            data_stream=data_stream,
            atlas_url="test",  # atlas_url is not used in the test
            keycloak_factory=keycloak_factory,
            credentials=("username", "password"),
        )

        output = list(get_entity.main.execute_and_collect())

        assert len(output) == 1

        error = output[0]

        assert isinstance(error, RuntimeError)


def test_get_entity_handle_keycloak_error_during_entity_lookup(
    environment: StreamExecutionEnvironment,
    event: AtlasChangeMessage,
    keycloak_factory: KeycloakFactory,
) -> None:
    """
    Test the GetEntity class's handling of Keycloak errors during entity lookup.

    This test checks the behavior when:
    - A data stream is created with a valid event.
    - A Keycloak error occurs during entity lookup.
    - The GetEntity class processes this stream.
    - The entity_lookup_errors stream is checked to ensure it reports the error.
    """
    data_stream = environment.from_collection([event.to_json()])

    with patch(
        __package__ + ".get_entity.GetEntityFunction.access_token",
        new=PropertyMock(side_effect=KeycloakError("Mock Error", 404, b"")),
    ):
        get_entity = GetEntity(
            data_stream=data_stream,
            atlas_url="test",  # atlas_url is not used in the test
            keycloak_factory=keycloak_factory,
            credentials=("username", "password"),
        )

        output = list(get_entity.main.execute_and_collect())

        assert len(output) == 1

        error = output[0]

        assert isinstance(error, RuntimeError)
