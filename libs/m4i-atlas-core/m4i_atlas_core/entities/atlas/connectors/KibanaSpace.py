from dataclasses import dataclass
from typing import Optional, Iterable, List

from dataclasses_json import LetterCase, dataclass_json

from .. import Cardinality
from ..core import (AttributeDef,
                    EntityDef, TypeCategory,
                    )

from ..data_dictionary.BusinessCollection import (ObjectId, BusinessCollection, BusinessCollectionAttributesBase,
                                                  BusinessCollectionAttributesDefaultsBase, BusinessCollectionBase,
                                                  BusinessCollectionAttributes, BusinessCollectionDefaultsBase)

kibana_space_super_type = ["m4i_collection"]

kibana_space_attributes_def = [
    AttributeDef(
        name="avatarInitials",
        type_name="string"
    ),
    AttributeDef(
        name="avatarColor",
        type_name="string"
    ),
    AttributeDef(
        name="elasticCluster",
        type_name="array<m4i_elastic_cluster>",
        cardinality=Cardinality.SET
    )
]

kibana_space_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_kibana_space",
    description="A type definition for a generic Kibana Space in the context of models4insight.com",
    type_version="1.0",
    super_types=kibana_space_super_type,
    attribute_defs=kibana_space_attributes_def
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KibanaSpaceAttributesBase(BusinessCollectionAttributesBase):
    elastic_cluster: List[ObjectId]


# END KibanaSpaceAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KibanaSpaceAttributesDefaultsBase(BusinessCollectionAttributesDefaultsBase):
    avatar_initials: Optional[str] = None
    avatar_color: Optional[str] = None


# END KibanaSpaceAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KibanaSpaceAttributes(BusinessCollectionAttributes,
                            KibanaSpaceAttributesDefaultsBase, KibanaSpaceAttributesBase):
    pass


# END KibanaSpaceAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KibanaSpaceBase(BusinessCollectionBase):
    attributes: KibanaSpaceAttributes


# END KibanaSpaceBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KibanaSpaceDefaultsBase(BusinessCollectionDefaultsBase):
    pass


# END KibanaSpaceDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KibanaSpace(BusinessCollection,
                  KibanaSpaceDefaultsBase, KibanaSpaceBase):
    type_name: str = "m4i_kibana_space"

    @classmethod
    def get_type_def(cls):
        return kibana_space_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Kibana Space:
        * Elastic Cluster
        """

        references = [*super().get_referred_entities(),
                      *self.attributes.elastic_cluster
                      ]

        return filter(None, references)
# END KibanaSpace
