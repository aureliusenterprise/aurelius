from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Attributes, Cardinality, Entity, EntityBase,
                    EntityDef, EntityDefaultsBase, ObjectId, RelationshipDef,
                    RelationshipEndDef, TypeCategory)
from ..m4i.M4IAttributes import M4IAttributesBase

data_entity_attributes_def = [
    AttributeDef(
        name="name",
        type_name="string",
        description="The unique functional name of the data entity",
        display_name="Name"
    ),
    AttributeDef(
        name="definition",
        type_name="string",
        description="The definition of the data entity determined by the data steward and data owner",
        display_name="Definition"
    ),
    AttributeDef(
        name="dataDomain",
        type_name="array<m4i_data_domain>",
        is_indexable=False,
        description="The functional name of the data domain that the data entity belongs to",
        display_name="Data Domain",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="attributes",
        type_name="array<m4i_data_attribute>",
        is_indexable=False,
        description="The functional names of the data attributes that belong to the data entity",
        display_name="Data Attribute",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="parentEntity",
        type_name="array<m4i_data_entity>",
        is_indexable=False,
        description="The functional names of the data entity that the data entity belongs to",
        display_name="Parent Data Entity",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="childEntity",
        type_name="array<m4i_data_entity>",
        is_indexable=False,
        description="The functional names of the data entity that belong to the data entity",
        display_name="Child Data Entity",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="steward",
        type_name="array<m4i_person>",
        is_indexable=False,
        description="The business data steward of the data entity",
        display_name="Business Data Steward",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="businessOwner",
        type_name="array<m4i_person>",
        is_indexable=False,
        description="The business owner steward of the data entity",
        display_name="Business Data Owner",
        cardinality=Cardinality.SET
    )
]

data_entity_super_type = ["m4i_referenceable"]

data_entity_def = EntityDef(
    category=TypeCategory.ENTITY,
    description="A type definition for a generic data entity",
    name="m4i_data_entity",
    type_version="1.0",
    attribute_defs=data_entity_attributes_def,
    super_types=data_entity_super_type
)

end_1_domain_entity = RelationshipEndDef(
    type="m4i_data_domain",
    name="dataEntity",
    cardinality=Cardinality.SET
)
end_2_data_entity = RelationshipEndDef(
    type="m4i_data_entity",
    name="dataDomain",
    cardinality=Cardinality.SET
)

m4i_domain_entity_rel_def = RelationshipDef(
    end_def1=end_1_domain_entity,
    end_def2=end_2_data_entity,
    name="m4i_data_entity_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the data domain and the data entity"
)

end_1_business_owner_entity = RelationshipEndDef(
    type="m4i_person",
    name="businessOwnerEntity"
)
end_2_business_owner_entity = RelationshipEndDef(
    type="m4i_data_entity",
    name="businessOwner"
)

m4i_business_owner_entity_rel_def = RelationshipDef(
    end_def1=end_1_business_owner_entity,
    end_def2=end_2_business_owner_entity,
    name="m4i_data_entity_business_owner_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the data entity and its business data owner"
)

end_1_steward_entity = RelationshipEndDef(
    type="m4i_person",
    name="stewardEntity"
)
end_2_steward_entity = RelationshipEndDef(
    type="m4i_data_entity",
    name="steward"

)

m4i_steward_entity_rel_def = RelationshipDef(
    end_def1=end_1_steward_entity,
    end_def2=end_2_steward_entity,
    name="m4i_data_entity_steward_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the data entity and its business data steward"
)

end_1_pentity_centity = RelationshipEndDef(
    type="m4i_data_entity",
    name="parentEntity"
)
end_2_pentity_centity = RelationshipEndDef(
    type="m4i_data_entity",
    name="childEntity"

)

m4i_pentity_centity_rel_def = RelationshipDef(
    end_def1=end_1_pentity_centity,
    end_def2=end_2_pentity_centity,
    name="m4i_parent_entity_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the data entity to other data entities"
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataEntityAttributesBase(M4IAttributesBase):
    name: str
# END BusinessDataEntityAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataEntityAttributesDefaultsBase(Attributes):
    attributes: List[ObjectId] = field(default_factory=list)
    business_owner: List[ObjectId] = field(default_factory=list)
    child_entity: List[ObjectId] = field(default_factory=list)
    data_domain: List[ObjectId] = field(default_factory=list)
    definition: Optional[str] = None
    source: List[ObjectId] = field(default_factory=list)
    parent_entity: List[ObjectId] = field(default_factory=list)
    steward: List[ObjectId] = field(default_factory=list)
# END BusinessDataEntityAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataEntityAttributes(BusinessDataEntityAttributesDefaultsBase, BusinessDataEntityAttributesBase):
    pass
# END BusinessDataEntityAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataEntityBase(EntityBase):
    attributes: BusinessDataEntityAttributes
# END BusinessDataEntityBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataEntityDefaultsBase(EntityDefaultsBase):
    pass
# END BusinessDataEntityDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataEntity(BusinessDataEntityDefaultsBase, BusinessDataEntityBase, Entity):
    type_name: str = "m4i_data_entity"

    @classmethod
    def get_type_def(cls):
        return data_entity_def

    def get_parents(self) -> Iterable[ObjectId]:
        return [*self.attributes.parent_entity, *self.attributes.data_domain]
    # END get_parents

    def get_children(self) -> Iterable[ObjectId]:
        return [*self.attributes.child_entity, *self.attributes.attributes]
    # END get_children

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this data entity:
        * Business Owner
        * Steward
        * Parent Entity
        * Child Entity
        * Data Domain
        """

        references = [
            *self.attributes.attributes,
            *self.attributes.business_owner,
            *self.attributes.steward,
            *self.attributes.data_domain,
            *self.attributes.parent_entity,
            *self.attributes.child_entity,
            *self.attributes.source
        ]

        return filter(None, references)
    # END get_referred_entities

# END BusinessDataEntity
