from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Attributes, Cardinality, Entity, EntityBase,
                    EntityDef, EntityDefaultsBase, ObjectId, PropagateTags,
                    RelationshipDef, RelationshipEndDef, TypeCategory)
from ..m4i.M4IAttributes import M4IAttributesBase

atlas_dataset_attributes_def = [
    AttributeDef(
        name="definition",
        type_name="string",
        description="The definition of the dataset",
        display_name="Definition"
    ),
    AttributeDef(
        name="fields",
        type_name="array<m4i_field>",
        is_indexable=False,
        description="The functional names of the data fields that belong to this data set",
        display_name="Data Fields",
        cardinality=Cardinality.SET
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
        name="parentDataset",
        type_name="array<m4i_dataset>",
        is_indexable=False,
        description="The functional names of the dataset that the dataset belongs to",
        display_name="Parent Dataset",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="childDataset",
        type_name="array<m4i_dataset>",
        is_indexable=False,
        description="The functional names of the dataset that belong to the dataset",
        display_name="Child Dataset",
        cardinality=Cardinality.SET
    )
]

dataset_super_type = ["m4i_referenceable", "DataSet"]

atlas_dataset_def = EntityDef(
    category=TypeCategory.ENTITY,
    description="A type definition for a generic dataset",
    name="m4i_dataset",
    type_version="1.0",
    attribute_defs=atlas_dataset_attributes_def,
    super_types=dataset_super_type
)

end_1_pdataset_cdataset = RelationshipEndDef(
    type="m4i_dataset",
    name="parentDataset"
)
end_2_pdataset_cdataset = RelationshipEndDef(
    type="m4i_dataset",
    name="childDataset"
)

m4i_pdataset_cdataset_rel_def = RelationshipDef(
    end_def1=end_1_pdataset_cdataset,
    end_def2=end_2_pdataset_cdataset,
    name="m4i_dataset_parent_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the dataset to other datasets"
)

end_1_dataset_collection = RelationshipEndDef(
    type="m4i_dataset",
    name="collections",
    cardinality=Cardinality.SET
)
end_2_dataset_collection = RelationshipEndDef(
    type="m4i_collection",
    name="datasets",
    cardinality=Cardinality.SET
)

m4i_dataset_collection_rel_def = RelationshipDef(
    end_def1=end_1_dataset_collection,
    end_def2=end_2_dataset_collection,
    name="m4i_dataset_assignment",
    category=TypeCategory.RELATIONSHIP,
    propagate_tags=PropagateTags.ONE_TO_TWO,
    type_version="1.0",
    description="The relationship between the collection and the dataset"
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDatasetAttributesBase(M4IAttributesBase):
    name: str
# END BusinessDatasetsAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDatasetAttributesDefaultsBase(Attributes):
    definition: Optional[str] = None
    collections: List[ObjectId] = field(default_factory=list)
    parent_dataset: List[ObjectId] = field(default_factory=list)
    child_dataset: List[ObjectId] = field(default_factory=list)
    fields: List[ObjectId] = field(default_factory=list)
    source: List[ObjectId] = field(default_factory=list)
# END BusinessDatasetAttributesDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDatasetAttributes(BusinessDatasetAttributesDefaultsBase, BusinessDatasetAttributesBase):
    pass
# END BusinessDatasetAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDatasetBase(EntityBase):
    attributes: BusinessDatasetAttributes
# END BusinessDatasetBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDatasetDefaultsBase(EntityDefaultsBase):
    pass
# END BusinessDatasetDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataset(BusinessDatasetDefaultsBase, BusinessDatasetBase, Entity):
    type_name: str = "m4i_dataset"

    @classmethod
    def get_type_def(cls):
        return atlas_dataset_def

    def get_parents(self) -> Iterable[ObjectId]:
        return [*self.attributes.parent_dataset, *self.attributes.collections]
    # END get_parents

    def get_children(self) -> Iterable[ObjectId]:
        return [*self.attributes.child_dataset, *self.attributes.fields]
    # END get_children

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the collection referenced by this dataset
        """
        references = [*self.attributes.collections]

        if self.attributes.fields is not None:
            references = [*references, *self.attributes.fields]
        # END IF

        if self.attributes.parent_dataset is not None:
            references = [*references, *self.attributes.parent_dataset]
        # END IF

        if self.attributes.child_dataset is not None:
            references = [*references, *self.attributes.child_dataset]
        # END IF

        if self.attributes.source is not None:
            references = [*references, *self.attributes.source]
        # END IF

        return filter(None, references)

    # END get_referred_entities

# END BusinessDataset
