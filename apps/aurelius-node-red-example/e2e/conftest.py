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
    record_subject_name_strategy,
)
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer
from pydantic_settings import BaseSettings, SettingsConfigDict
from testcontainers.compose import DockerCompose
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy, HttpWaitStrategy


class Settings(BaseSettings):
    """Test configuration."""

    schema_subject_name: str
    schema_subject_version: str

    model_config = SettingsConfigDict(
        env_file=dotenv.find_dotenv(),
        extra="ignore",
    )


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Return the test configuration."""
    return Settings()  # type: ignore[values are loaded from the environment]


@pytest.fixture(scope="session", autouse=True)
def _environment() -> None:
    """Load the environment variables from the .env file."""
    dotenv.load_dotenv(dotenv.find_dotenv())


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
    kafka_topic_name = "aurelius-node-red-example-e2e"

    kafka_topic = NewTopic(
        kafka_topic_name,
        num_partitions=1,
        replication_factor=1,
    )

    kafka_admin_client.create_topics(kafka_topic)

    yield kafka_topic_name

    kafka_admin_client.delete_topics(kafka_topic_name)


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
def value_schema() -> str:
    """Return the Avro schema as a string."""
    return json.dumps(Entity.avro_schema(namespace="com.aureliusenterprise.example"))


@pytest.fixture(scope="session")
def value_deserializer(schema_registry_client: SchemaRegistryClient, value_schema: str) -> AvroDeserializer:
    """Return an Avro deserializer."""
    return AvroDeserializer(
        schema_registry_client,  # type: ignore[arg-type]
        schema_str=value_schema,
        conf={"subject.name.strategy": record_subject_name_strategy},
    )


@pytest.fixture(scope="session")
def consumer(kafka_bootstrap_servers: str) -> Generator[Consumer]:
    """Return a Kafka consumer."""
    consumer = Consumer(
        {
            "bootstrap.servers": kafka_bootstrap_servers,
            "group.id": "test-group",
            "auto.offset.reset": "earliest",
        },
    )

    yield consumer

    consumer.close()


@pytest.fixture(scope="session", autouse=True)
def compose(kafka_topic: str) -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    os.environ["KAFKA_TOPIC_NAME"] = kafka_topic

    context = Path(__file__).parent.absolute()

    with DockerCompose(context=context, env_file=dotenv.find_dotenv()) as compose:
        port = compose.get_service_port("aurelius-node-red-example", 1880)

        if not port:
            message = "Failed to get the Node-RED service port from Docker Compose"
            raise RuntimeError(message)

        yield compose.waiting_for(
            {
                "aurelius-node-red-example": HttpWaitStrategy(port=port, path="/flows/state")
                .for_status_code(200)
                .with_body('{"state":"start"}'),
            },
        )
