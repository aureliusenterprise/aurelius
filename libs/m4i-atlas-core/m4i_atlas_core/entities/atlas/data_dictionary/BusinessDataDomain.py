from dataclasses import dataclass, field
from typing import Iterable, Optional, List

from dataclasses_json import LetterCase, dataclass_json
from ..core import (AttributeDef, Attributes, Entity, EntityBase,
                    EntityDef, EntityDefaultsBase, ObjectId,
                    TypeCategory, RelationshipEndDef, Cardinality, RelationshipDef)

from ..m4i.M4IAttributes import M4IAttributesBase

data_domain_attributes_def = [
    AttributeDef(
        name="name",
        type_name="string",
        description="The unique functional name of the domain",
        display_name="Name"
    ),
    AttributeDef(
        name="definition",
        type_name="string",
        description="The definition of the data domain determined by the data steward and data owner",
        display_name="Definition"
    ),
    AttributeDef(
        name="domainLead",
        type_name="array<m4i_person>",
        is_indexable=False,
        description="The owner of the data domain",
        display_name="Domain Lead",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="dataEntity",
        type_name="array<m4i_data_entity>",
        is_indexable=False,
        description="The functional names of the data entities that belong to the data domain",
        display_name="Data Entity",
        cardinality=Cardinality.SET
    )
]

data_domain_super_type = ["m4i_referenceable"]

data_domain_def = EntityDef(
    category=TypeCategory.ENTITY,
    description="A type definition for a generic data domain",
    name="m4i_data_domain",
    type_version="1.0",
    attribute_defs=data_domain_attributes_def,
    super_types=data_domain_super_type
)

end_1_lead_entity = RelationshipEndDef(
    type="m4i_person",
    name="domainLead"
)
end_2_lead_entity = RelationshipEndDef(
    type="m4i_data_domain",
    name="domainLead"
)

m4i_lead_entity_rel_def = RelationshipDef(
    end_def1=end_1_lead_entity,
    end_def2=end_2_lead_entity,
    name="m4i_domainLead_assignment",
    category=TypeCategory.RELATIONSHIP,
    type_version="1.0",
    description="The relationship between the data domain and the domain lead"

)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataDomainAttributesBase(M4IAttributesBase):
    name: str
# END BusinessDataDomainAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataDomainAttributesDefaultsBase(Attributes):
    data_entity: List[ObjectId] = field(default_factory=list)
    definition: Optional[str] = None
    domain_lead: List[ObjectId] = field(default_factory=list)
    source: List[ObjectId] = field(default_factory=list)
# END BusinessDataDomainAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataDomainAttributes(BusinessDataDomainAttributesDefaultsBase, BusinessDataDomainAttributesBase):
    pass
# END BusinessDataDomainAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataDomainBase(EntityBase):
    attributes: BusinessDataDomainAttributes
# END BusinessDataDomainBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataDomainDefaultsBase(EntityDefaultsBase):
    pass
# END BusinessDataDomainDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BusinessDataDomain(BusinessDataDomainDefaultsBase, BusinessDataDomainBase, Entity):
    type_name: str = "m4i_data_domain"

    @classmethod
    def get_type_def(cls):
        return data_domain_def
    
    def get_children(self) -> Iterable[ObjectId]:
        return self.attributes.data_entity
    # END get_children

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the domain leads referenced by this data domain
        """

        references = [
            *self.attributes.domain_lead,
            *self.attributes.source,
            *self.attributes.data_entity
        ]

        return filter(None, references)
    # END get_referred_entities

# END BusinessDataDomain
