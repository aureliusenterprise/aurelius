from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import (ObjectId, M4IAttributes, KafkaCluster as CoreKafkaCluster,
                            KafkaClusterAttributes as CoreKafkaClusterAttributes)
from typing import Optional, List

from ..utils import get_qualified_name


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaClusterBase(DataClassJsonMixin):
    name: str
    confluent_environment: str

    def _qualified_name(self):
        """
        Returns the qualified name of the KafkaCluster based on its `confluent_environment`
        """
        # KafkaClusterQualifiedName is based on confluent_environment
        return get_qualified_name(
            self.name,
            prefix=self.confluent_environment
        )
    # END _qualified_name


# END KafkaClusterBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaClusterDefaultsBase(DataClassJsonMixin):
    kafka_partitions: Optional[str] = None
    kafka_replicas: Optional[str] = None


# END KafkaClusterDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaCluster(
    KafkaClusterDefaultsBase,
    KafkaClusterBase
):

    def convert_to_atlas(self) -> CoreKafkaCluster:
        """
        Returns a corresponding Atlas `KafkaCluster` instance.
        """
        confluent_environment: List[ObjectId] = []

        confluent_environment_unique_attributes = M4IAttributes(
            qualified_name=self.confluent_environment
        )
        confluent_environment.append(ObjectId(
            type_name="m4i_confluent_environment",
            unique_attributes=confluent_environment_unique_attributes
        ))
        attributes = CoreKafkaClusterAttributes(
            kafka_partitions=self.kafka_partitions,
            kafka_replicas=self.kafka_replicas,
            name=self.name,
            confluent_environment=confluent_environment,
            qualified_name=self._qualified_name()
        )

        entity = CoreKafkaCluster(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END KafkaCluster
