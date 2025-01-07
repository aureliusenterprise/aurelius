from numpy import NaN
from pandas import DataFrame

from .conditional_completeness import conditional_completeness


def test__conditional_completeness_condition_met_with_value():

    values = ['.TMP', '.FREE']

    data = DataFrame([
        {
            "value": "Something",
            "conditional": "xx.FREE.eur"
        }
    ])

    result = conditional_completeness(data,  "conditional", "value", values)

    assert result.sum() == 1
# END test__conditional_completeness_condition_met_with_value


def test__conditional_completeness_condition_met_without_value():

    values = ['.TMP', '.FREE']

    data = DataFrame([
        {
            "value": NaN,
            "conditional": "xx.FREE.eur"
        }
    ])

    result = conditional_completeness(data, "conditional", "value", values)

    assert result.sum() == 0
# END test__conditional_completeness_condition_met_without_value


def test__conditional_completeness_condition_unmet_with_value():

    values = ['.TMP', '.FREE']

    data = DataFrame([
        {
            "value": "Something",
            "conditional": "Something"
        }
    ])

    result = conditional_completeness(data, "conditional", "value", values)

    assert result.sum() == 0
# END test__conditional_completeness_condition_unmet_with_value
