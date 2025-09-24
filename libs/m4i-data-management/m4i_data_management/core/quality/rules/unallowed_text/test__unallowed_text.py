from numpy import NaN
from pandas import DataFrame

from .unallowed_text import unallowed_text


def test__unallowed_text_with_unallowed_text():

    data = DataFrame([
        {
            "Organisation": "Stratonis Group"
        }
    ])

    result = unallowed_text(data, "Organisation", "Stratonis Group")

    assert result.sum() == 0


def test__unallowed_text_without_unallowed_text():

    data = DataFrame([
        {
            "Organisation": "Something Else"
        }
    ])

    result = unallowed_text(data, "Organisation", "Stratonis Group")

    assert result.sum() == 1


def test__unallowed_text_with_empty_value():

    data = DataFrame([
        {
            "Organisation": NaN
        }
    ])

    result = unallowed_text(data, "Organisation", "Stratonis Group")

    assert result.sum() == 1


def test__unallowed_text_with_non_existing_column():

    data = DataFrame([
        {
            "Organisation": "Stratonis Group"
        }
    ])

    result = unallowed_text(data, "non_existing_column", "Stratonis Group")

    assert result.sum() == 0
