from datetime import UTC, datetime
from unittest.mock import ANY

import pytest
from aurelius_example.models import PG_NOTIFY_ENTITY_CHANNEL, Entity, EntityNotification
from sqlalchemy import Connection, Engine, text
from sqlmodel import Session
from tenacity import Retrying, stop_after_attempt, wait_fixed


def parse_entity_notification_payload(payload: str) -> EntityNotification:
    """Helper function to parse a JSON payload into an EntityNotification."""
    notification = EntityNotification.model_validate_json(payload)

    if notification.value is not None:
        # Re-parse the value field to ensure it's fully typed as an Entity model.
        notification.value = Entity.model_validate(notification.value.model_dump())

    return notification


def test__example_creates_database_schema(db_connection: Connection) -> None:
    """Test that the database schema is created successfully."""
    result = db_connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public';"))
    tables = {row[0] for row in result}
    assert Entity.__tablename__ in tables


def test__example_entity_trigger_exists(db_connection: Connection) -> None:
    """Test that the PostgreSQL trigger for the Entity table exists."""
    result = db_connection.execute(
        text(
            """
                SELECT tgname
                FROM pg_trigger
                WHERE tgname = 'entity_table_change';
                """,
        ),
    )
    triggers = {row[0] for row in result}
    assert "entity_table_change" in triggers


def test__example_notify_function_exists(db_connection: Connection) -> None:
    """Test that the PostgreSQL trigger function for the Entity table exists."""
    result = db_connection.execute(
        text(
            """
                SELECT proname
                FROM pg_proc
                WHERE proname = 'entity_notify_change';
                """,
        ),
    )
    functions = {row[0] for row in result}
    assert "entity_notify_change" in functions


def test__example_entity_trigger_fires_on_insert(db_connection: Connection, db_session: Session) -> None:
    """Test that the PostgreSQL trigger for the Entity table fires on insert operations."""
    # Insert a new entity to trigger the notification
    entity = Entity(
        name="Test Entity",
        description="This is a test entity.",
    )

    # Listen for notifications on the entity channel
    with db_connection.connection.connection.cursor() as cursor:
        cursor.execute(f"LISTEN {PG_NOTIFY_ENTITY_CHANNEL};")
        db_connection.connection.connection.commit()

        db_session.add(entity)
        db_session.commit()
        db_session.refresh(entity)

        # Wait for the notification to be received
        for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_fixed(1)):
            with attempt:
                db_connection.connection.connection.poll()

                notifications = [
                    parse_entity_notification_payload(notification.payload)
                    for notification in db_connection.connection.connection.notifies
                ]

                expected = EntityNotification(
                    guid=entity.guid,
                    op="INSERT",
                    schema_name="public",
                    table_name=str(Entity.__tablename__),
                    value=entity,
                ).model_copy(update={"timestamp": ANY})

                assert any(notification == expected for notification in notifications)


def test__example_entity_trigger_fires_on_update(
    db_connection: Connection,
    db_session: Session,
    entity: Entity,
) -> None:
    """Test that the PostgreSQL trigger for the Entity table fires on update operations."""
    # Listen for notifications on the entity channel
    with db_connection.connection.connection.cursor() as cursor:
        cursor.execute(f"LISTEN {PG_NOTIFY_ENTITY_CHANNEL};")
        db_connection.connection.connection.commit()

        # Update the entity to trigger the notification
        entity.name = "Updated Test Entity"
        entity.description = "This is an updated test entity."
        db_session.commit()
        db_session.refresh(entity)

        # Wait for the notification to be received
        for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_fixed(1)):
            with attempt:
                db_connection.connection.connection.poll()

                notifications = [
                    parse_entity_notification_payload(notification.payload)
                    for notification in db_connection.connection.connection.notifies
                ]

                expected = EntityNotification(
                    guid=entity.guid,
                    op="UPDATE",
                    schema_name="public",
                    table_name=str(Entity.__tablename__),
                    value=entity,
                ).model_copy(update={"timestamp": ANY})

                assert any(notification == expected for notification in notifications)


def test__example_entity_trigger_fires_on_delete(
    db_connection: Connection,
    db_session: Session,
    entity: Entity,
) -> None:
    """Test that the PostgreSQL trigger for the Entity table fires on delete operations."""
    # Listen for notifications on the entity channel
    with db_connection.connection.connection.cursor() as cursor:
        cursor.execute(f"LISTEN {PG_NOTIFY_ENTITY_CHANNEL};")
        db_connection.connection.connection.commit()

        # Delete the entity to trigger the notification
        db_session.delete(entity)
        db_session.commit()

        # Wait for the notification to be received
        for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_fixed(1)):
            with attempt:
                db_connection.connection.connection.poll()

                notifications = [
                    parse_entity_notification_payload(notification.payload)
                    for notification in db_connection.connection.connection.notifies
                ]

                expected = EntityNotification(
                    guid=entity.guid,
                    op="DELETE",
                    schema_name="public",
                    table_name=str(Entity.__tablename__),
                    value=None,
                ).model_copy(update={"timestamp": ANY})

                assert any(notification == expected for notification in notifications)


def test__example_entity_time_created_is_set(entity: Entity) -> None:
    """Test that the time_created field is automatically set when an entity is created."""
    assert entity.time_created is not None, "time_created should be set automatically"
    assert entity.time_modified is None, "time_modified should be None when the entity is first created"


