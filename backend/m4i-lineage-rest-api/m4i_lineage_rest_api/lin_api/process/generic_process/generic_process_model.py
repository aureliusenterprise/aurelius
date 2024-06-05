from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, M4IAttributes
from m4i_atlas_core.entities.atlas.processes import (GenericProcess as CoreGenericProcess,
                                                     GenericProcessAttributes as CoreGenericProcessAttributes)
from typing import Optional, List


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenericProcessBase(DataClassJsonMixin):
    name: str
    qualified_name: str
    inputs: List[str]
    outputs: List[str]
    # END _qualified_name


# END GenericProcessBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenericProcessDefaultsBase(DataClassJsonMixin):
    description: Optional[str] = None
    process_owner: Optional[str] = None
    source: Optional[str] = None


# END GenericProcessDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenericProcess(
    GenericProcessDefaultsBase,
    GenericProcessBase
):
    def convert_to_atlas(self) -> CoreGenericProcess:
        """
        Returns a corresponding Atlas `GenericProcess` instance.
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

        attributes = CoreGenericProcessAttributes(
            description=self.description,
            name=self.name,
            inputs=inputs,
            outputs=outputs,
            qualified_name=self.qualified_name
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
        # END IF

        entity = CoreGenericProcess(
            attributes=attributes
        )

        return entity
    # END convert_to_atlas
# END GenericProcess
