from pandas import DataFrame

from m4i_data_management.core.quality.rules.invalidity.invalidity import invalidity


def test_invalidity_with_one_existing_value():
    example_values = ["x", "X", "TBD", "Name"]

    data = DataFrame([{"value": "X"}])

    result = invalidity(data, "value", example_values)

    assert result.sum() == 0


def test_invalidity_without_existing_value():
    example_values = ["x", "X", "TBD", "Name"]

    data = DataFrame([{"value": "Something Else"}])

    result = invalidity(data, "value", example_values)

    assert result.sum() == 1


def test_invalidity_with_non_existing_column():
    example_values = ["x", "X", "TBD", "Name"]

    data = DataFrame([{"value": "Something Else"}])

    result = invalidity(data, "non_existing_column", example_values)

    assert result.sum() == 0
