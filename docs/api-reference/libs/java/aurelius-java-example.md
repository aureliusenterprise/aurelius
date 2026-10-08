# aurelius-java-example

[![SonarQube Cloud](https://sonarcloud.io/images/project_badges/sonarcloud-light.svg)](https://sonarcloud.io/summary/new_code?id=aurelius-java-example)

This is a library that provides common utilities for Java example projects.

## API Documentation

Java is not covered by the generated API reference (mkdocstrings covers Python
only here). Generate the Javadoc for this library with:

```bash
./gradlew :aurelius-java-example:javadoc
```

The output is written to `libs/java/aurelius-java-example/build/docs/javadoc/`.

## Installation

You can include `aurelius-java-example` in your project by adding it to your `build.gradle.kts`:

```kotlin
dependencies {
    implementation(project(":aurelius-java-example"))
}
```

Ensure the path points to the correct location of the `aurelius-java-example` library.

## Documentation

The `com.aureliusenterprise.example` package provides automatically generated models based on the shared Avro
schemas. These models can be used in your Java projects to ensure type safety and consistency when working with
data that adheres to these schemas.

!!! INFO "Updating the Avro Schemas"

    If you need to update the Avro schemas, you can find them in the `schemas/avro` directory of the project.
    After making changes to the schemas, make sure to regenerate the Java models to reflect the updates.

    To regenerate the models, you can run the following command in the root directory of the project:

    ```bash
    nx run aurelius-java-example:generateAvro
    ```

    This command will use the Avro Maven plugin to generate Java classes from the Avro schemas defined in the
    `schemas/avro` directory. The generated classes will be placed in the `src/main/java` directory of the
    `aurelius-java-example` library.
