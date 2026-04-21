import asyncio
import queue
import select
import threading
from collections.abc import Callable
from functools import partial
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import aurelius_fastapi_example.providers.cdc as cdc_provider
import psycopg2
import pytest
from aurelius_example import Entity
from aurelius_fastapi_example.models import Settings
from aurelius_fastapi_example.providers import Broadcaster, get_broadcaster, notifications
from sqlmodel import Session

NOTIFICATION_PAYLOAD = '{"guid":"00000000-0000-0000-0000-000000000000","op":"INSERT"}'
CONNECT_ERROR = "boom"
JOIN_ERROR = "join failed"
UNLISTEN_ERROR = "unlisten failed"
CLOSE_ERROR = "close failed"
EPOLL_CLOSE_ERROR = "epoll close failed"
CONNECTION_CLOSE_ERROR = "connection close failed"
POLL_ERROR = "poll failed"


def _append_message(messages: list[str]) -> Callable[[str], None]:
    """Return a simple logger sink that appends each message to a list."""

    def append(message: str) -> None:
        messages.append(message)

    return append


def _fake_notify() -> psycopg2.extensions.Notify:
    """Create a minimal notify-like object for broadcast tests."""
    return cast("psycopg2.extensions.Notify", SimpleNamespace(payload=NOTIFICATION_PAYLOAD))


def test__broadcaster_starts_and_stops(db_settings: Settings) -> None:
    """Broadcaster should open a connection on start and close it on stop."""
    get_broadcaster.cache_clear()

    with get_broadcaster(settings=db_settings) as broadcaster:
        assert broadcaster.is_connected

    assert not broadcaster.is_connected


