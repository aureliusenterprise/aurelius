# aurelius-example

The shared `Entity` domain model (Avro + SQLModel). This file covers wiring
specific to this lib; workspace-wide rules live in the root `AGENTS.md` and the
Python lib recipe in `libs/python/AGENTS.md`.

## Layout

- `aurelius_example/` — `Entity` (AvroBase + SQLModel table),
  `EntityNotification`, `PG_NOTIFY_ENTITY_CHANNEL`
- `tests/test__*.py` — pytest suite

## ⚠️ Changing `Entity` ripples everywhere

`Entity` is the single domain model the whole workspace shares. After changing
it, update **all** of:

1. `schemas/avro/com/aureliusenterprise/example/Entity.avsc` — kept in sync by
   hand, then re-register the schema and bump the subject version used by
   producers/consumers.
2. Java codegen: `./gradlew :aurelius-java-example:generateAvro` (regenerates
   the Java `Entity` from the `.avsc`).
3. The Angular `Entity` type in `libs/angular/aurelius-data-access` (mirrored by
   hand).
4. The Postgres table (SQLModel side) — the FastAPI example creates it at
   startup in dev; drop/recreate the dev table after schema changes.
5. The JDBC sink connector mapping (`workers/connector.properties` transforms
   assume the current field set).

## Commands

```bash
uv run pytest libs/python/aurelius-example/tests
uv run pyright libs/python/aurelius-example
```

## Conventions

- Field additions must be optional or have server-side defaults so existing
  Avro records and Postgres rows stay valid.
- Keep the AvroBase and SQLModel halves on one class — that dual identity is
  the point of this lib.

## Removal

Part of the spine. Removing it means replacing the shared model in every place
listed above — effectively reworking the examples.
