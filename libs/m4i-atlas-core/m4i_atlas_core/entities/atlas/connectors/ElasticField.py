from dataclasses import dataclass, field
from typing import Iterable, List

from dataclasses_json import LetterCase, dataclass_json
from ..core import (EntityDef, TypeCategory, ObjectId)

from ..data_dictionary import (BusinessField, BusinessFieldAttributesBase,
                               BusinessFieldAttributesDefaultsBase, BusinessFieldBase,
                               BusinessFieldAttributes, BusinessFieldDefaultsBase)

elastic_field_super_type = ["m4i_field"]

elastic_field_attributes_def = [
]

elastic_field_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_elastic_field",
    description="A type definition for a generic Elastic Field in the context of models4insight.com",
    type_version="1.0",
    super_types=elastic_field_super_type,
    attribute_defs=elastic_field_attributes_def
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticFieldAttributesBase(BusinessFieldAttributesBase):
    pass


# END ElasticFieldAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticFieldAttributesDefaultsBase(BusinessFieldAttributesDefaultsBase):
    parent_field: List[ObjectId] = field(default_factory=list)


# END ElasticFieldAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticFieldAttributes(BusinessFieldAttributes,
                             ElasticFieldAttributesDefaultsBase, ElasticFieldAttributesBase):
    pass


# END ElasticFieldAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticFieldBase(BusinessFieldBase):
    attributes: ElasticFieldAttributes


# END ElasticFieldBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticFieldDefaultsBase(BusinessFieldDefaultsBase):
    pass


# END ElasticFieldDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticField(BusinessField,
                   ElasticFieldDefaultsBase, ElasticFieldBase):
    type_name: str = "m4i_elastic_field"

    @classmethod
    def get_type_def(cls):
        return elastic_field_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Kafka Field:
        * Parent Field
        """

        references = [
            *super().get_referred_entities(),
            *self.attributes.parent_field
        ]

        return filter(None, references)
    # END get_referred_entities

# END ElasticField
