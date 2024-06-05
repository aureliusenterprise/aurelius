from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, M4IAttributes
from m4i_atlas_core.entities.atlas.kubernetes import (KubernetesPod as CoreKubernetesPod,
                                                      KubernetesPodAttributes as CoreKubernetesPodAttributes)
from typing import Optional, List


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesPodBase(DataClassJsonMixin):
    name: str
    qualified_name: str


# END KubernetesPodBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesPodDefaultsBase(DataClassJsonMixin):
    description: Optional[str] = None
    kubernetes_deployment: Optional[str] = None
    kubernetes_cronjob: Optional[str] = None
    microservice: List[str] = field(default_factory=list)
    replicas: Optional[str] = None


# END KubernetesPodDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesPod(
    KubernetesPodDefaultsBase,
    KubernetesPodBase
):
    def convert_to_atlas(self) -> CoreKubernetesPod:
        """
        Returns a corresponding Atlas `KubernetesPod` instance.
        """

        attributes = CoreKubernetesPodAttributes(
            definition=self.description,
            name=self.name,
            qualified_name=self.qualified_name,
            replicas=self.replicas
        )

        if bool(self.kubernetes_deployment):
            kubernetes_deployment: List[ObjectId] = []

            kubernetes_deployment_unique_attributes = M4IAttributes(
                qualified_name=self.kubernetes_deployment
            )
            kubernetes_deployment.append(ObjectId(
                type_name="m4i_kubernetes_deployment",
                unique_attributes=kubernetes_deployment_unique_attributes
            ))
            attributes.kubernetes_deployment = kubernetes_deployment
        # END IF

        if bool(self.kubernetes_cronjob):
            kubernetes_cronjob: List[ObjectId] = []

            kubernetes_cronjob_unique_attributes = M4IAttributes(
                qualified_name=self.kubernetes_cronjob
            )
            kubernetes_cronjob.append(ObjectId(
                type_name="m4i_kubernetes_cronjob",
                unique_attributes=kubernetes_cronjob_unique_attributes
            ))
            attributes.kubernetes_cronjob = kubernetes_cronjob
        # END IF

        if bool(self.microservice):
            microservice: List[ObjectId] = []
            for ms in self.microservice:
                microservice_unique_attributes = M4IAttributes(
                    qualified_name=ms
                )
                microservice.append(ObjectId(
                    type_name="m4i_microservice_process",
                    unique_attributes=microservice_unique_attributes
                ))
            attributes.microservice = microservice
        # END IF

        entity = CoreKubernetesPod(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END KubernetesPod
