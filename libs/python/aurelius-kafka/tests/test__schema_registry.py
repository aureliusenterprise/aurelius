import pytest
from aurelius_kafka import build_schema_registry_header


@pytest.mark.parametrize(
    ("schema_id", "is_protobuf", "message_indexes", "expected"),
    [
        (12345, False, None, b"\x00\x00\x0009"),
        (12345, True, None, b"\x00\x00\x0009\x00"),
        (12345, True, [], b"\x00\x00\x0009\x00"),
        (12345, True, [0], b"\x00\x00\x0009\x00"),
        (12345, True, [0, 1, 2], b"\x00\x00\x0009\x06\x00\x02\x04"),
    ],
)
def test__build_schema_registry_header(
    schema_id: int,
    is_protobuf: bool,  # noqa: FBT001
    message_indexes: list[int] | None,
    expected: bytes,
) -> None:
    """
    Test the build_schema_registry_header function.

    Asserts:
        - The schema registry header is as expected.
    """
    assert build_schema_registry_header(schema_id, is_protobuf=is_protobuf, message_indexes=message_indexes) == expected
