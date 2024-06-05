from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, M4IAttributes
from m4i_atlas_core.entities.atlas.kubernetes import (KubernetesCronjob as CoreKubernetesCronjob,
                                                      KubernetesCronjobAttributes as CoreKubernetesCronjobAttributes)
from typing import Optional, List


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesCronjobBase(DataClassJsonMixin):
    name: str
    qualified_name: str
    kubernetes_namespace: str


# END KubernetesCronjobBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesCronjobDefaultsBase(DataClassJsonMixin):
    description: Optional[str] = None
    tags: Optional[str] = None
    schedule: Optional[str] = None
    kubernetes_pod: List[str] = field(default_factory=list)


# END KubernetesCronjobDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesCronjob(
    KubernetesCronjobDefaultsBase,
    KubernetesCronjobBase
):
    def convert_to_atlas(self) -> CoreKubernetesCronjob:
        """
        Returns a corresponding Atlas `KubernetesCronjob` instance.
        """
        kubernetes_namespace: List[ObjectId] = []

        kubernetes_namespace_unique_attributes = M4IAttributes(
            qualified_name=self.kubernetes_namespace
        )
        kubernetes_namespace.append(ObjectId(
            type_name="m4i_kubernetes_namespace",
            unique_attributes=kubernetes_namespace_unique_attributes
        ))

        attributes = CoreKubernetesCronjobAttributes(
            definition=self.description,
            name=self.name,
            qualified_name=self.qualified_name,
            kubernetes_namespace=kubernetes_namespace,
            tags=self.tags,
            schedule=self.schedule
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

        entity = CoreKubernetesCronjob(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END KubernetesCronjob
