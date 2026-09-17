import asyncio
import queue
from datetime import UTC, datetime
from functools import partial
from types import SimpleNamespace
from typing import cast
from unittest.mock import ANY, AsyncMock, MagicMock
from uuid import UUID

import psycopg
import pytest
from aurelius_example import Entity
from aurelius_fastapi_example.models import Envelope, Settings
from aurelius_fastapi_example.providers import EntityNotificationBroadcaster, get_broadcaster, notifications
from sqlmodel import Session


def test__entity_notification_broadcaster_starts_and_stops(db_settings: Settings) -> None:
    """EntityNotificationBroadcaster should start the PostgresListener on start and stop it on stop."""
    get_broadcaster.cache_clear()

    broadcaster = get_broadcaster(settings=db_settings)
    broadcaster.start()

    assert broadcaster._connection is not None  # noqa: SLF001
    assert broadcaster._postgres_listener is not None  # noqa: SLF001

    broadcaster.stop()

    assert broadcaster._connection is None  # noqa: SLF001
    assert broadcaster._postgres_listener is None  # noqa: SLF001


async def test__entity_notification_broadcaster_single_connection_serves_multiple_subscribers(
    broadcaster: EntityNotificationBroadcaster,
    db_session: Session,
) -> None:
    """All subscribers should receive the same notification through the shared connection."""
    queue_a = broadcaster.subscribe()
    queue_b = broadcaster.subscribe()

    entity = Entity(name="Multicast Entity", description="Fan-out test")
    db_session.add(entity)
    db_session.commit()

    notify_a = await asyncio.to_thread(partial(queue_a.get, timeout=10.0))
    notify_b = await asyncio.to_thread(partial(queue_b.get, timeout=10.0))

    assert notify_a == notify_b


async def test__entity_notification_broadcaster_unsubscribe_removes_queue(
    broadcaster: EntityNotificationBroadcaster,
    db_session: Session,
) -> None:
    """An unsubscribed queue should not receive further notifications."""
    subscriber_queue = broadcaster.subscribe()
    broadcaster.unsubscribe(subscriber_queue)

    entity = Entity(name="Unsubscribed Entity", description="Should not arrive")
    db_session.add(entity)
    db_session.commit()

    get_notification = partial(subscriber_queue.get, timeout=2.0)
    with pytest.raises(queue.Empty):
        await asyncio.to_thread(get_notification)


def _request_with_disconnect_checks(max_connected_checks: int) -> MagicMock:
    """Build a request mock that reports connected for a fixed number of checks."""
    request = MagicMock()
    disconnect_checks = 0

    async def is_disconnected() -> bool:
        nonlocal disconnect_checks
        await asyncio.sleep(0)
        disconnect_checks += 1
        return disconnect_checks > max_connected_checks

    request.is_disconnected = is_disconnected
    return request


async def test__notifications_yields_insert_trigger_payload(
    broadcaster: EntityNotificationBroadcaster,
    db_session: Session,
    db_settings: Settings,
) -> None:
    """notifications() generator should yield payloads from INSERT events."""
    request = _request_with_disconnect_checks(max_connected_checks=1)

    listener = notifications(broadcaster, request, db_settings)
    stream = listener()
    next_insert_notification = asyncio.create_task(anext(stream))
    await asyncio.sleep(0)  # allow task to start and call subscribe() before the commit fires

    entity = Entity(name="Entity", description="Trigger INSERT")
    db_session.add(entity)
    db_session.commit()
    db_session.refresh(entity)

    notification = await next_insert_notification

    expected = Envelope[Entity](
        guid=entity.guid,
        op="INSERT",
        value=entity,
    ).model_copy(update={"timestamp": ANY})

    assert notification == expected


async def test__notifications_yields_update_trigger_payload(
    broadcaster: EntityNotificationBroadcaster,
    db_session: Session,
    db_settings: Settings,
) -> None:
    """notifications() generator should yield payloads from UPDATE events."""
    request = _request_with_disconnect_checks(max_connected_checks=2)

    listener = notifications(broadcaster, request, db_settings)
    entity = Entity(name="Entity", description="Trigger UPDATE")

    stream = listener()
    next_insert_notification = asyncio.create_task(anext(stream))
    await asyncio.sleep(0)  # allow task to start and call subscribe() before the commit fires

    db_session.add(entity)
    db_session.commit()
    db_session.refresh(entity)

    insert_notification = await next_insert_notification

    expected_insert = Envelope[Entity](
        guid=entity.guid,
        op="INSERT",
        value=entity,
    ).model_copy(update={"timestamp": ANY})

    assert insert_notification == expected_insert

    next_update_notification = asyncio.create_task(anext(stream))

    entity.name = "Entity Updated"
    db_session.add(entity)
    db_session.commit()
    db_session.refresh(entity)

    update_notification = await next_update_notification

    expected_update = Envelope[Entity](
        guid=entity.guid,
        op="UPDATE",
        value=entity,
    ).model_copy(update={"timestamp": ANY})

    assert update_notification == expected_update


