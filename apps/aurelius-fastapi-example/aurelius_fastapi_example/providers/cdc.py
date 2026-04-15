import asyncio
import select
from collections.abc import AsyncGenerator, Callable, Generator
from typing import Annotated

import psycopg2
from aurelius_example.models import PG_NOTIFY_ENTITY_CHANNEL
from fastapi import Depends, Request

from aurelius_fastapi_example.globals import LOGGER

from .settings import Settings


def connection(settings: Settings) -> Generator[psycopg2.extensions.connection]:
    """Return a database connection instance."""
    LOGGER.debug("Setting up database connection for CDC")

    connection = psycopg2.connect(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_username,
        password=settings.database_password.get_secret_value(),
    )

    connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    try:
        yield connection
    finally:
        LOGGER.debug("Closing database connection for CDC")
        connection.close()


def cursor(
    db_connection: Annotated[psycopg2.extensions.connection, Depends(connection)],
) -> Generator[psycopg2.extensions.connection]:
    """Create a database cursor for listening to entity events and yield the database connection for polling."""
    LOGGER.debug("Creating a new CDC database cursor")

    cursor = db_connection.cursor()
    cursor.execute(f"LISTEN {PG_NOTIFY_ENTITY_CHANNEL};")

    try:
        yield db_connection
    finally:
        LOGGER.debug("Closing CDC database cursor")
        cursor.execute(f"UNLISTEN {PG_NOTIFY_ENTITY_CHANNEL};")
        cursor.close()


def epoll(
    db_connection: Annotated[psycopg2.extensions.connection, Depends(connection)],
) -> Generator[select.epoll]:
    """Create an epoll instance for listening to entity events."""
    LOGGER.debug("Creating a new CDC epoll instance")

    epoll = select.epoll()
    epoll.register(db_connection, select.EPOLLIN)

    try:
        yield epoll
    finally:
        LOGGER.debug("Closing CDC epoll instance")
        epoll.close()


def notifications(
    cursor: Annotated[psycopg2.extensions.connection, Depends(cursor)],
    epoll: Annotated[select.epoll, Depends(epoll)],
    request: Request,
    settings: Settings,
) -> Callable[[], AsyncGenerator[psycopg2.extensions.Notify]]:
    """Create a stream of PostgreSQL notifications for entity changes."""

    def poll() -> list[psycopg2.extensions.Notify]:
        """Poll for new PostgreSQL notifications and return them as a list."""
        epoll.poll(timeout=settings.cdc_epoll_timeout)
        cursor.poll()

        result = []

        while cursor.notifies:
            notification = cursor.notifies.pop(0)
            LOGGER.debug("Received PostgreSQL notification: %s", notification)
            result.append(notification)

        return result

    async def listener() -> AsyncGenerator[psycopg2.extensions.Notify]:
        """Poll for new notifications until the client disconnects."""
        while not (await request.is_disconnected()):
            for notification in await asyncio.to_thread(poll):
                yield notification

    return listener
