from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Cardinality, EntityDef, ObjectId,
                    RelationshipDef, RelationshipEndDef, TypeCategory)
from ..data_dictionary.BusinessSystem import (
    BusinessSystem, BusinessSystemAttributes, BusinessSystemAttributesBase,
    BusinessSystemAttributesDefaultsBase, BusinessSystemBase,
    BusinessSystemDefaultsBase)

kubernetes_deployment_super_type = ["m4i_system"]

kubernetes_deployment_attributes_def = [
    AttributeDef(
        name="kubernetesNamespace",
        type_name="array<m4i_kubernetes_namespace>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="kubernetesPod",
        type_name="array<m4i_kubernetes_pod>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="tags",
        type_name="string"
    )
]

kubernetes_deployment_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_kubernetes_deployment",
    description="A type definition for a generic Kubernetes Deployment in the context of models4insight.com",
    type_version="1.0",
    super_types=kubernetes_deployment_super_type,
    attribute_defs=kubernetes_deployment_attributes_def
)

end_1_knamespace_kdeployment = RelationshipEndDef(
    type="m4i_kubernetes_namespace",
    name="kubernetesDeployment",
)
end_2_knamespace_kdeployment = RelationshipEndDef(
    type="m4i_kubernetes_deployment",
    name="kubernetesNamespace"
)

m4i_knamespace_kdeployment_rel_def = RelationshipDef(
    end_def1=end_1_knamespace_kdeployment,
    end_def2=end_2_knamespace_kdeployment,
    name="m4i_kubernetes_namespace_deployment_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesDeploymentAttributesBase(BusinessSystemAttributesBase):
    pass


# END KubernetesDeploymentAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesDeploymentAttributesDefaultsBase(BusinessSystemAttributesDefaultsBase):
    kubernetes_namespace: List[ObjectId] = field(default_factory=list)
    kubernetes_pod: List[ObjectId] = field(default_factory=list)
    tags: Optional[str] = None


# END KubernetesDeploymentAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesDeploymentAttributes(BusinessSystemAttributes,
                                     KubernetesDeploymentAttributesDefaultsBase,
                                     KubernetesDeploymentAttributesBase):
    pass


# END KubernetesDeploymentAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesDeploymentBase(BusinessSystemBase):
    attributes: KubernetesDeploymentAttributes


# END KubernetesDeploymentBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesDeploymentDefaultsBase(BusinessSystemDefaultsBase):
    pass


# END KubernetesDeploymentDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesDeployment(BusinessSystem,
                           KubernetesDeploymentDefaultsBase,
                           KubernetesDeploymentBase
                           ):
    type_name: str = "m4i_kubernetes_deployment"

    @classmethod
    def get_type_def(cls):
        return kubernetes_deployment_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this kubernetes cluster:
        the kubernetes namespace
        * list of kubernetes pod
        """

        references = [*super().get_referred_entities(),
                      *self.attributes.kubernetes_namespace,
                      *self.attributes.kubernetes_pod]

        return filter(None, references)
    # END get_referred_entities

# END KubernetesDeployment
