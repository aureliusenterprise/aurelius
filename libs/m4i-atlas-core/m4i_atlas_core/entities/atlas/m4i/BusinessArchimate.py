from dataclasses import dataclass
from typing import Iterable

from dataclasses_json import LetterCase, dataclass_json
from ..core import (AttributeDef, Attributes, Entity, EntityBase,
                    EntityDef, EntityDefaultsBase, ObjectId,
                    TypeCategory, RelationshipDef, RelationshipEndDef, Cardinality)

from .M4IAttributes import M4IAttributesBase

# TypeDef for Entity & Relationships
archimate_project_attributes_def = [

    AttributeDef(
        name="name",
        type_name="string",
        description="The name of the archimate project",
        display_name="Name"
    ),
    AttributeDef(
        name="branch",
        type_name="string",
        description="The branch in the archimate project",
        display_name="Branch"
    ),
    AttributeDef(
        name="ArchiMateReference",
        type_name="array<m4i_referenceable>",
        cardinality=Cardinality.SET,
        description="A list of references to the archimate project",
        display_name="Archimate References"
    )
]

archimate_project_super_type = ["Referenceable"]

archimate_project_def = EntityDef(
    category=TypeCategory.ENTITY,
    description="Representation for a generic Archimate Project",
    name="m4i_archimate_project",
    type_version="1.0",
    super_types=archimate_project_super_type,
    attribute_defs=archimate_project_attributes_def,
)

end_1_referenceable_projects = RelationshipEndDef(
    type="m4i_referenceable",
    name="ArchiMateReference",
    cardinality=Cardinality.SET
)
end_2_archimate_projects = RelationshipEndDef(
    type="m4i_archimate_project",
    name="ArchiMateReference",
    cardinality=Cardinality.SET
)

m4i_archimate_project_rel_def = RelationshipDef(
    end_def1=end_1_referenceable_projects,
    end_def2=end_2_archimate_projects,
    name="m4i_referenceable_archimate_reference_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="This relationship demonstrates the connection between the referenced objects on Atlas to those in Archimate"
)


# END TypeDef for Entity & Relationships

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessArchimateAttributesBase(M4IAttributesBase):
    name: str
    branch: str
    archimate_reference: ObjectId


# END BusinessArchimateAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessArchimateAttributesDefaultsBase(Attributes):
    pass


# END BusinessArchimateAttributesDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessArchimateAttributes(BusinessArchimateAttributesDefaultsBase, BusinessArchimateAttributesBase):
    pass


# END BusinessArchimateAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessArchimateBase(EntityBase):
    attributes: BusinessArchimateAttributes


# END BusinessArchimateBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessArchimateDefaultsBase(EntityDefaultsBase):
    pass


# END BusinessArchimateDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessArchimate(Entity,
                        BusinessArchimateDefaultsBase,
                        BusinessArchimateBase):
    type_name: str = "m4i_archimate_project"

    @classmethod
    def get_type_def(cls):
        return archimate_project_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this archimate reference:
        * archimate_reference
        """
        references = [
            self.attributes.archimate_reference
        ]

        return references
    # END get_referred_entities

# END BusinessArchimate
