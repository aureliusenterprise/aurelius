from dataclasses import dataclass, field
from typing import Dict, List

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..entity_header import EntityHeader


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EntityMutationResponse(DataClassJsonMixin):

    guid_assignments: Dict[str, str] = field(default_factory=dict)
    mutated_entities: Dict[str, List[EntityHeader]] = field(
        default_factory=dict
    )
    partial_updated_entities: List[EntityHeader] = field(default_factory=list)

# END EntityMutationResponse
