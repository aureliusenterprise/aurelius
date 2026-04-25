import queue
import secrets
from collections.abc import Generator
from dataclasses import dataclass
from typing import TypedDict

import psycopg2
import pytest
from aurelius_sdk.postgresql import PostgresListener
from testcontainers.postgres import PostgresContainer


@dataclass
class ListenerTestSettings:
    """Settings consumed by PostgresListener in integration tests."""

    cdc_epoll_timeout: float = 0.1
    cdc_shutdown_join_timeout: float = 1.0


class PostgresConnectKwargs(TypedDict):
    """Typed connection kwargs for psycopg2.connect in integration tests."""

    host: str
    port: int
    dbname: str
    user: str
    password: str


@pytest.fixture(scope="session")
def db_credentials() -> dict[str, str]:
    """Return generated PostgreSQL credentials for the test container."""
    return {
        "database_name": "postgres",
        "database_username": "postgres",
        "database_password": secrets.token_urlsafe(16),
    }


@pytest.fixture(scope="session")
def db_container(db_credentials: dict[str, str]) -> Generator[PostgresContainer]:
    """Start a PostgreSQL container for SDK CDC integration tests."""
    with PostgresContainer(
        "postgres:latest",
        username=db_credentials["database_username"],
        password=db_credentials["database_password"],
        dbname=db_credentials["database_name"],
    ) as container:
        yield container


@pytest.fixture
def postgres_connect_kwargs(
    db_container: PostgresContainer,
    db_credentials: dict[str, str],
) -> PostgresConnectKwargs:
    """Return psycopg2 connect kwargs for the running test container."""
    return {
        "host": db_container.get_container_host_ip(),
        "port": int(db_container.get_exposed_port(5432)),
        "dbname": db_credentials["database_name"],
        "user": db_credentials["database_username"],
        "password": db_credentials["database_password"],
    }


def _connect(connect_kwargs: PostgresConnectKwargs) -> psycopg2.extensions.connection:
    """Create a psycopg2 connection from typed kwargs."""
    return psycopg2.connect(
        host=connect_kwargs["host"],
        port=connect_kwargs["port"],
        dbname=connect_kwargs["dbname"],
        user=connect_kwargs["user"],
        password=connect_kwargs["password"],
    )


def test__postgres_listener_receives_notify(
    postgres_connect_kwargs: PostgresConnectKwargs,
) -> None:
    """PostgresListener should receive notifications published on its configured channel."""
    channel = "sdk_listener_integration"
    payload = "hello-from-integration"
    settings = ListenerTestSettings()

    listener_connection = _connect(postgres_connect_kwargs)
    listener_connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    listener = PostgresListener(
        connection=listener_connection,
        channel=channel,
        settings=settings,
    )

    notifications: queue.Queue[psycopg2.extensions.Notify] = queue.Queue(maxsize=1)

    def on_notify(notification: psycopg2.extensions.Notify) -> None:
        notifications.put_nowait(notification)

    listener.subscribe(on_notify)
    listener.start()

    try:
        sender_connection = _connect(postgres_connect_kwargs)
        sender_connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            with sender_connection.cursor() as cursor:
                cursor.execute("SELECT pg_notify(%s, %s);", (channel, payload))
        finally:
            sender_connection.close()

        notification = notifications.get(timeout=5.0)
        assert notification.channel == channel
        assert notification.payload == payload
    finally:
        listener.stop()
        listener_connection.close()


def test__postgres_listener_does_not_emit_after_unsubscribe(
    postgres_connect_kwargs: PostgresConnectKwargs,
) -> None:
    """PostgresListener should not call a consumer after it has been unsubscribed."""
    channel = "sdk_listener_unsubscribe"
    payload = "should-not-arrive"
    settings = ListenerTestSettings()

    listener_connection = _connect(postgres_connect_kwargs)
    listener_connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    listener = PostgresListener(
        connection=listener_connection,
        channel=channel,
        settings=settings,
    )

    notifications: queue.Queue[psycopg2.extensions.Notify] = queue.Queue(maxsize=1)

    def on_notify(notification: psycopg2.extensions.Notify) -> None:
        notifications.put_nowait(notification)

    listener.subscribe(on_notify)
    listener.start()
    listener.unsubscribe(on_notify)

    try:
        sender_connection = _connect(postgres_connect_kwargs)
        sender_connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            with sender_connection.cursor() as cursor:
                cursor.execute("SELECT pg_notify(%s, %s);", (channel, payload))
        finally:
            sender_connection.close()

        with pytest.raises(queue.Empty):
            notifications.get(timeout=1.0)
    finally:
        listener.stop()
        listener_connection.close()
