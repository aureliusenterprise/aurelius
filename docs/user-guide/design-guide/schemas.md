# Schemas

When exchanging events using Kafka, it is important to define a schema for the data that is being shared. A schema
describes the structure of the data and the types of fields that are present in each event.

??? QUESTION "Why use a schema?"

    Creating a schema for your data is important because it allows consumers to understand the structure of the data
    and write code that can process it correctly. Schemas also provide a way to enforce data quality and consistency
    across different systems.

## Schema Definition

A schema is a formal description of the structure of the data being published to Kafka. It defines the fields
present in each event, the data types of these fields, and any constraints or rules that apply to the data.

Schema definitions should be published in a machine-readable format and stored in a centralized location, such
as the [Schema Registry](#schema-registry), to ensure that all producers and consumers can access them.

Additionally, schemas are included in the data dictionary for each topic, allowing users to understand the data
structure and interpret it using the conceptual data model.

??? EXAMPLE "Schema Definition"

    Here is an example of a schema for a event that represents a user profile:

    === "Avro"

        ```json
        {
            "type": "record",
            "name": "UserProfile",
            "fields": [
                {"name": "userId", "type": "string"},
                {"name": "firstName", "type": "string"},
                {"name": "lastName", "type": "string"},
                {"name": "email", "type": "string"},
                {"name": "createdAt", "type": "long"}
            ]
        }
        ```

    === "JSON Schema"

        ```json
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "userId": {"type": "string"},
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "email": {"type": "string"},
                "createdAt": {"type": "integer"}
            },
            "required": ["userId", "firstName", "lastName", "email", "createdAt"]
        }
        ```

    === "Protobuf"

        ```protobuf
        syntax = "proto3";

        message UserProfile {
            string userId = 1;
            string firstName = 2;
            string lastName = 3;
            string email = 4;
            int64 createdAt = 5;
        }
        ```

    In this schema, the `UserProfile` event has five fields: `userId`, `firstName`, `lastName`, `email`, and `createdAt`.
    The `userId` field is a string, the `createdAt` field is a long integer, and the other fields are strings.

## Key and Value Schemas

When publishing data to Kafka, each message consists of a key and a value. Both the key and the value can have
their own schema definitions, which describe the structure of the data in each part of the message.

??? TIP "Use separate schemas for keys and values"

    It is a good practice to use separate schemas for the key and value of a message, even if they have the same
    structure. This allows you to evolve the schemas independently and provides more flexibility when processing
    the data.

## Schema Registry

The [Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html) can be used to manage
schemas for data that is published to Kafka. The Schema Registry stores schemas in a centralized location and
provides a REST API for registering, retrieving, and validating schemas.

!!! SUCCESS "Use the Schema Registry"

    The Schema Registry is the preferred way to manage schemas for data that is published to Kafka. By using the
    Schema Registry, you can ensure that all producers and consumers of the data use the same schema, which helps
    to prevent data compatibility issues.

## Schema Subjects

When defining schemas for your data, it is important to follow a consistent naming convention to ensure that
schemas are easy to understand and maintain. Schemas are typically organized into subjects, which represent
the schema for a specific type of data as it changes over time.

A subject is a logical grouping of schemas that are related to each other. For example, you might have a subject
for user profiles, which contains all the schemas related to user profile events.

## Schema Evolution

Schemas are not static and will evolve over time as new fields are added, existing fields are removed, or the
data types of fields are changed. The Schema Registry supports [schema evolution](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html),
which allows you to make changes to a schema without breaking compatibility with existing consumers.

### Compatibility Strategy

We recommend using a [full compatibility strategy](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html#full-compatibility)
when evolving schemas. This means that it should be possible for old data to be read with the new schema, and
for new data to be read with the last schema.

Using a full compatibility strategy ensures that producers are able to evolve their schemas while consumers
are given the option to upgrade at their own pace. This approach works well in a microservices architecture where
there are many producers and consumers that need to communicate with each other.

The Protobuf documentation provides some guidance on how to [evolve Protobuf schemas](https://protobuf.dev/getting-started/pythontutorial/#extending-a-protobuf).

??? EXAMPLE "Making fully compatible changes"

    Consider a schema that represents a user profile with the following fields:

    === "Avro"

        ```json
        {
            "type": "record",
            "name": "UserProfile",
            "fields": [
                {"name": "userId", "type": "string"},
                {"name": "firstName", "type": "string"},
                {"name": "lastName", "type": "string"},
                {"name": "email", "type": "string"},
                {"name": "createdAt", "type": "long"}
            ]
        }
        ```

    === "JSON Schema"

        ```json
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "userId": {"type": "string"},
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "email": {"type": "string"},
                "createdAt": {"type": "integer"}
            },
            "required": ["userId", "firstName", "lastName", "email", "createdAt"]
        }
        ```

    === "Protobuf"

        ```protobuf
        syntax = "proto3";

        message UserProfile {
            string userId = 1;
            string firstName = 2;
            string lastName = 3;
            string email = 4;
            int64 createdAt = 5;
        }
        ```

    If you want to add a new field to the schema, such as `phoneNumber`, you should do so without breaking compatibility
    with previous schema versions. The updated schema would look like this:

    === "Avro"

        ```json
        {
            "type": "record",
            "name": "UserProfile",
            "fields": [
                {"name": "userId", "type": "string"},
                {"name": "firstName", "type": "string"},
                {"name": "lastName", "type": "string"},
                {"name": "email", "type": "string"},
                {"name": "createdAt", "type": "long"},
                {"name": "phoneNumber", "type": ["null", "string"], "default": null}
            ]
        }
        ```

    === "JSON Schema"

        ```json
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "userId": {"type": "string"},
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "email": {"type": "string"},
                "createdAt": {"type": "integer"},
                "phoneNumber": {"type": ["null", "string"], "default": null}
            },
            "required": ["userId", "firstName", "lastName", "email", "createdAt"]
        }
        ```

    === "Protobuf"

        ```protobuf
        syntax = "proto3";

        message UserProfile {
            string userId = 1;
            string firstName = 2;
            string lastName = 3;
            string email = 4;
            int64 createdAt = 5;
            optional string phoneNumber = 6;
        }
        ```

    Consumers that use the old version of the schema will ignore the `phoneNumber` field when processing events that
    include it.

    Consumers that use the updated schema will be able to read the `phoneNumber` field in addition to the other fields.
    They will also be able to process events that do not include the `phoneNumber` field, since it has a default value of
    `null`.

### Breaking Changes

If you need to make a non-backwards-compatible change to a schema, this is considered a breaking change. A breaking
change requires you to create a new version of your topic with the updated schema. The old version of the topic
should be deprecated and a migration plan should be put in place to move consumers to the new version.

!!! INFO "Naming Conventions"

    When creating a new version of a topic with a breaking change, you should use a new version number in the topic
    name. See the [naming conventions](./kafka-topics.md#naming-conventions) for guidance on how to name topics with
    different versions.

??? EXAMPLE "Breaking Changes"

    Consider the same user profile schema as before, but this time you want to change the `createdAt` field from
    a `long` to a `timestamp`. This is a breaking change because existing consumers that expect the `createdAt`
    field to be a `long` will not be able to process events that include a `timestamp` value.

    To make this change, you would create a new version of the schema with the updated `createdAt` field:

    === "Avro"

        ```json
        {
            "type": "record",
            "name": "UserProfile",
            "fields": [
                {"name": "userId", "type": "string"},
                {"name": "firstName", "type": "string"},
                {"name": "lastName", "type": "string"},
                {"name": "email", "type": "string"},
                {"name": "createdAt", "type": {"type": "long", "logicalType": "timestamp-millis"}}
            ]
        }
        ```

    === "JSON Schema"

        ```json
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "userId": {"type": "string"},
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "email": {"type": "string"},
                "createdAt": {"type": "string", "format": "date-time"}
            },
            "required": ["userId", "firstName", "lastName", "email", "createdAt"]
        }
        ```

    === "Protobuf"

        ```protobuf
        syntax = "proto3";

        import "google/protobuf/timestamp.proto";

        message UserProfile {
            string userId = 1;
            string firstName = 2;
            string lastName = 3;
            string email = 4;
            google.protobuf.Timestamp createdAt = 5;
        }
        ```

    You would then create a new version of the topic with the updated schema and migrate consumers to the new version
    over time.

## Serialization

Data published to Kafka must be serialized into a binary format that can be transmitted over the network.

We recommend using a serialization format that is compatible with the Schema Registry, such as Protobuf or Avro.
Make sure that your schema is registered in the Schema Registry before publishing data to Kafka, so that consumers
can deserialize the data correctly.

## Deserialization

Consumers should be able to deserialize data using the schemas that are stored in the Schema Registry.

Since schemas are required to be backward-compatible, consumers can deserialize data using an older version of
the schema if necessary.

??? TIP "Always specify the schema version"

    It's a good practice to always specify the schema version when consuming data from a Kafka topic. This ensures that
    your application can process the data in a consistent way, even as the schema evolves over time.
