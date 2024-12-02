from numpy import NaN
from pandas import Series

from ..columns import HASH_COLUMN
from .are_hashes_equal import are_hashes_equal


def test__are_hashes_equal_with_hash_given():
    a = Series({"a": "100", "b": 100, HASH_COLUMN: "1234"})
    b = Series({"a": "100", "b": 100, HASH_COLUMN: "1234"})

    assert are_hashes_equal(a, b)
# END test__are_hashes_equal_with_hash_given


def test__are_hashes_not_equal_with_different_hash_given():
    a = Series({"a": "100", "b": 100, HASH_COLUMN: "1234"})
    b = Series({"a": "100", "b": 100, HASH_COLUMN: "5678"})

    assert not are_hashes_equal(a, b)
# END test__are_hashes_not_equal_with_different_hash_given


def test__are_hashes_equal_with_no_hash_given():
    a = Series({"a": "100", "b": 100})
    b = Series({"a": "100", "b": 100})

    assert are_hashes_equal(a, b)
# END test__are_hashes_equal_with_no_hash_given


def test__are_hashes_not_equal_for_different_rows():
    a = Series({"a": "100", "b": 100})
    b = Series({"a": "200", "b": 200})

    assert not are_hashes_equal(a, b)
# END test__are_hashes_not_equal_for_different_rows


def test__are_hashes_equal_with_empty_column():
    a = Series({"a": "100", "b": 100, "c": NaN})
    b = Series({"a": "100", "b": 100})

    assert are_hashes_equal(a, b)
# END test__are_hashes_equal_with_empty_column


def test__are_hashes_equal_adds_hash_column_if_not_present():
    a = Series({"a": "100", "b": 100, HASH_COLUMN: "1234"})
    b = Series({"a": "100", "b": 100})

    are_hashes_equal(a, b)

    assert a[HASH_COLUMN] == "1234" and HASH_COLUMN in b
# END test__are_hashes_equal_adds_hash_column_if_not_present