async def test__broadcaster_single_connection_serves_multiple_subscribers(
    broadcaster: Broadcaster,
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

    assert notify_a.payload == notify_b.payload


async def test__broadcaster_unsubscribe_removes_queue(
    broadcaster: Broadcaster,
    db_session: Session,
) -> None:
    """An unsubscribed queue should not receive further notifications."""
    subscriber_queue = broadcaster.subscribe()
    broadcaster.unsubscribe(subscriber_queue)

    entity = Entity(name="Unsubscribed Entity", description="Should not arrive")
    db_session.add(entity)
    db_session.commit()

    with pytest.raises(queue.Empty):
        await asyncio.to_thread(partial(subscriber_queue.get, timeout=2.0))


def test__broadcaster_start_is_noop_when_already_connected(db_settings: Settings) -> None:
    """start() should return immediately when the shared connection is already open."""
    broadcaster = Broadcaster(settings=db_settings)
    broadcaster._connection = cast("psycopg2.extensions.connection", SimpleNamespace(closed=0))  # noqa: SLF001

    broadcaster.start()

    assert broadcaster._thread is None  # noqa: SLF001


def test__broadcaster_start_cleans_up_on_initialisation_failure(
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """start() should set the stop flag and clean up partial resources when initialisation fails."""
    broadcaster = Broadcaster(settings=db_settings)
    cleanup_calls: list[str] = []

    def fake_cleanup_resources() -> None:
        cleanup_calls.append("cleanup")

    def fail_to_connect(**_: object) -> object:
        raise OSError(CONNECT_ERROR)

    monkeypatch.setattr(cdc_provider.psycopg2, "connect", fail_to_connect)
    monkeypatch.setattr(broadcaster, "_cleanup_resources", fake_cleanup_resources)

    with pytest.raises(OSError, match=CONNECT_ERROR):
        broadcaster.start()

    stop_event = cast("threading.Event", broadcaster._stop_event)  # noqa: SLF001
    assert stop_event.is_set()
    assert cleanup_calls == ["cleanup"]


def test__broadcaster_stop_is_noop_when_already_stopped(db_settings: Settings) -> None:
    """stop() should return immediately when no resources are open."""
    broadcaster = Broadcaster(settings=db_settings)

    broadcaster.stop()

    assert broadcaster._thread is None  # noqa: SLF001
    assert broadcaster._cursor is None  # noqa: SLF001
    assert broadcaster._epoll is None  # noqa: SLF001


def test__broadcaster_cleanup_resources_calls_all_cleanup_steps(
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_cleanup_resources() should run every best-effort cleanup helper."""
    broadcaster = Broadcaster(settings=db_settings)
    cleanup_calls: list[str] = []

    monkeypatch.setattr(broadcaster, "_close_epoll", lambda: cleanup_calls.append("epoll"))
    monkeypatch.setattr(broadcaster, "_join_thread", lambda: cleanup_calls.append("thread"))
    monkeypatch.setattr(broadcaster, "_close_cursor", lambda: cleanup_calls.append("cursor"))
    monkeypatch.setattr(broadcaster, "_close_connection", lambda: cleanup_calls.append("connection"))

    broadcaster._cleanup_resources()  # noqa: SLF001

    assert cleanup_calls == ["epoll", "thread", "cursor", "connection"]


def test__broadcaster_join_thread_logs_runtime_error(
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_join_thread() should swallow RuntimeError from join and clear the thread reference."""
    broadcaster = Broadcaster(settings=db_settings)

    class ThreadThatFailsOnJoin:
        def join(self, timeout: float) -> None:
            del timeout
            raise RuntimeError(JOIN_ERROR)

    broadcaster._thread = cast("threading.Thread", ThreadThatFailsOnJoin())  # noqa: SLF001
    exception_calls: list[str] = []
    monkeypatch.setattr(cdc_provider.LOGGER, "exception", _append_message(exception_calls))

    broadcaster._join_thread()  # noqa: SLF001

    assert broadcaster._thread is None  # noqa: SLF001
    assert exception_calls == ["Failed to join CDC broadcaster polling thread"]


def test__broadcaster_join_thread_warns_when_thread_remains_alive(
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_join_thread() should warn when the polling thread does not stop before timeout."""
    broadcaster = Broadcaster(settings=db_settings)

    class ThreadThatStaysAlive:
        def join(self, timeout: float) -> None:
            del timeout

        def is_alive(self) -> bool:
            return True

    broadcaster._thread = cast("threading.Thread", ThreadThatStaysAlive())  # noqa: SLF001
    warning_calls: list[str] = []
    monkeypatch.setattr(cdc_provider.LOGGER, "warning", _append_message(warning_calls))

    broadcaster._join_thread()  # noqa: SLF001

    assert broadcaster._thread is None  # noqa: SLF001
    assert warning_calls == ["CDC broadcaster polling thread did not stop before timeout"]


def test__broadcaster_close_cursor_handles_unlisten_and_close_errors(
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_close_cursor() should keep going when UNLISTEN or close fails."""
    broadcaster = Broadcaster(settings=db_settings)

    class CursorThatFails:
        def execute(self, command: str) -> None:
            del command
            raise psycopg2.OperationalError(UNLISTEN_ERROR)

        def close(self) -> None:
            raise psycopg2.OperationalError(CLOSE_ERROR)

    broadcaster._cursor = cast("psycopg2.extensions.cursor", CursorThatFails())  # noqa: SLF001
    exception_calls: list[str] = []
    monkeypatch.setattr(cdc_provider.LOGGER, "exception", _append_message(exception_calls))

    broadcaster._close_cursor()  # noqa: SLF001

    assert broadcaster._cursor is None  # noqa: SLF001
    assert exception_calls == [
        "Failed to UNLISTEN from PostgreSQL notification channel",
        "Failed to close CDC broadcaster cursor",
    ]


def test__broadcaster_close_epoll_handles_os_error(
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_close_epoll() should clear the epoll reference even when close raises."""
    broadcaster = Broadcaster(settings=db_settings)

    class EpollThatFails:
        def close(self) -> None:
            raise OSError(EPOLL_CLOSE_ERROR)

    broadcaster._epoll = cast("select.epoll", EpollThatFails())  # noqa: SLF001
    exception_calls: list[str] = []
    monkeypatch.setattr(cdc_provider.LOGGER, "exception", _append_message(exception_calls))

    broadcaster._close_epoll()  # noqa: SLF001

    assert broadcaster._epoll is None  # noqa: SLF001
    assert exception_calls == ["Failed to close CDC broadcaster epoll instance"]


def test__broadcaster_close_connection_handles_psycopg_error(
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_close_connection() should clear the connection reference even when close raises."""
    broadcaster = Broadcaster(settings=db_settings)

    class ConnectionThatFails:
        def close(self) -> None:
            raise psycopg2.OperationalError(CONNECTION_CLOSE_ERROR)

    broadcaster._connection = cast("psycopg2.extensions.connection", ConnectionThatFails())  # noqa: SLF001
    exception_calls: list[str] = []
    monkeypatch.setattr(cdc_provider.LOGGER, "exception", _append_message(exception_calls))

    broadcaster._close_connection()  # noqa: SLF001

    assert broadcaster._connection is None  # noqa: SLF001
    assert exception_calls == ["Failed to close CDC broadcaster database connection"]


def test__broadcaster_poll_loop_returns_without_initialisation(
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_poll_loop() should stop immediately when required resources are missing."""
    broadcaster = Broadcaster(settings=db_settings)
    error_calls: list[str] = []
    monkeypatch.setattr(cdc_provider.LOGGER, "error", _append_message(error_calls))

    broadcaster._poll_loop()  # noqa: SLF001

    assert error_calls == ["CDC broadcaster poll loop started without proper initialisation"]


def test__broadcaster_poll_loop_stops_on_epoll_error(
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_poll_loop() should exit when epoll.poll() raises."""
    broadcaster = Broadcaster(settings=db_settings)

    class EpollThatFails:
        def poll(self, timeout: float) -> list[tuple[int, int]]:
            del timeout
            raise OSError(POLL_ERROR)

    broadcaster._epoll = cast("select.epoll", EpollThatFails())  # noqa: SLF001
    broadcaster._connection = cast("psycopg2.extensions.connection", SimpleNamespace(notifies=[]))  # noqa: SLF001
    exception_calls: list[str] = []
    monkeypatch.setattr(cdc_provider.LOGGER, "exception", _append_message(exception_calls))

    broadcaster._poll_loop()  # noqa: SLF001

    assert exception_calls == ["epoll error in CDC broadcaster; stopping poll loop"]


def test__broadcaster_poll_loop_stops_on_connection_poll_error(
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_poll_loop() should exit when psycopg2 connection polling fails."""
    broadcaster = Broadcaster(settings=db_settings)

    class EpollWithEvent:
        def poll(self, timeout: float) -> list[tuple[int, int]]:
            del timeout
            return [(1, 1)]

    class ConnectionThatFails:
        def __init__(self) -> None:
            self.notifies: list[object] = []

        def poll(self) -> None:
            raise psycopg2.OperationalError(POLL_ERROR)

    broadcaster._epoll = cast("select.epoll", EpollWithEvent())  # noqa: SLF001
    broadcaster._connection = cast("psycopg2.extensions.connection", ConnectionThatFails())  # noqa: SLF001
    exception_calls: list[str] = []
    monkeypatch.setattr(cdc_provider.LOGGER, "exception", _append_message(exception_calls))

    broadcaster._poll_loop()  # noqa: SLF001

    assert exception_calls == ["psycopg2 poll error in CDC broadcaster; stopping poll loop"]


def test__broadcaster_broadcast_drops_event_when_queue_is_empty_after_full(db_settings: Settings) -> None:
    """_broadcast() should skip a subscriber when it is full and has nothing to evict."""
    broadcaster = Broadcaster(settings=db_settings)

    class QueueThatCannotAcceptOrEvict(queue.Queue[psycopg2.extensions.Notify]):
        def put_nowait(self, item: psycopg2.extensions.Notify) -> None:
            del item
            raise queue.Full

        def get_nowait(self) -> psycopg2.extensions.Notify:
            raise queue.Empty

    stuck_queue = QueueThatCannotAcceptOrEvict()
    subscribers = broadcaster._subscribers  # noqa: SLF001
    subscribers.add(stuck_queue)

    broadcaster._broadcast(_fake_notify())  # noqa: SLF001


def test__broadcaster_broadcast_warns_when_queue_stays_full_after_drop(
    db_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_broadcast() should warn when a slow subscriber stays full even after dropping the oldest event."""
    broadcaster = Broadcaster(settings=db_settings)

    class QueueThatStaysFull(queue.Queue[psycopg2.extensions.Notify]):
        def __init__(self) -> None:
            self.put_attempts = 0

        def put_nowait(self, item: psycopg2.extensions.Notify) -> None:
            del item
            self.put_attempts += 1
            raise queue.Full

        def get_nowait(self) -> psycopg2.extensions.Notify:
            return _fake_notify()

    stuck_queue = QueueThatStaysFull()
    subscribers = broadcaster._subscribers  # noqa: SLF001
    subscribers.add(stuck_queue)
    warning_calls: list[str] = []
    monkeypatch.setattr(cdc_provider.LOGGER, "warning", _append_message(warning_calls))

    broadcaster._broadcast(_fake_notify())  # noqa: SLF001

    assert stuck_queue.put_attempts == 2
    assert warning_calls == ["Dropping CDC event for slow subscriber; queue remains full"]


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
    broadcaster: Broadcaster,
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

    notification = await next_insert_notification

    assert notification.guid == entity.guid
    assert notification.op == "INSERT"


async def test__notifications_yields_update_trigger_payload(
    broadcaster: Broadcaster,
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

    insert_notification = await next_insert_notification
    assert insert_notification.guid == entity.guid
    assert insert_notification.op == "INSERT"

    next_update_notification = asyncio.create_task(anext(stream))

    entity.name = "Entity Updated"
    db_session.add(entity)
    db_session.commit()

    notification = await next_update_notification

    assert notification.guid == entity.guid
    assert notification.op == "UPDATE"


async def test__notifications_yields_delete_trigger_payload(
    broadcaster: Broadcaster,
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

    insert_notification = await next_insert_notification
    assert insert_notification.guid == entity.guid
    assert insert_notification.op == "INSERT"

    next_delete_notification = asyncio.create_task(anext(stream))

    db_session.delete(entity)
    db_session.commit()

    notification = await next_delete_notification

    assert notification.guid == entity.guid
    assert notification.op == "DELETE"


async def test__notifications_unsubscribes_on_disconnect(
    broadcaster: Broadcaster,
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
    broadcaster: Broadcaster,
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
    monkeypatch.setattr(cdc_provider.asyncio, "to_thread", cancelled_to_thread)
    monkeypatch.setattr(broadcaster, "unsubscribe", unsubscribe_spy)

    with pytest.raises(asyncio.CancelledError):
        await anext(stream)

    assert unsubscribe_spy.call_count == 1
    assert broadcaster.subscriber_count == 0
