from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import Entity


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass
class ValidatedInput(DataClassJsonMixin):
    """
    Represents validated input containing an entity, and timestamps for event and message creation.

    This class is designed to ensure that the entity data being processed has passed validation
    checks and is ready for further processing .

    Attributes
    ----------
    entity : Entity
        The Entity object from Aurelius Atlas.

    event_time : int
        The timestamp (epoch) indicating when the event associated with the entity occurred.

    msg_creation_time : int
        The timestamp (epoch) indicating when the message about the entity was created.
    """

    entity: Entity
    event_time: int
    msg_creation_time: int
