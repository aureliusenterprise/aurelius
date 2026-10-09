import pytest
from aurelius_atlas_server.errors import INTERNAL_ERROR, AtlasError, ErrorCode


@pytest.mark.covers("aurelius_atlas_server.errors.ErrorCode.format", rules=["ERR-01"])
def test__format_fills_placeholders_like_message_format() -> None:
    """{0}, {1} are filled in order; placeholders without a parameter stay."""
    code = ErrorCode(400, "ATLAS-400-00-001", "{0} and {1} and {2}")

    assert code.format("a", "b") == "a and b and {2}"
    assert INTERNAL_ERROR.format("boom") == "Internal server error boom"


@pytest.mark.covers("aurelius_atlas_server.errors.AtlasError.body", rules=["ERR-01"])
def test__error_body_matches_atlas() -> None:
    """The body has errorCode and errorMessage, and errorCause only when there is a cause."""
    assert AtlasError(INTERNAL_ERROR, "x").body() == {
        "errorCode": "ATLAS-500-00-001",
        "errorMessage": "Internal server error x",
    }
    assert AtlasError(INTERNAL_ERROR, "x", cause="why").body()["errorCause"] == "why"
