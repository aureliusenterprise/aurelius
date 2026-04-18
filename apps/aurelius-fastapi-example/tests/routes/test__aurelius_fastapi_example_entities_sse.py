import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import uuid4

from aurelius_example.models import PG_NOTIFY_ENTITY_CHANNEL, Entity, EntityNotification
from aurelius_fastapi_example.providers import notifications as cdc_notifications
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test__sse_streams_existing_entity(app: FastAPI, authenticated_client: TestClient, entity: Entity) -> None:
    """SSE endpoint should stream a ServerSentEvent containing the entity when notified."""
    notifications = [
        EntityNotification(
            guid=entity.guid,
            op="INSERT",
            schema_name="public",
            table_name="entity",
            timestamp=datetime.now(tz=UTC),
        ),
    ]

    async def listener() -> AsyncGenerator:
        for notification in notifications:
            yield notification

    app.dependency_overrides[cdc_notifications] = lambda: listener

    response = authenticated_client.get("/entities/sse")

    assert response.status_code == 200

    lines = response.text.splitlines()
    event_lines = [line.removeprefix("event: ") for line in lines if line.startswith("event: ")]
    data_lines = [json.loads(line.removeprefix("data: ")) for line in lines if line.startswith("data: ")]

    assert event_lines == [PG_NOTIFY_ENTITY_CHANNEL]
    assert len(data_lines) == 1
    assert data_lines[0]["guid"] == str(entity.guid)
    assert data_lines[0]["value"]["name"] == entity.name


def test__sse_streams_deleted_entity(app: FastAPI, authenticated_client: TestClient) -> None:
    """SSE endpoint should stream an Envelope with a null value when the notified entity does not exist."""
    missing_guid = uuid4()

    notifications = [
        EntityNotification(
            guid=missing_guid,
            op="DELETE",
            schema_name="public",
            table_name="entity",
            timestamp=datetime.now(tz=UTC),
        ),
    ]

    async def listener() -> AsyncGenerator:
        for notification in notifications:
            yield notification

    app.dependency_overrides[cdc_notifications] = lambda: listener

    response = authenticated_client.get("/entities/sse")

    assert response.status_code == 200

    data_lines = [
        json.loads(line.removeprefix("data: ")) for line in response.text.splitlines() if line.startswith("data: ")
    ]

    assert len(data_lines) == 1
    assert data_lines[0]["guid"] == str(missing_guid)
    assert data_lines[0]["value"] is None


def test__sse_yields_no_events_for_empty_stream(app: FastAPI, authenticated_client: TestClient) -> None:
    """SSE endpoint should return a 200 response with no data lines when the notification stream is empty."""
    notifications = []

    async def listener() -> AsyncGenerator:
        for notification in notifications:
            yield notification

    app.dependency_overrides[cdc_notifications] = lambda: listener

    response = authenticated_client.get("/entities/sse")

    assert response.status_code == 200
    assert not any(line.startswith("data: ") for line in response.text.splitlines())


def test__sse_requires_authentication(app: FastAPI, unauthenticated_client: TestClient) -> None:
    """SSE endpoint should return 401 when no bearer token is provided."""
    notifications = []

    async def listener() -> AsyncGenerator:
        for notification in notifications:
            yield notification

    app.dependency_overrides[cdc_notifications] = lambda: listener

    response = unauthenticated_client.get("/entities/sse")

    assert response.status_code == 401
