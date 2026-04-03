from fastapi import APIRouter, Response

HEALTH = APIRouter()


@HEALTH.get(
    "/ready",
    summary="Check API readiness",
    description="Check if the API is ready to receive requests.",
)
def ready() -> Response:
    """
    Check the readiness of the API.

    Returns:
        Response: A 200 OK response if the API is ready.
    """
    return Response(status_code=200)
