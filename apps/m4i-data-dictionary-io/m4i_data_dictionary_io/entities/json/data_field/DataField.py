from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, BusinessField, BusinessFieldAttributes

from m4i_atlas_core import M4IAttributes
from ..base_object import BaseObject
from ..ToAtlasConvertible import ToAtlasConvertible
from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataFieldBase(BaseObject):

    dataset: str
    name: str

    def _qualified_name(self):
        """
        Returns the qualified name of the field based on its parent `dataset` and its `name`
        """

        return get_qualified_name(
            self.name,
            prefix=self.dataset
        )
    # END _qualified_name
# END DataFieldBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataFieldDefaultsBase(DataClassJsonMixin):

    attribute: Optional[str] = None
    definition: Optional[str] = None
    field_type: Optional[str] = None
    source: Optional[str] = None

# END DataFieldDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataField(
    DataFieldDefaultsBase,
    DataFieldBase,
    ToAtlasConvertible[BusinessField]
):
    def convert_to_atlas(self) -> BusinessField:
        """
        Returns a corresponding Atlas `BusinessField` instance.
        """

        if bool(self.attribute):
            attribute_unique_attributes = M4IAttributes(
                qualified_name=self.attribute
            )

            attribute = ObjectId(
                type_name="m4i_data_attribute",
                unique_attributes=attribute_unique_attributes
            )

        dataset_unique_attributes = M4IAttributes(
            qualified_name=self.dataset
        )

        dataset = ObjectId(
            type_name="m4i_dataset",
            unique_attributes=dataset_unique_attributes
        )

        attributes = BusinessFieldAttributes(
            attributes=[attribute] if bool(self.attribute) else [],
            datasets=[dataset],
            definition=self.definition,
            field_type=self.field_type,
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

        entity = BusinessField(
            attributes=attributes,
        )

        return entity
    # END convert_to_atlas
# END DataField

