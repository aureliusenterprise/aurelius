import select
import threading
from dataclasses import dataclass
from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import psycopg2
import pytest
from aurelius_sdk.postgresql import PostgresListener

CONNECT_ERROR = "boom"
JOIN_ERROR = "join failed"
UNLISTEN_ERROR = "unlisten failed"
CLOSE_ERROR = "close failed"
EPOLL_CLOSE_ERROR = "epoll close failed"
POLL_ERROR = "poll failed"


@dataclass
class ListenerSettings:
    """Typed test settings for PostgresListener unit tests."""

    cdc_epoll_timeout: float = 0.1
    cdc_shutdown_join_timeout: float = 0.1


@pytest.fixture
def listener_settings() -> ListenerSettings:
    """Return minimal settings required by PostgresListener."""
    return ListenerSettings()


def test__postgres_listener_start_is_noop_when_already_started(listener_settings: ListenerSettings) -> None:
    """start() should no-op when listener internals indicate it is already started."""
    connection = cast("psycopg2.extensions.connection", MagicMock())
    listener = PostgresListener(connection=connection, channel="test_channel", settings=listener_settings)
    listener._thread = cast("threading.Thread", MagicMock())  # noqa: SLF001
    listener._cursor = cast("psycopg2.extensions.cursor", MagicMock())  # noqa: SLF001
    listener._epoll = cast("select.epoll", MagicMock())  # noqa: SLF001

    listener.start()

    assert listener._thread is not None  # noqa: SLF001


