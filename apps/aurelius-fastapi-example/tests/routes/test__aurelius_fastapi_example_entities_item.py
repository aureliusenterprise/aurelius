from aurelius_example import Entity
from fastapi.testclient import TestClient
from sqlmodel import Session


def test__delete_entity(authenticated_client: TestClient, db_session: Session, entity: Entity) -> None:
    """Deleting an entity should remove it from the database."""
    response = authenticated_client.delete(f"/entities/{entity.guid}")

    assert response.status_code == 200

    stored = db_session.get(Entity, entity.guid)

    assert stored is None


def test__find_one_returns_410_for_missing_entity(authenticated_client: TestClient) -> None:
    """Requesting a non-existent entity should return 410 Gone."""
    response = authenticated_client.get("/entities/12345678-1234-5678-1234-567812345678")

    assert response.status_code == 410


def test__delete_returns_410_for_missing_entity(authenticated_client: TestClient) -> None:
    """Deleting a non-existent entity should return 410 Gone."""
    response = authenticated_client.delete("/entities/12345678-1234-5678-1234-567812345678")

    assert response.status_code == 410


def test__find_one_requires_authentication(unauthenticated_client: TestClient) -> None:
    """Find-one endpoint should return 401 when no bearer token is provided."""
    response = unauthenticated_client.get("/entities/12345678-1234-5678-1234-567812345678")

    assert response.status_code == 401


def test__delete_requires_authentication(unauthenticated_client: TestClient) -> None:
    """Delete endpoint should return 401 when no bearer token is provided."""
    response = unauthenticated_client.delete("/entities/12345678-1234-5678-1234-567812345678")

    assert response.status_code == 401
