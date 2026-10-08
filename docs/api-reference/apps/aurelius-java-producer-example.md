# aurelius-java-producer-example

[![SonarQube Cloud](https://sonarcloud.io/images/project_badges/sonarcloud-light.svg)](https://sonarcloud.io/summary/new_code?id=aurelius-java-producer-example)

This is an example Java application that demonstrates how to set up a simple Kafka producer.

The app produces a new message every 10 seconds. The content of the message is static with a randomly generated
`guid` field. The message is encoded using Avro and sent to a Kafka topic.

## Key Schema

Keys should be string representations of the entity's [`guid`][aurelius_example.models.Entity.guid] field.

## Value Schema

Values are Avro-encoded records that conform to the [`Entity`][aurelius_example.models.Entity] schema. The schema
is registered in the schema registry as `com.aureliusenterprise.example.Entity`.

## Deployment

Deploy using the provided Dockerfile.

## Configuration

The connector can be configured using the following environment variables:

| Name                      | Description                                        |
| ------------------------- | -------------------------------------------------- |
| `KAFKA_BOOTSTRAP_SERVERS` | A comma-separated list of Kafka bootstrap servers. |
| `KAFKA_TOPIC_NAME`        | The name of the Kafka topic to write to.           |
| `SCHEMA_REGISTRY_URL`     | The URL of the schema registry.                    |
