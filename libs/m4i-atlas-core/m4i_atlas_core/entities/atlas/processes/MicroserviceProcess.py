from dataclasses import dataclass, field
from typing import Iterable, List

from dataclasses_json import LetterCase, dataclass_json

from .. import RelationshipEndDef, Cardinality, RelationshipDef
from ..core import (AttributeDef, EntityDef, ObjectId,
                    TypeCategory)
from .GenericProcess import (GenericProcess,
                             GenericProcessAttributes,
                             GenericProcessAttributesBase,
                             GenericProcessAttributesDefaultsBase,
                             GenericProcessBase,
                             GenericProcessDefaultsBase)

microservice_process_super_type = ["m4i_generic_process"]

microservice_process_attributes_def = [
    AttributeDef(
        name="system",
        type_name="array<m4i_kubernetes_pod>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="service",
        type_name="array<m4i_kubernetes_service_process>",
        cardinality=Cardinality.SET
    ),
    AttributeDef(
        name="operation",
        type_name="array<m4i_api_operation_process>",
        cardinality=Cardinality.SET
    ),

]

microservice_process_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_microservice_process",
    description="A type definition for a microservice process in the context of models4insight.com",
    type_version="1.0",
    super_types=microservice_process_super_type,
    attribute_defs=microservice_process_attributes_def
)

end_1_system_msprocess = RelationshipEndDef(
    type="m4i_kubernetes_pod",
    name="microservice",
)
end_2_system_msprocess = RelationshipEndDef(
    type="m4i_microservice_process",
    name="system"
)

m4i_system_msprocess_rel_def = RelationshipDef(
    end_def1=end_1_system_msprocess,
    end_def2=end_2_system_msprocess,
    name="m4i_system_microservice_assignment",
    category=TypeCategory.RELATIONSHIP
)

end_1_ksprocess_msprocess = RelationshipEndDef(
    type="m4i_kubernetes_service_process",
    name="microservice",
)
end_2_ksprocess_msprocess = RelationshipEndDef(
    type="m4i_microservice_process",
    name="service"
)

m4i_ksprocess_msprocess_rel_def = RelationshipDef(
    end_def1=end_1_ksprocess_msprocess,
    end_def2=end_2_ksprocess_msprocess,
    name="m4i_kubernetes_service_microservice_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MicroserviceProcessAttributesBase(GenericProcessAttributesBase):
    pass


# END MicroserviceProcessAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MicroserviceProcessAttributesDefaultsBase(GenericProcessAttributesDefaultsBase):
    system: List[ObjectId] = field(default_factory=list)
    api_operation: List[ObjectId] = field(default_factory=list)
    service: List[ObjectId] = field(default_factory=list)


# END MicroserviceProcessAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MicroserviceProcessAttributes(GenericProcessAttributes,
                                    MicroserviceProcessAttributesDefaultsBase,
                                    MicroserviceProcessAttributesBase):
    pass


# END MicroserviceProcessAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MicroserviceProcessBase(GenericProcessBase):
    attributes: MicroserviceProcessAttributes


# END MicroserviceProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MicroserviceProcessDefaultsBase(GenericProcessDefaultsBase):
    pass


# END MicroserviceProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MicroserviceProcess(GenericProcess,
                          MicroserviceProcessDefaultsBase,
                          MicroserviceProcessBase
                          ):
    type_name: str = "m4i_microservice_process"

    @classmethod
    def get_type_def(cls):
        return microservice_process_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this Microservice process:
        system
        service
        list api operation
        """

        references = [*super().get_referred_entities(),
                      *self.attributes.system,
                      *self.attributes.service,
                      *self.attributes.api_operation]

        return filter(None, references)
    # END get_referred_entities

# END MicroserviceProcess
