import asyncio
from typing import cast

from aurelius_example import Entity
from aurelius_example.models import PG_NOTIFY_ENTITY_CHANNEL
from aurelius_fastapi_example.models import Settings
from aurelius_fastapi_example.providers import cdc
from fastapi import Request
from sqlmodel import Session


class DisconnectAfterFirstPoll:
    """Request stub that stays connected for one listener poll iteration."""

    def __init__(self) -> None:
        self.calls = 0

    async def is_disconnected(self) -> bool:
        """Return False on the first call and True on the second."""
        await asyncio.sleep(0)
        self.calls += 1
        return self.calls > 1


def test__connection_opens_autocommit_connection(db_settings: Settings) -> None:
    """Connection provider should return an open psycopg2 connection in autocommit mode."""
    connection_generator = cdc.connection(db_settings)
    db_connection = next(connection_generator)

    try:
        assert db_connection.closed == 0
        assert db_connection.autocommit is True

        with db_connection.cursor() as cursor:
            cursor.execute("SELECT 1")

            assert cursor.fetchone() == (1,)
    finally:
        connection_generator.close()

    assert db_connection.closed != 0


def test__cursor_listens_and_unlistens_to_entity_channel(db_settings: Settings) -> None:
    """Cursor provider should register and unregister the entity LISTEN channel."""
    connection_generator = cdc.connection(db_settings)
    db_connection = next(connection_generator)
    cursor_generator = cdc.cursor(db_connection)
    listened_connection = next(cursor_generator)

    try:
        with listened_connection.cursor() as inspection_cursor:
            inspection_cursor.execute("SELECT * FROM pg_listening_channels()")

            assert inspection_cursor.fetchall() == [(PG_NOTIFY_ENTITY_CHANNEL,)]
    finally:
        cursor_generator.close()

    with db_connection.cursor() as inspection_cursor:
        inspection_cursor.execute("SELECT * FROM pg_listening_channels()")

        assert inspection_cursor.fetchall() == []

    connection_generator.close()


def test__epoll_receives_activity_when_entity_changes(db_settings: Settings, db_session: Session) -> None:
    """Epoll provider should become readable when PostgreSQL delivers an entity notification."""
    connection_generator = cdc.connection(db_settings)
    db_connection = next(connection_generator)
    cursor_generator = cdc.cursor(db_connection)
    next(cursor_generator)
    epoll_generator = cdc.epoll(db_connection)
    epoll = next(epoll_generator)

    try:
        entity = Entity(name="CDC Entity", description="Trigger epoll")
        db_session.add(entity)
        db_session.commit()

        events = epoll.poll(timeout=1.0)

        assert events
        assert any(file_descriptor == db_connection.fileno() for file_descriptor, _ in events)
    finally:
        epoll_generator.close()
        cursor_generator.close()
        connection_generator.close()


async def test__notifications_yields_insert_trigger_payload(
    db_settings: Settings,
    db_session: Session,
) -> None:
    """Notifications provider should yield the entity guid emitted by the insert trigger."""
    connection_generator = cdc.connection(db_settings)
    db_connection = next(connection_generator)
    cursor_generator = cdc.cursor(db_connection)
    listened_connection = next(cursor_generator)
    epoll_generator = cdc.epoll(db_connection)
    epoll = next(epoll_generator)
    request = DisconnectAfterFirstPoll()

    try:
        listener = cdc.notifications(listened_connection, epoll, cast("Request", request), db_settings)

        entity = Entity(name="Inserted Entity", description="Trigger notification")
        db_session.add(entity)
        db_session.commit()

        notification = await anext(listener())

        assert notification.guid == entity.guid
        assert notification.op == "INSERT"
    finally:
        epoll_generator.close()
        cursor_generator.close()
        connection_generator.close()


async def test__notifications_yields_delete_trigger_payload(
    db_settings: Settings,
    db_session: Session,
) -> None:
    """Notifications provider should yield the deleted entity guid emitted by the delete trigger."""
    entity = Entity(name="Deleted Entity", description="Delete notification")
    db_session.add(entity)
    db_session.commit()

    connection_generator = cdc.connection(db_settings)
    db_connection = next(connection_generator)
    cursor_generator = cdc.cursor(db_connection)
    listened_connection = next(cursor_generator)
    epoll_generator = cdc.epoll(db_connection)
    epoll = next(epoll_generator)
    request = DisconnectAfterFirstPoll()

    try:
        listener = cdc.notifications(listened_connection, epoll, cast("Request", request), db_settings)

        db_session.delete(entity)
        db_session.commit()

        notification = await anext(listener())

        assert notification.guid == entity.guid
        assert notification.op == "DELETE"
    finally:
        epoll_generator.close()
        cursor_generator.close()
        connection_generator.close()


async def test__notifications_yields_update_trigger_payload(
    db_settings: Settings,
    db_session: Session,
) -> None:
    """Notifications provider should yield the updated entity guid emitted by the update trigger."""
    entity = Entity(name="Updated Entity", description="Before update")
    db_session.add(entity)
    db_session.commit()

    connection_generator = cdc.connection(db_settings)
    db_connection = next(connection_generator)
    cursor_generator = cdc.cursor(db_connection)
    listened_connection = next(cursor_generator)
    epoll_generator = cdc.epoll(db_connection)
    epoll = next(epoll_generator)
    request = DisconnectAfterFirstPoll()

    try:
        listener = cdc.notifications(listened_connection, epoll, cast("Request", request), db_settings)

        entity.name = "Updated Entity Name"
        entity.description = "After update"
        db_session.add(entity)
        db_session.commit()

        notification = await anext(listener())

        assert notification.guid == entity.guid
        assert notification.op == "UPDATE"
    finally:
        epoll_generator.close()
        cursor_generator.close()
        connection_generator.close()
