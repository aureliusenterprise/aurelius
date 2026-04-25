import pytest
from aurelius_sdk.encoding import zigzag_decode, zigzag_encode


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, 0),
        (-1, 1),
        (1, 2),
    ],
)
def test__zigzag_encode(value: int, expected: int) -> None:
    """
    Test the zigzag encoding function.

    Asserts:
        - The zigzag encoded integer is as expected.
    """
    assert zigzag_encode(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, 0),
        (1, -1),
        (2, 1),
    ],
)
def test__zigzag_decode(value: int, expected: int) -> None:
    """
    Test the zigzag decoding function.

    Asserts:
        - The zigzag decoded integer is as expected.
    """
    assert zigzag_decode(value) == expected
