
from typing import Iterable

def index_by_property(data: Iterable[dict], property_name: str) -> dict:
    """
    Creates a dictionary of the rows from the given dataset, keyed by the given property.

    :returns: A dictionary of the rows from the given dataset, keyed by the given property.
    :rtype: dict

    :param Iterable[dict] data: The dataset that should be indexed.
    :param str property_name: The name of the property to index by.
    """

    result = {}
    for row in data:
        key = row.get(property_name)
        if key is not None:
            result[key] = row
        # END IF
    # END LOOP
    return result
# END index_by_property
