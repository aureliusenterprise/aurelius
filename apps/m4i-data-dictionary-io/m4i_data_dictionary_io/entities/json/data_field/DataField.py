from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import (
    BusinessField,
    BusinessFieldAttributes,
    M4IAttributes,
    ObjectId,
)

from ..base_object import BaseObject
from ..ToAtlasConvertible import ToAtlasConvertible
from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataFieldBase(BaseObject):
    dataset: str
    name: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataFieldDefaultsBase(DataClassJsonMixin):
    attribute: Optional[str] = None
    definition: Optional[str] = None
    field_type: Optional[str] = None
    parent_field: Optional[str] = None
    source: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataField(
    DataFieldDefaultsBase,
    DataFieldBase,
    ToAtlasConvertible[BusinessField],
):
    def convert_to_atlas(self) -> BusinessField:
        """
        Returns a corresponding Atlas `BusinessField` instance.
        """

        if bool(self.attribute):
            attribute_unique_attributes = M4IAttributes(qualified_name=self.attribute)

            attribute = ObjectId(
                type_name="m4i_data_attribute",
                unique_attributes=attribute_unique_attributes,
            )

       
        attributes = BusinessFieldAttributes(
            attributes=[attribute] if bool(self.attribute) else [],
            definition=self.definition,
            field_type=self.field_type,
            name=self.name,
            qualified_name=self.qualified_name,
        )

        if bool(self.parent_field):
            parent_field_unique_attributes = M4IAttributes(
                qualified_name=self.parent_field
            )

            parent_field = ObjectId(
                type_name="m4i_data_field",
                unique_attributes=parent_field_unique_attributes,
            )

            attributes.parent_field = [parent_field]
        
        else:
            dataset_unique_attributes = M4IAttributes(qualified_name=self.dataset)

            dataset = ObjectId(
                type_name="m4i_dataset", unique_attributes=dataset_unique_attributes
            )

            attributes.datasets = [dataset]

        if bool(self.source):
            unique_attributes = M4IAttributes(qualified_name=self.source)

            source = ObjectId(
                type_name="m4i_source", unique_attributes=unique_attributes
            )

            attributes.source = [source]

        entity = BusinessField(
            attributes=attributes,
        )

        return entity

    def _qualified_name(self):
        """
        Returns the qualified name of the field based on either the parent field or the dataset and the name of the field.
        """
        return get_qualified_name(
            self.name,
            prefix=self.parent_field if self.parent_field else self.dataset,
        )
