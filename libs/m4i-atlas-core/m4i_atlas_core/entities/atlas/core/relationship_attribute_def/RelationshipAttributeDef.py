from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json

from ..attribute_def import (AttributeDef, AttributeDefBase,
                             AttributeDefDefaultsBase)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipAttributeDefBase(AttributeDefBase):

    relationship_type_name: str

# END RelationshipAttributeDefBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipAttributeDefDefaultsBase(AttributeDefDefaultsBase):

    is_legacy_attribute: bool = False

# END RelationshipAttributeDefDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipAttributeDef(AttributeDef, RelationshipAttributeDefDefaultsBase, RelationshipAttributeDefBase):

    pass

# END RelationshipAttributeDef
