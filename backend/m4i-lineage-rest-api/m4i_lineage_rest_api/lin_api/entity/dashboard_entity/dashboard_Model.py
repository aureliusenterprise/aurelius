from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import (ObjectId, Dashboard as CoreDashboard, M4IAttributes,
                            DashboardAttributes as CoreDashboardAttributes)
from typing import Optional, List

from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DashboardBase(DataClassJsonMixin):
    name: str
    qualified_name: str

    def _qualified_name(self):
        """
        Returns the qualified name of the Dashboard based on its `name`
        """
        return get_qualified_name(
            self.qualified_name
        )
    # END _qualified_name


# END DashboardBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DashboardDefaultsBase(DataClassJsonMixin):
    description: Optional[str] = None
    updated_at: Optional[str] = None
    version: Optional[str] = None
    creator: Optional[List[str]] = None
    child_dataset: Optional[List[str]] = None
    kibana_space: Optional[str] = None


# END DashboardDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Dashboard(
    DashboardDefaultsBase,
    DashboardBase
):

    def convert_to_atlas(self) -> CoreDashboard:
        """
        Returns a corresponding Atlas `Dashboard` instance.
        """
        attributes = CoreDashboardAttributes(
            updated_at=self.updated_at,
            version=self.version,
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
                    type_name="m4i_visualization",
                    unique_attributes=unique_attributes)
                )
            attributes.child_dataset = child_dataset_list
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

        # Kibana Space
        if bool(self.kibana_space):
            unique_attributes = M4IAttributes(
                qualified_name=self.kibana_space
            )

            kibana_space = ObjectId(
                type_name="m4i_kibana_space",
                unique_attributes=unique_attributes
            )

            attributes.kibana_space = [kibana_space]
        # END IF

        entity = CoreDashboard(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END Dashboard
