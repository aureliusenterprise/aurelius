from numpy import NaN
from pandas import DataFrame

from .bijacency import bijacency


def test__bijacency_with_bijacent_columns():

    data = DataFrame([
        {
            "id": 1234,
            "name": "John Doe",
            "function": "Developer",
            "from": "01-01-2021"
        },
        {
            "id": 1234,
            "name": "John Doe",
            "function": "Senior developer",
            "from": "01-01-2022"
        }
    ])

    result = bijacency(data, "id", "name")

    assert result.sum() == 2
# END test__bijacency_with_bijacent_columns


def test__bijacency_with_non_bijacent_columns():

    data = DataFrame([
        {
            "id": 1234,
            "name": "John Doe",
            "function": "Developer",
            "from": "01-01-2021"
        },
        {
            "id": 5678,
            "name": "John Doe",
            "function": "Senior developer",
            "from": "01-01-2022"
        }
    ])

    result = bijacency(data, "id", "name")

    assert result.sum() == 0
# END test__bijacency_with_non_bijacent_columns


def test__bijacency_with_one_empty_value():

    data = DataFrame([
        {
            "id": 1234,
            "name": NaN,
            "function": "Developer",
            "from": "01-01-2021"
        },
        {
            "id": 1234,
            "name": "John Doe",
            "function": "Senior developer",
            "from": "01-01-2022"
        }
    ])

    result = bijacency(data, "id", "name")

    assert result.sum() == 0
# END test__bijacency_with_one_empty_value


def test__bijacency_with_both_empty_values():

    data = DataFrame([
        {
            "id": 1234,
            "name": NaN,
            "function": "Developer",
            "from": "01-01-2021"
        },
        {
            "id": 1234,
            "name": None,
            "function": "Senior developer",
            "from": "01-01-2022"
        }
    ])

    result = bijacency(data, "id", "name")

    assert result.sum() == 2
# END test__bijacency_with_both_empty_values
