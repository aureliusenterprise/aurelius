import pytest
from pandas import DataFrame

from ..change_types import CDCChangeType
from ..columns import CHANGE_TYPE_COLUMN
from .compare_datasets import compare_datasets


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


def test__compare_datasets_annotates_changes(old_data, new_data):
    result = compare_datasets(old_data, new_data)

    assert len(result.index) == 3

    added = result[result[CHANGE_TYPE_COLUMN] == CDCChangeType.ADDED]
    removed = result[result[CHANGE_TYPE_COLUMN] == CDCChangeType.REMOVED]
    changed = result[result[CHANGE_TYPE_COLUMN] == CDCChangeType.CHANGED]

    assert len(added.index) == 1
    assert len(removed.index) == 1
    assert len(changed.index) == 1
# END test__compare_datasets_annotates_changes
