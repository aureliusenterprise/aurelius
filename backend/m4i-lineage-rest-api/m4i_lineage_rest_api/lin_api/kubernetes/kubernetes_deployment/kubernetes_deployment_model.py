from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, M4IAttributes
from m4i_atlas_core.entities.atlas.kubernetes import (KubernetesDeployment as CoreKubernetesDeployment,
                                                      KubernetesDeploymentAttributes as CoreKubernetesDeploymentAttributes)
from typing import Optional, List


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesDeploymentBase(DataClassJsonMixin):
    name: str
    qualified_name: str
    kubernetes_namespace: str


# END KubernetesDeploymentBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesDeploymentDefaultsBase(DataClassJsonMixin):
    description: Optional[str] = None
    tags: Optional[str] = None
    kubernetes_pod: List[str] = field(default_factory=list)


# END KubernetesDeploymentDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesDeployment(
    KubernetesDeploymentDefaultsBase,
    KubernetesDeploymentBase
):
    def convert_to_atlas(self) -> CoreKubernetesDeployment:
        """
        Returns a corresponding Atlas `KubernetesDeployment` instance.
        """
        kubernetes_namespace: List[ObjectId] = []

        kubernetes_namespace_unique_attributes = M4IAttributes(
            qualified_name=self.kubernetes_namespace
        )
        kubernetes_namespace.append(ObjectId(
            type_name="m4i_kubernetes_namespace",
            unique_attributes=kubernetes_namespace_unique_attributes
        ))

        attributes = CoreKubernetesDeploymentAttributes(
            definition=self.description,
            name=self.name,
            qualified_name=self.qualified_name,
            kubernetes_namespace=kubernetes_namespace,
            tags=self.tags
        )

        if bool(self.kubernetes_pod):
            kubernetes_pod: List[ObjectId] = []
            for kp in self.kubernetes_pod:
                kubernetes_pod_unique_attributes = M4IAttributes(
                    qualified_name=kp
                )
                kubernetes_pod.append(ObjectId(
                    type_name="m4i_kubernetes_pod",
                    unique_attributes=kubernetes_pod_unique_attributes
                ))
            # END FOR
            attributes.kubernetes_pod = kubernetes_pod
        # END IF

        entity = CoreKubernetesDeployment(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END KubernetesDeployment
