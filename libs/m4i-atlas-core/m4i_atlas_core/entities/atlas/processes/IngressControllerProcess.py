from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from typing import Iterable, Optional, List

from dataclasses_json import LetterCase, dataclass_json

from ..core import RelationshipEndDef, Cardinality, RelationshipDef, RelationshipAttributeDef
from ..core import (AttributeDef, EntityDef, ObjectId,
                    TypeCategory, RelationshipAttribute, Relationship)

from .GenericProcess import (GenericProcess,
                             GenericProcessAttributes,
                             GenericProcessAttributesBase,
                             GenericProcessAttributesDefaultsBase,
                             GenericProcessBase,
                             GenericProcessDefaultsBase)

ingress_controller_process_super_type = ["m4i_generic_process"]

ingress_controller_process_attributes_def = [
    AttributeDef(
        name="ingressObject",
        type_name="array<m4i_ingress_object_process>",
        cardinality=Cardinality.SET
    )
]

ingress_controller_process_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_ingress_controller_process",
    description="A type definition for a microservice process in the context of models4insight.com",
    type_version="1.0",
    super_types=ingress_controller_process_super_type,
    attribute_defs=ingress_controller_process_attributes_def
)

end_1_kcluster_icprocess = RelationshipEndDef(
    type="m4i_kubernetes_cluster",
    name="ingressController",
)
end_2_kcluster_icprocess = RelationshipEndDef(
    type="m4i_ingress_controller_process",
    name="cluster"
)

m4i_kcluster_icprocess_rel_def = RelationshipDef(
    end_def1=end_1_kcluster_icprocess,
    end_def2=end_2_kcluster_icprocess,
    name="m4i_cluster_ingress_controller_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressControllerProcessAttributesBase(GenericProcessAttributesBase):
    pass


# END IngressControllerProcessAttributesBase

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressControllerProcessRelationshipAttributes(DataClassJsonMixin):
    cluster: List[ObjectId] = field(default_factory=list)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressControllerProcessAttributesDefaultsBase(GenericProcessAttributesDefaultsBase):
    ingress_object: List[ObjectId] = field(default_factory=list)



# END IngressControllerProcessAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressControllerProcessAttributes(GenericProcessAttributes,
                                         IngressControllerProcessAttributesDefaultsBase,
                                         IngressControllerProcessAttributesBase):
    pass


# END IngressControllerProcessAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressControllerProcessBase(GenericProcessBase):
    attributes: IngressControllerProcessAttributes


# END IngressControllerProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressControllerProcessDefaultsBase(GenericProcessDefaultsBase):
    relationship_attributes: IngressControllerProcessRelationshipAttributes = None


# END IngressControllerProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IngressControllerProcess(GenericProcess,
                               IngressControllerProcessDefaultsBase,
                               IngressControllerProcessBase
                               ):
    type_name: str = "m4i_ingress_controller_process"

    @classmethod
    def get_type_def(cls):
        return ingress_controller_process_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Ingress Controller process:
        list of ingress objects
        cluster
        """

        references = [*super().get_referred_entities(),
                      *self.attributes.ingress_object,
                      *self.relationship_attributes.cluster]

        return filter(None, references)
    # END get_referred_entities

# END IngressControllerProcess
