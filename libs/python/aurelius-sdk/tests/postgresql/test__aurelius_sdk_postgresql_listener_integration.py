import queue
import secrets
import threading
from collections.abc import Generator
from typing import TypedDict

import psycopg
import pytest
from aurelius_sdk.postgresql import PostgresListener
from testcontainers.postgres import PostgresContainer


class PostgresConnectKwargs(TypedDict):
    """Typed connection kwargs for psycopg.connect in integration tests."""

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
    """Return psycopg connect kwargs for the running test container."""
    return {
        "host": db_container.get_container_host_ip(),
        "port": int(db_container.get_exposed_port(5432)),
        "dbname": db_credentials["database_name"],
        "user": db_credentials["database_username"],
        "password": db_credentials["database_password"],
    }


def _connect(connect_kwargs: PostgresConnectKwargs) -> psycopg.Connection:
    """Create a psycopg connection from typed kwargs."""
    return psycopg.connect(
        autocommit=True,
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

    listener_connection = _connect(postgres_connect_kwargs)

    listener = PostgresListener(
        connection=listener_connection,
        channel=channel,
    )

    listener.start()

    notifications: queue.Queue[psycopg.Notify] = queue.Queue(maxsize=1)
    stop_event = threading.Event()

    def consume_one() -> None:
        for notification in listener:
            notifications.put_nowait(notification)
            break

        stop_event.set()

    consumer = threading.Thread(target=consume_one, daemon=True)
    consumer.start()

    try:
        sender_connection = _connect(postgres_connect_kwargs)
        try:
            sender_connection.execute("SELECT pg_notify(%s, %s);", (channel, payload))
        finally:
            sender_connection.close()

        notification = notifications.get(timeout=5.0)
        assert notification.channel == channel
        assert notification.payload == payload
    finally:
        stop_event.set()
        consumer.join(timeout=1.0)
        listener.stop()
        listener_connection.close()


def test__postgres_listener_stops_emitting_after_stop(
    postgres_connect_kwargs: PostgresConnectKwargs,
) -> None:
    """PostgresListener iterator should stop when the listener is stopped."""
    channel = "sdk_listener_unsubscribe"

    listener_connection = _connect(postgres_connect_kwargs)

    listener = PostgresListener(
        connection=listener_connection,
        channel=channel,
    )

    listener.start()
    listener.stop()

    try:
        with pytest.raises(RuntimeError, match="not running"):
            next(iter(listener))
    finally:
        listener.stop()
        listener_connection.close()
