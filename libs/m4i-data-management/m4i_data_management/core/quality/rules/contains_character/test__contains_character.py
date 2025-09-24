from numpy import NaN
from pandas import DataFrame

from .contains_character import contains_character


def test__contains_character_with_single_occurrence():

    data = DataFrame([
        {
            "id": "12.12"
        }
    ])

    result = contains_character(data, "id", ".", 1)

    assert result.sum() == 1


def test__contains_character_with_multiple_occurrences():

    data = DataFrame([
        {
            "id": "12.1.2"
        }
    ])

    result = contains_character(data, "id", ".", 2)

    assert result.sum() == 1


def test__contains_character_with_no_occurrence():

    data = DataFrame([
        {
            "id": "1212"
        }
    ])

    result = contains_character(data, "id", ".", 1)

    assert result.sum() == 0


def test__contains_character_with_multiple_characters():

    data = DataFrame([
        {
            "id": "1234"
        }
    ])

    result = contains_character(data, "id", "12", 1)

    assert result.sum() == 1


def test__contains_character_with_empty_value():

    data = DataFrame([
        {
            "id": NaN
        }
    ])

    result = contains_character(data, "id", ".", 1)

    assert result.sum() == 1


def test__contains_character_with_non_existing_column():

    data = DataFrame([
        {
            "id": "12.12"
        }
    ])

    result = contains_character(data, "non_existing_column", ".", 1)

    assert result.sum() == 0
