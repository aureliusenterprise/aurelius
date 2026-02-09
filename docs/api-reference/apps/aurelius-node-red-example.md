# aurelius-kafka-connect-jdbc-sink-example

This is an example Node-RED application that demonstrates how to set up a simple Kafka producer.

The app produces a new message every 10 seconds. The content of the message is static with a randomly generated
`guid` field. The message is encoded using Avro and sent to a Kafka topic.

## Key Schema

Keys should be string representations of the entity's [`guid`][aurelius_example.models.Entity.guid] field.

## Value Schema

Values are Avro-encoded records that conform to the [`Entity`][aurelius_example.models.Entity] schema. The schema
is registered in the schema registry as `aurelius_example.models.Entity`.

## Deployment

Deploy using the provided Dockerfile. By default, the app listens on port `1880`.

## Configuration

The connector can be configured using the following environment variables:

| Name                      | Description                                                     |
| ------------------------- | --------------------------------------------------------------- |
| `KAFKA_BOOTSTRAP_SERVERS` | A comma-separated list of Kafka bootstrap servers.              |
| `KAFKA_TOPIC_NAME`        | The name of the Kafka topic to write to.                        |
| `SCHEMA_REGISTRY_URL`     | The URL of the schema registry.                                 |
| `SCHEMA_SUBJECT_NAME`     | The name of the schema subject to use for encoding messages.    |
| `SCHEMA_SUBJECT_VERSION`  | The version of the schema subject to use for encoding messages. |
