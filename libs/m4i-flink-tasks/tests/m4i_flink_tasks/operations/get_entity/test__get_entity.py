"""Tests for the GetEntityFunction class."""

import importlib
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

from aiohttp.web import HTTPError
from keycloak.exceptions import KeycloakError
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

from m4i_flink_tasks.operations.get_entity.get_entity import GetEntityFunction


def _make_event(guid: str = "1234") -> AtlasChangeMessage:
    """Create a sample AtlasChangeMessage for testing."""
    return AtlasChangeMessage(
        version=AtlasChangeMessageVersion(version="1", version_parts=[]),
        msg_compression_kind="",
        msg_split_idx=1,
        msg_split_count=1,
        msg_source_ip="localhost",
        msg_created_by="test",
        msg_creation_time=1,
        spooled=False,
        source={},
        message=AtlasChangeMessageBody(
            event_time=1,
            operation_type=EntityAuditAction.ENTITY_CREATE,
            type=EntityNotificationType.ENTITY_NOTIFICATION_V1,
            entity=Entity(guid=guid),
            relationship=None,
        ),
    )


def test_get_entity_process_valid_input_event() -> None:
    """Test successful processing of a valid event returns AtlasChangeMessage with entity."""
    func = GetEntityFunction(atlas_url="test", keycloak_factory=Mock(), credentials=("username", "password"))
    func.open(Mock())

    entity = Entity(guid="1234", attributes=Attributes(unmapped_attributes={"hello": "world"}))
    event = _make_event()

    get_entity_module = importlib.import_module("m4i_flink_tasks.operations.get_entity.get_entity")

    with patch.object(
        GetEntityFunction, "access_token", new=PropertyMock(return_value="test-token")
    ), patch.object(get_entity_module, "get_entity_by_guid", new=AsyncMock(return_value=entity)):
        result = func.map(event.to_json())

        assert isinstance(result, AtlasChangeMessage)
        assert result.message.entity == entity


def test_get_entity_handle_invalid_input_event() -> None:
    """Test invalid JSON input returns ValidationError."""
    func = GetEntityFunction(atlas_url="test", keycloak_factory=Mock(), credentials=("username", "password"))
    func.open(Mock())

    result = func.map('{"hello": "world"}')

    assert isinstance(result, ValidationError)


def test_get_entity_handle_event_without_entity() -> None:
    """Test event without entity returns ValueError."""
    func = GetEntityFunction(atlas_url="test", keycloak_factory=Mock(), credentials=("username", "password"))
    func.open(Mock())

    event = AtlasChangeMessage(
        version=AtlasChangeMessageVersion(version="1", version_parts=[]),
        msg_compression_kind="",
        msg_split_idx=1,
        msg_split_count=1,
        msg_source_ip="localhost",
        msg_created_by="test",
        msg_creation_time=1,
        spooled=False,
        source={},
        message=AtlasChangeMessageBody(
            event_time=1,
            operation_type=EntityAuditAction.ENTITY_CREATE,
            type=EntityNotificationType.ENTITY_NOTIFICATION_V1,
            entity=None,
            relationship=None,
        ),
    )

    result = func.map(event.to_json())

    assert isinstance(result, ValueError)


def test_get_entity_handle_http_error_during_entity_lookup() -> None:
    """Test HTTPError during entity lookup is wrapped in RuntimeError."""
    func = GetEntityFunction(atlas_url="test", keycloak_factory=Mock(), credentials=("username", "password"))
    func.open(Mock())

    event = _make_event()

    get_entity_module = importlib.import_module("m4i_flink_tasks.operations.get_entity.get_entity")

    with patch.object(
        GetEntityFunction, "access_token", new=PropertyMock(return_value="test-token")
    ), patch.object(get_entity_module, "get_entity_by_guid", new=AsyncMock(side_effect=HTTPError())):
        result = func.map(event.to_json())

        assert isinstance(result, RuntimeError)


def test_get_entity_handle_keycloak_error_during_entity_lookup() -> None:
    """Test KeycloakError during token refresh is wrapped in RuntimeError."""
    func = GetEntityFunction(atlas_url="test", keycloak_factory=Mock(), credentials=("username", "password"))
    func.open(Mock())

    event = _make_event()

    with patch.object(
        GetEntityFunction, "access_token", new=PropertyMock(side_effect=KeycloakError("Mock Error", 404, b""))
    ):
        result = func.map(event.to_json())

        assert isinstance(result, RuntimeError)
