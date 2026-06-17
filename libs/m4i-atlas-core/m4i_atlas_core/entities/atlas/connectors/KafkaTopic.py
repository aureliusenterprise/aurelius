from dataclasses import dataclass
from typing import Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import AttributeDef, EntityDef, TypeCategory
from ..data_dictionary import (
    BusinessDataset,
    BusinessDatasetAttributes,
    BusinessDatasetAttributesBase,
    BusinessDatasetAttributesDefaultsBase,
    BusinessDatasetBase,
    BusinessDatasetDefaultsBase,
)

kafka_topic_super_type = ["m4i_dataset"]

kafka_topic_attributes_def = [
    AttributeDef(name="partitions", type_name="int"),
    AttributeDef(name="replicas", type_name="int"),
]

kafka_topic_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_kafka_topic",
    description="A type definition for a generic Kafka Topic in the context of models4insight.com",
    type_version="1.0",
    super_types=kafka_topic_super_type,
    attribute_defs=kafka_topic_attributes_def,
)


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class KafkaTopicAttributesBase(BusinessDatasetAttributesBase):
    pass


# END KafkaTopicAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class KafkaTopicAttributesDefaultsBase(BusinessDatasetAttributesDefaultsBase):
    partitions: Optional[int] = None
    replicas: Optional[int] = None


# END KafkaTopicAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class KafkaTopicAttributes(
    BusinessDatasetAttributes, KafkaTopicAttributesDefaultsBase, KafkaTopicAttributesBase
):
    pass


# END KafkaTopicAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class KafkaTopicBase(BusinessDatasetBase):
    attributes: KafkaTopicAttributes  # type: ignore[reportIncompatibleMethodOverride]


# END KafkaTopicBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class KafkaTopicDefaultsBase(BusinessDatasetDefaultsBase):
    pass


# END KafkaTopicDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class KafkaTopic(BusinessDataset, KafkaTopicDefaultsBase, KafkaTopicBase):  # type: ignore[reportGeneralTypeIssues]
    type_name: str = "m4i_kafka_topic"

    @classmethod
    def get_type_def(cls):
        return kafka_topic_def


# END KafkaTopic
