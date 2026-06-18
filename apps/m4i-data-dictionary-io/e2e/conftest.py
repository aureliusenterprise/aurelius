import json
import subprocess
from pathlib import Path
from typing import Any, Generator, cast
import aiohttp
import dotenv
import pytest
import pytest_asyncio
import requests
from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient
from confluent_kafka.schema_registry import SchemaRegistryClient, record_subject_name_strategy
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import StringSerializer
from m4i_atlas_core import (
    ConfigStore,
    create_type_defs,
    data_dictionary_entity_type_mapping,
    data_dictionary_types_def,
    register_atlas_entity_types,
)
from m4i_data_dictionary_io.testing.models import Envelope
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from testcontainers.compose import DockerCompose
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy

AvroSerializerCtor = cast(Any, AvroSerializer)
JSONSerializerCtor = cast(Any, JSONSerializer)


class Settings(BaseSettings):
    """Settings for e2e tests, loaded from the .env file."""

    atlas_username: str
    atlas_password: SecretStr
    keycloak_realm_name: str

    model_config = SettingsConfigDict(env_file=dotenv.find_dotenv(), extra="ignore")


@pytest.fixture(scope="session", autouse=True)
def _environment() -> None:
    """Fixture to set up the environment for the tests."""
    dotenv.load_dotenv(dotenv.find_dotenv())


@pytest.fixture(scope="session")
def dev() -> DockerCompose:
    """
    Return a Docker Compose instance for the dev stack.

    Note: While this fixture spins up the dev stack, it does not tear it down. This is intentional, as the dev
    stack is expected to be long-running and shared across multiple test sessions.
    """
    context = Path(__file__).parents[3] / "dev"
    env_file = context / ".env"

    compose = DockerCompose(context, env_file=env_file.as_posix(), profiles=["atlas", "kafka", "keycloak"])

    try:
        compose.start()
    except subprocess.CalledProcessError as e:
        # The setup jobs for Keycloak and Elasticsearch exit after completing its one-time setup,
        # which causes docker compose to return a non-zero exit code.
        if b"setup-1 exited" not in e.stderr:
            raise

    return compose.waiting_for(
        {
            "atlas": HealthcheckWaitStrategy(),
            "broker": HealthcheckWaitStrategy(),
            "keycloak": HealthcheckWaitStrategy(),
            "schema-registry": HealthcheckWaitStrategy(),
        }
    )


@pytest.fixture(scope="session")
def compose() -> Generator[DockerCompose, None, None]:
    with DockerCompose(Path(__file__).parent.absolute(), env_file=dotenv.find_dotenv()) as compose:
        yield compose


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()  # type: ignore[settings are loaded from the environment]


@pytest.fixture(scope="session")
def keycloak_url(dev: DockerCompose) -> str:
    """Return the Keycloak base URL."""
    port = dev.get_service_port("keycloak", 8180)
    return f"http://keycloak.localhost:{port}"


@pytest.fixture(scope="session")
def auth_token(keycloak_url: str, settings: Settings) -> str:
    """Obtain a JWT Bearer token."""
    resp = requests.post(
        f"{keycloak_url}/realms/{settings.keycloak_realm_name}/protocol/openid-connect/token",
        data={
            "client_id": "m4i_atlas",
            "username": settings.atlas_username,
            "password": settings.atlas_password.get_secret_value(),
            "grant_type": "password",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _init_atlas(dev: DockerCompose, auth_token: str) -> None:
    """Fixture to initialize the Atlas configuration."""
    store = ConfigStore.get_instance()

    atlas_port = dev.get_service_port("atlas", 21000)

    store.load({"atlas.server.url": f"http://localhost:{atlas_port}/api/atlas"})

    register_atlas_entity_types(data_dictionary_entity_type_mapping)

    try:
        await create_type_defs(data_dictionary_types_def, access_token=auth_token)
    except aiohttp.ClientResponseError as e:
        if e.status != 409:  # 409 Conflict is expected if types are already registered
            raise


@pytest.fixture(scope="session")
def kafka_bootstrap_servers(dev: DockerCompose) -> str:
    """Fixture to get the Kafka bootstrap servers."""
    kafka_port = dev.get_service_port("broker", 9092)
    return f"localhost:{kafka_port}"


@pytest.fixture(scope="session")
def kafka_admin_client(kafka_bootstrap_servers: str) -> AdminClient:
    """Fixture to create a Kafka AdminClient."""
    return AdminClient({"bootstrap.servers": kafka_bootstrap_servers})


@pytest.fixture(scope="session")
def kafka_cluster_id(kafka_admin_client: AdminClient) -> str | None:
    """Fixture to get the Kafka cluster ID."""
    future = kafka_admin_client.describe_cluster()

    return cluster_metadata.cluster_id if (cluster_metadata := future.result()) else None


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
    return Producer({"bootstrap.servers": kafka_bootstrap_servers})


@pytest.fixture(scope="session")
def schema_registry_client(dev: DockerCompose) -> SchemaRegistryClient:
    """Fixture to create a SchemaRegistryClient."""
    schema_registry_port = dev.get_service_port("schema-registry", 8083)

    schema_registry_client = SchemaRegistryClient({"url": f"http://localhost:{schema_registry_port}"})

    return schema_registry_client


@pytest.fixture(scope="session")
def avro_serializer(schema_registry_client: SchemaRegistryClient) -> AvroSerializer:
    """Fixture to create an AvroSerializer."""
    return AvroSerializerCtor(
        schema_registry_client,
        json.dumps(Envelope.avro_schema()),
        None,
        {"subject.name.strategy": record_subject_name_strategy},
    )


@pytest.fixture(scope="session")
def json_serializer(schema_registry_client: SchemaRegistryClient) -> JSONSerializer:
    """Fixture to create a JSONSerializer."""
    return JSONSerializerCtor(json.dumps(Envelope.model_json_schema()), schema_registry_client, None)


@pytest.fixture(scope="session")
def string_serializer() -> StringSerializer:
    """Fixture to create a StringSerializer."""
    return StringSerializer()
