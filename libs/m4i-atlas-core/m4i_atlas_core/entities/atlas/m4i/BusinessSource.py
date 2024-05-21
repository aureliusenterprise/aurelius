from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Attributes, Cardinality, EntityBase,
                    EntityDef, EntityDefaultsBase, ObjectId,
                    RelationshipAttribute, RelationshipAttributeDef,
                    RelationshipDef, RelationshipEndDef, TypeCategory)
from .M4IAttributes import M4IAttributesBase
from .BusinessReferenceable import BusinessReferenceable

# TypeDef for Entity & Relationships
business_source_attributes_def = [
    AttributeDef(
        name="name",
        type_name="string",
        description="The unique functional name of the source",
        display_name="Name"
    ),
    AttributeDef(
        name="hashCode",
        type_name="string",
        description="The unique hash code of the source",
        display_name="Hash Code"
    ),
    AttributeDef(
        name="branch",
        type_name="string",
        description="The branch of the source",
        display_name="Branch"
    ),
    RelationshipAttributeDef(
        name="changeLog",
        type_name="array<m4i_referenceable>",
        relationship_type_name="m4i_referenceable_source_assignment",
        cardinality=Cardinality.SET,
        description="A list of the most recent added/updated relationships with the source",
        display_name="Change Log"
    )  # TODO depends on what we decide, this might just be an attribute
]

business_source_super_type = ["m4i_referenceable"]

business_source_def = EntityDef(
    category=TypeCategory.ENTITY,
    description="A type definition for a generic Business Source in the context of models4insight.com",
    name="m4i_source",
    type_version="1.0",
    super_types=business_source_super_type,
    attribute_defs=business_source_attributes_def,
)
end_1_source_changelog = RelationshipEndDef(
    type="m4i_source",
    name="changeLog",
    cardinality=Cardinality.SET
)
end_2_source_references = RelationshipEndDef(
    type="m4i_referenceable",
    name="source",
    cardinality=Cardinality.SET
)

m4i_business_source_rel_def = RelationshipDef(
    end_def1=end_1_source_changelog,
    end_def2=end_2_source_references,
    name="m4i_referenceable_source_assignment",
    category=TypeCategory.RELATIONSHIP,
    description="A list of the most recent added/updated relationships with the source",
    type_version="1.0",
)


# END TypeDef for Entity & Relationships


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSourceAttributesBase(M4IAttributesBase):
    name: Optional[str] = None
    hash_code: Optional[str] = None
    branch: Optional[str] = None


# END BusinessSourceAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSourceAttributesDefaultsBase(Attributes):
    pass


# END BusinessSourceAttributesDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSourceAttributes(BusinessSourceAttributesDefaultsBase,
                               BusinessSourceAttributesBase):
    pass


# END BusinessSourceAttributes

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSourceRelationshipAttributes(Attributes):
    change_log: List[RelationshipAttribute] = field(default_factory=list)


# END BusinessSourceRelationshipAttributes

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSourceBase(EntityBase):
    attributes: BusinessSourceAttributes


# END BusinessSourceBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSourceDefaultsBase(EntityDefaultsBase):
    relationship_attributes: Optional[BusinessSourceRelationshipAttributes] = None


# END BusinessSourceDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSource(BusinessReferenceable,
                     BusinessSourceDefaultsBase,
                     BusinessSourceBase,
                     ):
    type_name: str = "m4i_source"

    @classmethod
    def get_type_def(cls):
        return business_source_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this archimate project:
        * source
        """
        references = [
            *self.relationship_attributes.change_log
        ]

        return references
    # END get_referred_entities

# END BusinessSource
