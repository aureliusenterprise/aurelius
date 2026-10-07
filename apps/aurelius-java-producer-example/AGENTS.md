# aurelius-java-producer-example

Example Java Kafka producer application. This file covers wiring specific to this
app; workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `src/main/java/com/aureliusenterprise/producer/` — `App` (main loop + shutdown
  hook), `EntityProducer` (KafkaProducer wrapper), `AppConfig` (env-backed record)
- `src/test/java/` — JUnit 5 + Mockito
- `e2e/` — pytest suite against a real broker (runs via `uv`, not Gradle)
- Build config lives in `build.gradle.kts` — including the Nx target metadata
  (`nx { ... }` blocks) that registers `e2e` and `sonar` with the Nx graph

## Configuration

- `.env` in this directory is loaded into the `run` task's process environment by a
  hand-rolled loader in `build.gradle.kts` (comments and quotes supported).
- Runtime keys: `KAFKA_TOPIC_NAME`, `KAFKA_BOOTSTRAP_SERVERS`,
  `SCHEMA_REGISTRY_URL`, `MESSAGE_INTERVAL_MILLIS`.

## Wiring Checklist

- `settings.gradle.kts` (root) — this module is `include`d there; renaming or
  moving it means updating that file.
- `build.gradle.kts` — `implementation(project(":aurelius-java-example"))` pulls
  in the generated Avro `Entity` class; Confluent artifacts need the
  `packages.confluent.io` repository.
- `gradle/libs.versions.toml` — add new dependencies to the version catalog, not
  inline.
- `Dockerfile` — the `e2e` target depends on `docker-build`; keep the image entry
  point in sync with `application.mainClass`.
- `nx { array("implicitDependencies", "aurelius-dev-kafka") }` — controls what
  `e2e`/`up` starts.

## Commands

```bash
nx run aurelius-java-producer-example:run       # produce messages (needs Kafka up)
./gradlew :aurelius-java-producer-example:test  # JUnit 5 + JaCoCo
nx e2e aurelius-java-producer-example           # pytest E2E
nx sonar aurelius-java-producer-example
```

## Conventions

- The `Entity` class is generated — change `schemas/avro/` (and the Python model in
  `libs/python/aurelius-example`), then regenerate via
  `./gradlew :aurelius-java-example:generateAvro`.
- Avro serializer config must stay: `SERIALIZABLE_PACKAGES=com.aureliusenterprise.example`,
  header schema-id, `RecordNameStrategy` — consumers depend on it.
- Keep `AppConfig` as the only place reading environment variables.

## Removal

Part of the optional Kafka streaming slice. Removing this app also removes (or
makes dead): `libs/java/aurelius-java-example`, its `settings.gradle.kts` include,
the slice row in the root `AGENTS.md` module map, and `mkdocs.yaml` nav entries.
