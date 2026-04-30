import secrets
from collections.abc import Generator

import pytest
from aurelius_example import Entity
from aurelius_fastapi_example.models import Settings
from pydantic import HttpUrl, SecretStr, TypeAdapter
from sqlalchemy import Engine, create_engine
from sqlmodel import Session, SQLModel, delete
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def db_credentials() -> dict[str, str]:
    """Return generated PostgreSQL credentials for the test container."""
    return {
        "database_name": "postgres",
        "database_username": "postgres",
        "database_password": secrets.token_urlsafe(16),
    }


@pytest.fixture(scope="session")
def db_container(db_credentials: dict[str, str]) -> Generator[PostgresContainer]:
    """Start a real PostgreSQL container for tests."""
    with PostgresContainer(
        "postgres:latest",
        username=db_credentials["database_username"],
        password=db_credentials["database_password"],
        dbname=db_credentials["database_name"],
    ) as container:
        yield container


@pytest.fixture(scope="session")
def db_settings(db_container: PostgresContainer, db_credentials: dict[str, str]) -> Settings:
    """Return application settings pointed at the test PostgreSQL container."""
    return Settings(
        auth_realm_name="test-realm",
        auth_server_url=TypeAdapter(HttpUrl).validate_python("http://localhost:8080"),
        database_host=db_container.get_container_host_ip(),
        database_name=db_credentials["database_name"],
        database_password=SecretStr(db_credentials["database_password"]),
        database_port=int(db_container.get_exposed_port(5432)),
        database_username=db_credentials["database_username"],
        environment="development",
    )


@pytest.fixture(scope="session")
def db_engine(db_settings: Settings) -> Generator[Engine]:
    """Create the SQLModel schema in the test PostgreSQL database."""
    engine = create_engine(db_settings.database_url)

    SQLModel.metadata.create_all(engine)

    yield engine

    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine: Engine) -> Generator[Session]:
    """Provide a clean SQLModel session for each test."""
    with Session(db_engine, expire_on_commit=False) as session:
        yield session

    with Session(db_engine) as cleanup_session:
        cleanup_session.exec(delete(Entity))
        cleanup_session.commit()
