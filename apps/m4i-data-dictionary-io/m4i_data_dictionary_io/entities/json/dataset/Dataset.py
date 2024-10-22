from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, BusinessDataset, BusinessDatasetAttributes

from m4i_atlas_core import M4IAttributes
from ..base_object import BaseObject
from ..ToAtlasConvertible import ToAtlasConvertible
from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DatasetBase(BaseObject):

    collection: str
    name: str

    def _qualified_name(self):
        """
        Returns the qualified name of the dataset based on its parent `collection` and its `name`
        """

        return get_qualified_name(
            self.name,
            prefix=self.collection
        )
    # END _qualified_name
# END DatasetBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DatasetDefaultsBase(DataClassJsonMixin):

    definition: Optional[str] = None
    source: Optional[str] = None

# END DatasetDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Dataset(
    DatasetDefaultsBase,
    DatasetBase,
    ToAtlasConvertible[BusinessDataset]
):
    def convert_to_atlas(self) -> BusinessDataset:
        """
        Returns a corresponding Atlas `BusinessDataset` instance.
        """

        collection_unique_attributes = M4IAttributes(
            qualified_name=self.collection
        )

        collection = ObjectId(
            type_name="m4i_collection",
            unique_attributes=collection_unique_attributes
        )

        attributes = BusinessDatasetAttributes(
            collections=[collection],
            definition=self.definition,
            name=self.name,
            qualified_name=self.qualified_name
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

        entity = BusinessDataset(
            attributes=attributes,
        )

        return entity
    # END convert_to_atlas
# END Dataset
