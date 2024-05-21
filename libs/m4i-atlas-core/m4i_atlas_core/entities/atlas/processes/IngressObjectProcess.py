from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from typing import Iterable, List

from dataclasses_json import LetterCase, dataclass_json

from ..core import RelationshipEndDef, Cardinality, RelationshipDef
from ..core import (AttributeDef, EntityDef, ObjectId,
                    TypeCategory)

from .GenericProcess import (GenericProcess,
                             GenericProcessAttributes,
                             GenericProcessAttributesBase,
                             GenericProcessAttributesDefaultsBase,
                             GenericProcessBase,
                             GenericProcessDefaultsBase)

ingress_object_process_super_type = ["m4i_generic_process"]

ingress_object_process_attributes_def = [
    AttributeDef(
        name="ingressController",
        type_name="array<m4i_ingress_controller_process>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="kubernetesService",
        type_name="array<m4i_kubernetes_service_process>",
        cardinality=Cardinality.SET
    )
]

ingress_object_process_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_ingress_object_process",
    description="A type definition for a kubernetes ingress object process in the context of models4insight.com",
    type_version="1.0",
    super_types=ingress_object_process_super_type,
    attribute_defs=ingress_object_process_attributes_def
)

end_1_knamespace_ioprocess = RelationshipEndDef(
    type="m4i_kubernetes_namespace",
    name="ingressObject",

)
end_2_knamespace_ioprocess = RelationshipEndDef(
    type="m4i_ingress_object_process",
    name="namespace"
)

m4i_knamespace_ioprocess_rel_def = RelationshipDef(
    end_def1=end_1_knamespace_ioprocess,
    end_def2=end_2_knamespace_ioprocess,
    name="m4i_namespace_ingress_object_assignment",
    category=TypeCategory.RELATIONSHIP
)

end_1_icprocess_ioprocess = RelationshipEndDef(
    type="m4i_ingress_controller_process",
    name="ingressObject",

)
end_2_icprocess_ioprocess = RelationshipEndDef(
    type="m4i_ingress_object_process",
    name="ingressController"
)

m4i_icprocess_ioprocess_rel_def = RelationshipDef(
    end_def1=end_1_icprocess_ioprocess,
    end_def2=end_2_icprocess_ioprocess,
    name="m4i_ingress_controller_ingress_object_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressObjectProcessAttributesBase(GenericProcessAttributesBase):
    pass


# END IngressObjectProcessAttributesBase

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressObjectProcessRelationshipAttributes(DataClassJsonMixin):
    namespace: List[ObjectId] = field(default_factory=list)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressObjectProcessAttributesDefaultsBase(GenericProcessAttributesDefaultsBase):
    ingress_controller: List[ObjectId] = field(default_factory=list)
    kubernetes_service: List[ObjectId] = field(default_factory=list)


# END IngressObjectProcessAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressObjectProcessAttributes(GenericProcessAttributes,
                                     IngressObjectProcessAttributesDefaultsBase,
                                     IngressObjectProcessAttributesBase):
    pass


# END IngressObjectProcessAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressObjectProcessBase(GenericProcessBase):
    attributes: IngressObjectProcessAttributes


# END IngressObjectProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressObjectProcessDefaultsBase(GenericProcessDefaultsBase):
    relationship_attributes: IngressObjectProcessRelationshipAttributes = None


# END IngressObjectProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressObjectProcess(GenericProcess,
                           IngressObjectProcessDefaultsBase,
                           IngressObjectProcessBase
                           ):
    type_name: str = "m4i_ingress_object_process"

    @classmethod
    def get_type_def(cls):
        return ingress_object_process_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Ingress Object process:
        list of kubernetes service
        ingress controller
        namespace
        """

        references = [*super().get_referred_entities(),
                      *self.attributes.kubernetes_service,
                      *self.attributes.ingress_controller,
                      *self.relationship_attributes.namespace]

        return filter(None, references)
    # END get_referred_entities

# END IngressObjectProcess
