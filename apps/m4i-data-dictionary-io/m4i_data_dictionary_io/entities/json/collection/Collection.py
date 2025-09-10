from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, BusinessCollection, BusinessCollectionAttributes

from m4i_atlas_core import M4IAttributes
from ..base_object import BaseObject
from ..ToAtlasConvertible import ToAtlasConvertible
from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CollectionBase(BaseObject):

    name: str
    system: str

    def _qualified_name(self):
        """
        Returns the qualified name of the collection based on the parent `system` and its `name`
        """

        return get_qualified_name(
            self.name,
            prefix=self.system
        )
    # END _qualified_name
# END CollectionBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CollectionDefaultsBase(DataClassJsonMixin):

    definition: Optional[str] = None
    source: Optional[str] = None

# END CollectionDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Collection(
    CollectionDefaultsBase,
    CollectionBase,
    ToAtlasConvertible[BusinessCollection]
):
    def convert_to_atlas(self) -> BusinessCollection:
        """
        Returns a corresponding Atlas `BusinessCollection` instance.
        """

        unique_attributes = M4IAttributes(
            qualified_name=self.system
        )

        system = ObjectId(
            type_name="m4i_system",
            unique_attributes=unique_attributes
        )

        attributes = BusinessCollectionAttributes(
            definition=self.definition,
            name=self.name,
            qualified_name=self.qualified_name,
            systems=[system]
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

        entity = BusinessCollection(
            attributes=attributes,
        )

        return entity
    # END convert_to_atlas
# END Collection
