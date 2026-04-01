from collections.abc import Generator
from unittest.mock import Mock

import pytest
from aurelius_fastapi_example.app import create_app
from aurelius_fastapi_example.models import Settings
from aurelius_fastapi_example.providers import get_settings
from aurelius_fastapi_example.providers import session as db_session
from aurelius_fastapi_example.providers import user_info as auth_user_info
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import Engine, StaticPool, create_engine
from sqlmodel import Session, SQLModel


@pytest.fixture(scope="session")
def engine() -> Generator[Engine]:
    """Create a shared in-memory SQLite engine for the test session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def session(engine: Engine) -> Generator[Session]:
    """Provide a clean database session per test, rolling back after each one."""
    with Session(engine, expire_on_commit=False) as session:
        yield session
        session.rollback()


@pytest.fixture()
def mock_user() -> dict:
    """Return a minimal decoded JWT payload for use in tests."""
    return {"sub": "test-user-id", "preferred_username": "testuser"}


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Return a mock Settings instance for testing."""
    return Mock(spec=Settings, log_level="DEBUG", is_development=True)


@pytest.fixture(scope="session")
def app(settings: Settings) -> FastAPI:
    """Create a FastAPI app instance for testing."""
    return create_app(settings)


@pytest.fixture()
def unauthenticated_client(app: FastAPI, session: Session, settings: Settings) -> Generator[TestClient]:
    """Provide a TestClient that forces authentication failure with a 401 response."""

    def override_session() -> Session:
        return session

    def override_user_info() -> dict:
        raise HTTPException(status_code=401)

    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[db_session] = override_session
    app.dependency_overrides[auth_user_info] = override_user_info

    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def authenticated_client(app: FastAPI, mock_user: dict, session: Session, settings: Settings) -> Generator[TestClient]:
    """Provide a FastAPI TestClient with DB and auth overrides."""

    def override_session() -> Session:
        return session

    def override_user_info() -> dict:
        return mock_user

    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[db_session] = override_session
    app.dependency_overrides[auth_user_info] = override_user_info

    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client

    app.dependency_overrides.clear()
