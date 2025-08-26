import json
from pathlib import Path
from typing import Generator

import dotenv
import pytest
from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient
from confluent_kafka.schema_registry import (
    SchemaRegistryClient,
    record_subject_name_strategy,
)
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import StringSerializer
from m4i_atlas_core import (
    ConfigStore,
    create_type_defs,
    data_dictionary_entity_types,
    data_dictionary_types_def,
    register_atlas_entity_types,
    m4i_types_def,
)
from m4i_data_dictionary_io.testing.models import Envelope
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from tenacity import (
    Retrying,
    stop_after_attempt,
    wait_exponential,
)
from testcontainers.compose import DockerCompose
from testcontainers.core.waiting_utils import wait_container_is_ready
import pytest_asyncio


class Settings(BaseSettings):
    atlas_username: str
    atlas_password: SecretStr
    cluster_id: str
    kafka_port: int

    model_config = SettingsConfigDict(
        env_file=dotenv.find_dotenv(),
        extra="ignore",
    )


@pytest.fixture(scope="session", autouse=True)
def _environment() -> None:
    """Fixture to set up the environment for the tests."""
    dotenv.load_dotenv(dotenv.find_dotenv())


@pytest.fixture(scope="session")
@wait_container_is_ready()  # type: ignore
def compose() -> Generator[DockerCompose, None, None]:
    with DockerCompose(
        Path(__file__).parent.absolute(),
        env_file=dotenv.find_dotenv(),
    ) as compose:
        yield compose


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()  # type: ignore[settings are loaded from the environment]


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _init_atlas(compose: DockerCompose, settings: Settings) -> None:
    """Fixture to initialize the Atlas configuration."""
    store = ConfigStore.get_instance()

    atlas_host = compose.get_service_host("atlas", 21000)
    atlas_port = compose.get_service_port("atlas", 21000)

    store.load(
        {
            "atlas.server.url": f"http://{atlas_host}:{atlas_port}/api/atlas",
            "atlas.credentials.username": settings.atlas_username,
            "atlas.credentials.password": settings.atlas_password.get_secret_value(),
        }
    )

    register_atlas_entity_types(data_dictionary_entity_types)

    # Wait for Atlas to be ready
    for attempt in Retrying(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    ):
        with attempt:
            await create_type_defs(data_dictionary_types_def)


@pytest.fixture(scope="session")
def kafka_bootstrap_servers(
    compose: DockerCompose,
    settings: Settings,
) -> str:
    """Fixture to get the Kafka bootstrap servers."""
    kafka_host = compose.get_service_host("broker", settings.kafka_port)
    kafka_port = compose.get_service_port("broker", settings.kafka_port)

    return f"{kafka_host}:{kafka_port}"


@pytest.fixture(scope="session")
def kafka_cluster_id(settings: Settings) -> str:
    """Fixture to get the Kafka cluster ID."""
    return settings.cluster_id


@pytest.fixture(scope="session")
def kafka_admin_client(kafka_bootstrap_servers: str) -> AdminClient:
    """Fixture to create a Kafka AdminClient."""
    return AdminClient(
        {
            "bootstrap.servers": kafka_bootstrap_servers,
        }
    )


@pytest.fixture(scope="session")
def kafka_consumer(kafka_bootstrap_servers: str) -> Consumer:
    """Fixture to create a Kafka Consumer."""
    return Consumer(
        {
            "bootstrap.servers": kafka_bootstrap_servers,
            "group.id": "test_group",
            "auto.offset.reset": "earliest",
        }
    )


@pytest.fixture(scope="session")
def kafka_producer(kafka_bootstrap_servers: str) -> Producer:
    """Fixture to create a Kafka Producer."""
    return Producer(
        {
            "bootstrap.servers": kafka_bootstrap_servers,
        }
    )


@pytest.fixture(scope="session")
def schema_registry_client(compose: DockerCompose) -> SchemaRegistryClient:
    """Fixture to create a SchemaRegistryClient."""
    schema_registry_host = compose.get_service_host("schema-registry", 8081)
    schema_registry_port = compose.get_service_port("schema-registry", 8081)

    schema_registry_client = SchemaRegistryClient(
        {"url": f"http://{schema_registry_host}:{schema_registry_port}"}
    )

    # Wait for the Schema Registry to be ready
    for attempt in Retrying(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    ):
        with attempt:
            schema_registry_client.get_subjects()

    return schema_registry_client


@pytest.fixture(scope="session")
def avro_serializer(schema_registry_client: SchemaRegistryClient) -> AvroSerializer:
    """Fixture to create an AvroSerializer."""
    return AvroSerializer(
        schema_registry_client=schema_registry_client,
        schema_str=json.dumps(Envelope.avro_schema()),
        conf={
            "subject.name.strategy": record_subject_name_strategy,
        },
    )


@pytest.fixture(scope="session")
def json_serializer(schema_registry_client: SchemaRegistryClient) -> JSONSerializer:
    """Fixture to create a JSONSerializer."""
    return JSONSerializer(
        schema_registry_client=schema_registry_client,
        schema_str=json.dumps(Envelope.model_json_schema()),
    )


@pytest.fixture(scope="session")
def string_serializer() -> StringSerializer:
    """Fixture to create a StringSerializer."""
    return StringSerializer()
