from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Attributes, Cardinality, Entity, EntityBase,
                    EntityDef, EntityDefaultsBase, ObjectId, RelationshipDef,
                    RelationshipEndDef, TypeCategory)
from ..m4i.M4IAttributes import M4IAttributesBase

atlas_collection_attributes_def = [
    AttributeDef(
        name="name",
        type_name="string",
        description="The unique functional name of the  collection",
        display_name="Name"
    ),
    AttributeDef(
        name="definition",
        type_name="string",
        description="The definition of the collection",
        display_name="Definition"
    ),
    AttributeDef(
        name="systems",
        type_name="array<m4i_system>",
        is_indexable=False,
        description="The functional name of the system that the collection belongs to",
        display_name="System",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="datasets",
        type_name="array<m4i_dataset>",
        is_indexable=False,
        description="The functional names of the datasets that belong to the collection",
        display_name="Datasets",
        cardinality=Cardinality.SET
    )
]

collection_super_type = ["m4i_referenceable"]

atlas_collection_def = EntityDef(
    category=TypeCategory.ENTITY,
    description="Represents a specific collection in the organization",
    name="m4i_collection",
    type_version="1.0",
    attribute_defs=atlas_collection_attributes_def,
    super_types=collection_super_type
)

end_1_collection_system = RelationshipEndDef(
    type="m4i_collection",
    name="systems",
    cardinality=Cardinality.SET
)
end_2_collection_system = RelationshipEndDef(
    type="m4i_system",
    name="collections",
    cardinality=Cardinality.SET
)

m4i_collection_system_rel_def = RelationshipDef(
    end_def1=end_1_collection_system,
    end_def2=end_2_collection_system,
    name="m4i_collection_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the system and the collection"
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessCollectionAttributesBase(M4IAttributesBase):
    name: str
# END BusinessCollectionsAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessCollectionAttributesDefaultsBase(Attributes):
    definition: Optional[str] = None
    datasets: List[ObjectId] = field(default_factory=list)
    source: List[ObjectId] = field(default_factory=list)
    systems: List[ObjectId] = field(default_factory=list)
# END BusinessCollectionAttributesDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessCollectionAttributes(BusinessCollectionAttributesDefaultsBase, BusinessCollectionAttributesBase):
    pass
# END BusinessCollectionAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessCollectionBase(EntityBase):
    attributes: BusinessCollectionAttributes
# END BusinessCollectionBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessCollectionDefaultsBase(EntityDefaultsBase):
    pass
# END BusinessCollectionDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessCollection(BusinessCollectionDefaultsBase, BusinessCollectionBase, Entity):
    type_name: str = "m4i_collection"

    @classmethod
    def get_type_def(cls):
        return atlas_collection_def

    def get_parents(self) -> Iterable[ObjectId]:
        return self.attributes.systems
    # END get_parents

    def get_children(self) -> Iterable[ObjectId]:
        return self.attributes.datasets
    # END get_children

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the systems, datasets and sources referenced by this collection
        """
        references = [
            *self.attributes.systems,
            *self.attributes.datasets,
            *self.attributes.source
        ]

        return filter(None, references)
    # END get_referred_entities

# END BusinessCollection
