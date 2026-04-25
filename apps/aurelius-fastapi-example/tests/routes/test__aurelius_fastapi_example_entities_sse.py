import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import uuid4

from aurelius_example.models import PG_NOTIFY_ENTITY_CHANNEL, Entity
from aurelius_fastapi_example.models import Envelope
from aurelius_fastapi_example.providers import notifications as cdc_notifications
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test__sse_streams_existing_entity(app: FastAPI, authenticated_client: TestClient, entity: Entity) -> None:
    """SSE endpoint should stream a ServerSentEvent containing the entity when notified."""
    inserted = Envelope[Entity](
        guid=entity.guid,
        op="INSERT",
        timestamp=datetime.now(tz=UTC),
        value=entity,
    )

    notifications = [inserted]

    async def listener() -> AsyncGenerator:
        for notification in notifications:
            yield notification

    app.dependency_overrides[cdc_notifications] = lambda: listener

    response = authenticated_client.get("/entities/sse")

    assert response.status_code == 200

    lines = response.text.splitlines()
    event_lines = [line.removeprefix("event: ") for line in lines if line.startswith("event: ")]
    data_lines = [line.removeprefix("data: ") for line in lines if line.startswith("data: ")]

    assert event_lines == [PG_NOTIFY_ENTITY_CHANNEL]
    assert len(data_lines) == 1

    expected = inserted.model_dump(mode="json")

    actual = json.loads(data_lines[0])

    assert expected == actual


def test__sse_streams_deleted_entity(app: FastAPI, authenticated_client: TestClient) -> None:
    """SSE endpoint should stream an Envelope with a null value when the notified entity does not exist."""
    missing_guid = uuid4()

    deleted = Envelope[Entity](
        guid=missing_guid,
        op="DELETE",
        timestamp=datetime.now(tz=UTC),
        value=None,
    )

    notifications = [deleted]

    async def listener() -> AsyncGenerator:
        for notification in notifications:
            yield notification

    app.dependency_overrides[cdc_notifications] = lambda: listener

    response = authenticated_client.get("/entities/sse")

    assert response.status_code == 200

    lines = response.text.splitlines()
    event_lines = [line.removeprefix("event: ") for line in lines if line.startswith("event: ")]
    data_lines = [line.removeprefix("data: ") for line in lines if line.startswith("data: ")]

    assert event_lines == [PG_NOTIFY_ENTITY_CHANNEL]
    assert len(data_lines) == 1

    expected = deleted.model_dump(mode="json")

    actual = json.loads(data_lines[0])

    assert expected == actual


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
