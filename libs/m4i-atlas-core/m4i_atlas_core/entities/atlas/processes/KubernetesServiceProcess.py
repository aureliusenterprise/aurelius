from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from typing import Iterable, Optional, List

from dataclasses_json import LetterCase, dataclass_json

from ..core import RelationshipEndDef, Cardinality, RelationshipDef, RelationshipAttributeDef
from ..core import (AttributeDef, EntityDef, ObjectId,
                    TypeCategory, RelationshipAttribute)

from .GenericProcess import (GenericProcess,
                             GenericProcessAttributes,
                             GenericProcessAttributesBase,
                             GenericProcessAttributesDefaultsBase,
                             GenericProcessBase,
                             GenericProcessDefaultsBase)

kubernetes_service_process_super_type = ["m4i_generic_process"]

kubernetes_service_process_attributes_def = [
    AttributeDef(
        name="ingressObject",
        type_name="array<m4i_ingress_object_process>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="microservice",
        type_name="array<m4i_microservice_process>",
        cardinality=Cardinality.SET
    )
]

kubernetes_service_process_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_kubernetes_service_process",
    description="A type definition for a kubernetes ingress object process in the context of models4insight.com",
    type_version="1.0",
    super_types=kubernetes_service_process_super_type,
    attribute_defs=kubernetes_service_process_attributes_def
)

end_1_knamespace_ksprocess = RelationshipEndDef(
    type="m4i_kubernetes_namespace",
    name="service",
)
end_2_knamespace_ksprocess = RelationshipEndDef(
    type="m4i_kubernetes_service_process",
    name="namespace"
)

m4i_knamespace_ksprocess_rel_def = RelationshipDef(
    end_def1=end_1_knamespace_ksprocess,
    end_def2=end_2_knamespace_ksprocess,
    name="m4i_namespace_kubernetes_service_assignment",
    category=TypeCategory.RELATIONSHIP
)
end_1_ioprocess_ksprocess = RelationshipEndDef(
    type="m4i_ingress_object_process",
    name="kubernetesService",
)
end_2_ioprocess_ksprocess = RelationshipEndDef(
    type="m4i_kubernetes_service_process",
    name="ingressObject"
)

m4i_ioprocess_ksprocess_rel_def = RelationshipDef(
    end_def1=end_1_ioprocess_ksprocess,
    end_def2=end_2_ioprocess_ksprocess,
    name="m4i_ingress_object_kubernetes_service_assignment",
    category=TypeCategory.RELATIONSHIP
)

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesServiceProcessAttributesBase(GenericProcessAttributesBase):
    pass


# END KubernetesServiceProcessAttributesBase

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesServiceProcessRelationshipAttributes(DataClassJsonMixin):
    namespace: List[ObjectId] = field(default_factory=list)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesServiceProcessAttributesDefaultsBase(GenericProcessAttributesDefaultsBase):
    ingress_object: List[ObjectId] = field(default_factory=list)
    microservice: List[ObjectId] = field(default_factory=list)


# END KubernetesServiceProcessAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesServiceProcessAttributes(GenericProcessAttributes,
                                         KubernetesServiceProcessAttributesDefaultsBase,
                                         KubernetesServiceProcessAttributesBase):
    pass


# END KubernetesServiceProcessAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesServiceProcessBase(GenericProcessBase):
    attributes: KubernetesServiceProcessAttributes


# END KubernetesServiceProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesServiceProcessDefaultsBase(GenericProcessDefaultsBase):
    relationship_attributes: KubernetesServiceProcessRelationshipAttributes = None


# END KubernetesServiceProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class KubernetesServiceProcess(GenericProcess,
                               KubernetesServiceProcessDefaultsBase,
                               KubernetesServiceProcessBase
                               ):
    type_name: str = "m4i_kubernetes_service_process"

    @classmethod
    def get_type_def(cls):
        return kubernetes_service_process_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Kubernetes Service process:
        list of microservice
        ingress object
        namespace
        """

        references = [*super().get_referred_entities(),
                      *self.attributes.microservice,
                      *self.attributes.ingress_object,
                      *self.relationship_attributes.namespace]

        return filter(None, references)
    # END get_referred_entities

# END KubernetesServiceProcess
