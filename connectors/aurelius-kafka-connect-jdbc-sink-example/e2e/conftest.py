import json
import os
from collections.abc import Generator
from pathlib import Path
from typing import cast

import dotenv
import pytest
from aurelius_example import Entity
from aurelius_kafka import KafkaAdminClient
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic
from confluent_kafka.schema_registry import (
    SchemaRegistryClient,
    header_schema_id_serializer,
    prefix_schema_id_serializer,
    record_subject_name_strategy,
)
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import Serializer, StringSerializer
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL, Engine, create_engine
from sqlmodel import Session, SQLModel
from testcontainers.compose import DockerCompose
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy, HttpWaitStrategy


class Settings(BaseSettings):
    """Test configuration."""

    dlq_topic_name: str
    kafka_topic_name: str
    postgres_db: str
    postgres_password: SecretStr
    postgres_user: str

    model_config = SettingsConfigDict(
        env_file=dotenv.find_dotenv(),
        extra="ignore",
    )


@pytest.fixture(scope="session", autouse=True)
def _environment() -> None:
    """Set the environment variables."""
    dotenv.load_dotenv(dotenv.find_dotenv())


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Return the test configuration."""
    return Settings()  # type: ignore[values are loaded from the environment]


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
def postgres() -> DockerCompose:
    """
    Return a Docker Compose instance for the Postgres service.

    Note: This fixture starts the Postgres service if it's not already running, but does not stop it after the tests.
    This allows the service to be reused across multiple test sessions, but may require manual cleanup if the service is
    no longer needed.
    """
    context = Path(__file__).parents[3].absolute() / "dev" / "postgres"
    compose = DockerCompose(context=context)

    compose.start()

    return compose.waiting_for(
        {
            "postgres": HealthcheckWaitStrategy(),
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
def kafka_topic(kafka_admin_client: KafkaAdminClient, settings: Settings) -> Generator[str]:
    """Create the Kafka topic and return its name."""
    kafka_topic_name = settings.kafka_topic_name

    kafka_topic = NewTopic(
        kafka_topic_name,
        num_partitions=1,
        replication_factor=1,
    )

    kafka_admin_client.create_topics(kafka_topic)

    yield kafka_topic_name

    kafka_admin_client.delete_topics(kafka_topic_name)


@pytest.fixture(scope="session")
def dlq_topic(kafka_admin_client: KafkaAdminClient, settings: Settings) -> Generator[str]:
    """Create the Kafka topic and return its name."""
    kafka_topic_name = settings.dlq_topic_name

    kafka_topic = NewTopic(
        kafka_topic_name,
        num_partitions=1,
        replication_factor=1,
    )

    kafka_admin_client.create_topics(kafka_topic)

    yield kafka_topic_name

    kafka_admin_client.delete_topics(kafka_topic_name)


@pytest.fixture(scope="session")
def database(postgres: DockerCompose, settings: Settings) -> Generator[Engine]:
    """Setup and teardown the database."""
    hostname, port = postgres.get_service_host_and_port("postgres", 5432)

    if not (hostname and port):
        message = "PostgreSQL service not found in Docker Compose"
        raise ValueError(message)

    url = URL.create(
        drivername="postgresql+psycopg",
        username=settings.postgres_user,
        password=settings.postgres_password.get_secret_value(),
        host=hostname,
        port=cast("int", port),
        database=settings.postgres_db,
    )

    engine = create_engine(url)

    # Create the database schema
    SQLModel.metadata.create_all(engine)

    yield engine

    # Drop the database schema
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def session(database: Engine) -> Generator[Session]:
    """Return a SQLModel session."""
    with Session(database) as session:
        yield session


@pytest.fixture(scope="session")
def key_serializer() -> Serializer:
    """Return the key serializer."""
    return StringSerializer()


@pytest.fixture(scope="session")
def schema_registry_client(kafka: DockerCompose) -> SchemaRegistryClient:
    """Return a Schema Registry client instance."""
    hostname, port = kafka.get_service_host_and_port("schema-registry", 8081)
    return SchemaRegistryClient({"url": f"http://{hostname}:{port}"})


@pytest.fixture(scope="session")
def value_schema() -> str:
    """Return the Avro schema for the value."""
    schema = Entity.avro_schema(namespace="com.aureliusenterprise.example")
    return json.dumps(schema)


@pytest.fixture(scope="session")
def value_serializer_with_header_schema_id(
    schema_registry_client: SchemaRegistryClient,
    value_schema: str,
) -> Serializer:
    """Return a value serializer that uses the header schema ID serializer."""
    return AvroSerializer(
        conf={  # type: ignore[arg-type]
            "schema.id.serializer": header_schema_id_serializer,
            "subject.name.strategy": record_subject_name_strategy,
        },
        schema_registry_client=schema_registry_client,  # type: ignore[arg-type]
        schema_str=value_schema,  # type: ignore[arg-type]
    )


@pytest.fixture(scope="session")
def value_serializer_with_prefix_schema_id(
    schema_registry_client: SchemaRegistryClient,
    value_schema: str,
) -> Serializer:
    """Return a value serializer that uses the prefix schema ID serializer."""
    return AvroSerializer(
        conf={  # type: ignore[arg-type]
            "schema.id.serializer": prefix_schema_id_serializer,
            "subject.name.strategy": record_subject_name_strategy,
        },
        schema_registry_client=schema_registry_client,  # type: ignore[arg-type]
        schema_str=value_schema,  # type: ignore[arg-type]
    )


@pytest.fixture(scope="session")
def kafka_producer(kafka_bootstrap_servers: str) -> Producer:
    """Return a Kafka producer instance."""
    return Producer({"bootstrap.servers": kafka_bootstrap_servers})


@pytest.fixture(scope="session", autouse=True)
def compose(database: Engine, dlq_topic: str, kafka_topic: str) -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    _ = database  # Ensure the database is set up before starting Kafka Connect
    os.environ["DLQ_TOPIC_NAME"] = dlq_topic
    os.environ["KAFKA_TOPIC_NAME"] = kafka_topic

    context = Path(__file__).parents[1].absolute()

    with DockerCompose(context=context) as compose:
        port = compose.get_service_port("kafka-connect", 8083)

        if not port:
            message = "Kafka Connect service not found in Docker Compose"
            raise ValueError(message)

        yield compose.waiting_for(
            {
                "kafka-connect": HttpWaitStrategy(port=port, path="/connectors").for_status_code(200),
            },
        )
