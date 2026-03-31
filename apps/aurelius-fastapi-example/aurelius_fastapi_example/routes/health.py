from fastapi import APIRouter

HEALTH = APIRouter()


@HEALTH.get(
    "/ready",
    summary="Check API readiness",
    description="Check if the API is ready to receive requests.",
)
def ready() -> None:
    """
    Check the readiness of the API.

    Returns:
        None: A 200 OK response if the API is ready.
    """
