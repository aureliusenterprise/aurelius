from numpy import NaN
from pandas import DataFrame

from .validity import validity


def test_validity_with_one_existing_value():

    exampleValues = ['Definite Contract', 'Indefinite Contract']

    data = DataFrame([
        {
            "value": "Definite Contract"
        }
    ])

    result = validity(data, "value", exampleValues)

    assert result.sum() == 1


def test_validity_with_two_existing_values():

    exampleValues = ['Definite Contract', 'Indefinite Contract']

    data = DataFrame([
        {
            "value": "Definite Contract"
        },
        {
            "value": "Indefinite Contract"
        }
    ])

    result = validity(data, "value", exampleValues)

    assert result.sum() == 2


def test_validity_with_nonexisting_value():

    exampleValues = ['Definite Contract', 'Indefinite Contract']

    data = DataFrame([
        {
            "value": "Something Else"
        }
    ])

    result = validity(data, "value", exampleValues)

    assert result.sum() == 0


def test_validity_with_empty_values():

    exampleValues = ['Definite Contract', 'Indefinite Contract']

    data = DataFrame([
        {
            "value": NaN
        },
        {
            "value": None
        }
    ])

    result = validity(data, "value", exampleValues)

    assert result.sum() == 0


def test_validity_with_non_existing_column():

    exampleValues = ['Definite Contract', 'Indefinite Contract']

    data = DataFrame([
        {
            "value": "Definite Contract"
        }
    ])

    result = validity(data, "non_existing_column", exampleValues)

    assert result.sum() == 0
