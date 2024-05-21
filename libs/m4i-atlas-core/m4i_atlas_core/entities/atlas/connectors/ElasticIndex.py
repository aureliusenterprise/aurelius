from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json

from ..core import (EntityDef, TypeCategory
                    )

from ..data_dictionary.BusinessDataset import (BusinessDataset, BusinessDatasetAttributesBase,
                                               BusinessDatasetAttributesDefaultsBase, BusinessDatasetBase,
                                               BusinessDatasetAttributes, BusinessDatasetDefaultsBase)

elastic_index_super_type = ["m4i_dataset"]

elastic_index_attributes_def = [
]

elastic_index_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_elastic_index",
    description="A type definition for a generic Kafka Index in the context of models4insight.com",
    type_version="1.0",
    super_types=elastic_index_super_type,
    attribute_defs=elastic_index_attributes_def
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexAttributesBase(BusinessDatasetAttributesBase):
    pass


# END ElasticIndexAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexAttributesDefaultsBase(BusinessDatasetAttributesDefaultsBase):
    pass


# END ElasticIndexAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexAttributes(BusinessDatasetAttributes,
                             ElasticIndexAttributesDefaultsBase, ElasticIndexAttributesBase):
    pass


# END ElasticIndexAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexBase(BusinessDatasetBase):
    attributes: ElasticIndexAttributes


# END ElasticIndexBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndexDefaultsBase(BusinessDatasetDefaultsBase):
    pass


# END ElasticIndexDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ElasticIndex(BusinessDataset,
                   ElasticIndexDefaultsBase,
                   ElasticIndexBase
                   ):
    type_name: str = "m4i_elastic_index"

    @classmethod
    def get_type_def(cls):
        return elastic_index_def

# END ElasticIndex
