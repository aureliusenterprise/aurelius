from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..cardinality import Cardinality
from ..constraint_def import ConstraintDef


class IndexType(Enum):
    DEFAULT = "DEFAULT"
    STRING = "STRING"
# END IndexType


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AttributeDefBase(DataClassJsonMixin):

    name: str
    type_name: str

# END AttributeDefBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AttributeDefDefaultsBase(DataClassJsonMixin):

    cardinality: Cardinality = Cardinality.SINGLE
    constraints: List[ConstraintDef] = field(default_factory=list)
    default_value: Optional[str] = None
    description: Optional[str] = None
    display_name: Optional[str] = None
    include_in_notification: bool = True
    index_type: IndexType = IndexType.DEFAULT
    is_indexable: bool = True
    is_optional: bool = True
    is_unique: bool = False
    options: Dict[str, str] = field(default_factory=dict)
    search_weight: int = 1
    values_max_count: Optional[int] = None
    values_min_count: Optional[int] = None

# END AttributeDefDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AttributeDef(AttributeDefDefaultsBase, AttributeDefBase):

    pass

# END AttributeDef
