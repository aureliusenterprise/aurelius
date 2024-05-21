from dataclasses import dataclass, field
from typing import Iterable, List

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, EntityDef, TypeCategory,
                    ObjectId,
                    RelationshipEndDef, RelationshipDef, Cardinality)

from ..data_dictionary.BusinessSystem import (BusinessSystem, BusinessSystemAttributesBase,
                                              BusinessSystemAttributesDefaultsBase, BusinessSystemBase,
                                              BusinessSystemAttributes, BusinessSystemDefaultsBase)

confluent_cloud_super_type = ["m4i_system"]

confluent_cloud_attributes_def = [
    AttributeDef(
        name="confluentEnvironment",
        type_name="array<m4i_confluent_environment>",
        cardinality=Cardinality.SET
    )
]

confluent_cloud_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_confluent_cloud",
    description="A type definition for a generic Confluent Cloud in the context of models4insight.com",
    type_version="1.0",
    super_types=confluent_cloud_super_type,
    attribute_defs=confluent_cloud_attributes_def
)

end_1_ccloud_cenvironment = RelationshipEndDef(
    type="m4i_confluent_environment",
    name="confluentCloud"
)
end_2_ccloud_cenvironment = RelationshipEndDef(
    type="m4i_confluent_cloud",
    name="confluentEnvironment"
)

m4i_ccloud_cenvironment_rel_def = RelationshipDef(
    end_def1=end_1_ccloud_cenvironment,
    end_def2=end_2_ccloud_cenvironment,
    name="m4i_confluent_environment_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentCloudAttributesBase(BusinessSystemAttributesBase):
    pass


# END ConfluentCloudAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentCloudAttributesDefaultsBase(BusinessSystemAttributesDefaultsBase):
    confluent_environment: List[ObjectId] = field(default_factory=list)


# END ConfluentCloudAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentCloudAttributes(BusinessSystemAttributes,
                               ConfluentCloudAttributesDefaultsBase,
                               ConfluentCloudAttributesBase):
    pass


# END ConfluentCloudAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentCloudBase(BusinessSystemBase):
    attributes: ConfluentCloudAttributes


# END ConfluentCloudBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentCloudDefaultsBase(BusinessSystemDefaultsBase):
    pass


# END ConfluentCloudDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentCloud(BusinessSystem,
                     ConfluentCloudDefaultsBase,
                     ConfluentCloudBase
                     ):
    type_name: str = "m4i_confluent_cloud"

    @classmethod
    def get_type_def(cls):
        return confluent_cloud_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Confluent Cloud:
        * Confluent Environment
        """

        references = [*super().get_referred_entities(),
                      *self.attributes.confluent_environment]

        return filter(None, references)
    # END get_referred_entities

# END ConfluentCloud
