from dataclasses import dataclass, field
from typing import Dict, List

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..entity import Entity


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EntitiesWithExtInfo(DataClassJsonMixin):

    entities: List[Entity] = field(default_factory=list)
    referred_entities: Dict[str, Entity] = field(default_factory=dict)

# END EntitiesWithExtInfo
