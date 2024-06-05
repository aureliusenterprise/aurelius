from dataclasses import dataclass, field
from dataclasses_json import LetterCase, dataclass_json, DataClassJsonMixin
from m4i_atlas_core import ObjectId, M4IAttributes
from m4i_atlas_core.entities.atlas.processes.MicroserviceProcess import (MicroserviceProcess as CoreMicroserviceProcess,
                                                                         MicroserviceProcessAttributes as CoreMicroserviceProcessAttributes)
from typing import List


from ..generic_process.generic_process_model import GenericProcessBase, GenericProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MicroserviceProcessBase(DataClassJsonMixin):
    name: str
    qualified_name: str
    system: str


# END MicroserviceProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MicroserviceProcessDefaultsBase(GenericProcessDefaultsBase):
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


# END MicroserviceProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MicroserviceProcess(
    MicroserviceProcessDefaultsBase,
    MicroserviceProcessBase
):
    def convert_to_atlas(self) -> CoreMicroserviceProcess:
        """
        Returns a corresponding Atlas `MicroserviceProcess` instance.
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

        attributes = CoreMicroserviceProcessAttributes(
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

        if bool(self.source):
            source: List[ObjectId] = []
            for so in self.source:
                source_unique_attributes = M4IAttributes(
                    qualified_name=so
                )
                source.append(ObjectId(
                    type_name="m4i_source",
                    unique_attributes=source_unique_attributes
                ))
            # END FOR
            attributes.source = source
        # END

        if bool(self.system):
            system: List[ObjectId] = []
            system_unique_attributes = M4IAttributes(
                qualified_name=self.system
            )
            system.append(ObjectId(
                type_name="m4i_kubernetes_pod",
                unique_attributes=system_unique_attributes
            ))
            attributes.system = system
        # END IF

        entity = CoreMicroserviceProcess(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END MicroserviceProcess
