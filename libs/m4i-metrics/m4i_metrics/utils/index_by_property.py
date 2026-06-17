from typing import Any, Dict, Iterable, Optional


def index_by_property(
    data: Optional[Iterable[Dict[str, Any]]], property_name: Optional[str]
) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
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
