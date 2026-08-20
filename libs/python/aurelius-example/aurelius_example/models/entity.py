from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel
from pydantic_avro.to_avro.base import AvroBase
from sqlalchemy import DDL, Connection, event, types
from sqlalchemy.schema import MetaData
from sqlmodel import Field, SQLModel, func


class Entity(AvroBase, SQLModel, table=True):
    """A model that represents an simple entity that can be serialized to Avro and stored in a SQL database."""

    # Deletes may legitimately match 0 rows (e.g. idempotent test teardown or
    # CDC-triggered deletes where the row is already gone), so suppress the
    # "expected to delete N row(s); 0 were matched" warning.
    __mapper_args__ = {"confirm_deleted_rows": False}
    description: str | None = Field(
        default=None,
        description="A description of the entity",
        max_length=255,
    )

    guid: UUID = Field(
        default_factory=uuid4,
        description="The unique identifier for the entity",
        primary_key=True,
    )

    name: str | None = Field(
        default=None,
        description="The name of the entity",
        max_length=100,
    )

    time_created: datetime | None = Field(
        default=None,
        description="The timestamp when the entity was created with timezone info",
        sa_type=types.TIMESTAMP(timezone=True),  # type: ignore[timestamp with timezone is allowed]
        sa_column_kwargs={"server_default": func.now()},
    )

    time_modified: datetime | None = Field(
        default=None,
        description="The timestamp when the entity was last modified with timezone info",
        sa_type=types.TIMESTAMP(timezone=True),  # type: ignore[timestamp with timezone is allowed]
        sa_column_kwargs={"onupdate": func.now()},
    )

    def __lt__(self, other: Entity) -> bool:
        """Compare entities based on their latest change timestamp."""
        latest_change_self = self.time_modified or self.time_created or datetime.min.replace(tzinfo=UTC)
        latest_change_other = other.time_modified or other.time_created or datetime.min.replace(tzinfo=UTC)
        return latest_change_self < latest_change_other


class EntityNotification(BaseModel):
    """A model that represents the payload of a notification about changes to the Entity table."""

    guid: UUID = Field(
        description="The primary key of the affected row",
    )

    op: Literal["INSERT", "UPDATE", "DELETE"] = Field(
        description="The type of operation that triggered the notification",
    )

    schema_name: str = Field(
        description="The database schema where the change occurred",
    )

    table_name: str = Field(
        description="The database table where the change occurred",
    )

    timestamp: datetime = Field(
        description="The timestamp when the change occurred with timezone info",
        default_factory=lambda: datetime.now(tz=UTC),
    )

    value: Entity | None = Field(
        default=None,
        description="The current state of the affected row; null for DELETE operations",
    )


# The name of the PostgreSQL channel that will be used for notifications about changes to the Entity table.
PG_NOTIFY_ENTITY_CHANNEL = "entity"

# PostgreSQL trigger that notifies on Entity table changes (INSERT, UPDATE, DELETE).
# Sends pg_notify with the affected row's guid and state as JSON metadata.
# For DELETE operations, uses the OLD row's guid with NULL state; for others, uses NEW row with full state.
PG_NOTIFY_ENTITY_TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION entity_notify_change() RETURNS TRIGGER AS $$
DECLARE
    -- Build a JSON payload with CDC metadata for the notification.
    -- This makes the notification self-describing and eliminates the need
    -- for consumers to perform a separate SELECT query.
    _payload text;
BEGIN
    -- Construct the notification payload as a JSON string.
    _payload := jsonb_build_object(
        'guid', CASE WHEN (TG_OP = 'DELETE') THEN OLD.guid::text ELSE NEW.guid::text END,
        'op', TG_OP,
        'schema_name', TG_TABLE_SCHEMA,
        'table_name', TG_TABLE_NAME,
        'timestamp', to_jsonb(now()),
        'value', CASE
            WHEN (TG_OP = 'DELETE') THEN NULL
            ELSE to_jsonb(NEW)
        END
    )::text;

    -- Send pg_notify with the enriched payload, wrapped in EXCEPTION handling
    -- to prevent notification failures from rolling back the original DML operation.
    BEGIN
        PERFORM pg_notify('%(channel)s'::text, _payload);
    EXCEPTION
        WHEN OTHERS THEN
            -- Log the error but do not fail the original INSERT/UPDATE/DELETE operation.
            RAISE LOG
                'Failed to send pg_notify for %% on table %%.%%: SQLSTATE %%, message %%',
                TG_OP, TG_TABLE_SCHEMA, TG_TABLE_NAME, SQLSTATE, SQLERRM;
    END;

    -- For DELETE operations, return the old row to allow trigger access; for INSERT/UPDATE, return the new row.
    RETURN CASE WHEN (TG_OP = 'DELETE') THEN OLD ELSE NEW END;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER entity_table_change
    AFTER INSERT OR UPDATE OR DELETE ON %(schema)s.%(tablename)s
    FOR EACH ROW EXECUTE PROCEDURE entity_notify_change();
"""


@event.listens_for(Entity.metadata, "after_create")
def after_create_entity_table(metadata: MetaData, connection: Connection, **_: dict) -> None:
    """Create the entity trigger after the Entity table is created."""
    if connection.dialect.name != "postgresql":
        return

    context = {
        "channel": PG_NOTIFY_ENTITY_CHANNEL,
        "schema": metadata.schema or "public",
        "tablename": Entity.__tablename__,
    }

    connection.execute(DDL(PG_NOTIFY_ENTITY_TRIGGER_SQL, context))


PG_NOTIFY_ENTITY_TRIGGER_CLEANUP_SQL = """
DROP TRIGGER IF EXISTS entity_table_change ON %(schema)s.%(tablename)s;
DROP FUNCTION IF EXISTS entity_notify_change() CASCADE;
"""


@event.listens_for(Entity.metadata, "before_drop")
def before_drop_entity_table(metadata: MetaData, connection: Connection, **_: dict) -> None:
    """Clean up the entity trigger before the Entity table is dropped."""
    if connection.dialect.name != "postgresql":
        return

    context = {
        "schema": metadata.schema or "public",
        "tablename": Entity.__tablename__,
    }

    connection.execute(DDL(PG_NOTIFY_ENTITY_TRIGGER_CLEANUP_SQL, context))
