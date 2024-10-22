from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from m4i_atlas_core import AtlasPerson, AtlasPersonAttributes, M4IAttributes, ObjectId
from ..ToAtlasConvertible import ToAtlasConvertible


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PersonBase(DataClassJsonMixin):

    email: str

# END PersonBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PersonDefaultsBase(DataClassJsonMixin):

    name: Optional[str] = None
    source: Optional[str] = None

# END PersonDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Person(
    PersonDefaultsBase,
    PersonBase,
    ToAtlasConvertible[AtlasPerson]
):

    def convert_to_atlas(self) -> AtlasPerson:
        """
        Returns a corresponding Atlas `AtlasPerson` instance.
        """

        attributes = AtlasPersonAttributes(
            email=self.email,
            name=self.name,
            qualified_name=self.email
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

        entity = AtlasPerson(
            attributes=attributes,
        )

        return entity
    # END convert_to_atlas

# END Person
