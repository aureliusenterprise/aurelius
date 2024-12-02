from datetime import datetime

from numpy import NaN
from pandas import Series

from .calculate_hash_for_row import calculate_hash_for_row


def test__calculate_hash_for_row_is_idempotent():
    row = Series({
        "abc": "def"
    })

    assert calculate_hash_for_row(row) == calculate_hash_for_row(row)
# END test__calculate_hash_for_row_is_idempotent


def test_calculate_hash_for_row_produces_different_hash_for_different_input():
    row_a = Series({
        "abc": "def"
    })

    row_b = Series({
        "abc": "ghi",
    })

    assert calculate_hash_for_row(row_a) != calculate_hash_for_row(row_b)
# END test_calculate_hash_for_row_produces_different_hash_for_different_input


def test__calculate_hash_for_row_empty_fields_do_not_influence_hash():
    row_a = Series({
        "abc": "def"
    })

    row_b = Series({
        "abc": "def",
        "jkl": None,
        "mno": NaN
    })

    assert calculate_hash_for_row(row_a) == calculate_hash_for_row(row_b)
# END test__calculate_hash_for_row_empty_fields_do_not_influence_hash


def test_calculate_hash_for_row_can_handle_data_types():
    row = Series({
        "abc": "def",           # string
        "ghi": 1,               # number
        "jkl": 2.3,             # float
        "mno": datetime.now()   # datetime
    })

    calculate_hash_for_row(row)
# END test_calculate_hash_for_row_can_handle_data_types
