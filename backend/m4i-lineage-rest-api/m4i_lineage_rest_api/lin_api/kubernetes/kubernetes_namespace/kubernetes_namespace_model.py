from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, M4IAttributes
from m4i_atlas_core.entities.atlas.kubernetes import (KubernetesNamespace as CoreKubernetesNamespace,
                                                      KubernetesNamespaceAttributes as CoreKubernetesNamespaceAttributes)
from typing import Optional, List


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesNamespaceBase(DataClassJsonMixin):
    name: str
    qualified_name: str
    kubernetes_cluster: str


# END KubernetesNamespaceBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesNamespaceDefaultsBase(DataClassJsonMixin):
    description: Optional[str] = None
    kubernetes_deployment: List[str] = field(default_factory=list)
    kubernetes_cronjob: List[str] = field(default_factory=list)


# END KubernetesNamespaceDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesNamespace(
    KubernetesNamespaceDefaultsBase,
    KubernetesNamespaceBase
):
    def convert_to_atlas(self) -> CoreKubernetesNamespace:
        """
        Returns a corresponding Atlas `KubernetesNamespace` instance.
        """

        kubernetes_cluster: List[ObjectId] = []

        kubernetes_cluster_unique_attributes = M4IAttributes(
            qualified_name=self.kubernetes_cluster
        )
        kubernetes_cluster.append(ObjectId(
            type_name="m4i_kubernetes_cluster",
            unique_attributes=kubernetes_cluster_unique_attributes
        ))

        attributes = CoreKubernetesNamespaceAttributes(
            definition=self.description,
            name=self.name,
            qualified_name=self.qualified_name,
            kubernetes_cluster=kubernetes_cluster
        )

        if bool(self.kubernetes_deployment):
            kubernetes_deployment: List[ObjectId] = []
            for kd in self.kubernetes_deployment:
                kubernetes_deployment_unique_attributes = M4IAttributes(
                    qualified_name=kd
                )
                kubernetes_deployment.append(ObjectId(
                    type_name="m4i_kubernetes_deployment",
                    unique_attributes=kubernetes_deployment_unique_attributes
                ))
            # END FOR
            attributes.kubernetes_deployment = kubernetes_deployment
        # END IF

        if bool(self.kubernetes_cronjob):
            kubernetes_cronjob: List[ObjectId] = []
            for kc in self.kubernetes_cronjob:
                kubernetes_cronjob_unique_attributes = M4IAttributes(
                    qualified_name=kc
                )
                kubernetes_cronjob.append(ObjectId(
                    type_name="m4i_kubernetes_cronjob",
                    unique_attributes=kubernetes_cronjob_unique_attributes
                ))
            # END FOR
            attributes.kubernetes_cronjob = kubernetes_cronjob
        # END IF

        entity = CoreKubernetesNamespace(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END KubernetesNamespace
