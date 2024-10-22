from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, BusinessDataQuality, BusinessDataQualityAttributes

from m4i_atlas_core import M4IAttributes
from ..base_object import BaseObject
from ..ToAtlasConvertible import ToAtlasConvertible
from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataQualityBase(BaseObject):
    data_field: str
    id: str

    def _qualified_name(self):
        """
        Returns the qualified name of the Quality based on its `name`
        """
        # DataQualityQualifiedName is based on name and id
        return get_qualified_name(
            self.id,
            prefix=self.data_field
        )
    # END _qualified_name
# END DataQualityBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataQualityDefaultsBase(DataClassJsonMixin):
    rule_description: Optional[str] = None
    expression: Optional[str] = None
    active: Optional[str] = None
    expression_version: Optional[str] = None
    business_rule_description: Optional[str] = None
    filter_required: Optional[str] = None
    quality_dimension: Optional[str] = None
    source: Optional[str] = None
# END DataQualityDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataQuality(
    DataQualityDefaultsBase,
    DataQualityBase,
    ToAtlasConvertible[BusinessDataQuality]
):
    def convert_to_atlas(self) -> BusinessDataQuality:
        """
        Returns a corresponding Atlas `BusinessDataQuality` instance.
        """
        data_field_unique_attributes = M4IAttributes(
            qualified_name=self.data_field
        )

        data_field = ObjectId(
            type_name="m4i_field",
            unique_attributes=data_field_unique_attributes
        )

        attributes = BusinessDataQualityAttributes(
            id=self.id,
            name=self.qualified_name,
            rule_description=self.rule_description,
            expression=self.expression,
            active=bool(self.active),
            expression_version=self.expression_version,
            business_rule_description=self.business_rule_description,
            filter_required=bool(self.filter_required),
            quality_dimension=self.quality_dimension,
            qualified_name=self.qualified_name,
            fields=[data_field]
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

        entity = BusinessDataQuality(
            attributes=attributes,
        )

        return entity
    # END convert_to_atlas
# END DataQuality
