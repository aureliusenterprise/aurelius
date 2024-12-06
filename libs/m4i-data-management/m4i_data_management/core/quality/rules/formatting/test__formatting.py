from .formatting import formatting
from numpy import NaN
from pandas import DataFrame

def test__formatting_with_correct_numeric_format():

    data = DataFrame([
        {
            "name": 1234
        }
    ])

    result = formatting(data, "name", r'^[0-9]+$')

    assert result.sum() == 1
# END test__formatting_with_correct_numeric_format

def test__formatting_with_correct_text_format():

    data = DataFrame([
        {
            "name": 'ExampleText'
        }
    ])

    result = formatting(data, "name", r'^[a-zA-Z]+$')

    assert result.sum() == 1
# END test__formatting_with_correct_text_format

def test__formatting_with_incorrect_text_format():

    data = DataFrame([
        {
            "name": "1234"
        }
    ])

    result = formatting(data, "name", r'^[a-zA-Z]+$')

    assert result.sum() == 0
# END test__formatting_with_incorrect_text_format

def test__formatting_with_incorrect_text_format_combined():

    data = DataFrame([
        {
            "name": "a1234"
        }
    ])

    result = formatting(data, "name", r'^[a-zA-Z]+$')

    assert result.sum() == 0
# END test__formatting_with_incorrect_text_format_combined

def test__formatting_with_incorrect_numeric_format_combined():

    data = DataFrame([
        {
            "name": "a1234"
        }
    ])

    result = formatting(data, "name", r'^[0-9]+$')

    assert result.sum() == 0
# END test__formatting_with_incorrect_numeric_format_combined

def test__formatting_without_value():

    data = DataFrame([
        {
            "name": NaN
        }
    ])

    result = formatting(data, "name", r'^[a-zA-Z]+$')

    assert result.sum() == 0
# END test__formatting_without_value
