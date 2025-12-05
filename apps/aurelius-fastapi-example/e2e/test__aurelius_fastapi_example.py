import http.client
import json
from collections.abc import Generator

import pytest
from aurelius_example import Entity
from sqlmodel import Session
from tenacity import Retrying, stop_after_attempt, wait_fixed


def test__aurelius_fastapi_example_has_swagger_docs(connection: http.client.HTTPConnection) -> None:
    """
    Test that the API has Swagger documentation.

    Asserts:
        - The API returns a 200 OK status code when the Swagger documentation is requested.
    """
    connection.request(
        "GET",
        "/docs",
    )
    response = connection.getresponse()

    assert response.status == 200


def test__aurelius_fastapi_example_has_openapi_spec(connection: http.client.HTTPConnection) -> None:
    """
    Test that the API has an OpenAPI specification.

    Asserts:
        - The API returns a 200 OK status code when the OpenAPI specification is requested.
    """
    connection.request(
        "GET",
        "/openapi.json",
    )
    response = connection.getresponse()

    assert response.status == 200


def test__aurelius_fastapi_example_has_healthcheck(connection: http.client.HTTPConnection) -> None:
    """
    Test that the API has a healthcheck endpoint.

    Asserts:
        - The API returns a 200 OK status code when the healthcheck endpoint is requested.
    """
    connection.request(
        "GET",
        "/healthcheck",
    )
    response = connection.getresponse()

    assert response.status == 200


@pytest.fixture()
def entities(session: Session) -> Generator[list[Entity]]:
    """
    Fixture to create and return a list of entities for testing.

    Yields:
        A list of Entity instances.
    """
    entities = [Entity() for _ in range(3)]
    session.add_all(entities)
    session.commit()

    yield entities

    for entity in entities:
        session.delete(entity)

    session.commit()


def test__aurelius_fastapi_example_find_many(
    connection: http.client.HTTPConnection,
    entities: list[Entity],
    token: str,
) -> None:
    """
    Test the find_many endpoint of the Aurelius FastAPI example.

    Asserts:
        - The API returns a 200 OK status code.
        - All expected entities are returned in the response.
    """
    connection.request(
        "GET",
        "/entities/",
        headers={"Authorization": f"Bearer {token}"},
    )
    response = connection.getresponse()

    assert response.status == 200

    data = [Entity.model_validate(item) for item in json.loads(response.read())]

    assert all(entity in data for entity in entities), "Not all entities were returned in the response"


def test__aurelius_fastapi_example_find_many_requires_auth(
    connection: http.client.HTTPConnection,
) -> None:
    """
    Test that the find_many endpoint requires authentication.

    Asserts:
        - The API returns a 401 Unauthorized status code when no token is provided.
    """
    connection.request(
        "GET",
        "/entities/",
    )
    response = connection.getresponse()

    assert response.status == 401, "Expected 401 Unauthorized status for unauthenticated request"


def test__aurelius_fastapi_example_find_one(
    connection: http.client.HTTPConnection,
    session: Session,
    token: str,
) -> None:
    """
    Test the find_one endpoint of the Aurelius FastAPI example.

    Asserts:
        - The API returns a 200 OK status code.
        - The returned entity matches one of the created entities.
    """
    entity = Entity(name="Find One Test", description="This is a test entity")

    session.add(entity)
    session.commit()
    session.expunge(entity)

    connection.request(
        "GET",
        f"/entities/{entity.guid}",
        headers={"Authorization": f"Bearer {token}"},
    )

    response = connection.getresponse()

    assert response.status == 200

    data = Entity.model_validate(json.loads(response.read()))

    assert data == entity, "The returned entity does not match the expected entity"


def test__aurelius_fastapi_example_find_one_requires_auth(
    connection: http.client.HTTPConnection,
) -> None:
    """
    Test that the find_one endpoint requires authentication.

    Asserts:
        - The API returns a 401 Unauthorized status code when no token is provided.
    """
    entity_guid = "12345678-1234-5678-1234-567812345678"

    connection.request(
        "GET",
        f"/entities/{entity_guid}",
    )
    response = connection.getresponse()

    assert response.status == 401, "Expected 401 Unauthorized status for unauthenticated request"


def test__aurelius_fastapi_example_find_one_not_exists(
    connection: http.client.HTTPConnection,
    token: str,
) -> None:
    """
    Test the find_one endpoint of the Aurelius FastAPI example for a non-existing entity.

    Asserts:
        - The API returns a 410 Gone status code when the entity does not exist.
    """
    non_existing_guid = "12345678-1234-5678-1234-567812345678"

    connection.request(
        "GET",
        f"/entities/{non_existing_guid}",
        headers={"Authorization": f"Bearer {token}"},
    )

    response = connection.getresponse()

    assert response.status == 410, "Expected 410 Gone status for non-existing entity"


