from typing import Iterable


def index_by_property(data: Iterable[dict], property_name: str) -> dict:
    index = {}
    if data is None or property_name is None:
        return index
    # END IF
    for row in data:
        value = row.get(property_name)
        if value is not None:
            index[value] = row
        # END IF
    # END LOOP
    return index
# END index_by_property
