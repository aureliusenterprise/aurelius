from numpy import NaN
from pandas import DataFrame

from .starts_with import starts_with


def test__starts_with_with_single_prefix():

    data = DataFrame([
        {
            "id": 1234
        }
    ])

    result = starts_with(data, "id", "1")

    assert result.sum() == 1


def test__starts_with_with_invalid_prefix():

    data = DataFrame([
        {
            "id": 1234
        }
    ])

    result = starts_with(data, "id", "2")

    assert result.sum() == 0


def test__starts_with_with_multi_character_prefix():

    data = DataFrame([
        {
            "id": 1234
        }
    ])

    result = starts_with(data, "id", "12")

    assert result.sum() == 1


def test__starts_with_with_multiple_prefixes():

    data = DataFrame([
        {
            "id": 1234
        },
        {
            "id": 2345
        }
    ])

    result = starts_with(data, "id", "1", "2")

    assert result.sum() == 2


def test__starts_with_with_empty_value():

    data = DataFrame([
        {
            "id": NaN
        }
    ])

    result = starts_with(data, "id", "1")

    assert result.sum() == 1


def test__starts_with_with_non_existing_column():

    data = DataFrame([
        {
            "id": 1234
        }
    ])

    result = starts_with(data, "non_existing_column", "1")

    assert result.sum() == 0
