import json
from pathlib import Path
from typing import TYPE_CHECKING, cast

import dotenv
import pytest
from aurelius_example import Entity
from aurelius_kafka import KafkaAdminClient, KafkaProducer
from aurelius_sdk.testing import capture_docker_compose_logs
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import SchemaRegistryClient, record_subject_name_strategy
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import Serializer, StringSerializer
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL, Engine, create_engine
from sqlmodel import Session, SQLModel
from testcontainers.compose import DockerCompose
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy

if TYPE_CHECKING:
    from collections.abc import Generator

    from pydantic import SecretStr


class Settings(BaseSettings):
    """Test configuration."""

    connect_topic_name: str
    kafka_port: int
    postgres_db: str
    postgres_password: SecretStr
    postgres_user: str

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
    """Set the environment variables."""
    dotenv.load_dotenv(dotenv.find_dotenv())


@pytest.fixture(scope="session")
def compose() -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    context = Path(__file__).parent.absolute()
    with DockerCompose(context=context, env_file=dotenv.find_dotenv()) as compose:
        yield compose.waiting_for(
            {
                "kafka-connect": HealthcheckWaitStrategy(),
            },
        )
        capture_docker_compose_logs(compose)


@pytest.fixture(scope="session", autouse=True)
def database(compose: DockerCompose, settings: Settings) -> Generator[Engine]:
    """Setup and teardown the database."""
    hostname, port = compose.get_service_host_and_port("postgres", 5432)

    if not (hostname and port):
        message = "PostgreSQL service not found in Docker Compose"
        raise ValueError(message)

    url = URL.create(
        drivername="postgresql",
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
def kafka_bootstrap_servers(compose: DockerCompose, settings: Settings) -> str:
    """Return the Kafka bootstrap servers."""
    hostname, port = compose.get_service_host_and_port("broker", settings.kafka_port)
    return f"{hostname}:{port}"


@pytest.fixture(scope="session")
def kafka_producer(kafka_bootstrap_servers: str) -> KafkaProducer:
    """Return a Kafka producer instance."""
    return KafkaProducer(
        producer=Producer(
            {
                "bootstrap.servers": kafka_bootstrap_servers,
            },
        ),
    )


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
    kafka_topic_name = settings.connect_topic_name

    kafka_topic = NewTopic(
        kafka_topic_name,
        num_partitions=1,
        replication_factor=1,
    )

    kafka_admin_client.create_topics(kafka_topic)

    return kafka_topic_name


@pytest.fixture(scope="session")
def key_serializer() -> Serializer:
    """Return the key serializer."""
    return StringSerializer()


@pytest.fixture(scope="session")
def schema_registry_client(compose: DockerCompose) -> SchemaRegistryClient:
    """Return a Schema Registry client instance."""
    hostname, port = compose.get_service_host_and_port("schema-registry", 8081)
    return SchemaRegistryClient({"url": f"http://{hostname}:{port}"})


@pytest.fixture(scope="session")
def value_schema() -> str:
    """Return the Avro schema for the value."""
    schema = Entity.avro_schema(namespace="aurelius_example.models")
    return json.dumps(schema)


@pytest.fixture(scope="session")
def value_serializer(schema_registry_client: SchemaRegistryClient, value_schema: str) -> Serializer:
    """Return the value serializer."""
    return AvroSerializer(
        conf={"subject.name.strategy": record_subject_name_strategy},  # type: ignore[arg-type]
        schema_registry_client=schema_registry_client,  # type: ignore[arg-type]
        schema_str=value_schema,  # type: ignore[arg-type]
    )
