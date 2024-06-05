import copy
from dataclasses import dataclass, field
from dataclasses_json import (DataClassJsonMixin, LetterCase, config,
                              dataclass_json)
from enum import Enum
from m4i_atlas_core import KafkaField, KafkaFieldAttributes, ObjectId, M4IAttributes
from typing import Iterable, List, Optional, Union

from ...utils import get_qualified_name


class KafkaTopicEntityFieldTypeName(Enum):
    ARRAY = "array"
    LONG = "long"
    NULL = "null"
    OBJECT = "object"
    RECORD = "record"
    STRING = "string"
    FLOAT = "float"
    INT = "int"
    DOUBLE = "double"


# END KafkaTopicEntityFieldTypeName


def kafkaTopicEntityFieldTypeDecoder(data: Union[str, dict, List[Union[str, dict]]]):
    def decoder(data: Union[str, dict]):
        if isinstance(data, str):
            return KafkaTopicEntityFieldTypeName(data)
        else:
            return KafkaTopicEntityField.from_dict(data)
        # END IF

    # END decoder

    if isinstance(data, list):
        return [decoder(item) for item in data]
    else:
        return decoder(data)
    # END IF


# END kafkaTopicEntityFieldTypeDecoder


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaTopicEntityFieldBase(DataClassJsonMixin):
    type: Union[
        KafkaTopicEntityFieldTypeName,
        'KafkaTopicEntityField',
        List[
            Union[
                KafkaTopicEntityFieldTypeName,
                'KafkaTopicEntityField'
            ]
        ]
    ] = field(
        metadata=config(
            decoder=kafkaTopicEntityFieldTypeDecoder
        )
    )


# END KafkaTopicEntityFieldBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaTopicEntityFieldDefaultsBase(DataClassJsonMixin):
    doc: Optional[Union[str, List[str]]] = None
    fields: List['KafkaTopicEntityField'] = field(default_factory=list)
    logical_type: Optional[str] = None
    name: Optional[str] = None
    parent_field: Optional[str] = None
    dataset: Optional[str] = None

    def _get_qualified_name(self):
        """
        Returns the qualified name of the field based on its parent `dataset` and its `name`
        """
        if self.parent_field is None:
            return get_qualified_name(
                self.name,
                prefix=self.dataset
            )
        else:
            return get_qualified_name(
                self.name,
                prefix=self.parent_field
            )
    # END _qualified_name


# END KafkaTopicEntityFieldDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KafkaTopicEntityField(
    KafkaTopicEntityFieldDefaultsBase,
    KafkaTopicEntityFieldBase
):

    def convert_to_atlas(self, dataset_qualified_name: str, dataset_guid: str = None, parent_field: str = None,
                         parent_guid: str = None):
        self.parent_field = parent_field
        self.dataset = dataset_qualified_name

        dataset_qualified_name_unique_attributes = M4IAttributes(
            qualified_name=self.dataset

        )

        dataset_qualified_name_attribute = [ObjectId(
            type_name="m4i_kafka_topic",
            unique_attributes=dataset_qualified_name_unique_attributes,
            guid=dataset_guid

        )]

        attributes = KafkaFieldAttributes(
            qualified_name=self._get_qualified_name(),
            datasets=dataset_qualified_name_attribute,
            name=self.name,
            field_type=self.derived_type_name
        )

        if bool(self.doc):
            docs = []
            if isinstance(self.doc, str):
                self.doc = [self.doc]

            for att in self.doc:
                attribute_unique_attributes = M4IAttributes(
                    qualified_name=att
                )
                docs.append(ObjectId(
                    type_name="m4i_data_attribute",
                    unique_attributes=attribute_unique_attributes
                ))
            attributes.attributes = docs
        # END IF

        if parent_field is not None:
            parent_unique_attributes = M4IAttributes(
                qualified_name=self.parent_field
            )

            parent_attribute = ObjectId(
                type_name="m4i_kafka_field",
                unique_attributes=parent_unique_attributes,
                guid=parent_guid
            )

            attributes.parent_field = [parent_attribute]
            attributes.datasets = None
        # END IF

        atlas_field = KafkaField(attributes=attributes)
        atlas_field_ref = copy.deepcopy(atlas_field)
        child_fields = []
        child_field_ref = []
        for child_field in self.get_child_fields():
            child_atlas_field = child_field.convert_to_atlas(dataset_qualified_name, dataset_guid,
                                                             self._get_qualified_name(), atlas_field.guid)
            child_fields = [*child_fields, child_atlas_field[0]]
            child_field_ref = [*child_field_ref, *child_atlas_field[1]]
        atlas_field_ref.attributes.child_field = child_fields

        return atlas_field, [atlas_field_ref, *child_field_ref]

    # END convert_to_atlas

    def get_child_fields(self) -> Iterable['KafkaTopicEntityField']:

        if isinstance(self.type, KafkaTopicEntityField):
            yield self.type
        # END IF

        if isinstance(self.type, list):
            child_fields_from_type = (
                type_item
                for type_item in self.type
                if isinstance(type_item, KafkaTopicEntityField)
            )
            yield from child_fields_from_type
        # END IF

        yield from self.fields

    # END get_child_fields

    @property
    def derived_type_name(self) -> Optional[str]:

        if self.logical_type is not None:
            return self.logical_type
        # END IF

        derived_type = self.type

        if isinstance(self.type, list):
            non_null_types = (
                t for t in self.type
                if t != KafkaTopicEntityFieldTypeName.NULL
            )
            derived_type = next(non_null_types, None)
        # END IF

        if derived_type is None:
            return None
        # END IF

        if isinstance(derived_type, KafkaTopicEntityFieldTypeName):
            return derived_type.value
        # END IF

        if isinstance(derived_type, KafkaTopicEntityField):
            return KafkaTopicEntityFieldTypeName.RECORD.value
        # END IF

        return None

    # END get_derived_type

    @property
    def is_optional(self):
        return isinstance(self.type, list) and KafkaTopicEntityFieldTypeName.NULL in self.type
    # END is_optional

# END KafkaTopicEntityFields
