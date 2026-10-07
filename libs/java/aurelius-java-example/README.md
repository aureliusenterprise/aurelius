# aurelius-java-example

Java Avro codegen library: generates the `com.aureliusenterprise.example.Entity`
Java class from the Avro schemas in `schemas/avro/` so Java services can
produce/consume Avro records without hand-written model code.

Part of the optional **Kafka streaming slice** — remove this library together
with the rest of that slice.

## How it works

- The `generateAvro` task (`GenerateAvroJavaTask` from the
  `com.github.davidmc24.gradle.plugin.avro` plugin) reads `../../../schemas/avro`
  and writes Java sources into `src/main/java` — generated code is committed so
  IDEs and SonarQube see it.
- ⚠️ Never edit files under `src/main/java/com/aureliusenterprise/` by hand; change
  the `.avsc` schema (which mirrors `libs/python/aurelius-example`) and regenerate.
- Java 21 toolchain (provisioned via foojay-resolver); Avro runtime from the
  version catalog (`gradle/libs.versions.toml`).

## Consuming

`apps/aurelius-java-producer-example` depends on `:aurelius-java-example` and sets
the Avro `SERIALIZABLE_PACKAGES` config to `com.aureliusenterprise.example`.

## Commands

```bash
./gradlew :aurelius-java-example:generateAvro   # regenerate from schemas
./gradlew :aurelius-java-example:test           # JUnit 5
nx sonar aurelius-java-example                  # SonarQube analysis
```
