from time import time
from uuid import uuid4 as uuid

from pandas import DataFrame, Series, notnull

from ..cdc import CHANGE_TYPE_COLUMN, CDCChangeType
from ..utils import omit


def format_change_event(event: Series, source_name: str, target_index_name: str) -> dict:
    """
    Returns a standardized change event message based on the given change `event`.
    """

    id = str(uuid())
    change_type = event[CHANGE_TYPE_COLUMN].value

    timestamp = int(time())

    payload = None

    if event[CHANGE_TYPE_COLUMN] != CDCChangeType.REMOVED:
        # Convert the event to a dict. Replaces `nan` values with `None`.
        event_dict = event.where(notnull(event), None).to_dict()

        payload = omit(
            event_dict,
            CHANGE_TYPE_COLUMN
        )
    # END IF

    message = {
        "id": id,
        "change_type": change_type,
        "source": source_name,
        "target": target_index_name,
        "timestamp": timestamp,
        "payload": payload
    }

    return message
# END format_change_event


def format_change_events(events: DataFrame, source_name: str, target_index_name: str) -> Series:
    """
    Returns a Series of all given change events as standardized change event messages.
    """

    return events.apply(
        format_change_event,
        axis=1,
        source_name=source_name,
        target_index_name=target_index_name
    )
# END format_change_events
