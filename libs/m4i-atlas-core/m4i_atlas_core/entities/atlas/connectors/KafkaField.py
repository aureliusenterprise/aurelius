from dataclasses import dataclass, field
from typing import Iterable, List

from dataclasses_json import LetterCase, dataclass_json

from ..core import (EntityDef, ObjectId, TypeCategory)
from ..data_dictionary import (BusinessField, BusinessFieldAttributes,
                               BusinessFieldAttributesBase,
                               BusinessFieldAttributesDefaultsBase,
                               BusinessFieldBase,
                               BusinessFieldDefaultsBase)

kafka_field_super_type = ["m4i_field"]

kafka_field_attributes_def = [
]

kafka_field_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_kafka_field",
    description="A type definition for a generic Kafka Field in the context of models4insight.com",
    type_version="1.0",
    super_types=kafka_field_super_type,
    attribute_defs=kafka_field_attributes_def
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaFieldAttributesBase(BusinessFieldAttributesBase):
    pass


# END KafkaFieldAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaFieldAttributesDefaultsBase(BusinessFieldAttributesDefaultsBase):
    parent_field: List[ObjectId] = field(default_factory=list)


# END KafkaFieldAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaFieldAttributes(BusinessFieldAttributes,
                           KafkaFieldAttributesDefaultsBase, KafkaFieldAttributesBase):
    pass


# END KafkaFieldAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaFieldBase(BusinessFieldBase):
    attributes: KafkaFieldAttributes


# END KafkaFieldBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaFieldDefaultsBase(BusinessFieldDefaultsBase):
    pass


# END KafkaFieldDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaField(BusinessField,
                 KafkaFieldDefaultsBase, KafkaFieldBase):
    type_name: str = "m4i_kafka_field"

    @classmethod
    def get_type_def(cls):
        return kafka_field_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Kafka Field:
        * Parent Entity
        """

        references = [
            *super().get_referred_entities(),
            *self.attributes.parent_field
        ]

        return filter(None, references)
    # END get_referred_entities

# END KafkaField
