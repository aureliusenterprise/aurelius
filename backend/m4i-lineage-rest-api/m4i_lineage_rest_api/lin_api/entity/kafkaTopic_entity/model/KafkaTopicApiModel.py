from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import (KafkaTopic, KafkaTopicAttributes, M4IAttributes,
                            ObjectId)
from typing import Optional, Union, List

from .KafkaTopicEntityFields import KafkaTopicEntityField


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaTopicValueSchemaBase(DataClassJsonMixin):
    fields: List[KafkaTopicEntityField]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaTopicApiModelBase(DataClassJsonMixin):
    name: str
    cluster: str
    partitions: int
    replicas: int
    key_schema: str
    value_schema: Union[KafkaTopicValueSchemaBase, str]

    def _qualified_name(self):
        """
        Returns the qualified name of the KafkaTopic based on its `confluent_environment`
        """
        # KafkaTopicQualifiedName is based on confluent_environment
        return f"{self.environment}--{self.cluster}--{self.name}"
    # END _qualified_name


# END KafkaTopicApiModelBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaTopicApiModelDefaultsBase(DataClassJsonMixin):
    environment: Optional[str] = None


# END KafkaTopicApiModelDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaTopicApiModel(
    KafkaTopicApiModelDefaultsBase,
    KafkaTopicApiModelBase
):

    def convert_to_atlas(self):
        """
        Returns a corresponding Atlas `KafkaTopic` instance, along with `KafkaField` instances representing the value schema.
        """

        collection_unique_attributes = M4IAttributes(
            qualified_name=f"{self.environment}--{self.cluster}--data"
        )

        collection = [ObjectId(
            type_name="m4i_collection",
            unique_attributes=collection_unique_attributes,
            guid='-1'
        )]
        cluster_unique_attributes = M4IAttributes(
            qualified_name=f"{self.environment}--{self.cluster}"
        )

        cluster = [ObjectId(
            type_name="m4i_kafka_cluster",
            unique_attributes=cluster_unique_attributes,
        )]

        collection_ref = {'-1': {
            "guid": "-1",
            "typeName": "m4i_collection",
            "attributes": {
                "qualifiedName": collection_unique_attributes.qualified_name,
                "systems": cluster,
                "name": collection_unique_attributes.qualified_name
            }
        }}

        attributes = KafkaTopicAttributes(
            name=self.name,
            collections=collection,
            partitions=self.partitions,
            replicas=self.replicas,
            qualified_name=self._qualified_name()
        )

        entity = KafkaTopic(
            attributes=attributes
        )

        if not isinstance(self.value_schema, str):
            fields = []
            fields_ref = []
            for field in self.value_schema['fields']:
                field = KafkaTopicEntityField.from_dict(field)
                fields_entity, field_refs = field.convert_to_atlas(self._qualified_name(), entity.guid, None, None)
                fields = [*fields, fields_entity]
                fields_ref = [*fields_ref, *field_refs]
            entity.attributes.fields = fields
            for i in fields_ref:
                collection_ref[i.guid] = i

        return [entity], collection_ref
    # END convert_to_atlas

# END KafkaTopicApiModel
