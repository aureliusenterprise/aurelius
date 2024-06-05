from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import (ObjectId, M4IAttributes, IndexPattern as CoreIndexPattern,
                            IndexPatternAttributes as CoreIndexPatternAttributes)
from typing import Optional, List

from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IndexPatternBase(DataClassJsonMixin):
    name: str
    qualified_name: str

    def _qualified_name(self):
        """
        Returns the qualified name of the IndexPattern based on its `name`
        """
        return get_qualified_name(
            self.qualified_name
        )
    # END _qualified_name


# END IndexPatternBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IndexPatternDefaultsBase(DataClassJsonMixin):
    description: Optional[str] = None
    index_pattern: Optional[str] = None
    updated_at: Optional[str] = None
    version: Optional[str] = None
    creator: Optional[List[str]] = None
    parent_dataset: Optional[List[str]] = None


# END IndexPatternDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IndexPattern(
    IndexPatternDefaultsBase,
    IndexPatternBase
):

    def convert_to_atlas(self) -> CoreIndexPattern:
        """
        Returns a corresponding Atlas `IndexPattern` instance.
        """

        # Object Relationships
        # Parent Dataset
        attr_parent_dataset = None
        if bool(self.parent_dataset):
            parent_dataset_list = []
            for parent_dataset in self.parent_dataset:
                unique_attributes = M4IAttributes(
                    qualified_name=parent_dataset
                )
                parent_dataset_list.append(ObjectId(
                    type_name="m4i_visualization",
                    unique_attributes=unique_attributes)
                )
            attr_parent_dataset = parent_dataset_list
        # END IF

        # Creator
        attr_creator = None
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
            attr_creator = creator_list
        # END IF

        attributes = CoreIndexPatternAttributes(
            updated_at=self.updated_at,
            version=self.version,
            name=self.name,
            creator=attr_creator,
            qualified_name=self._qualified_name(),
            parent_dataset=attr_parent_dataset,
            description=self.description
        )

        entity = CoreIndexPattern(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END IndexPattern
