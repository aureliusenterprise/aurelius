import pytest
from pandas import DataFrame

from .find_different_rows import find_different_rows


@pytest.fixture
def old_data():
    return DataFrame([
        {
            "id": 1,
            "abc": "def"
        },
        {
            "id": 2,
            "abc": "def"
        }
    ]).set_index("id")
# END old_data


@pytest.fixture
def new_data():
    return DataFrame([
        {
            "id": 1,
            "abc": "ghi"
        },
        {
            "id": 3,
            "abc": "def"
        }
    ]).set_index("id")
# END new_data


def test__find_different_rows_finds_difference(old_data: DataFrame, new_data: DataFrame):
    difference = find_different_rows(old_data, new_data)

    assert len(difference) == 1
# END test_find_different_rows_finds_difference
