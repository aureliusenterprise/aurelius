from numpy import NaN
from pandas import DataFrame

from .conditional_value import conditional_value


def test__conditional_value_condition_met_with_expected_value():

    values = {
        "xx.TMP": "XX No Grade"
    }

    data = DataFrame([
        {
            "value": "XX No Grade",
            "conditional": "xx.TMP"
        }
    ])

    result = conditional_value(data, "conditional", "value", values)

    assert result.sum() == 1
# END test__test__conditional_value_condition_met_with_expected_value


def test__conditional_value_condition_met_with_multiple_possible_values():

    values = {
        "xx.TMP": ["XX No Grade", "Hello world"]
    }

    data = DataFrame([
        {
            "value": "XX No Grade",
            "conditional": "xx.TMP"
        }
    ])

    result = conditional_value(data, "conditional", "value", values)

    assert result.sum() == 1
# END test__test__conditional_value_condition_met_with_expected_value


def test__conditional_value_condition_met_with_no_valid_values():

    values = {
        "xx.TMP": ["Something else", "Hello world"]
    }

    data = DataFrame([
        {
            "value": "XX No Grade",
            "conditional": "xx.TMP"
        }
    ])

    result = conditional_value(data, "conditional", "value", values)

    assert result.sum() == 0
# END test__test__conditional_value_condition_met_with_expected_value



def test__conditional_value_condition_met_with_non_expected_value():

    values = {
        "xx.TMP": "XX No Grade"
    }

    data = DataFrame([
        {
            "value": "Something Else",
            "conditional": "xx.TMP"
        }
    ])

    result = conditional_value(data,  "conditional", "value", values)

    assert result.sum() == 0
# END test__test__conditional_value_condition_met_with_non_expected_value


def test__conditional_value_condition_unmet_with_expected_value():

    values = {
        "xx.TMP": "XX No Grade"
    }

    data = DataFrame([
        {
            "value": "Something Else",
            "conditional": "xx.xx"
        }
    ])

    result = conditional_value(data, "conditional", "value", values)

    assert result.sum() == 0
# END test__test__conditional_value_condition_unmet_wih_expected_value


def test__conditional_value_condition_unmet_with_no_value():

    values = {
        "xx.TMP": "XX No Grade"
    }

    data = DataFrame([
        {
            "value": NaN,
            "conditional": "xx.xx"
        }
    ])

    result = conditional_value(data, "conditional", "value", values)

    assert result.sum() == 0
# END test__test__conditional_value_condition_unmet_wih_no_value
