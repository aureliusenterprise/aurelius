from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import (ObjectId, M4IAttributes, ConfluentCloud as CoreConfluentCloud,
                            ConfluentCloudAttributes as CoreConfluentCloudAttributes)
from typing import List

from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentCloudBase(DataClassJsonMixin):
    name: str

    def _qualified_name(self):
        """
        Returns the qualified name of the ConfluentCloud based on its `confluent_environment`
        """
        # ConfluentCloudQualifiedName is based on confluent_environment
        return get_qualified_name(
            self.name
        )
    # END _qualified_name


# END ConfluentCloudBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentCloudDefaultsBase(DataClassJsonMixin):
    confluent_environment: List[str] = field(default_factory=list)


# END ConfluentCloudDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentCloud(
    ConfluentCloudDefaultsBase,
    ConfluentCloudBase
):

    def convert_to_atlas(self) -> CoreConfluentCloud:
        """
        Returns a corresponding Atlas `ConfluentCloud` instance.
        """
        attributes = CoreConfluentCloudAttributes(
            name=self.name,
            qualified_name=self._qualified_name()
        )

        if bool(self.confluent_environment):
            confluent_environment: List[ObjectId] = []
            for ce in self.confluent_environment:
                confluent_environment_unique_attributes = M4IAttributes(
                    qualified_name=ce
                )
                confluent_environment.append(ObjectId(
                    type_name="m4i_confluent_environment",
                    unique_attributes=confluent_environment_unique_attributes
                ))
            # END FOR
            attributes.confluent_environment = confluent_environment
        # END IF

        entity = CoreConfluentCloud(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END ConfluentCloud
