from numpy import NaN
from pandas import DataFrame

from .length import length


def test__length_with_equal_length():

    data = DataFrame([
        {
            "id": "1234"
        }
    ])

    result = length(data, "id", 4)

    assert result.sum() == 1
# END test__length_with_equal_length


def test__length_with_greater_length():

    data = DataFrame([
        {
            "id": "123456"
        }
    ])

    result = length(data, "id", 4)

    assert result.sum() == 1
# END test__length_with_equal_length


def test__length_with_smaller_length():

    data = DataFrame([
        {
            "id": "12"
        }
    ])

    result = length(data, "id", 4)

    assert result.sum() == 0
# END test__length_with_smaller_length


def test__length_without_value():

    data = DataFrame([
        {
            "id": NaN
        }
    ])

    result = length(data, "id", 4)

    assert result.sum() == 0
# END test__length_without_value


def test__length_with_list():

    data = DataFrame([
        {
            "id": [1, 2, 3, 4]
        }
    ])

    result = length(data, "id", 4)

    assert result.sum() == 1
# END test__length_without_value


def test__length_with_empty_list():

    data = DataFrame([
        {
            "id": []
        }
    ])

    result = length(data, "id", 4)

    assert result.sum() == 0
# END test__length_without_value