def test__postgres_listener_start_cleans_up_on_initialisation_failure(
    listener_settings: ListenerSettings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """start() should set the stop flag and run cleanup when initialization fails."""
    connection: object = MagicMock()

    def fail_to_get_cursor() -> object:
        raise OSError(CONNECT_ERROR)

    connection.cursor = fail_to_get_cursor

    listener = PostgresListener(
        connection=cast("psycopg2.extensions.connection", connection),
        channel="test_channel",
        settings=listener_settings,
    )
    cleanup_calls: list[str] = []

    def fake_cleanup_resources() -> None:
        cleanup_calls.append("cleanup")

    monkeypatch.setattr(listener, "_cleanup_resources", fake_cleanup_resources)

    with pytest.raises(OSError, match=CONNECT_ERROR):
        listener.start()

    stop_event = cast("threading.Event", listener._stop_event)  # noqa: SLF001
    assert stop_event.is_set()
    assert cleanup_calls == ["cleanup"]


def test__postgres_listener_stop_is_noop_when_already_stopped(listener_settings: ListenerSettings) -> None:
    """stop() should return safely when there are no resources to close."""
    connection = cast("psycopg2.extensions.connection", MagicMock())
    listener = PostgresListener(connection=connection, channel="test_channel", settings=listener_settings)

    listener.stop()

    assert listener._thread is None  # noqa: SLF001
    assert listener._cursor is None  # noqa: SLF001
    assert listener._epoll is None  # noqa: SLF001


def test__postgres_listener_cleanup_resources_calls_all_cleanup_steps(
    listener_settings: ListenerSettings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_cleanup_resources() should invoke all best-effort cleanup helpers."""
    connection = cast("psycopg2.extensions.connection", MagicMock())
    listener = PostgresListener(connection=connection, channel="test_channel", settings=listener_settings)
    cleanup_calls: list[str] = []

    monkeypatch.setattr(listener, "_close_epoll", lambda: cleanup_calls.append("epoll"))
    monkeypatch.setattr(listener, "_join_thread", lambda: cleanup_calls.append("thread"))
    monkeypatch.setattr(listener, "_close_cursor", lambda: cleanup_calls.append("cursor"))

    listener._cleanup_resources()  # noqa: SLF001

    assert cleanup_calls == ["epoll", "thread", "cursor"]


def test__postgres_listener_join_thread_logs_runtime_error(
    listener_settings: ListenerSettings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_join_thread() should swallow RuntimeError and clear thread reference."""
    connection = cast("psycopg2.extensions.connection", MagicMock())
    listener = PostgresListener(connection=connection, channel="test_channel", settings=listener_settings)

    class ThreadThatFailsOnJoin:
        def join(self, timeout: float) -> None:
            del timeout
            raise RuntimeError(JOIN_ERROR)

    listener._thread = cast("threading.Thread", ThreadThatFailsOnJoin())  # noqa: SLF001
    exception_spy = MagicMock()
    monkeypatch.setattr("aurelius_sdk.postgresql.listener.LOGGER.exception", exception_spy)

    listener._join_thread()  # noqa: SLF001

    assert listener._thread is None  # noqa: SLF001
    exception_spy.assert_called_once()


def test__postgres_listener_join_thread_warns_when_thread_remains_alive(
    listener_settings: ListenerSettings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_join_thread() should warn when the thread remains alive after join."""
    connection = cast("psycopg2.extensions.connection", MagicMock())
    listener = PostgresListener(connection=connection, channel="test_channel", settings=listener_settings)

    class ThreadThatStaysAlive:
        def join(self, timeout: float) -> None:
            del timeout

        def is_alive(self) -> bool:
            return True

    listener._thread = cast("threading.Thread", ThreadThatStaysAlive())  # noqa: SLF001
    warning_spy = MagicMock()
    monkeypatch.setattr("aurelius_sdk.postgresql.listener.LOGGER.warning", warning_spy)

    listener._join_thread()  # noqa: SLF001

    assert listener._thread is None  # noqa: SLF001
    warning_spy.assert_called_once()


def test__postgres_listener_close_cursor_handles_unlisten_and_close_errors(
    listener_settings: ListenerSettings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_close_cursor() should keep going when UNLISTEN and close both fail."""
    connection = cast("psycopg2.extensions.connection", MagicMock())
    listener = PostgresListener(connection=connection, channel="test_channel", settings=listener_settings)

    class CursorThatFails:
        def execute(self, command: str) -> None:
            del command
            raise psycopg2.OperationalError(UNLISTEN_ERROR)

        def close(self) -> None:
            raise psycopg2.OperationalError(CLOSE_ERROR)

    listener._cursor = cast("psycopg2.extensions.cursor", CursorThatFails())  # noqa: SLF001
    exception_spy = MagicMock()
    monkeypatch.setattr("aurelius_sdk.postgresql.listener.LOGGER.exception", exception_spy)

    listener._close_cursor()  # noqa: SLF001

    assert listener._cursor is None  # noqa: SLF001
    assert exception_spy.call_count == 2


def test__postgres_listener_close_epoll_handles_os_error(
    listener_settings: ListenerSettings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_close_epoll() should clear the epoll reference even when close fails."""
    connection = cast("psycopg2.extensions.connection", MagicMock())
    listener = PostgresListener(connection=connection, channel="test_channel", settings=listener_settings)

    class EpollThatFails:
        def close(self) -> None:
            raise OSError(EPOLL_CLOSE_ERROR)

    listener._epoll = cast("select.epoll", EpollThatFails())  # noqa: SLF001
    exception_spy = MagicMock()
    monkeypatch.setattr("aurelius_sdk.postgresql.listener.LOGGER.exception", exception_spy)

    listener._close_epoll()  # noqa: SLF001

    assert listener._epoll is None  # noqa: SLF001
    exception_spy.assert_called_once()


def test__postgres_listener_poll_loop_returns_without_initialisation(
    listener_settings: ListenerSettings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_poll_loop() should stop immediately when epoll/connection are missing."""
    connection = cast("psycopg2.extensions.connection", MagicMock())
    listener = PostgresListener(connection=connection, channel="test_channel", settings=listener_settings)
    error_spy = MagicMock()
    monkeypatch.setattr("aurelius_sdk.postgresql.listener.LOGGER.error", error_spy)

    listener._poll_loop()  # noqa: SLF001

    error_spy.assert_called_once()


def test__postgres_listener_poll_loop_stops_on_epoll_error(
    listener_settings: ListenerSettings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_poll_loop() should exit when epoll.poll raises."""
    connection = cast("psycopg2.extensions.connection", SimpleNamespace(notifies=[]))
    listener = PostgresListener(connection=connection, channel="test_channel", settings=listener_settings)

    class EpollThatFails:
        def poll(self, timeout: float) -> list[tuple[int, int]]:
            del timeout
            raise OSError(POLL_ERROR)

    listener._epoll = cast("select.epoll", EpollThatFails())  # noqa: SLF001
    exception_spy = MagicMock()
    monkeypatch.setattr("aurelius_sdk.postgresql.listener.LOGGER.exception", exception_spy)

    listener._poll_loop()  # noqa: SLF001

    exception_spy.assert_called_once()


def test__postgres_listener_poll_loop_stops_on_connection_poll_error(
    listener_settings: ListenerSettings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_poll_loop() should exit when connection.poll raises psycopg2 error."""

    class EpollWithEvent:
        def poll(self, timeout: float) -> list[tuple[int, int]]:
            del timeout
            return [(1, 1)]

    class ConnectionThatFails:
        def __init__(self) -> None:
            self.notifies: list[object] = []

        def poll(self) -> None:
            raise psycopg2.OperationalError(POLL_ERROR)

    connection = cast("psycopg2.extensions.connection", ConnectionThatFails())
    listener = PostgresListener(connection=connection, channel="test_channel", settings=listener_settings)
    listener._epoll = cast("select.epoll", EpollWithEvent())  # noqa: SLF001
    exception_spy = MagicMock()
    monkeypatch.setattr("aurelius_sdk.postgresql.listener.LOGGER.exception", exception_spy)

    listener._poll_loop()  # noqa: SLF001

    exception_spy.assert_called_once()
