from pandas import DataFrame

from .invalidity import invalidity


def test_invalidity_with_one_existing_value():

    exampleValues = ['x', 'X', 'TBD', 'Name']

    data = DataFrame([
        {
            "value": "X"
        }
    ])

    result = invalidity(data, "value", exampleValues)

    assert result.sum() == 0


def test_invalidity_without_existing_value():

    exampleValues = ['x', 'X', 'TBD', 'Name']

    data = DataFrame([
        {
            "value": "Something Else"
        }
    ])

    result = invalidity(data, "value", exampleValues)

    assert result.sum() == 1


def test_invalidity_with_non_existing_column():

    exampleValues = ['x', 'X', 'TBD', 'Name']

    data = DataFrame([
        {
            "value": "Something Else"
        }
    ])

    result = invalidity(data, "non_existing_column", exampleValues)

    assert result.sum() == 0
