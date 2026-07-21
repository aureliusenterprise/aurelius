import http.client
import json
import os
from collections.abc import Generator
from pathlib import Path

import dotenv
import pytest
from aurelius_example import Entity
from aurelius_kafka import KafkaAdminClient
from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic
from confluent_kafka.schema_registry import (
    SchemaRegistryClient,
    header_schema_id_serializer,
    prefix_schema_id_serializer,
    record_subject_name_strategy,
)
from confluent_kafka.schema_registry.avro import AvroDeserializer, AvroSerializer
from confluent_kafka.serialization import StringDeserializer, StringSerializer
from testcontainers.compose import DockerCompose
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy

BASE_SERIALIZER_CONFIG = {
    "subject.name.strategy": record_subject_name_strategy,
}


@pytest.fixture(scope="session")
def kafka() -> DockerCompose:
    """
    Return a Docker Compose instance for the Kafka service.

    Note: This fixture starts the Kafka service if it's not already running, but does not stop it after the tests.
    This allows the service to be reused across multiple test sessions, but may require manual cleanup if the service is
    no longer needed.
    """
    context = Path(__file__).parents[3].absolute() / "dev" / "kafka"
    compose = DockerCompose(context=context)

    compose.start()

    return compose.waiting_for(
        {
            "broker": HealthcheckWaitStrategy(),
            "schema-registry": HealthcheckWaitStrategy(),
        },
    )


@pytest.fixture(scope="session")
def kafka_bootstrap_servers(kafka: DockerCompose) -> str:
    """Return the Kafka bootstrap servers."""
    hostname, port = kafka.get_service_host_and_port("broker", 9092)
    return f"{hostname}:{port}"


@pytest.fixture(scope="session")
def consumer(kafka_bootstrap_servers: str) -> Generator[Consumer]:
    """Return a Kafka consumer."""
    consumer = Consumer(
        {
            "bootstrap.servers": kafka_bootstrap_servers,
            "group.id": "aurelius-aws-lambda-example-e2e",
            "auto.offset.reset": "earliest",
        },
    )

    yield consumer

    consumer.close()


@pytest.fixture(scope="session")
def kafka_admin_client(kafka_bootstrap_servers: str) -> KafkaAdminClient:
    """Return a KafkaAdminClient instance."""
    return KafkaAdminClient(
        admin_client=AdminClient(
            {
                "bootstrap.servers": kafka_bootstrap_servers,
            },
        ),
    )


@pytest.fixture(scope="session")
def kafka_topic(kafka_admin_client: KafkaAdminClient) -> Generator[str]:
    """Create the Kafka topic and return its name."""
    kafka_topic_name = "aurelius-aws-lambda-example-e2e"

    kafka_topic = NewTopic(
        kafka_topic_name,
        num_partitions=1,
        replication_factor=1,
    )

    kafka_admin_client.create_topics(kafka_topic)

    yield kafka_topic_name

    kafka_admin_client.delete_topics(kafka_topic_name)


@pytest.fixture(scope="session")
def compose(kafka_topic: str) -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    os.environ["KAFKA_TOPIC_NAME"] = kafka_topic

    context = Path(__file__).parent.absolute()

    with DockerCompose(context=context, env_file=dotenv.find_dotenv()) as compose:
        yield compose.waiting_for(
            {
                "aurelius-aws-lambda-example": HealthcheckWaitStrategy(),
            },
        )


@pytest.fixture(scope="session")
def schema_registry_client(kafka: DockerCompose) -> SchemaRegistryClient:
    """Return a Schema Registry client instance."""
    hostname, port = kafka.get_service_host_and_port("schema-registry", 8081)
    return SchemaRegistryClient({"url": f"http://{hostname}:{port}"})


@pytest.fixture(scope="session")
def key_deserializer() -> StringDeserializer:
    """Return a string deserializer."""
    return StringDeserializer()


@pytest.fixture(scope="session")
def key_serializer() -> StringSerializer:
    """Return a string serializer."""
    return StringSerializer()


@pytest.fixture(scope="session")
def value_schema() -> str:
    """Return the Avro schema as a string."""
    return json.dumps(Entity.avro_schema(namespace="com.aureliusenterprise.example"))


@pytest.fixture(scope="session")
def value_deserializer(schema_registry_client: SchemaRegistryClient, value_schema: str) -> AvroDeserializer:
    """Return an Avro deserializer."""
    return AvroDeserializer(
        schema_registry_client,  # type: ignore[arg-type]
        schema_str=value_schema,
        conf=BASE_SERIALIZER_CONFIG,
    )


@pytest.fixture(scope="session")
def value_serializer_with_header_schema_id(
    schema_registry_client: SchemaRegistryClient,
    value_schema: str,
) -> AvroSerializer:
    """Return a value serializer that uses the header schema ID serializer."""
    return AvroSerializer(
        conf={  # type: ignore[arg-type]
            **BASE_SERIALIZER_CONFIG,
            "schema.id.serializer": header_schema_id_serializer,
        },
        schema_registry_client=schema_registry_client,  # type: ignore[arg-type]
        schema_str=value_schema,  # type: ignore[arg-type]
    )


@pytest.fixture(scope="session")
def value_serializer_with_prefix_schema_id(
    schema_registry_client: SchemaRegistryClient,
    value_schema: str,
) -> AvroSerializer:
    """Return a value serializer that uses the prefix schema ID serializer."""
    return AvroSerializer(
        conf={  # type: ignore[arg-type]
            **BASE_SERIALIZER_CONFIG,
            "schema.id.serializer": prefix_schema_id_serializer,
        },
        schema_registry_client=schema_registry_client,  # type: ignore[arg-type]
        schema_str=value_schema,  # type: ignore[arg-type]
    )


@pytest.fixture()
def connection(compose: DockerCompose) -> http.client.HTTPConnection:
    """Return an HTTP connection to the lambda service."""
    host, port = compose.get_service_host_and_port("aurelius-aws-lambda-example", 8080)

    if not (host and port):
        message = "Could not find the host and port for the lambda service."
        raise ValueError(message)

    return http.client.HTTPConnection(host, port)