async def test__notifications_yields_delete_trigger_payload(
    broadcaster: EntityNotificationBroadcaster,
    db_session: Session,
    db_settings: Settings,
) -> None:
    """notifications() generator should yield payloads from DELETE events."""
    request = _request_with_disconnect_checks(max_connected_checks=2)

    listener = notifications(broadcaster, request, db_settings)
    entity = Entity(name="Entity", description="Trigger DELETE")

    stream = listener()
    next_insert_notification = asyncio.create_task(anext(stream))
    await asyncio.sleep(0)  # allow task to start and call subscribe() before the commit fires

    db_session.add(entity)
    db_session.commit()
    db_session.refresh(entity)

    insert_notification = await next_insert_notification

    expected_insert = Envelope[Entity](
        guid=entity.guid,
        op="INSERT",
        value=entity,
    ).model_copy(update={"timestamp": ANY})

    assert insert_notification == expected_insert

    next_delete_notification = asyncio.create_task(anext(stream))

    db_session.delete(entity)
    db_session.commit()

    delete_notification = await next_delete_notification

    expected_delete = Envelope[Entity](
        guid=entity.guid,
        op="DELETE",
        value=None,
    ).model_copy(update={"timestamp": ANY})

    assert delete_notification == expected_delete


async def test__notifications_unsubscribes_on_disconnect(
    broadcaster: EntityNotificationBroadcaster,
    db_settings: Settings,
) -> None:
    """notifications() listener should unsubscribe from the broadcaster when the client disconnects."""
    request = MagicMock()
    request.is_disconnected = AsyncMock(return_value=True)

    listener = notifications(broadcaster, request, db_settings)

    async for _ in listener():
        pass  # drain immediately; client is "already disconnected"

    assert broadcaster.subscriber_count == 0


async def test__notifications_unsubscribes_on_cancelled_error(
    broadcaster: EntityNotificationBroadcaster,
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """notifications() listener should unsubscribe when cancelled while waiting for the next event."""
    request = MagicMock()
    request.is_disconnected = AsyncMock(return_value=False)

    async def cancelled_to_thread(_: object) -> object:
        raise asyncio.CancelledError

    listener = notifications(broadcaster, request, db_settings)
    stream = listener()
    unsubscribe_spy = MagicMock(wraps=broadcaster.unsubscribe)
    monkeypatch.setattr(asyncio, "to_thread", cancelled_to_thread)
    monkeypatch.setattr(broadcaster, "unsubscribe", unsubscribe_spy)

    with pytest.raises(asyncio.CancelledError):
        await anext(stream)

    assert unsubscribe_spy.call_count == 1
    assert broadcaster.subscriber_count == 0


def test__entity_notification_broadcaster_process_notification_ignores_invalid_payload(
    broadcaster: EntityNotificationBroadcaster,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_process_notification() should log and skip invalid JSON payloads."""
    subscriber_queue = broadcaster.subscribe()
    exception_spy = MagicMock()
    monkeypatch.setattr("aurelius_fastapi_example.providers.cdc.LOGGER.exception", exception_spy)

    invalid_notify: psycopg.Notify = cast(
        "psycopg.Notify",
        SimpleNamespace(payload="{not-json"),
    )
    broadcaster._process_notification(invalid_notify)  # noqa: SLF001

    with pytest.raises(queue.Empty):
        subscriber_queue.get_nowait()
    exception_spy.assert_called_once()


async def test__notifications_continues_after_queue_empty(
    broadcaster: EntityNotificationBroadcaster,
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """notifications() should continue listening after queue.Empty and still yield later events."""
    request = _request_with_disconnect_checks(max_connected_checks=2)
    expected_notification = Envelope[Entity](
        guid=UUID("00000000-0000-0000-0000-000000000001"),
        op="INSERT",
        timestamp=datetime.now(tz=UTC),
        value=Entity(
            guid=UUID("00000000-0000-0000-0000-000000000001"),
            name="Recovered entity",
            description="queue.Empty recovery",
        ),
    )
    call_count = 0

    async def queue_empty_once_then_return(_: object) -> Envelope[Entity]:  # NOSONAR(S7503)
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise queue.Empty
        return expected_notification

    listener = notifications(broadcaster, request, db_settings)
    stream = listener()
    monkeypatch.setattr(asyncio, "to_thread", queue_empty_once_then_return)

    yielded_notification = await anext(stream)

    assert yielded_notification == expected_notification
    assert call_count == 2
