from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..cardinality import Cardinality


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipEndDefBase(DataClassJsonMixin):

    name: str
    type: str

# END RelationshipEndDefBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipEndDefDefaultsBase(DataClassJsonMixin):

    cardinality: Cardinality = Cardinality.SET
    description: Optional[str] = None
    is_container: bool = False
    is_legacy_attribute: bool = False

# END RelationshipEndDefDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipEndDef(RelationshipEndDefDefaultsBase, RelationshipEndDefBase):

    pass

# END RelationshipEndDef
