# aurelius-example

The shared `Entity` domain model used by every example in the template. One class
serves simultaneously as the Avro schema source and the SQLModel database table,
keeping the streaming and storage halves of the examples in lockstep.

Part of the template **spine**.

## What's inside

- `Entity` — an `AvroBase` + `SQLModel` (`table=True`) model: `guid` (UUID PK),
  `name`, `description`, and `time_created` / `time_modified`
  (`timestamptz`, server-side defaults)
- `EntityNotification` — the payload shape sent over Postgres `NOTIFY`
- `PG_NOTIFY_ENTITY_CHANNEL` — the channel name the FastAPI example listens on

## ⚠️ This class is load-bearing

`Entity` is the domain model the whole workspace shares, so changes ripple far:

- `schemas/avro/com/aureliusenterprise/example/Entity.avsc` must be kept in sync
  by hand (pydantic-avro defines the shape; nothing regenerates the file
  automatically). Java codegen (`aurelius-java-example`) generates the Java
  `Entity` class from that schema, and the Schema Registry subject and JDBC sink
  follow it.
- The Postgres table schema in the FastAPI example comes from the SQLModel side.
- The Angular `Entity` type in `aurelius-data-access` mirrors it by hand — update
  both when the model changes.

After changing the model, update the `.avsc` file, re-register the schema, and bump
the subject version used by producers and consumers.

## Testing

```bash
uv run pytest libs/python/aurelius-example/tests
```
