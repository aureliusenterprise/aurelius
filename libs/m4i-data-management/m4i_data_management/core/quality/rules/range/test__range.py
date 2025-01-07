from numpy import NaN
from pandas import DataFrame

from .range import range

def test__range_with_value_within_range():

    data = DataFrame([
        {
            "value": 0.1
        }
    ])

    result = range(data, "value", 0, 1)

    assert result.sum() == 1
# END test__range_with_value_within_range


def test__range_with_value_out_of_range():

    data = DataFrame([
        {
            "value": 2
        }
    ])

    result = range(data, "value", 0, 1)

    assert result.sum() == 0
# END test__range_with_value_out_of_range


def test__range_with_empty_values():

    data = DataFrame([
        {
            "value": NaN
        },
        {
            "value": None
        }
    ])

    result = range(data, "value", 0, 1)

    assert result.sum() == 0
# END test__range_with_empty_values
