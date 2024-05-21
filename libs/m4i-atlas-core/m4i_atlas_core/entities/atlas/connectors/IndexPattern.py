from dataclasses import dataclass
from typing import Iterable, Optional, List

from dataclasses_json import LetterCase, dataclass_json

from ..core import AttributeDef, EntityDef, ObjectId, TypeCategory, Cardinality, RelationshipEndDef, RelationshipDef
from ..data_dictionary import (BusinessCollection,
                               BusinessCollectionAttributes,
                               BusinessCollectionAttributesBase,
                               BusinessCollectionAttributesDefaultsBase,
                               BusinessCollectionBase,
                               BusinessCollectionDefaultsBase, BusinessDataset,
                               BusinessDatasetAttributes,
                               BusinessDatasetAttributesBase,
                               BusinessDatasetAttributesDefaultsBase,
                               BusinessDatasetBase,
                               BusinessDatasetDefaultsBase)

index_pattern_super_type = ["m4i_dataset", "m4i_collection"]

index_pattern_attributes_def = [
    AttributeDef(
        name="creator",
        type_name="array<m4i_person>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="indexPattern",
        type_name="string"
    ),
    AttributeDef(
        name="updatedAt",
        type_name="string"
    ),
    AttributeDef(
        name="version",
        type_name="string"
    ),

]

index_pattern_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_index_pattern",
    description="A type definition for a generic Index Pattern in the context of models4insight.com",
    type_version="1.0",
    super_types=index_pattern_super_type,
    attribute_defs=index_pattern_attributes_def
)

end_1_person_index_pattern = RelationshipEndDef(
    type="m4i_person",
    name="indexPatterns",
)
end_2_person_index_pattern = RelationshipEndDef(
    type="m4i_index_pattern",
    name="creator",
)

m4i_person_index_pattern_rel_def = RelationshipDef(
    end_def1=end_1_person_index_pattern,
    end_def2=end_2_person_index_pattern,
    name="m4i_person_index_pattern_assignment",
    category=TypeCategory.RELATIONSHIP
)

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IndexPatternAttributesBase(BusinessDatasetAttributesBase,
                                 BusinessCollectionAttributesBase):
    creator: List[ObjectId]


# END IndexPatternAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IndexPatternAttributesDefaultsBase(BusinessDatasetAttributesDefaultsBase,
                                         BusinessCollectionAttributesDefaultsBase):
    description: Optional[str] = None
    index_pattern: Optional[str] = None
    updated_at: Optional[str] = None
    version: Optional[str] = None


# END IndexPatternAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IndexPatternAttributes(BusinessDatasetAttributes,
                             BusinessCollectionAttributes,
                             IndexPatternAttributesDefaultsBase, IndexPatternAttributesBase):
    pass


# END IndexPatternAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IndexPatternBase(BusinessDatasetBase, BusinessCollectionBase):
    attributes: IndexPatternAttributes


# END IndexPatternBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IndexPatternDefaultsBase(BusinessDatasetDefaultsBase, BusinessCollectionDefaultsBase):
    pass


# END IndexPatternDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IndexPattern(BusinessDataset, BusinessCollection,
                   IndexPatternDefaultsBase,
                   IndexPatternBase
                   ):
    type_name: str = "m4i_index_pattern"

    @classmethod
    def get_type_def(cls):
        return index_pattern_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this IndexPattern:
        * Parent Dataset
        * Atlas Person
        """

        references = [
            *super().get_referred_entities(),
            *self.attributes.creator
        ]

        return filter(None, references)
    # END get_referred_entities

# END IndexPattern
