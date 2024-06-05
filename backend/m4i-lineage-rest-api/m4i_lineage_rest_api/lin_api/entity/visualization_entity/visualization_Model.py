from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import (ObjectId, M4IAttributes, Visualization as CoreVisualization,
                            VisualizationAttributes as CoreVisualizationAttributes)
from typing import Optional, List

from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class VisualizationBase(DataClassJsonMixin):
    name: str
    qualified_name: str

    def _qualified_name(self):
        """
        Returns the qualified name of the Visualization based on its `name`
        """
        # VisualizationQualifiedName is based on confluent_environment
        return get_qualified_name(
            self.qualified_name
        )
    # END _qualified_name


# END VisualizationBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class VisualizationDefaultsBase(DataClassJsonMixin):
    type: Optional[str] = None
    updated_at: Optional[str] = None
    version: Optional[str] = None
    visualization_type: Optional[str] = None
    creator: Optional[List[str]] = None
    parent_dataset: Optional[List[str]] = None
    child_dataset: Optional[List[str]] = None


# END VisualizationDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Visualization(
    VisualizationDefaultsBase,
    VisualizationBase
):

    def convert_to_atlas(self) -> CoreVisualization:
        """
        Returns a corresponding Atlas `Visualization` instance.
        """
        attributes = CoreVisualizationAttributes(
            type=self.type,
            updated_at=self.updated_at,
            version=self.version,
            visualization_type=self.visualization_type,
            name=self.name,
            qualified_name=self._qualified_name()
        )

        # Object Relationships
        # Child Dataset
        if bool(self.child_dataset):
            child_dataset_list = []
            for child_dataset in self.child_dataset:
                unique_attributes = M4IAttributes(
                    qualified_name=child_dataset
                )
                child_dataset_list.append(ObjectId(
                    type_name="m4i_index_pattern",
                    unique_attributes=unique_attributes)
                )
            attributes.child_dataset = child_dataset_list
        # END IF

        # Parent Dataset
        if bool(self.parent_dataset):
            parent_dataset_list = []
            for parent_dataset in self.parent_dataset:
                unique_attributes = M4IAttributes(
                    qualified_name=parent_dataset
                )
                parent_dataset_list.append(ObjectId(
                    type_name="m4i_dashboard",
                    unique_attributes=unique_attributes)
                )
            attributes.parent_dataset = parent_dataset_list
        # END IF

        # Creator
        if bool(self.creator):
            creator_list = []
            for creator in self.creator:
                unique_attributes = M4IAttributes(
                    qualified_name=creator
                )
                creator_list.append(ObjectId(
                    type_name="m4i_person",
                    unique_attributes=unique_attributes)
                )
            attributes.creator = creator_list
        # END IF

        entity = CoreVisualization(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END Visualization
