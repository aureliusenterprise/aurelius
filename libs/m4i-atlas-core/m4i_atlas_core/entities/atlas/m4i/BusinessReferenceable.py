from dataclasses import dataclass, field
from typing import Iterable, List, Optional
from uuid import uuid4 as uuid

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Attributes, Cardinality, Entity, EntityBase,
                    EntityDef, EntityDefaultsBase, ObjectId, TypeCategory)
from .M4IAttributes import M4IAttributesBase

# TypeDef for Entity & Relationships
m4i_referenceable_attributes_def = [
    AttributeDef(
        name="archimateReference",
        type_name="array<m4i_archimate_project>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="source",
        type_name="array<m4i_source>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="typeAlias",
        type_name="string",
        description="Type name to display in the UI instead of the base type name.",
        display_name="Type alias"
    )
]

m4i_referenceable_super_type = ["Referenceable"]

m4i_referenceable_def = EntityDef(
    category=TypeCategory.ENTITY,
    description="A type definition for a generic m4i Referenceable in the context of models4insight.com",
    name="m4i_referenceable",
    type_version="1.0",
    super_types=m4i_referenceable_super_type,
    attribute_defs=m4i_referenceable_attributes_def,
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessReferenceableAttributesBase(M4IAttributesBase):
    pass
# END BusinessReferenceableAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessReferenceableAttributesDefaultsBase(Attributes):
    archimate_reference: List[ObjectId] = field(default_factory=list)
    source: List[ObjectId] = field(default_factory=list)
    type_alias: Optional[str] = field(default=None)
# END BusinessReferenceableAttributesDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessReferenceableAttributes(BusinessReferenceableAttributesDefaultsBase, BusinessReferenceableAttributesBase):
    pass
# END BusinessReferenceableAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessReferenceableBase(EntityBase):
    pass
# END BusinessReferenceableBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessReferenceableDefaultsBase(EntityDefaultsBase):
    attributes: BusinessReferenceableAttributes = field(
        default_factory=lambda: BusinessReferenceableAttributes(str(uuid()))
    )
# END BusinessReferenceableDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessReferenceable(
        Entity,
        BusinessReferenceableDefaultsBase,
        BusinessReferenceableBase
):
    type_name: str = "m4i_referenceable"

    @staticmethod
    def get_type_def() -> EntityDef:
        return m4i_referenceable_def
    # END get_type_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this archimate project:
        * archimate_reference
        * source
        """
        references = [
            *self.attributes.archimate_reference,
            *self.attributes.source
        ]

        return filter(None, references)
    # END get_referred_entities

# END BusinessReferenceable
