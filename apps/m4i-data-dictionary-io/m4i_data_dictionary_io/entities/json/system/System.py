from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from m4i_atlas_core import BusinessSystem, BusinessSystemAttributes, M4IAttributes, ObjectId
from ..base_object import BaseObject
from ..ToAtlasConvertible import ToAtlasConvertible
from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SystemBase(BaseObject):

    name: str

    def _qualified_name(self):
        """
        Returns the qualified name of the system based on its `name`
        """

        return get_qualified_name(self.name)
    # END _qualified_name
# END SystemBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SystemDefaultsBase(DataClassJsonMixin):

    definition: Optional[str] = None
    source: Optional[str] = None

# END SystemDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class System(
    SystemDefaultsBase,
    SystemBase,
    ToAtlasConvertible[BusinessSystem]
):
    def convert_to_atlas(self) -> BusinessSystem:
        """
        Returns a corresponding Atlas `BusinessSystem` instance.
        """

        attributes = BusinessSystemAttributes(
            definition=self.definition,
            name=self.name,
            qualified_name=self.qualified_name,
        )

        if bool(self.source):
            unique_attributes = M4IAttributes(
                qualified_name=self.source
            )

            source = ObjectId(
                type_name="m4i_source",
                unique_attributes=unique_attributes
            )

            attributes.source = [source]
        # END IF

        entity = BusinessSystem(
            attributes=attributes,
        )


        return entity
    # END convert_to_atlas
# END System
