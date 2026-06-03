from flask import Blueprint, Response

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health() -> Response:
    """Health check endpoint."""
    return Response(None, status=200)
