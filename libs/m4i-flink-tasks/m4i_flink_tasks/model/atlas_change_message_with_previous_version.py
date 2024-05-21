from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json
from m4i_atlas_core import AtlasChangeMessage, Entity


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore
@dataclass
class AtlasChangeMessageWithPreviousVersion(AtlasChangeMessage):
    """An AtlasChangeMessage with a previous version of the entity."""

    previous_version: Entity | None = None
