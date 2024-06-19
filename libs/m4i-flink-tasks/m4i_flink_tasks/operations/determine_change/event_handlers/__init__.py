"""
The event_handlers module maps entity audit actions to their corresponding change event handlers.

Each audit action is associated with a callable that takes an
`AtlasChangeMessageWithPreviousVersion` object as input and returns
a list of `EntityMessage` objects representing the determined changes.

Attributes
----------
EVENT_HANDLERS : dict
    A dictionary that maps `EntityAuditAction` to their corresponding change event handling
    functions, which process change messages and determine the resulting entity state changes.
"""

from typing import Callable, Dict, List

from m4i_atlas_core import EntityAuditAction

from m4i_flink_tasks import AtlasChangeMessageWithPreviousVersion, EntityMessage

from .handle_create_operation import handle_create_operation
from .handle_delete_operation import handle_delete_operation
from .handle_update_operation import handle_update_operation

# Type alias for change event handler functions
ChangeEventHandler = Callable[[AtlasChangeMessageWithPreviousVersion], List[EntityMessage]]

# Dictionary mapping entity audit actions to their respective event handler functions
EVENT_HANDLERS: Dict[EntityAuditAction, ChangeEventHandler] = {
    EntityAuditAction.ENTITY_CREATE: handle_create_operation,
    EntityAuditAction.ENTITY_UPDATE: handle_update_operation,
    EntityAuditAction.ENTITY_DELETE: handle_delete_operation,
}

__all__ = ("EVENT_HANDLERS", "ChangeEventHandler")
