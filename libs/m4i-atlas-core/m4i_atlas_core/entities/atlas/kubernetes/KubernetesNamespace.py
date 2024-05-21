from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json, DataClassJsonMixin

from ..core import (AttributeDef, Cardinality, EntityDef, ObjectId,
                    RelationshipDef, RelationshipEndDef, TypeCategory)
from ..data_dictionary.BusinessSystem import (
    BusinessSystem, BusinessSystemAttributes, BusinessSystemAttributesBase,
    BusinessSystemAttributesDefaultsBase, BusinessSystemBase,
    BusinessSystemDefaultsBase)

kubernetes_namespace_super_type = ["m4i_system"]

kubernetes_namespace_attributes_def = [
    AttributeDef(
        name="kubernetesCluster",
        type_name="array<m4i_kubernetes_cluster>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="kubernetesCronjob",
        type_name="array<m4i_kubernetes_cronjob>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="kubernetesDeployment",
        type_name="array<m4i_kubernetes_deployment>",
        cardinality=Cardinality.SET
    )
]

kubernetes_namespace_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_kubernetes_namespace",
    description="A type definition for a generic Kubernetes Namespace in the context of models4insight.com",
    type_version="1.0",
    super_types=kubernetes_namespace_super_type,
    attribute_defs=kubernetes_namespace_attributes_def
)

end_1_kcluster_knamespace = RelationshipEndDef(
    type="m4i_kubernetes_cluster",
    name="kubernetesNamespace",
)
end_2_kcluster_knamespace = RelationshipEndDef(
    type="m4i_kubernetes_namespace",
    name="kubernetesCluster"
)

m4i_kcluster_knamespace_rel_def = RelationshipDef(
    end_def1=end_1_kcluster_knamespace,
    end_def2=end_2_kcluster_knamespace,
    name="m4i_kubernetes_cluster_namespace_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesNamespaceAttributesBase(BusinessSystemAttributesBase):
    pass


# END KubernetesNamespaceAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesNamespaceAttributesDefaultsBase(BusinessSystemAttributesDefaultsBase):
    kubernetes_cluster: List[ObjectId] = field(default_factory=list)
    kubernetes_cronjob: List[ObjectId] = field(default_factory=list)
    kubernetes_deployment: List[ObjectId] = field(default_factory=list)


# END KubernetesNamespaceAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesNamespaceAttributes(BusinessSystemAttributes,
                                    KubernetesNamespaceAttributesDefaultsBase,
                                    KubernetesNamespaceAttributesBase):
    pass


# END KubernetesNamespaceAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesNamespaceBase(BusinessSystemBase):
    attributes: KubernetesNamespaceAttributes


# END KubernetesNamespaceBase

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesNamespaceRelationshipAttributes(DataClassJsonMixin):
    ingress_object: List[ObjectId] = field(default_factory=list)
    kubernetes_service: List[ObjectId] = field(default_factory=list)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesNamespaceDefaultsBase(BusinessSystemDefaultsBase):
    relationship_attributes: KubernetesNamespaceRelationshipAttributes = None


# END KubernetesNamespaceDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesNamespace(BusinessSystem,
                          KubernetesNamespaceDefaultsBase,
                          KubernetesNamespaceBase
                          ):
    type_name: str = "m4i_kubernetes_namespace"

    @classmethod
    def get_type_def(cls):
        return kubernetes_namespace_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this kubernetes cluster:
        the kubernetes cluster
        * list of kubernetes cronjob
        * list of kubernetes deployment
        * ingress object relationship
        * kubernetes service relationship
        """

        references = [*super().get_referred_entities(),
                      *self.attributes.kubernetes_cluster,
                      *self.attributes.kubernetes_cronjob,
                      *self.attributes.kubernetes_deployment,
                      *self.relationship_attributes.ingress_object,
                      *self.relationship_attributes.kubernetes_service]

        return filter(None, references)
    # END get_referred_entities

# END KubernetesNamespace
