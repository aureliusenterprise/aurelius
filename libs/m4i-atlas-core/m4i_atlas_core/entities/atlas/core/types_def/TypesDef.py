from dataclasses import dataclass, field
from typing import List

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..business_metadata_def import BusinessMetadataDef
from ..classification_def import ClassificationDef
from ..entity_def import EntityDef
from ..enum_def import EnumDef
from ..relationship_def import RelationshipDef
from ..struct_def import StructDef


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TypesDef(DataClassJsonMixin):

    business_metadata_defs: List[BusinessMetadataDef] = field(
        default_factory=list
    )
    classification_defs: List[ClassificationDef] = field(default_factory=list)
    entity_defs: List[EntityDef] = field(default_factory=list)
    enum_defs: List[EnumDef] = field(default_factory=list)
    relationship_defs: List[RelationshipDef] = field(default_factory=list)
    struct_defs: List[StructDef] = field(default_factory=list)

# END TypesDef
