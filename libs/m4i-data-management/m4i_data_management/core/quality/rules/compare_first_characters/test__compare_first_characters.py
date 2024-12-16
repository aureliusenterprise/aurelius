from .compare_first_characters import compare_first_characters
from numpy import NaN
from pandas import DataFrame

def test__compare_first_characters_with_similar_values():

    data = DataFrame([
        {
            "id": "NL.xxx",
            "name": "NL.xxx",

        }
    ])

    result = compare_first_characters(data, "id", "name", 2)

    assert result.sum() == 1
# END test__compare_first_characters_with_similar_values

def test__compare_first_characters_with_other_values():

    data = DataFrame([
        {
            "id": "NL.xxx",
            "name": "BE.xxx",

        }
    ])

    result = compare_first_characters(data, "id", "name", 2)

    assert result.sum() == 0
# END test__compare_first_characters_with_other_values

def test__compare_first_characters_without_values():

    data = DataFrame([
        {
            "id": NaN,
            "name": NaN,

        }
    ])

    result = compare_first_characters(data, "id", "name", 2)

    assert result.sum() == 0
# END test__compare_first_characters_without_values