from numpy import NaN
from pandas import DataFrame

from .compare_first_characters_starting_without import \
    compare_first_characters_starting_without


def test__compare_first_characters_starting_without_match_without():
    # Match, 'id' doesnt start with BE
    data = DataFrame([
        {
            "id": "NL.xxx",
            "name": "NL.xxx",

        }
    ])

    result = compare_first_characters_starting_without(
        data, "id", "name", 2, 'BE')

    assert result.sum() == 1


# END test___compare_first_characters_with_similar_values


def test__compare_first_characters_starting_without_notmatch_without():
    # Don't Match, 'id' doesnt start with BE
    data = DataFrame([
        {
            "id": "NL.xxx",
            "name": "BE.xxx",

        }
    ])

    result = compare_first_characters_starting_without(
        data, "id", "name", 2, 'BE')

    assert result.sum() == 0


# END test__compare_first_characters_starting_without_notmatch_without

def test__compare_first_characters_starting_without_match_with():
    # Match, but 'id' start with BE
    data = DataFrame([
        {
            "id": "BE.xxx",
            "name": "BE.xxx",

        }
    ])

    result = compare_first_characters_starting_without(
        data, "id", "name", 2, 'BE')

    assert result.sum() == 0


# END test__compare_first_characters_starting_without_match_with


def test__compare_first_characters_starting_without_nan():
    data = DataFrame([
        {
            "id": NaN,
            "name": NaN,

        }
    ])

    result = compare_first_characters_starting_without(
        data, "id", "name", 2, 'BE')

    assert result.sum() == 0


# END test__compare_first_characters_starting_without_nan

def test__compare_first_characters_starting_without_all():

    # Test all at once
    info = {
        "id": ["NL.xxx", "NL.xxx", "BE.xxx", NaN, NaN, "NL.xxx"],
        "name": ["NL.xxx", "BE.xxx", "BE.xxx", NaN, "NL.xxx", NaN],

    }

    columns = ['id', 'name']

    data = DataFrame(data=info, columns=columns)

    result = compare_first_characters_starting_without(
        data, "id", "name", 2, 'BE')

    assert (result == [1, 0, 0, 0, 0, 0]).all()
# END test__compare_first_characters_starting_without_all


def test__result_index_matches_original_index():
    info = {
        "index": ["a", "b", "c", "d", "e", "f"],
        "id": ["NL.xxx", "NL.xxx", "BE.xxx", NaN, NaN, "NL.xxx"],
        "name": ["NL.xxx", "BE.xxx", "BE.xxx", NaN, "NL.xxx", NaN],
    }

    data = DataFrame(info, columns=info.keys()).set_index("index")

    result = compare_first_characters_starting_without(
        data, "id", "name", 2, "BE")

    assert all(data.index == result.index)
# END test__result_index_matches_original_index
