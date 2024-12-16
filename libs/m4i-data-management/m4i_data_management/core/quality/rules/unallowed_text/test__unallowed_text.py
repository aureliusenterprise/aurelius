from numpy import NaN
from pandas import DataFrame

from .unallowed_text import unallowed_text


def test__unallowed_text_with_unallowed_text():

    data = DataFrame([
        {
            "Organisation": "BG Van Oord"
        }
    ])

    result = unallowed_text(data, "Organisation", "BG Van Oord")

    assert result.sum() == 0
# END test__unallowed_text_with_unallowed_text


def test__unallowed_text_without_unallowed_text():

    data = DataFrame([
        {
            "Organisation": "Something Else"
        }
    ])

    result = unallowed_text(data, "Organisation", "BG Van Oord")

    assert result.sum() == 1
# END test__unallowed_text_without_unallowed_text


def test__unallowed_text_with_empty_value():

    data = DataFrame([
        {
            "Organisation": NaN
        }
    ])

    result = unallowed_text(data, "Organisation", "BG Van Oord")

    assert result.sum() == 1
# END test__unallowed_text_with_empty_value
