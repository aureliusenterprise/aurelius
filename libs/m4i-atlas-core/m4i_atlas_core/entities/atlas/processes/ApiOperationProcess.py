from dataclasses import dataclass, field
from typing import Iterable,  List

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

api_operation_process_super_type = ["m4i_generic_process"]

api_operation_process_attributes_def = [
    AttributeDef(
        name="microservice",
        type_name="array<m4i_microservice_process>",
        cardinality=Cardinality.SET
    )
]

api_operation_process_def = EntityDef(
    category=TypeCategory.ENTITY,
    name="m4i_api_operation_process",
    description="A type definition for a API Operation process in the context of models4insight.com",
    type_version="1.0",
    super_types=api_operation_process_super_type,
    attribute_defs=api_operation_process_attributes_def
)

end_1_msprocess_aoprocess = RelationshipEndDef(
    type="m4i_microservice_process",
    name="operation",
)
end_2_msprocess_aoprocess = RelationshipEndDef(
    type="m4i_api_operation_process",
    name="microservice"
)

m4i_msprocess_aoprocess_rel_def = RelationshipDef(
    end_def1=end_1_msprocess_aoprocess,
    end_def2=end_2_msprocess_aoprocess,
    name="m4i_microservice_api_operation_assignment",
    category=TypeCategory.RELATIONSHIP
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiOperationProcessAttributesBase(GenericProcessAttributesBase):
    pass


# END ApiOperationProcessAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiOperationProcessAttributesDefaultsBase(GenericProcessAttributesDefaultsBase):
    microservice: List[ObjectId] = field(default_factory=list)


# END ApiOperationProcessAttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiOperationProcessAttributes(GenericProcessAttributes,
                                    ApiOperationProcessAttributesDefaultsBase,
                                    ApiOperationProcessAttributesBase):
    pass


# END ApiOperationProcessAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiOperationProcessBase(GenericProcessBase):
    attributes: ApiOperationProcessAttributes


# END ApiOperationProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiOperationProcessDefaultsBase(GenericProcessDefaultsBase):
    pass


# END ApiOperationProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiOperationProcess(GenericProcess,
                          ApiOperationProcessDefaultsBase,
                          ApiOperationProcessBase
                          ):
    type_name: str = "m4i_api_operation_process"

    @classmethod
    def get_type_def(cls):
        return api_operation_process_def

    def get_referred_entities(self) -> Iterable[ObjectId]:
        """
        Returns the following references for this API Operation process:
        microservice
        """

        references = [*super().get_referred_entities(),
                      *self.attributes.microservice]

        return filter(None, references)
    # END get_referred_entities

# END ApiOperationProcess
