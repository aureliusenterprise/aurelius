from dataclasses import dataclass
from enum import Enum
from typing import Optional

from dataclasses_json import LetterCase, dataclass_json

from ..base_type_def import BaseTypeDefBase, BaseTypeDefDefaultsBase
from ..propagate_tags import PropagateTags
from ..relationship_end_def import RelationshipEndDef
from ..struct_def import StructDef


class RelationshipCategory(Enum):
    ASSOCIATION = "ASSOCIATION"
    AGGREGATION = "AGGREGATION"
    COMPOSITION = "COMPOSITION"
# END RelationshipCategory


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipDefBase(BaseTypeDefBase):

    end_def1: RelationshipEndDef
    end_def2: RelationshipEndDef

# END RelationshipDefBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipDefDefaultsBase(BaseTypeDefDefaultsBase):

    propagate_tags: PropagateTags = PropagateTags.NONE
    relationship_category: RelationshipCategory = RelationshipCategory.ASSOCIATION
    relationship_label: Optional[str] = None

# END RelationshipDefDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipDef(StructDef, RelationshipDefDefaultsBase, RelationshipDefBase):

    pass

# END RelationshipDef
