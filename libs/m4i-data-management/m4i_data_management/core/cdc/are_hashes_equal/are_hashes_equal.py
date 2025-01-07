from pandas import Series

from ..columns import HASH_COLUMN
from ..utils import calculate_hash_for_row


def are_hashes_equal(old: Series, new: Series) -> bool:
    """
    Compares the given `old` and `new` rows for equality by using the row hash. 
    If the row hash is not included with a row, it is added.
    Returns whether or not the given rows are equal.
    """

    if HASH_COLUMN not in new:
        new[HASH_COLUMN] = calculate_hash_for_row(new)
    # END IF

    if HASH_COLUMN not in old:
        old[HASH_COLUMN] = calculate_hash_for_row(old)
    # END IF

    return old[HASH_COLUMN] == new[HASH_COLUMN]
# END are_hashes_equal
