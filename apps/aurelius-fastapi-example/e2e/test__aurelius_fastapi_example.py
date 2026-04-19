import http.client
import json
from unittest.mock import ANY

from aurelius_example import Entity
from aurelius_fastapi_example.models import Envelope, PaginatedResponse
from sqlmodel import Session
from tenacity import Retrying, stop_after_attempt, stop_after_delay, wait_fixed


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
    Test that the API has a readiness check endpoint.

    Asserts:
        - The API returns a 200 OK status code when the readiness check endpoint is requested.
    """
    connection.request(
        "GET",
        "/health/ready",
    )
    response = connection.getresponse()

    assert response.status == 200


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
        - The response contains data and total fields.
    """
    connection.request(
        "GET",
        "/entities/",
        headers={"Authorization": f"Bearer {token}"},
    )
    response = connection.getresponse()

    assert response.status == 200

    page = PaginatedResponse[Entity].model_validate(json.loads(response.read()))
    actual = [entity.model_dump(mode="json") for entity in page.data]
    expected = [entity.model_dump(mode="json") for entity in entities]

    assert actual == expected, "Not all entities were returned in the response"
    assert page.total == len(entities), "Total count does not match number of entities"


def test__aurelius_fastapi_example_find_many_search_query(
    connection: http.client.HTTPConnection,
    entities: list[Entity],
    token: str,
) -> None:
    """The list endpoint should filter results by search query."""
    connection.request(
        "GET",
        "/entities/?search=alpha",
        headers={"Authorization": f"Bearer {token}"},
    )
    response = connection.getresponse()

    assert response.status == 200

    page = PaginatedResponse[Entity].model_validate(json.loads(response.read()))
    actual = [entity.model_dump(mode="json") for entity in page.data]
    expected = [entities[0].model_dump(mode="json"), entities[1].model_dump(mode="json")]

    assert actual == expected, "The search query did not return the expected entities"
    assert page.total == 2, "Total count does not match number of expected entities"


def test__aurelius_fastapi_example_find_many_search_with_pagination(
    connection: http.client.HTTPConnection,
    entities: list[Entity],
    token: str,
) -> None:
    """Filtered total count should remain correct when pagination is applied."""
    connection.request(
        "GET",
        "/entities/?search=alpha&skip=1&limit=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    response = connection.getresponse()

    assert response.status == 200

    page = PaginatedResponse[Entity].model_validate(json.loads(response.read()))
    actual = [entity.model_dump(mode="json") for entity in page.data]
    expected = [entities[1].model_dump(mode="json")]

    assert actual == expected, "The search query did not return the expected entities"
    assert page.total == 2, "Total count does not match number of expected entities"


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
    expected = entity.model_copy(update={"time_created": data.time_created})
    assert data == expected, "The created entity does not match the expected entity"

    for attempt in Retrying(wait=wait_fixed(1), stop=stop_after_attempt(5)):
        with attempt:
            assert session.get(Entity, entity.guid) == expected, (
                "The entity was not found in the database after creation"
            )


def test__aurelius_fastapi_example_update(
    connection: http.client.HTTPConnection,
    entity: Entity,
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
    expected = entity.model_copy(update={"time_modified": ANY})

    assert data == expected, "The updated entity does not match the expected entity"

    for attempt in Retrying(wait=wait_fixed(1), stop=stop_after_attempt(5)):
        with attempt:
            actual = session.get(Entity, entity.guid)
            try:
                assert actual == expected, "The entity was not found in the database after update"
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
    entity: Entity,
    session: Session,
    token: str,
) -> None:
    """
    Test the delete endpoint of the Aurelius FastAPI example.

    Asserts:
        - The API returns a 200 OK status code.
        - The entity is deleted from the database.
    """
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


def test__aurelius_fastapi_example_sse_requires_auth(
    connection: http.client.HTTPConnection,
) -> None:
    """
    Test that the SSE endpoint requires authentication.

    Asserts:
        - The API returns a 401 Unauthorized status code when no token is provided.
    """
    connection.request(
        "GET",
        "/entities/sse",
    )

    response = connection.getresponse()

    assert response.status == 401, "Expected 401 Unauthorized status for unauthenticated request"


def read_notification(response: http.client.HTTPResponse) -> list[str]:
    """
    Helper function to read lines from an SSE stream.

    Yields:
        Lines of text from the SSE stream.
    """
    notification = []

    while (line := response.readline().decode().strip()) != "":
        notification.append(line)

    return notification


def parse_notification(notification: list[str]) -> dict[str, str]:
    """
    Helper function to parse an SSE notification into a dictionary.

    Args:
        notification: A list of lines from an SSE notification.

    Returns:
        A dictionary containing the event type and data from the notification.
    """
    event = {}

    for line in notification:
        if line.startswith("event:"):
            event["event"] = line[len("event:") :].strip()
        elif line.startswith("data:"):
            event["data"] = json.loads(line[len("data:") :].strip())

    return event


def test__aurelius_fastapi_example_sse_streams_changes(
    connection: http.client.HTTPConnection,
    session: Session,
    token: str,
) -> None:
    """
    Test that the SSE endpoint streams changes to entities.

    Asserts:
        - The API returns a 200 OK status code when the SSE endpoint is requested.
        - Changes to entities are streamed to the client.
    """
    connection.request(
        "GET",
        "/entities/sse",
        headers={"Authorization": f"Bearer {token}"},
    )

    response = connection.getresponse()

    assert response.status == 200

    # Insert a new entity to trigger the notification
    entity = Entity(
        name="SSE Test",
        description="This is a test entity for SSE streaming",
    )

    session.add(entity)
    session.commit()
    session.refresh(entity)

    expected = Envelope[Entity](
        guid=entity.guid,
        op="INSERT",
        value=entity,
    ).model_copy(update={"timestamp": ANY})

    # Wait for the notification to be received
    for attempt in Retrying(stop=stop_after_delay(90), wait=wait_fixed(1)):
        with attempt:
            notification = read_notification(response)

            event = parse_notification(notification)

            if not event:
                continue  # Ignore heartbeat lines

            assert event["event"] == "entity"

            actual = Envelope[Entity].model_validate_json(event["data"])
            assert actual == expected
