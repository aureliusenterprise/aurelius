from numpy import NaN
from pandas import DataFrame

from m4i_data_management.core.quality.rules.validity.validity import validity


def test_validity_with_one_existing_value():
    example_values = ["Definite Contract", "Indefinite Contract"]

    data = DataFrame([{"value": "Definite Contract"}])

    result = validity(data, "value", example_values)

    assert result.sum() == 1


def test_validity_with_two_existing_values():
    example_values = ["Definite Contract", "Indefinite Contract"]

    data = DataFrame([{"value": "Definite Contract"}, {"value": "Indefinite Contract"}])

    result = validity(data, "value", example_values)

    assert result.sum() == 2


def test_validity_with_nonexisting_value():
    example_values = ["Definite Contract", "Indefinite Contract"]

    data = DataFrame([{"value": "Something Else"}])

    result = validity(data, "value", example_values)

    assert result.sum() == 0


def test_validity_with_empty_values():
    example_values = ["Definite Contract", "Indefinite Contract"]

    data = DataFrame([{"value": NaN}, {"value": None}])

    result = validity(data, "value", example_values)

    assert result.sum() == 0


def test_validity_with_non_existing_column():
    example_values = ["Definite Contract", "Indefinite Contract"]

    data = DataFrame([{"value": "Definite Contract"}])

    result = validity(data, "non_existing_column", example_values)

    assert result.sum() == 0
