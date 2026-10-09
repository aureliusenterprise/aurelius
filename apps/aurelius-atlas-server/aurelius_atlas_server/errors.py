"""Atlas error answers: ``{"errorCode": ..., "errorMessage": ...}`` (ADR 046).

Mirrors ``org.apache.atlas.AtlasErrorCode`` and ``AtlasBaseExceptionMapper``: every error
has an HTTP status, a stable code such as ``ATLAS-500-00-001`` and a message template whose
``{0}``, ``{1}``… are filled with parameters.
"""

import re
from dataclasses import dataclass

from fastapi import Request
from fastapi.responses import JSONResponse

_PLACEHOLDER = re.compile(r"\{(\d+)\}")


@dataclass(frozen=True)
class ErrorCode:
    """One Atlas error code.

    Attributes:
        http_status: The HTTP status of the answer.
        code: The Atlas error code, for example ``ATLAS-500-00-001``.
        template: The message, with ``{0}``-style placeholders.
    """

    http_status: int
    code: str
    template: str

    def format(self, *params: str) -> str:
        """Fill the message placeholders like Java's ``MessageFormat``.

        Placeholders without a parameter are left as they are.

        Args:
            params: The parameters, in placeholder order.

        Returns:
            The message.
        """
        return _PLACEHOLDER.sub(
            lambda m: params[int(m.group(1))] if int(m.group(1)) < len(params) else m.group(0), self.template
        )


INTERNAL_ERROR = ErrorCode(500, "ATLAS-500-00-001", "Internal server error {0}")


class AtlasError(Exception):
    """An error answered in Atlas's format.

    Args:
        error: The error code.
        params: Parameters for the message.
        cause: The message of the underlying cause, reported as ``errorCause``.
    """

    def __init__(self, error: ErrorCode, *params: str, cause: str | None = None) -> None:
        self.error = error
        self.message = error.format(*params)
        self.cause = cause
        super().__init__(self.message)

    def body(self) -> dict[str, str]:
        """Return the JSON body Atlas sends for this error.

        Returns:
            ``errorCode``, ``errorMessage`` and, when known, ``errorCause``.
        """
        body = {"errorCode": self.error.code, "errorMessage": self.message}
        if self.cause is not None:
            body["errorCause"] = self.cause
        return body


async def atlas_error_handler(_: Request, exc: Exception) -> JSONResponse:
    """Turn an :class:`AtlasError` into Atlas's JSON error answer.

    Args:
        _: The request (unused).
        exc: The error; must be an :class:`AtlasError`.

    Returns:
        The answer with the error's HTTP status.
    """
    if not isinstance(exc, AtlasError):  # pragma: no cover - registered for AtlasError only
        raise exc
    return JSONResponse(status_code=exc.error.http_status, content=exc.body())
