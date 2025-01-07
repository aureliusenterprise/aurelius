import pytest
from pandas import DataFrame, Series

from .find_changed_rows import find_changed_rows


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


def test__find_changed_rows_finds_mutations(old_data: DataFrame, new_data: DataFrame):
    mutations = list(find_changed_rows(old_data, new_data, Series.equals))

    assert len(mutations) == 1
# END test__find_changed_rows_calls_comparator_function
