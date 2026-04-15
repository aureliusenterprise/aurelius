from uuid import UUID, uuid4

from pydantic_avro.to_avro.base import AvroBase
from sqlalchemy import DDL, Connection, event
from sqlalchemy.schema import MetaData
from sqlmodel import Field, SQLModel


class Entity(AvroBase, SQLModel, table=True):
    """A model that represents an simple entity that can be serialized to Avro and stored in a SQL database."""

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


# The name of the PostgreSQL channel that will be used for notifications about changes to the Entity table.
PG_NOTIFY_ENTITY_CHANNEL = "entity"


# SQL statement to create a trigger that notifies a PostgreSQL channel on any insert, update, or delete operation on the
# Entity table. The trigger function uses the pg_notify function to send a notification with the guid of the affected
# row. For delete operations, the OLD row's guid is used, while for insert and update operations, the NEW row's guid is
# used. The trigger is set to execute after each row is modified in the Entity table.
PG_NOTIFY_ENTITY_TRIGGER_SQL = f"""
CREATE OR REPLACE FUNCTION entity_notify_change() RETURNS TRIGGER AS $$
  BEGIN
    -- For DELETE operations, use the OLD row's guid; for other operations, use the NEW row's guid
    PERFORM pg_notify(
      '{PG_NOTIFY_ENTITY_CHANNEL}'::text,
      CASE WHEN (TG_OP = 'DELETE') THEN OLD.guid::text ELSE NEW.guid::text END
    );

    -- For DELETE operations, return the old row to allow trigger access
    RETURN CASE WHEN (TG_OP = 'DELETE') THEN OLD ELSE NEW END;
  END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER entity_table_change
  AFTER INSERT OR UPDATE OR DELETE ON {Entity.__tablename__}
  FOR EACH ROW EXECUTE PROCEDURE entity_notify_change();
"""

PG_NOTIFY_ENTITY_TRIGGER = DDL(PG_NOTIFY_ENTITY_TRIGGER_SQL)


@event.listens_for(Entity.metadata, "after_create")
def after_create_entity(_: MetaData, connection: Connection, **__: dict) -> None:
    """Create the entity trigger after the Entity table is created."""
    # Only apply PostgreSQL-specific triggers on PostgreSQL databases
    if connection.dialect.name == "postgresql":
        connection.execute(PG_NOTIFY_ENTITY_TRIGGER)
