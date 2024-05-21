from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..core import (AttributeDef, Cardinality, EntityDef, ObjectId,
                    RelationshipDef, RelationshipEndDef, TypeCategory)
from ..data_dictionary.BusinessSystem import (
    BusinessSystem, BusinessSystemAttributes, BusinessSystemAttributesBase,
    BusinessSystemAttributesDefaultsBase, BusinessSystemBase,
    BusinessSystemDefaultsBase)

kubernetes_cronjob_super_type = ["m4i_system"]

kubernetes_cronjob_attributes_def = [
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
        name="schedule",
        type_name="string"
    ),
    AttributeDef(
        name="tags",
        type_name="string"
    )
]

kubernetes_cronjob_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_kubernetes_cronjob",
    description="A type definition for a generic Kubernetes CronJob in the context of models4insight.com",
    type_version="1.0",
    super_types=kubernetes_cronjob_super_type,
    attribute_defs=kubernetes_cronjob_attributes_def
)

end_1_knamespace_kcronjob = RelationshipEndDef(
    type="m4i_kubernetes_namespace",
    name="kubernetesCronjob",
)
end_2_knamespace_kcronjob = RelationshipEndDef(
    type="m4i_kubernetes_cronjob",
    name="kubernetesNamespace"
)

m4i_knamespace_kcronjob_rel_def = RelationshipDef(
    end_def1=end_1_knamespace_kcronjob,
    end_def2=end_2_knamespace_kcronjob,
    name="m4i_kubernetes_namespace_cronjob_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesCronjobAttributesBase(BusinessSystemAttributesBase):
    pass


# END KubernetesCronjobAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesCronjobAttributesDefaultsBase(BusinessSystemAttributesDefaultsBase):
    kubernetes_namespace: List[ObjectId] = field(default_factory=list)
    kubernetes_pod: List[ObjectId] = field(default_factory=list)
    schedule: Optional[str] = None
    tags: Optional[str] = None


# END KubernetesCronjobAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesCronjobAttributes(BusinessSystemAttributes,
                                  KubernetesCronjobAttributesDefaultsBase,
                                  KubernetesCronjobAttributesBase):
    pass


# END KubernetesCronjobAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesCronjobBase(BusinessSystemBase):
    attributes: KubernetesCronjobAttributes


# END KubernetesCronjobBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesCronjobDefaultsBase(BusinessSystemDefaultsBase):
    pass


# END KubernetesCronjobDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesCronjob(BusinessSystem,
                        KubernetesCronjobDefaultsBase,
                        KubernetesCronjobBase
                        ):
    type_name: str = "m4i_kubernetes_cronjob"

    @classmethod
    def get_type_def(cls):
        return kubernetes_cronjob_def

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

# END KubernetesCronjob
