from numpy import NaN
from pandas import DataFrame

from .uniqueness import uniqueness


def test__uniqueness_with_single_duplicate_value():

    data = DataFrame([
        {
            "id": "1234"
        },
        {
            "id": "1234"
        }
    ])

    result = uniqueness(data, "id")

    assert result.sum() == 0
# END test__uniqueness_with_single_duplicate_value


def test__uniqueness_with_duplicate_and_unique_values():

    data = DataFrame([
        {
            "id": "1234"
        },
        {
            "id": "1234"
        },
        {
            "id": "2345"
        }
    ])

    result = uniqueness(data, "id")

    assert result.sum() == 1
# END test__uniqueness_with_duplicate_and_unique_values


def test__uniqueness_without_duplicate_value():

    data = DataFrame([
        {
            "id": "1234"
        },
        {
            "id": "5678"
        }
    ])

    result = uniqueness(data, "id")

    assert result.sum() == 2
# END test__uniqueness_without_duplicate_value


def test__uniqueness_without_any_values():

    data = DataFrame([
        {
            "id": NaN
        },
        {
            "id": NaN
        }
    ])

    result = uniqueness(data, "id")

    assert result.sum() == 2
# END test__uniqueness_without_any_values
