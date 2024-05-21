from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Attributes, Cardinality, ClassificationDef,
                    Entity, EntityBase, EntityDef, EntityDefaultsBase,
                    ObjectId, PropagateTags, RelationshipDef,
                    RelationshipEndDef, TypeCategory)
from ..m4i.M4IAttributes import M4IAttributesBase

data_attribute_attributes_def = [
    AttributeDef(
        name="name",
        type_name="string",
        description="The unique functional name of the data attribute",
        display_name="Name"
    ),
    AttributeDef(
        name="definition",
        type_name="string",
        description="The definition of the data attribute determined by the data steward and data owner",
        display_name="Definition"
    ),
    AttributeDef(
        name="attributeType",
        type_name="string",
        description="The data type of the data attribute",
        display_name="Attribute Type"
    ),
    AttributeDef(
        name="isKeyData",
        type_name="string",
        is_indexable=False,
        description="If this attribute represents any key",
        display_name="isKeyData"
    ),
    AttributeDef(
        name="dataEntity",
        type_name="array<m4i_data_entity>",
        is_indexable=False,
        description="The functional name of the data entity that the data attribute belongs to",
        display_name="Data Entity",
        cardinality=Cardinality.SET

    ),
    AttributeDef(
        name="steward",
        type_name="array<m4i_person>",
        is_indexable=False,
        description="The business data steward of the data attribute",
        display_name="Business Data Steward",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="businessOwner",
        type_name="array<m4i_person>",
        is_indexable=False,
        description="The business owner steward of the data attribute",
        display_name="Business Data Owner",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="riskClassification",
        type_name="string",
        is_indexable=False,
        description="The risk classification of the data attribute determined by the data steward and data owner",
        display_name="Risk Classification"
    ),
    AttributeDef(
        name="hasPII",
        type_name="string",
        is_indexable=False,
        description="The classification if this attribute holds information about a person",
        display_name="hasPII"
    ),
    AttributeDef(
        name="fields",
        type_name="array<m4i_field>",
        is_indexable=False,
        description="The functional names of the data fields that belong to the data attribute",
        display_name="Data Fields",
        cardinality=Cardinality.SET
    )

]

data_attribute_super_type = ["m4i_referenceable"]

data_attribute_def = EntityDef(
    category=TypeCategory.ENTITY,
    description="A type definition for a generic data attribute",
    name="m4i_data_attribute",
    type_version="1.0",
    attribute_defs=data_attribute_attributes_def,
    super_types=data_attribute_super_type
)

end_1_entity_attribute = RelationshipEndDef(
    type="m4i_data_entity",
    name="attributes",
    cardinality=Cardinality.SET

)
end_2_entity_attribute = RelationshipEndDef(
    type="m4i_data_attribute",
    name="dataEntity",
    cardinality=Cardinality.SET
)

m4i_entity_attribute_rel_def = RelationshipDef(
    end_def1=end_1_entity_attribute,
    end_def2=end_2_entity_attribute,
    name="m4i_data_entity_attribute_assignment",
    category=TypeCategory.RELATIONSHIP,
    propagate_tags=PropagateTags.TWO_TO_ONE,
    type_version="1.0",
    description="The relationship between the data entity and the data attribute"
)

end_1_business_owner_attribute = RelationshipEndDef(
    type="m4i_person",
    name="businessOwnerAttribute",
    cardinality=Cardinality.SET
)
end_2_business_owner_attribute = RelationshipEndDef(
    type="m4i_data_attribute",
    name="businessOwner",
    cardinality=Cardinality.SET
)

m4i_business_owner_attribute_rel_def = RelationshipDef(
    end_def1=end_1_business_owner_attribute,
    end_def2=end_2_business_owner_attribute,
    name="m4i_data_attribute_business_owner_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the data attribute and its business data owner"
)

end_1_steward_attribute = RelationshipEndDef(
    type="m4i_person",
    name="stewardAttribute",
    cardinality=Cardinality.SET
)
end_2_steward_attribute = RelationshipEndDef(
    type="m4i_data_attribute",
    name="steward",
    cardinality=Cardinality.SET
)

m4i_steward_attribute_rel_def = RelationshipDef(
    end_def1=end_1_steward_attribute,
    end_def2=end_2_steward_attribute,
    name="m4i_data_attribute_steward_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the data attribute and its business data steward"
)

m4i_classification_pii = ClassificationDef(
    name="PII",
    entity_types=["m4i_data_entity", "m4i_data_attribute",
                  "m4i_field", "m4i_dataset", "m4i_collection"],
    category=TypeCategory.CLASSIFICATION
)
m4i_classification_key_data = ClassificationDef(
    name="key_data",
    entity_types=["m4i_data_attribute", "m4i_field"],
    category=TypeCategory.CLASSIFICATION
)
m4i_classification_high_risk = ClassificationDef(
    name="high_risk",
    entity_types=["m4i_data_entity",
                  "m4i_data_attribute", "m4i_field", "m4i_dataset"],
    category=TypeCategory.CLASSIFICATION
)
m4i_classification_medium_risk = ClassificationDef(
    name="medium_risk",
    entity_types=["m4i_data_attribute", "m4i_field"],
    category=TypeCategory.CLASSIFICATION
)
m4i_classification_low_risk = ClassificationDef(
    name="low_risk",
    entity_types=["m4i_data_attribute", "m4i_field"],
    category=TypeCategory.CLASSIFICATION
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataAttributesAttributesBase(M4IAttributesBase):
    name: str
# END BusinessDataAttributesAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataAttributeAttributesDefaultsBase(Attributes):
    attribute_type: Optional[str] = None
    business_owner: List[ObjectId] = field(default_factory=list)
    data_entity: List[ObjectId] = field(default_factory=list)
    definition: Optional[str] = None
    has_pii: Optional[str] = None
    is_key_data: Optional[str] = None
    steward: List[ObjectId] = field(default_factory=list)
    risk_classification: Optional[str] = None
    source: List[ObjectId] = field(default_factory=list)
# END BusinessDataAttributeAttributesDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataAttributeAttributes(BusinessDataAttributeAttributesDefaultsBase,
                                      BusinessDataAttributesAttributesBase):
    pass
# END BusinessDataAttributeAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataAttributeBase(EntityBase):
    attributes: BusinessDataAttributeAttributes
# END BusinessDataAttributeBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataAttributeDefaultsBase(EntityDefaultsBase):
    pass
# END BusinessDataAttributeDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataAttribute(BusinessDataAttributeDefaultsBase, BusinessDataAttributeBase, Entity):
    type_name: str = "m4i_data_attribute"

    @classmethod
    def get_type_def(cls):
        return data_attribute_def

    def get_parents(self) -> Iterable[ObjectId]:
        return self.attributes.data_entity
    # END get_parents

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this data attribute:
        * Business Owner
        * Steward
        * Data entity
        """
        references = [
            *self.attributes.business_owner,
            *self.attributes.steward,
            *self.attributes.data_entity,
            *self.attributes.source
        ]

        return filter(None, references)
    # END get_referred_entities

# END BusinessDataAttribute