def test__aurelius_fastapi_example_create(
    connection: http.client.HTTPConnection,
    session: Session,
    token: str,
) -> None:
    """
    Test the create endpoint of the Aurelius FastAPI example.

    Asserts:
        - The API returns a 200 OK status code.
        - The created entity is returned in the response.
        - The entity is stored in the database.
    """
    entity = Entity(name="Create Test", description="This is a test entity")

    assert session.get(Entity, entity.guid) is None, "Entity already exists in the database"

    connection.request(
        "PUT",
        "/entities/",
        entity.model_dump_json(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )

    response = connection.getresponse()

    assert response.status == 200

    data = Entity.model_validate(json.loads(response.read()))

    assert data == entity, "The created entity does not match the expected entity"

    for attempt in Retrying(wait=wait_fixed(1), stop=stop_after_attempt(5)):
        with attempt:
            assert session.get(Entity, entity.guid) == entity, "The entity was not found in the database after creation"


def test__aurelius_fastapi_example_update(
    connection: http.client.HTTPConnection,
    session: Session,
    token: str,
) -> None:
    """
    Test the update endpoint of the Aurelius FastAPI example.

    Asserts:
        - The API returns a 200 OK status code.
        - The updated entity is returned in the response.
        - The entity is updated in the database.
    """
    entity = Entity(name="Update Test", description="This is a test entity")

    session.add(entity)
    session.commit()
    session.expunge(entity)

    entity.description = "This is an updated description"

    connection.request(
        "PUT",
        "/entities/",
        entity.model_dump_json(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )

    response = connection.getresponse()

    assert response.status == 200

    data = Entity.model_validate(json.loads(response.read()))

    assert data == entity, "The updated entity does not match the expected entity"

    for attempt in Retrying(wait=wait_fixed(1), stop=stop_after_attempt(5)):
        with attempt:
            actual = session.get(Entity, entity.guid)
            try:
                assert actual == entity, "The entity was not found in the database after update"
            except AssertionError:
                session.expunge(actual)
                raise


def test__aurelius_fastapi_example_put_requires_auth(
    connection: http.client.HTTPConnection,
) -> None:
    """
    Test that the update endpoint requires authentication.

    Asserts:
        - The API returns a 401 Unauthorized status code when no token is provided.
    """
    entity = Entity(name="Unauthenticated Test", description="This is a test entity")

    connection.request(
        "PUT",
        "/entities/",
        entity.model_dump_json(),
    )

    response = connection.getresponse()

    assert response.status == 401, "Expected 401 Unauthorized status for unauthenticated request"


def test__aurelius_fastapi_example_delete(
    connection: http.client.HTTPConnection,
    session: Session,
    token: str,
) -> None:
    """
    Test the delete endpoint of the Aurelius FastAPI example.

    Asserts:
        - The API returns a 200 OK status code.
        - The entity is deleted from the database.
    """
    entity = Entity(name="Delete Test", description="This is a test entity")

    session.add(entity)
    session.commit()
    session.expunge(entity)

    connection.request(
        "DELETE",
        f"/entities/{entity.guid}",
        headers={"Authorization": f"Bearer {token}"},
    )

    response = connection.getresponse()

    assert response.status == 200

    for attempt in Retrying(wait=wait_fixed(1), stop=stop_after_attempt(5)):
        with attempt:
            actual = session.get(Entity, entity.guid)
            try:
                assert actual is None, "The entity was not deleted from the database"
            except AssertionError:
                session.expunge(actual)
                raise


def test__aurelius_fastapi_example_delete_requires_auth(
    connection: http.client.HTTPConnection,
) -> None:
    """
    Test that the delete endpoint requires authentication.

    Asserts:
        - The API returns a 401 Unauthorized status code when no token is provided.
    """
    entity_guid = "12345678-1234-5678-1234-567812345678"

    connection.request(
        "DELETE",
        f"/entities/{entity_guid}",
    )

    response = connection.getresponse()

    assert response.status == 401, "Expected 401 Unauthorized status for unauthenticated request"


def test__aurelius_fastapi_example_delete_not_exists(
    connection: http.client.HTTPConnection,
    token: str,
) -> None:
    """
    Test the delete endpoint of the Aurelius FastAPI example for a non-existing entity.

    Asserts:
        - The API returns a 410 Gone status code when the entity does not exist.
    """
    non_existing_guid = "12345678-1234-5678-1234-567812345678"

    connection.request(
        "DELETE",
        f"/entities/{non_existing_guid}",
        headers={"Authorization": f"Bearer {token}"},
    )

    response = connection.getresponse()

    assert response.status == 410, "Expected 410 Gone status for non-existing entity"
