from .completeness import completeness
from numpy import NaN
from pandas import DataFrame

def test__completeness_with_non_empty_value():

    data = DataFrame([
        {
            "id": 1234,
            "name": "John Doe",
            "function": "Developer",
            "from": "01-01-2021"
        }
    ])

    result = completeness(data, "name")

    assert result.sum() == 1
# END test__completeness_with_non_empty_value


def test__completeness_with_one_empty_value():

    data = DataFrame([
        {
            "id": 1234,
            "name": NaN,
            "function": "Developer",
            "from": "01-01-2021"
        }
    ])

    result = completeness(data, "name")

    assert result.sum() == 0
# END test__completeness_with_non_empty_value
