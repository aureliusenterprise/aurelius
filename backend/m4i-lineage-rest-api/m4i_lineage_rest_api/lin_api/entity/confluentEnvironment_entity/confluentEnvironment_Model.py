from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import (ObjectId, M4IAttributes, ConfluentEnvironment as CoreConfluentEnvironment,
                            ConfluentEnvironmentAttributes as CoreConfluentEnvironmentAttributes)
from typing import Optional, List

from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentEnvironmentBase(DataClassJsonMixin):
    name: str
    confluent_cloud: Optional[str] = None
    schema_registry: Optional[bool] = False

    def _qualified_name(self):
        """
        Returns the qualified name of the ConfluentEnvironment based on its `name`
        """
        # ConfluentEnvironmentQualifiedName is based on name
        return get_qualified_name(
            self.name,
            prefix=self.confluent_cloud
        )
    # END _qualified_name


# END ConfluentEnvironmentBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentEnvironmentDefaultsBase(DataClassJsonMixin):
    pass


# END ConfluentEnvironmentDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentEnvironment(
    ConfluentEnvironmentDefaultsBase,
    ConfluentEnvironmentBase
):
    def convert_to_atlas(self) -> CoreConfluentEnvironment:
        """
        Returns a corresponding Atlas `ConfluentEnvironment` instance.
        """
        confluent_cloud: List[ObjectId] = []

        confluent_cloud_unique_attributes = M4IAttributes(
            qualified_name=self.confluent_cloud
        )
        confluent_cloud.append(ObjectId(
            type_name="m4i_confluent_cloud",
            unique_attributes=confluent_cloud_unique_attributes
        ))

        attributes = CoreConfluentEnvironmentAttributes(
            schema_registry=self.schema_registry,
            name=self.name,
            confluent_cloud=confluent_cloud,
            qualified_name=self._qualified_name()
        )

        entity = CoreConfluentEnvironment(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END ConfluentEnvironment
