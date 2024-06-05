from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, M4IAttributes
from m4i_atlas_core.entities.atlas.kubernetes import (KubernetesEnvironment as CoreKubernetesEnvironment,
                                                      KubernetesEnvironmentAttributes as CoreKubernetesEnvironmentAttributes)
from typing import Optional, List


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesEnvironmentBase(DataClassJsonMixin):
    name: str
    qualified_name: str
    # END _qualified_name


# END KubernetesEnvironmentBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesEnvironmentDefaultsBase(DataClassJsonMixin):
    description: Optional[str] = None
    kubernetes_clusters: List[str] = field(default_factory=list)


# END KubernetesEnvironmentDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesEnvironment(
    KubernetesEnvironmentDefaultsBase,
    KubernetesEnvironmentBase
):
    def convert_to_atlas(self) -> CoreKubernetesEnvironment:
        """
        Returns a corresponding Atlas `KubernetesEnvironment` instance.
        """

        attributes = CoreKubernetesEnvironmentAttributes(
            definition=self.description,
            name=self.name,
            qualified_name=self.qualified_name
        )

        if bool(self.kubernetes_clusters):
            kubernetes_clusters: List[ObjectId] = []
            for kc in self.kubernetes_clusters:
                kubernetes_clusters_unique_attributes = M4IAttributes(
                    qualified_name=kc
                )
                kubernetes_clusters.append(ObjectId(
                    type_name="m4i_kubernetes_cluster",
                    unique_attributes=kubernetes_clusters_unique_attributes
                ))
            # END FOR
            attributes.kubernetes_clusters = kubernetes_clusters
        # END IF

        entity = CoreKubernetesEnvironment(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END KubernetesEnvironment
