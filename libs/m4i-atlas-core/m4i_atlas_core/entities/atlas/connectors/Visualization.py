from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import AttributeDef, Cardinality, EntityDef, ObjectId, TypeCategory, RelationshipEndDef, RelationshipDef
from ..data_dictionary import (BusinessDataset, BusinessDatasetAttributes,
                               BusinessDatasetAttributesBase,
                               BusinessDatasetAttributesDefaultsBase,
                               BusinessDatasetBase,
                               BusinessDatasetDefaultsBase)

visualization_super_type = ["m4i_dataset"]

visualization_attributes_def = [
    AttributeDef(
        name="type",
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
    AttributeDef(
        name="creator",
        type_name="array<m4i_person>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="visualizationType",
        type_name="string"
    )
]

visualization_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_visualization",
    description="A type definition for a generic Virtualization in the context of models4insight.com",
    type_version="1.0",
    super_types=visualization_super_type,
    attribute_defs=visualization_attributes_def
)

end_1_person_visualization = RelationshipEndDef(
    type="m4i_person",
    name="visualizations",
)
end_2_person_visualization = RelationshipEndDef(
    type="m4i_visualization",
    name="creator",
)

m4i_person_visualization_rel_def = RelationshipDef(
    end_def1=end_1_person_visualization,
    end_def2=end_2_person_visualization,
    name="m4i_person_visualization_assignment",
    category=TypeCategory.RELATIONSHIP
)

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class VisualizationAttributesBase(BusinessDatasetAttributesBase):
    pass


# END VisualizationAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class VisualizationAttributesDefaultsBase(BusinessDatasetAttributesDefaultsBase):
    type: Optional[str] = None
    updated_at: Optional[str] = None
    version: Optional[str] = None
    visualization_type: Optional[str] = None
    creator: List[ObjectId] = field(default_factory=list)


# END VisualizationAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class VisualizationAttributes(BusinessDatasetAttributes,
                              VisualizationAttributesDefaultsBase, VisualizationAttributesBase):
    pass


# END VisualizationAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class VisualizationBase(BusinessDatasetBase):
    attributes: VisualizationAttributes


# END VisualizationBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class VisualizationDefaultsBase(BusinessDatasetDefaultsBase):
    pass


# END VisualizationDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Visualization(BusinessDataset,
                    VisualizationDefaultsBase,
                    VisualizationBase,
                    ):
    type_name: str = "m4i_visualization"

    @classmethod
    def get_type_def(cls):
        return visualization_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Visualization:
        * Atlas Person
        """

        references = [
            *super().get_referred_entities(),
            *self.attributes.creator
        ]

        return filter(None, references)
    # END get_referred_entities

# END Visualization