def test__example_entity_time_modified_updates_on_change(
    db_session: Session,
    entity: Entity,
) -> None:
    """Test that the time_modified field is updated when an entity is modified."""
    entity.name = "Updated Test Entity"

    db_session.commit()
    db_session.refresh(entity)

    assert entity.time_modified is not None, "time_modified should be updated when the entity is modified"


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (
            Entity(time_created=datetime(2024, 1, 1, tzinfo=UTC)),
            Entity(time_created=datetime(2024, 1, 2, tzinfo=UTC)),
            True,
        ),
        (
            Entity(time_created=datetime(2024, 1, 2, tzinfo=UTC)),
            Entity(time_created=datetime(2024, 1, 1, tzinfo=UTC)),
            False,
        ),
        (
            Entity(time_created=datetime(2024, 1, 1, tzinfo=UTC)),
            Entity(time_created=datetime(2024, 1, 1, tzinfo=UTC)),
            False,
        ),
        (
            Entity(time_modified=datetime(2024, 1, 1, tzinfo=UTC)),
            Entity(time_modified=datetime(2024, 1, 2, tzinfo=UTC)),
            True,
        ),
        (
            Entity(time_modified=datetime(2024, 1, 2, tzinfo=UTC)),
            Entity(time_modified=datetime(2024, 1, 1, tzinfo=UTC)),
            False,
        ),
        (
            Entity(time_modified=datetime(2024, 1, 1, tzinfo=UTC)),
            Entity(time_modified=datetime(2024, 1, 1, tzinfo=UTC)),
            False,
        ),
        (
            Entity(time_created=datetime(2024, 1, 1, tzinfo=UTC), time_modified=datetime(2024, 1, 1, tzinfo=UTC)),
            Entity(time_created=datetime(2024, 1, 2, tzinfo=UTC), time_modified=datetime(2024, 1, 2, tzinfo=UTC)),
            True,
        ),
        (
            Entity(time_created=datetime(2024, 1, 2, tzinfo=UTC), time_modified=datetime(2024, 1, 2, tzinfo=UTC)),
            Entity(time_created=datetime(2024, 1, 1, tzinfo=UTC), time_modified=datetime(2024, 1, 1, tzinfo=UTC)),
            False,
        ),
        (
            Entity(time_created=datetime(2024, 1, 1, tzinfo=UTC), time_modified=datetime(2024, 1, 1, tzinfo=UTC)),
            Entity(time_created=datetime(2024, 1, 1, tzinfo=UTC), time_modified=datetime(2024, 1, 1, tzinfo=UTC)),
            False,
        ),
        (
            Entity(time_created=datetime(2024, 1, 1, tzinfo=UTC)),
            Entity(time_modified=datetime(2024, 1, 2, tzinfo=UTC)),
            True,
        ),
        (
            Entity(time_created=datetime(2024, 1, 2, tzinfo=UTC)),
            Entity(time_modified=datetime(2024, 1, 1, tzinfo=UTC)),
            False,
        ),
        (
            Entity(time_created=datetime(2024, 1, 1, tzinfo=UTC)),
            Entity(time_modified=datetime(2024, 1, 1, tzinfo=UTC)),
            False,
        ),
        (
            Entity(),
            Entity(time_created=datetime(2024, 1, 1, tzinfo=UTC)),
            True,
        ),
        (
            Entity(time_created=datetime(2024, 1, 1, tzinfo=UTC)),
            Entity(),
            False,
        ),
        (
            Entity(),
            Entity(),
            False,
        ),
    ],
    ids=[
        "created_1_before_2",
        "created_2_before_1",
        "created_1_equals_2",
        "modified_1_before_2",
        "modified_2_before_1",
        "modified_1_equals_2",
        "created_and_modified_1_before_2",
        "created_and_modified_2_before_1",
        "created_and_modified_1_equals_2",
        "created_1_before_modified_2",
        "created_2_before_modified_1",
        "created_1_equals_modified_1",
        "created_none_before_created_1",
        "created_1_before_created_none",
        "created_none_equals_created_none",
    ],
)
def test__example_entity_comparator(a: Entity, b: Entity, *, expected: bool) -> None:
    """Test the comparison operator for the Entity class."""
    assert (a < b) == expected


def test__example_entity_trigger_cleanup_on_drop(db_engine: Engine, db_connection: Connection) -> None:
    """Test that the PostgreSQL trigger and function are cleaned up when the Entity table is dropped."""
    # Verify the trigger and function exist
    result = db_connection.execute(
        text(
            """
                SELECT tgname
                FROM pg_trigger
                WHERE tgname = 'entity_table_change';
                """,
        ),
    )
    triggers = {row[0] for row in result}
    assert "entity_table_change" in triggers, "Trigger should exist before drop"

    result = db_connection.execute(
        text(
            """
                SELECT proname
                FROM pg_proc
                WHERE proname = 'entity_notify_change';
                """,
        ),
    )
    functions = {row[0] for row in result}
    assert "entity_notify_change" in functions, "Trigger function should exist before drop"

    # Drop the Entity table
    Entity.metadata.drop_all(db_engine)

    # Verify the trigger no longer exists
    result = db_connection.execute(
        text(
            """
                SELECT tgname
                FROM pg_trigger
                WHERE tgname = 'entity_table_change';
                """,
        ),
    )
    triggers = {row[0] for row in result}
    assert "entity_table_change" not in triggers, "Trigger should be removed after table drop"

    # Verify the function no longer exists
    result = db_connection.execute(
        text(
            """
                SELECT proname
                FROM pg_proc
                WHERE proname = 'entity_notify_change';
                """,
        ),
    )
    functions = {row[0] for row in result}
    assert "entity_notify_change" not in functions, "Trigger function should be removed after table drop"
