from collections.abc import Generator
from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import psycopg
import pytest
from aurelius_sdk.postgresql import PostgresListener


def test__postgres_listener_start_is_noop_when_already_started() -> None:
    """start() should no-op when already started."""
    connection = MagicMock()
    listener = PostgresListener(connection=cast("psycopg.Connection", connection), channel="test_channel")
    listener._notifies = cast("Generator[psycopg.Notify]", iter(()))  # noqa: SLF001

    listener.start()

    connection.execute.assert_not_called()


def test__postgres_listener_start_executes_listen_and_creates_generator() -> None:
    """start() should LISTEN and initialize the notifies generator."""
    fake_notifies = iter([])
    connection = MagicMock()
    connection.notifies = MagicMock(return_value=fake_notifies)
    listener = PostgresListener(connection=cast("psycopg.Connection", connection), channel="test_channel")

    listener.start()

    assert connection.execute.call_count == 1
    connection.notifies.assert_called_once()
    assert listener._notifies is fake_notifies  # noqa: SLF001


def test__postgres_listener_stop_unlistens_and_closes_generator() -> None:
    """stop() should UNLISTEN and close the generator."""
    connection = MagicMock()
    listener = PostgresListener(connection=cast("psycopg.Connection", connection), channel="test_channel")

    fake_generator = MagicMock()
    listener._notifies = cast("Generator[psycopg.Notify]", fake_generator)  # noqa: SLF001

    listener.stop()

    assert connection.execute.call_count == 1
    fake_generator.close.assert_called_once()
    assert listener._notifies is None  # noqa: SLF001


def test__postgres_listener_iter_yields_from_running_generator() -> None:
    """__iter__() should yield notifications from initialized generator."""
    notify = cast("psycopg.Notify", SimpleNamespace(channel="test", payload="hello"))

    connection = MagicMock()
    listener = PostgresListener(connection=cast("psycopg.Connection", connection), channel="test_channel")

    listener._notifies = cast("Generator[psycopg.Notify]", iter([notify]))  # noqa: SLF001

    yielded = next(iter(listener))

    assert yielded is notify


def test__postgres_listener_iter_raises_when_not_running() -> None:
    """__iter__() should fail fast when listener has not started."""
    connection = MagicMock()
    listener = PostgresListener(connection=cast("psycopg.Connection", connection), channel="test_channel")

    with pytest.raises(RuntimeError, match="not running"):
        next(iter(listener))
