from dataclasses import dataclass, field
from typing import Dict, List

from dataclasses_json import LetterCase, dataclass_json

from ..attribute_def import AttributeDef
from ..relationship_attribute_def import RelationshipAttributeDef
from ..struct_def import StructDef

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EntityDef(StructDef):

    business_attribute_defs: Dict[str, List[AttributeDef]] = field(
        default_factory=dict
    )
    relationship_attribute_defs: List[RelationshipAttributeDef] = field(
        default_factory=list
    )
    sub_types: List[str] = field(default_factory=list)
    super_types: List[str] = field(default_factory=list)

# END EntityDef
