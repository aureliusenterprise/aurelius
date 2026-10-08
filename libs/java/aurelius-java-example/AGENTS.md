# aurelius-java-example

Java Avro codegen library (`com.aureliusenterprise.example.Entity`). This file
covers wiring specific to this lib; workspace-wide rules live in the root
`AGENTS.md`.

## Layout

- `src/main/java/com/aureliusenterprise/example/` — **generated** Avro code,
  committed on purpose (IDEs and SonarQube need to see it)
- `build.gradle.kts` — Avro plugin config, `nx{}` metadata (sonar target),
  Java toolchain (version in `gradle/libs.versions.toml`)
- `sonar-project.properties` — SonarQube module config

## Wiring Checklist

- Source of truth is `schemas/avro/com/aureliusenterprise/example/Entity.avsc`,
  which mirrors `libs/python/aurelius-example` — change the schema, then
  regenerate; never hand-edit generated Java.
- `settings.gradle.kts` — `include("libs:java:aurelius-java-example")`.
- Dependencies come from the version catalog (`gradle/libs.versions.toml`).
- Consumed by `apps/aurelius-java-producer-example` via
  `project(":aurelius-java-example")`; that app sets Avro
  `SERIALIZABLE_PACKAGES=com.aureliusenterprise.example`.

## Commands

```bash
./gradlew :aurelius-java-example:generateAvro   # regenerate from schemas
./gradlew :aurelius-java-example:test           # JUnit 5
nx sonar aurelius-java-example                  # SonarQube analysis
```

## Conventions

- Regenerate and commit generated sources in the same change as the `.avsc`
  edit, and bump the Schema Registry subject version used by producers and
  consumers.
- There is no Nx `test` target — run tests through Gradle (see above).

## Removal

Part of the Kafka streaming slice. Removing it means removing the
`settings.gradle.kts` include, the `project(":aurelius-java-example")`
dependency in the Java producer, and its `mkdocs.yaml` entries — or removing the
whole slice per the root `AGENTS.md` module map.
