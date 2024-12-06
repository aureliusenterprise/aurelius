import logging
from logging import log
from typing import Callable

from pandas import DataFrame, Series, concat

from ..are_hashes_equal import are_hashes_equal
from ..change_types import CDCChangeType
from ..columns import CHANGE_TYPE_COLUMN, HASH_COLUMN
from ..utils import (calculate_hash_for_row, find_changed_rows,
                     find_different_rows)

log = logging.getLogger(__name__)


def compare_datasets(old: DataFrame, new: DataFrame, is_equal: Callable[[Series, Series], bool] = are_hashes_equal) -> DataFrame:
    """
    Compares the given `old` and `new` datasets and returns all `added`, `changed` and `removed` rows.
    You can specify how the rows should be compared by passing a custom `is_equal` function.
    All returned rows are annotated with their respective `change_type`.
    """

    log.info(
        f"Comparing {len(new.index)} new records against {len(old.index)} old records"
    )

    removed_rows = find_different_rows(old, new)
    removed_rows[CHANGE_TYPE_COLUMN] = CDCChangeType.REMOVED

    log.info(f"Found {len(removed_rows.index)} removed records")

    added_rows = find_different_rows(new, old)
    #added_rows[HASH_COLUMN] = added_rows.apply(calculate_hash_for_row, axis=1)
    added_rows[CHANGE_TYPE_COLUMN] = CDCChangeType.ADDED

    log.info(f"Found {len(added_rows.index)} added records")

    changed_rows = DataFrame()

    if len(old.index) > 0 and len(new.index) > 0:
        changed_rows = DataFrame(find_changed_rows(old, new, is_equal))
        changed_rows[CHANGE_TYPE_COLUMN] = CDCChangeType.CHANGED
    # END IF

    log.info(f"Found {len(changed_rows.index)} changed records")

    return concat([added_rows, removed_rows, changed_rows])
# END compare_datasets
