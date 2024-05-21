from dataclasses import dataclass, field
from typing import Iterable, Optional, List

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Cardinality, EntityDef, ObjectId,
                    RelationshipDef, RelationshipEndDef, TypeCategory)
from ..data_dictionary.BusinessSystem import (
    BusinessSystem, BusinessSystemAttributes, BusinessSystemAttributesBase,
    BusinessSystemAttributesDefaultsBase, BusinessSystemBase,
    BusinessSystemDefaultsBase)

kubernetes_pod_super_type = ["m4i_system"]

kubernetes_pod_attributes_def = [
    AttributeDef(
        name="kubernetesCronjob",
        type_name="array<m4i_kubernetes_cronjob>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="kubernetesDeployment",
        type_name="array<m4i_kubernetes_deployment>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="replicas",
        type_name="string",
    ),
    AttributeDef(
        name="microservice",
        type_name="array<m4i_microservice_process>",
        cardinality=Cardinality.SET
    )
]

kubernetes_pod_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_kubernetes_pod",
    description="A type definition for a generic Kubernetes Pod in the context of models4insight.com",
    type_version="1.0",
    super_types=kubernetes_pod_super_type,
    attribute_defs=kubernetes_pod_attributes_def
)

end_1_kdeployment_kpod = RelationshipEndDef(
    type="m4i_kubernetes_deployment",
    name="kubernetesPod",
)
end_2_kdeployment_kpod = RelationshipEndDef(
    type="m4i_kubernetes_pod",
    name="kubernetesDeployment"
)

m4i_kdeployment_kpod_rel_def = RelationshipDef(
    end_def1=end_1_kdeployment_kpod,
    end_def2=end_2_kdeployment_kpod,
    name="m4i_kubernetes_deployment_pod_assignment",
    category=TypeCategory.RELATIONSHIP
)

end_1_kcronjob_kpod = RelationshipEndDef(
    type="m4i_kubernetes_cronjob",
    name="kubernetesPod",
    cardinality=Cardinality.SET
)
end_2_kcronjob_kpod = RelationshipEndDef(
    type="m4i_kubernetes_pod",
    name="kubernetesCronjob"
)

m4i_kcronjob_kpod_rel_def = RelationshipDef(
    end_def1=end_1_kcronjob_kpod,
    end_def2=end_2_kcronjob_kpod,
    name="m4i_kubernetes_cronjob_pod_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesPodAttributesBase(BusinessSystemAttributesBase):
    pass


# END KubernetesPodAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesPodAttributesDefaultsBase(BusinessSystemAttributesDefaultsBase):
    kubernetes_cronjob: List[ObjectId] = field(default_factory=list)
    kubernetes_deployment: List[ObjectId] = field(default_factory=list)
    replicas: Optional[str] = None
    microservice: List[ObjectId] = field(default_factory=list)


# END KubernetesPodAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesPodAttributes(BusinessSystemAttributes,
                              KubernetesPodAttributesDefaultsBase,
                              KubernetesPodAttributesBase):
    pass


# END KubernetesPodAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesPodBase(BusinessSystemBase):
    attributes: KubernetesPodAttributes


# END KubernetesPodBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesPodDefaultsBase(BusinessSystemDefaultsBase):
    pass


# END KubernetesPodDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesPod(BusinessSystem,
                    KubernetesPodDefaultsBase,
                    KubernetesPodBase
                    ):
    type_name: str = "m4i_kubernetes_pod"

    @classmethod
    def get_type_def(cls):
        return kubernetes_pod_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this kubernetes Pod:
        list of kubernetes cronjob
        list of kubernetes deployment
        list of microservices
        """

        references = [*super().get_referred_entities(),
                      *self.attributes.kubernetes_cronjob,
                      *self.attributes.kubernetes_deployment,
                      *self.attributes.microservice]

        return filter(None, references)
    # END get_referred_entities

# END KubernetesPod
