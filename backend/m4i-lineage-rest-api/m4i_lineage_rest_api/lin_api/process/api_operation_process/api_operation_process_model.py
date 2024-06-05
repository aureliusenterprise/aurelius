from dataclasses import dataclass, field
from dataclasses_json import LetterCase, dataclass_json, DataClassJsonMixin
from m4i_atlas_core import ObjectId, M4IAttributes
from m4i_atlas_core.entities.atlas.processes.ApiOperationProcess import (ApiOperationProcess as CoreApiOperationProcess,
                                                                         ApiOperationProcessAttributes as CoreApiOperationProcessAttributes)
from typing import List, Optional

from ..generic_process.generic_process_model import GenericProcessBase, GenericProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiOperationProcessBase(DataClassJsonMixin):
    name: str
    qualified_name: str
    microservice: str


# END ApiOperationProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiOperationProcessDefaultsBase(GenericProcessDefaultsBase):
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    process_owner: Optional[str] = None
    description: Optional[str] = None


# END ApiOperationProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiOperationProcess(
    ApiOperationProcessDefaultsBase,
    ApiOperationProcessBase
):
    def convert_to_atlas(self) -> CoreApiOperationProcess:
        """
        Returns a corresponding Atlas `ApiOperationProcess` instance.
        """
        inputs: List[ObjectId] = []
        for input in self.inputs:
            input_unique_attributes = M4IAttributes(
                qualified_name=input
            )
            inputs.append(ObjectId(
                type_name="m4i_dataset",
                unique_attributes=input_unique_attributes
            ))
        # END FOR

        outputs: List[ObjectId] = []
        for output in self.outputs:
            output_unique_attributes = M4IAttributes(
                qualified_name=output
            )
            outputs.append(ObjectId(
                type_name="m4i_dataset",
                unique_attributes=output_unique_attributes
            ))
        # END FOR

        attributes = CoreApiOperationProcessAttributes(
            description=self.description,
            name=self.name,
            inputs=inputs,
            outputs=outputs,
            qualified_name=self.qualified_name,

        )

        if bool(self.process_owner):
            process_owner: List[ObjectId] = []
            process_owner_unique_attributes = M4IAttributes(
                qualified_name=self.process_owner
            )
            process_owner.append(ObjectId(
                type_name="m4i_person",
                unique_attributes=process_owner_unique_attributes
            ))
            attributes.process_owner = process_owner
        # END IF

        if bool(self.microservice):
            microservice: List[ObjectId] = []
            microservice_unique_attributes = M4IAttributes(
                qualified_name=self.microservice
            )
            microservice.append(ObjectId(
                type_name="m4i_microservice_process",
                unique_attributes=microservice_unique_attributes
            ))
            attributes.microservice = microservice
        # END IF

        entity = CoreApiOperationProcess(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END ApiOperationProcess
