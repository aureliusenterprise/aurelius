from dataclasses import dataclass
from typing import Iterable, Optional, List

from dataclasses_json import LetterCase, dataclass_json

from .. import Cardinality
from ..core import AttributeDef, EntityDef, ObjectId, TypeCategory
from ..data_dictionary import (BusinessSystem, BusinessSystemAttributes,
                               BusinessSystemAttributesBase,
                               BusinessSystemAttributesDefaultsBase,
                               BusinessSystemBase, BusinessSystemDefaultsBase)

kafka_cluster_super_type = ["m4i_system"]

kafka_cluster_attributes_def = [
    AttributeDef(
        name="kafkaPartitions",
        type_name="int"
    ),
    AttributeDef(
        name="kafkaReplicas",
        type_name="int"
    ),
    AttributeDef(
        name="confluentEnvironment",
        type_name="array<m4i_confluent_environment>",
        cardinality=Cardinality.SET
    )
]

kafka_cluster_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_kafka_cluster",
    description="a type definition for a generic confluent_environment in the context of models4insight.com",
    type_version="1.0",
    super_types=kafka_cluster_super_type,
    attribute_defs=kafka_cluster_attributes_def
)



@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaClusterAttributesBase(BusinessSystemAttributesBase):
    confluent_environment: List[ObjectId]


# END KafkaClusterAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaClusterAttributesDefaultsBase(BusinessSystemAttributesDefaultsBase):
    kafka_partitions: Optional[int] = None
    kafka_replicas: Optional[int] = None


# END KafkaClusterAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaClusterAttributes(BusinessSystemAttributes,
                             KafkaClusterAttributesDefaultsBase, KafkaClusterAttributesBase):
    pass


# END KafkaClusterAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaClusterBase(BusinessSystemBase):
    attributes: KafkaClusterAttributes


# END KafkaClusterBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaClusterDefaultsBase(BusinessSystemDefaultsBase):
    pass


# END KafkaClusterDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaCluster(BusinessSystem,
                   KafkaClusterDefaultsBase, KafkaClusterBase):
    type_name: str = "m4i_kafka_cluster"

    @classmethod
    def get_type_def(cls):
        return kafka_cluster_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Confluent Environment:
        * Confluent Environment
        """

        references = [
            *super().get_referred_entities(),
            *self.attributes.confluent_environment
        ]

        return filter(None, references)
    # END get_referred_entities

# END KafkaCluster
