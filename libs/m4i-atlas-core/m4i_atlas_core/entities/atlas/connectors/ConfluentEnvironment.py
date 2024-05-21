from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Cardinality, EntityDef, ObjectId,
                    RelationshipDef, RelationshipEndDef, TypeCategory)
from ..data_dictionary.BusinessSystem import (
    BusinessSystem, BusinessSystemAttributes, BusinessSystemAttributesBase,
    BusinessSystemAttributesDefaultsBase, BusinessSystemBase,
    BusinessSystemDefaultsBase)

confluent_environment_super_type = ["m4i_system"]

confluent_environment_attributes_def = [
    AttributeDef(
        name="schemaRegistry",
        type_name="boolean"
    ),
    AttributeDef(
        name="confluentCloud",
        type_name="array<m4i_confluent_cloud>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="kafkaClusters",
        type_name="array<m4i_kafka_cluster>",
        cardinality=Cardinality.SET
    )
]

confluent_environment_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_confluent_environment",
    description="A type definition for a generic Confluent Environment in the context of models4insight.com",
    type_version="1.0",
    super_types=confluent_environment_super_type,
    attribute_defs=confluent_environment_attributes_def
)

end_1_kcluster_cenvironment = RelationshipEndDef(
    type="m4i_confluent_environment",
    name="kafkaClusters",
    cardinality=Cardinality.SET
)
end_2_kcluster_cenvironment = RelationshipEndDef(
    type="m4i_kafka_cluster",
    name="confluentEnvironment",
    cardinality=Cardinality.SET
)

m4i_kcluster_cenvironment_rel_def = RelationshipDef(
    end_def1=end_1_kcluster_cenvironment,
    end_def2=end_2_kcluster_cenvironment,
    name="m4i_kafka_cluster_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentEnvironmentAttributesBase(BusinessSystemAttributesBase):
    confluent_cloud: List[ObjectId]


# END ConfluentEnvironmentAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentEnvironmentAttributesDefaultsBase(BusinessSystemAttributesDefaultsBase):
    schema_registry: Optional[bool] = None
    kafka_clusters: List[ObjectId] = field(default_factory=list)


# END ConfluentEnvironmentAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentEnvironmentAttributes(BusinessSystemAttributes,
                                     ConfluentEnvironmentAttributesDefaultsBase,
                                     ConfluentEnvironmentAttributesBase):
    pass


# END ConfluentEnvironmentAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentEnvironmentBase(BusinessSystemBase):
    attributes: ConfluentEnvironmentAttributes


# END ConfluentEnvironmentBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentEnvironmentDefaultsBase(BusinessSystemDefaultsBase):
    pass


# END ConfluentEnvironmentDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ConfluentEnvironment(BusinessSystem,
                           ConfluentEnvironmentDefaultsBase,
                           ConfluentEnvironmentBase
                           ):
    type_name: str = "m4i_confluent_environment"

    @classmethod
    def get_type_def(cls):
        return confluent_environment_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Confluent Environment:
        * List of Confluent Cloud
        * List of Kafka Clusters
        """

        references = [
            *super().get_referred_entities(),
            *self.attributes.confluent_cloud,
            *self.attributes.kafka_clusters
        ]

        return filter(None, references)
    # END get_referred_entities

# END ConfluentEnvironment
