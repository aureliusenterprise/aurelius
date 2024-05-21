from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Attributes, Cardinality, Entity, EntityBase,
                    EntityDef, EntityDefaultsBase, ObjectId, RelationshipDef,
                    RelationshipEndDef, TypeCategory)
from ..m4i.M4IAttributes import M4IAttributesBase

# TypeDef for Entity & Relationships
data_quality_attributes_def = [
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
        description="Functional description on what the data field needs to adhere to including the related data fields which can be used to program into a measurable rule.",
        display_name="Rule Description"
    ),
    AttributeDef(
        name="expression",
        type_name="string",
        description="The expression that is used by a Python script to apply the correct functionality for a data quality rule.",
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
        name="businessRuleDescription",
        type_name="string",
        description="Functional description on what the data field needs to adhere to.",
        display_name="Business Rule Description"
    ),
    AttributeDef(
        name="filterRequired",
        type_name="boolean",
        description="Classification if a filter is required for a data quality rule (this is required in case a field contains a content structure).",
        display_name="Filter Required"
    ),
    AttributeDef(
        name="qualityDimension",
        type_name="string",
        description="Classification of the type of data quality that needs to be measured.",
        display_name="Quality Dimension"
    ),
    AttributeDef(
        name="fields",
        type_name="array<m4i_field>",
        cardinality=Cardinality.SET,
        description="The unique technical name of a field, for which a data quality rule needs to be applied",
        display_name="Fields"
    )
]

data_quality_super_type = ["m4i_referenceable", "DataSet"]

data_quality_def = EntityDef(
    category=TypeCategory.ENTITY,
    description="A type definition for a generic Data Quality Rule",
    name="m4i_data_quality",
    type_version="1.0",
    super_types=data_quality_super_type,
    attribute_defs=data_quality_attributes_def,
)
end_1_dataQuality_fields = RelationshipEndDef(
    type="m4i_data_quality",
    name="fields",
    cardinality=Cardinality.SET
)
end_2_dataQuality_fields = RelationshipEndDef(
    type="m4i_field",
    name="dataQuality",
    cardinality=Cardinality.SET
)

m4i_dataQuality_fields_rel_def = RelationshipDef(
    end_def1=end_1_dataQuality_fields,
    end_def2=end_2_dataQuality_fields,
    name="m4i_data_quality_field_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the data field and the data quality rule"
)


# END TypeDef for Entity & Relationships

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataQualityAttributesBase(M4IAttributesBase):
    name: str
# END BusinessDataQualityAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataQualityAttributesDefaultsBase(Attributes):
    id: Optional[str] = None
    rule_description: Optional[str] = None
    expression: Optional[str] = None
    active: Optional[bool] = True
    expression_version: Optional[str] = None
    business_rule_description: Optional[str] = None
    fields: List[ObjectId] = field(default_factory=list)
    filter_required: Optional[bool] = False
    quality_dimension: Optional[str] = None
    source: List[ObjectId] = field(default_factory=list)
# END BusinessDataQualityAttributesDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataQualityAttributes(BusinessDataQualityAttributesDefaultsBase, BusinessDataQualityAttributesBase):
    pass
# END BusinessDataQualityAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataQualityBase(EntityBase):
    attributes: BusinessDataQualityAttributes
# END BusinessDataQualityBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataQualityDefaultsBase(EntityDefaultsBase):
    pass
# END BusinessDataQualityDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataQuality(BusinessDataQualityDefaultsBase, BusinessDataQualityBase, Entity):
    type_name: str = "m4i_data_quality"

    @classmethod
    def get_type_def(cls):
        return data_quality_def

    def get_parents(self) -> Iterable[ObjectId]:
        return self.attributes.fields
    # END get_parents

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this data entity:
        * fields
        """
        references = self.attributes.fields

        if self.attributes.source is not None:
            references = [*references, *self.attributes.source]
        # END IF

        return filter(None, references)
    # END get_referred_entities

# END BusinessDataQuality
