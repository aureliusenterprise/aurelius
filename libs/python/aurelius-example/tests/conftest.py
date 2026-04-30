import secrets
from collections.abc import Generator

import psycopg
import pytest
from aurelius_example import Entity
from sqlalchemy import URL, Connection, Engine, create_engine
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
def db_url(db_container: PostgresContainer) -> URL:
    """Return a SQLAlchemy URL for connecting to the test PostgreSQL container."""
    return URL.create(
        drivername="postgresql+psycopg",
        username=db_container.username,
        password=db_container.password,
        host=db_container.get_container_host_ip(),
        port=db_container.get_exposed_port(5432),
        database=db_container.dbname,
    )


@pytest.fixture()
def db_engine(db_url: URL) -> Generator[Engine]:
    """Create the SQLModel schema in the test PostgreSQL database."""
    engine = create_engine(db_url)

    SQLModel.metadata.create_all(engine)

    yield engine

    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_connection(db_engine: Engine) -> Generator[Connection]:
    """Provide a database connection for each test."""
    with db_engine.connect() as connection:
        yield connection


@pytest.fixture()
def db_connection_cdc(db_url: URL, db_engine: Engine) -> Generator[psycopg.Connection]:
    """Provide a database connection for each test."""
    del db_engine

    connection = psycopg.connect(
        autocommit=True,
        host=db_url.host,
        port=db_url.port,
        dbname=db_url.database,
        user=db_url.username,
        password=db_url.password,
    )

    yield connection

    connection.close()


@pytest.fixture()
def db_session(db_engine: Engine) -> Generator[Session]:
    """Provide a clean SQLModel session for each test."""
    with Session(db_engine, expire_on_commit=False) as session:
        yield session

    with Session(db_engine) as cleanup_session:
        cleanup_session.exec(delete(Entity))
        cleanup_session.commit()


@pytest.fixture()
def entity(db_session: Session) -> Generator[Entity]:
    """Create and return a single test entity."""
    entity = Entity(name="Test Entity", description="A test entity")

    db_session.add(entity)
    db_session.commit()

    db_session.refresh(entity)

    yield entity

    db_session.delete(entity)
    db_session.commit()
