from dataclasses import dataclass
from typing import Iterable, Optional, List

from dataclasses_json import LetterCase, dataclass_json
from m4i_atlas_core.entities.atlas.core import (AttributeDef, Attributes, Entity, EntityBase,
                                                EntityDef, EntityDefaultsBase, ObjectId,
                                                TypeCategory)

from m4i_atlas_core.entities.atlas.m4i.M4IAttributes import M4IAttributesBase

# TypeDef for Entity & Relationships
data_quality_gov_attributes_def = [
    AttributeDef(
        name="id",
        type_name="int",
        is_optional=False,
        description="The unique identifier of the data quality rule",
        display_name="ID"
    ),
    AttributeDef(
        name="ruleDescription",
        type_name="string",
        description="Functional description on what the data field needs to adhere to including the related data "
                    "fields which can be used to program into a measurable rule.",
        display_name="Rule Description"
    ),
    AttributeDef(
        name="expression",
        type_name="string",
        description="The expression that is used by a Python script to apply the correct functionality for a data "
                    "quality rule.",
        display_name="Expression"
    ),
    AttributeDef(
        name="active",
        type_name="boolean",
        description="Classification if a data quality rule is active or inactive.",
        display_name="Active"
    ),
    AttributeDef(
        name="expressionVersion",
        type_name="string",
        description="The version of the expression that is used.",
        display_name="Expression Version"

    ),
    AttributeDef(
        name="qualityDimension",
        type_name="string",
        description="Classification of the type of data quality that needs to be measured.",
        display_name="Quality Dimension"
    ),
    AttributeDef(
        name="compliantMessage",
        type_name="string",
        description="Message displayed when data quality is Complaint",
        display_name="Complaint Message"
    ),
    AttributeDef(
        name="nonCompliantMessage",
        type_name="string",
        description="Message displayed when data quality is not Complaint",
        display_name="Non-complaint Message"
    ),
    AttributeDef(
        name="ruleType",
        type_name="string",
        description="Rules are either applied on Attributes or relationship. This field captures this information.",
        display_name="Rule Type"
    )
]

data_quality_super_type = ["m4i_referenceable", "DataSet"]

data_quality_gov_def = EntityDef(
    category=TypeCategory.ENTITY,
    description="A type definition for a Governance Data Quality Rule",
    name="m4i_gov_data_quality",
    type_version="1.0",
    super_types=data_quality_super_type,
    attribute_defs=data_quality_gov_attributes_def,
)


# END TypeDef for Entity & Relationships

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessGovDataQualityAttributesBase(M4IAttributesBase):
    name: str


# END BusinessGovDataQualityAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessGovDataQualityAttributesDefaultsBase(Attributes):
    id: Optional[str] = None
    rule_description: Optional[str] = None
    expression: Optional[str] = None
    active: Optional[bool] = True
    expression_version: Optional[str] = None
    quality_dimension: Optional[str] = None
    rule_type: Optional[str] = None
    compliant_message: Optional[str] = None
    non_compliant_message: Optional[str] = None
    source: Optional[List[ObjectId]] = None


# END BusinessGovDataQualityAttributesDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessGovDataQualityAttributes(BusinessGovDataQualityAttributesDefaultsBase,
                                       BusinessGovDataQualityAttributesBase):
    pass


# END BusinessGovDataQualityAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessGovDataQualityBase(EntityBase):
    attributes: BusinessGovDataQualityAttributes


# END BusinessGovDataQualityBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessGovDataQualityDefaultsBase(EntityDefaultsBase):
    pass


# END BusinessGovDataQualityDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessGovDataQuality(BusinessGovDataQualityDefaultsBase, BusinessGovDataQualityBase, Entity):
    type_name: str = "m4i_gov_data_quality"

    @classmethod
    def get_type_def(cls):
        return data_quality_gov_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this data entity:

        """
        references = []

        if self.attributes.source is not None:
            references = [*self.attributes.source]
        # END IF

        return filter(None, references)
    # END get_referred_entities

# END BusinessGovDataQuality
