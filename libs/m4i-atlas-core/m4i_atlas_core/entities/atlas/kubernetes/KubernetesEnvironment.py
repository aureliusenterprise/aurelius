from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Cardinality, EntityDef, ObjectId,
                    TypeCategory)
from ..data_dictionary.BusinessSystem import (
    BusinessSystem, BusinessSystemAttributes, BusinessSystemAttributesBase,
    BusinessSystemAttributesDefaultsBase, BusinessSystemBase,
    BusinessSystemDefaultsBase)

kubernetes_environment_super_type = ["m4i_system"]

kubernetes_environment_attributes_def = [
    AttributeDef(
        name="kubernetesClusters",
        type_name="array<m4i_kubernetes_cluster>",
        cardinality=Cardinality.SET
    )
]

kubernetes_environment_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_kubernetes_environment",
    description="A type definition for a generic Kubernetes Environment in the context of models4insight.com",
    type_version="1.0",
    super_types=kubernetes_environment_super_type,
    attribute_defs=kubernetes_environment_attributes_def
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesEnvironmentAttributesBase(BusinessSystemAttributesBase):
    pass


# END KubernetesEnvironmentAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesEnvironmentAttributesDefaultsBase(BusinessSystemAttributesDefaultsBase):
    kubernetes_clusters: Optional[List[ObjectId]] = field(default_factory=list)

# END KubernetesEnvironmentAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesEnvironmentAttributes(BusinessSystemAttributes,
                                     KubernetesEnvironmentAttributesDefaultsBase,
                                     KubernetesEnvironmentAttributesBase):
    pass


# END KubernetesEnvironmentAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesEnvironmentBase(BusinessSystemBase):
    attributes: KubernetesEnvironmentAttributes


# END KubernetesEnvironmentBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesEnvironmentDefaultsBase(BusinessSystemDefaultsBase):
    pass


# END KubernetesEnvironmentDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesEnvironment(BusinessSystem,
                           KubernetesEnvironmentDefaultsBase,
                           KubernetesEnvironmentBase
                           ):
    type_name: str = "m4i_kubernetes_environment"

    @classmethod
    def get_type_def(cls):
        return kubernetes_environment_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Kubernetes Environment:
        * List of Kubernetes Clusters
        """

        references = [*super().get_referred_entities(),
                      *self.attributes.kubernetes_clusters]

        return filter(None, references)
    # END get_referred_entities

# END KubernetesEnvironment
