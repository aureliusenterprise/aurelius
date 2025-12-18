import http.client
import json
from collections.abc import Generator
from pathlib import Path

import dotenv
import pytest
from aurelius_example import Entity
from aurelius_kafka import KafkaAdminClient
from aurelius_sdk.testing import capture_docker_compose_logs
from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import (
    SchemaRegistryClient,
    record_subject_name_strategy,
)
from confluent_kafka.schema_registry.avro import AvroDeserializer, AvroSerializer
from confluent_kafka.serialization import StringDeserializer, StringSerializer
from pydantic_settings import BaseSettings, SettingsConfigDict
from testcontainers.compose import DockerCompose
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy


class Settings(BaseSettings):
    """Test configuration."""

    kafka_port: int
    kafka_topic_name: str

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


@pytest.fixture(scope="session", autouse=True)
def compose() -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    context = Path(__file__).parent.absolute()
    with DockerCompose(context=context, env_file=dotenv.find_dotenv()) as compose:
        yield compose.waiting_for(
            {
                "aurelius-aws-lambda-example": HealthcheckWaitStrategy(),
            },
        )


@pytest.fixture(scope="session", autouse=True)
def _capture_docker_compose_logs(compose: DockerCompose) -> Generator[None]:
    """Capture logs from the Docker Compose services."""
    yield
    capture_docker_compose_logs(compose)


@pytest.fixture(scope="session")
def kafka_bootstrap_servers(compose: DockerCompose, settings: Settings) -> str:
    """Return the Kafka bootstrap servers."""
    hostname, port = compose.get_service_host_and_port("broker", settings.kafka_port)
    return f"{hostname}:{port}"


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
def kafka_topic(kafka_admin_client: KafkaAdminClient, settings: Settings) -> str:
    """Create a Kafka topic and return its name."""
    kafka_topic_name = settings.kafka_topic_name

    kafka_topic = NewTopic(
        kafka_topic_name,
        num_partitions=1,
        replication_factor=1,
    )

    kafka_admin_client.create_topics(kafka_topic)

    return kafka_topic_name


@pytest.fixture(scope="session")
def schema_registry_client(compose: DockerCompose) -> SchemaRegistryClient:
    """Return a Schema Registry client instance."""
    hostname, port = compose.get_service_host_and_port("schema-registry", 8081)
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
    return json.dumps(Entity.avro_schema(namespace="aurelius_example.models"))


@pytest.fixture(scope="session")
def value_deserializer(schema_registry_client: SchemaRegistryClient, value_schema: str) -> AvroDeserializer:
    """Return an Avro deserializer."""
    return AvroDeserializer(
        schema_registry_client,  # type: ignore[arg-type]
        schema_str=value_schema,
        conf={"subject.name.strategy": record_subject_name_strategy},
    )


@pytest.fixture(scope="session")
def value_serializer(schema_registry_client: SchemaRegistryClient, value_schema: str) -> AvroSerializer:
    """Return an Avro serializer."""
    return AvroSerializer(
        schema_registry_client,  # type: ignore[arg-type]
        schema_str=value_schema,
        conf={"subject.name.strategy": record_subject_name_strategy},
    )


@pytest.fixture()
def connection(compose: DockerCompose) -> http.client.HTTPConnection:
    """Return an HTTP connection to the lambda service."""
    host, port = compose.get_service_host_and_port("aurelius-aws-lambda-example", 8080)

    if not (host and port):
        message = "Could not find the host and port for the lambda service."
        raise ValueError(message)

    return http.client.HTTPConnection(host, port)
