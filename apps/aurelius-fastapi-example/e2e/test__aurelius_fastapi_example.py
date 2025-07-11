import http.client


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
