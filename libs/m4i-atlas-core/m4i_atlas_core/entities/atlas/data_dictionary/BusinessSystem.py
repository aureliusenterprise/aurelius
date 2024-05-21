from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Attributes, Cardinality, Entity, EntityBase,
                    EntityDef, EntityDefaultsBase, ObjectId, RelationshipDef,
                    RelationshipEndDef, TypeCategory)
from ..m4i.M4IAttributes import M4IAttributesBase

atlas_system_attributes_def = [
    AttributeDef(
        name="name",
        type_name="string",
        description="The unique functional name of the system",
        display_name="Name"
    ),
    AttributeDef(
        name="definition",
        type_name="string",
        description="The definition of the system",
        display_name="Definition"
    ),
    AttributeDef(
        name="collections",
        type_name="array<m4i_collection>",
        is_indexable=False,
        description="The functional name of the collection that the dataset belongs to",
        display_name="Collection",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="parentSystem",
        type_name="array<m4i_system>",
        is_indexable=False,
        description="The functional names of the System that the System belongs to",
        display_name="Parent System",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="childSystem",
        type_name="array<m4i_system>",
        is_indexable=False,
        description="The functional names of the System that belong to the System",
        display_name="Child System",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="processes",
        type_name="array<m4i_generic_process>",
        is_indexable=False,
        description="The functional names of the Process that belong to the System",
        display_name="Child Process",
        cardinality=Cardinality.SET
    )
]

atlas_system_super_type = ["m4i_referenceable"]

atlas_system_def = EntityDef(
    category=TypeCategory.ENTITY,
    description="Represents a generic system",
    name="m4i_system",
    type_version="1.0",
    attribute_defs=atlas_system_attributes_def,
    super_types=atlas_system_super_type
)

end_1_psystem_csystem = RelationshipEndDef(
    type="m4i_system",
    name="parentSystem",
    cardinality=Cardinality.SET
)
end_2_psystem_csystem = RelationshipEndDef(
    type="m4i_system",
    name="childSystem",
    cardinality=Cardinality.SET
)

m4i_psystem_csystem_rel_def = RelationshipDef(
    end_def1=end_1_psystem_csystem,
    end_def2=end_2_psystem_csystem,
    name="m4i_system_parent_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the system to other systems"
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSystemAttributesBase(M4IAttributesBase):
    name: str
# END BusinessSystemsAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSystemAttributesDefaultsBase(Attributes):
    collections: List[ObjectId] = field(default_factory=list)
    definition: Optional[str] = None
    parent_system: List[ObjectId] = field(default_factory=list)
    child_system: List[ObjectId] = field(default_factory=list)
    processes: List[ObjectId] = field(default_factory=list)
    source: List[ObjectId] = field(default_factory=list)
# END BusinessSystemAttributesDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSystemAttributes(BusinessSystemAttributesDefaultsBase, BusinessSystemAttributesBase):
    pass
# END BusinessSystemAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSystemBase(EntityBase):
    attributes: BusinessSystemAttributes
# END BusinessSystemBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSystemDefaultsBase(EntityDefaultsBase):
    pass
# END BusinessSystemDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessSystem(BusinessSystemDefaultsBase, BusinessSystemBase, Entity):
    type_name: str = "m4i_system"

    @classmethod
    def get_type_def(cls):
        return atlas_system_def

    def get_parents(self) -> Iterable[ObjectId]:
        return self.attributes.parent_system
    # END get_parents

    def get_children(self) -> Iterable[ObjectId]:
        return [*self.attributes.child_system, *self.attributes.collections]
    # END get_children

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the collection referenced by this dataset
        """
        references = [
            *self.attributes.collections,
            *self.attributes.parent_system,
            *self.attributes.child_system,
            *self.attributes.processes,
            *self.attributes.source
        ]

        return filter(None, references)
# END BusinessSystem
