from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, M4IAttributes
from m4i_atlas_core.entities.atlas.kubernetes import (KubernetesCluster as CoreKubernetesCluster,
                                                      KubernetesClusterAttributes as CoreKubernetesClusterAttributes)
from typing import Optional, List


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesClusterBase(DataClassJsonMixin):
    name: str
    qualified_name: str
    kubernetes_environment: str
    # END _qualified_name


# END KubernetesClusterBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesClusterDefaultsBase(DataClassJsonMixin):
    description: Optional[str] = None
    kubernetes_namespace: List[str] = field(default_factory=list)


# END KubernetesClusterDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesCluster(
    KubernetesClusterDefaultsBase,
    KubernetesClusterBase
):
    def convert_to_atlas(self) -> CoreKubernetesCluster:
        """
        Returns a corresponding Atlas `KubernetesCluster` instance.
        """

        kubernetes_environment: List[ObjectId] = []

        kubernetes_environment_unique_attributes = M4IAttributes(
            qualified_name=self.kubernetes_environment
        )
        kubernetes_environment.append(ObjectId(
            type_name="m4i_kubernetes_environment",
            unique_attributes=kubernetes_environment_unique_attributes
        ))
        # END FOR

        attributes = CoreKubernetesClusterAttributes(
            definition=self.description,
            name=self.name,
            qualified_name=self.qualified_name,
            kubernetes_environment=kubernetes_environment
        )

        if bool(self.kubernetes_namespace):
            kubernetes_namespace: List[ObjectId] = []
            for kc in self.kubernetes_namespace:
                kubernetes_namespace_unique_attributes = M4IAttributes(
                    qualified_name=kc
                )
                kubernetes_namespace.append(ObjectId(
                    type_name="m4i_kubernetes_namespace",
                    unique_attributes=kubernetes_namespace_unique_attributes
                ))
            # END FOR
            attributes.kubernetes_namespace = kubernetes_namespace
        # END IF

        entity = CoreKubernetesCluster(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END KubernetesCluster
