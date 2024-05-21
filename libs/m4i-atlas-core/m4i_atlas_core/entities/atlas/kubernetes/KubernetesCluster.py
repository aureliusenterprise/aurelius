from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json, DataClassJsonMixin

from ..core import (AttributeDef, Cardinality, EntityDef, ObjectId,
                    RelationshipDef, RelationshipEndDef, TypeCategory)
from ..data_dictionary.BusinessSystem import (
    BusinessSystem, BusinessSystemAttributes, BusinessSystemAttributesBase,
    BusinessSystemAttributesDefaultsBase, BusinessSystemBase,
    BusinessSystemDefaultsBase)

kubernetes_cluster_super_type = ["m4i_system"]

kubernetes_cluster_attributes_def = [
    AttributeDef(
        name="kubernetesEnvironment",
        type_name="array<m4i_kubernetes_environment>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="kubernetesNamespace",
        type_name="array<m4i_kubernetes_namespace>",
        cardinality=Cardinality.SET
    )
]

kubernetes_cluster_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_kubernetes_cluster",
    description="A type definition for a generic Kubernetes Cluster in the context of models4insight.com",
    type_version="1.0",
    super_types=kubernetes_cluster_super_type,
    attribute_defs=kubernetes_cluster_attributes_def
)

end_1_kcluster_kenvironment = RelationshipEndDef(
    type="m4i_kubernetes_environment",
    name="kubernetesClusters",
)
end_2_kcluster_kenvironment = RelationshipEndDef(
    type="m4i_kubernetes_cluster",
    name="kubernetesEnvironment"
)

m4i_kcluster_kenvironment_rel_def = RelationshipDef(
    end_def1=end_1_kcluster_kenvironment,
    end_def2=end_2_kcluster_kenvironment,
    name="m4i_kubernetes_environment_cluster_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesClusterAttributesBase(BusinessSystemAttributesBase):
    pass


# END KubernetesClusterAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesClusterAttributesDefaultsBase(BusinessSystemAttributesDefaultsBase):
    kubernetes_environment: List[ObjectId] = field(default_factory=list)
    kubernetes_namespace: List[ObjectId] = field(default_factory=list)


# END KubernetesClusterAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesClusterAttributes(BusinessSystemAttributes,
                                  KubernetesClusterAttributesDefaultsBase,
                                  KubernetesClusterAttributesBase):
    pass


# END KubernetesClusterAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesClusterBase(BusinessSystemBase):
    attributes: KubernetesClusterAttributes


# END KubernetesClusterBase
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesClusterRelationshipAttributes(DataClassJsonMixin):
    ingress_controller: List[ObjectId] = field(default_factory=list)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesClusterDefaultsBase(BusinessSystemDefaultsBase):
    relationship_attributes: KubernetesClusterRelationshipAttributes = None


# END KubernetesClusterDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesCluster(BusinessSystem,
                        KubernetesClusterDefaultsBase,
                        KubernetesClusterBase
                        ):
    type_name: str = "m4i_kubernetes_cluster"

    @classmethod
    def get_type_def(cls):
        return kubernetes_cluster_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this kubernetes cluster:
        * List of kubernetes namespaces
        * list of the kubernetes environment
        """

        references = [*super().get_referred_entities(),
                      *self.attributes.kubernetes_namespace,
                      *self.attributes.kubernetes_environment]

        return filter(None, references)
    # END get_referred_entities

# END KubernetesCluster
