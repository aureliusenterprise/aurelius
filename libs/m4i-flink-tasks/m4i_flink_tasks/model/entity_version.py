from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import Entity


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass
class EntityVersion(DataClassJsonMixin):
    """
    Represents a version of an entity with metadata about the event and message creation.

    Attributes
    ----------
    body : Entity
        The core entity data.
    doc_id : str
        The identifier for the document.
    event_time : int
        The timestamp (epoch) indicating when the event occurred.
    msg_creation_time : int
        The timestamp (epoch) indicating when the message was created.
    """

    body: Entity
    doc_id: str
    event_time: int
    msg_creation_time: int
