from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, BusinessDataAttribute, BusinessDataAttributeAttributes, Classification, \
    M4IAttributes, create_placehoder_guid

from ..base_object import BaseObject
from ..ToAtlasConvertible import ToAtlasConvertible
from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataAttributeBase(BaseObject):
    data_entity: Optional[str] = None
    name: str

    def _qualified_name(self):
        """
        Returns the qualified name of the attribute based on its parent `data_entity` and its `name`
        """

        return get_qualified_name(
            self.name,
            prefix=self.data_entity
        )
    # END _qualified_name


# END DataAttributeBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataAttributeDefaultsBase(DataClassJsonMixin):
    business_owner: Optional[str] = None
    definition: Optional[str] = None
    steward: Optional[str] = None
    attribute_type: Optional[str] = None
    risk_classification: Optional[str] = None
    has_pii: Optional[str] = None
    is_key_data: Optional[str] = None
    source: Optional[str] = None


# END DataAttributeDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataAttribute(
    DataAttributeDefaultsBase,
    DataAttributeBase,
    ToAtlasConvertible[BusinessDataAttribute]
):
    def convert_to_atlas(self) -> BusinessDataAttribute:
        """
        Returns a corresponding Atlas `BusinessDataAttribute` instance.
        """

        if bool(self.data_entity):
            data_entity_unique_attributes = M4IAttributes(
                qualified_name=self.data_entity
            )

            data_entity = ObjectId(
                type_name="m4i_data_entity",
                unique_attributes=data_entity_unique_attributes
            )
        else:
            data_entity = None

        attributes = BusinessDataAttributeAttributes(
            data_entity=[data_entity] if data_entity else [],
            definition=self.definition,
            name=self.name,
            qualified_name=self.qualified_name,
            attribute_type=self.attribute_type,
            risk_classification=self.risk_classification,
            has_pii=self.has_pii,
            is_key_data=self.is_key_data
        )

        if bool(self.business_owner):
            unique_attributes = M4IAttributes(
                qualified_name=self.business_owner
            )

            business_owner = ObjectId(
                type_name="m4i_person",
                unique_attributes=unique_attributes
            )

            attributes.business_owner = [business_owner]
        # END IF

        if bool(self.steward):
            unique_attributes = M4IAttributes(
                qualified_name=self.steward
            )

            steward = ObjectId(
                type_name="m4i_person",
                unique_attributes=unique_attributes
            )

            attributes.steward = [steward]
        # END IF

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

        ## make classifications
        classifications = []

        if self.has_pii == "Yes":
            classifications.append(Classification(
                type_name="PII",
                entity_guids=create_placehoder_guid()
            ))
        if self.is_key_data == "Yes":
            classifications.append(Classification(
                type_name="key_data",
                entity_guids=create_placehoder_guid()
            ))
        if self.risk_classification == "Low":
            classifications.append(Classification(
                type_name="low_risk",
                entity_guids=create_placehoder_guid()
            ))
        if self.risk_classification == "Medium":
            classifications.append(Classification(
                type_name="medium_risk",
                entity_guids=create_placehoder_guid()
            ))
        if self.risk_classification == "High":
            classifications.append(Classification(
                type_name="high_risk",
                entity_guids=create_placehoder_guid()
            ))


        entity = BusinessDataAttribute(
            attributes=attributes,
            classifications= classifications
        )

        return entity
    # END convert_to_atlas
# END DataAttribute
