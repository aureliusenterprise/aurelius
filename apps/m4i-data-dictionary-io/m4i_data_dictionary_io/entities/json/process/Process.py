from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json
from m4i_atlas_core import ObjectId, GenericProcess, GenericProcessAttributes

from m4i_atlas_core import M4IAttributes
from ..base_object import BaseObject
from ..ToAtlasConvertible import ToAtlasConvertible
from ..utils import get_qualified_name

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ProcessBase(BaseObject):

    name: str

    def _qualified_name(self):
      """
      Returns the qualified name of the domain based on its `name`
      """

      return get_qualified_name(self.name)
    # END _qualified_name
# END DatasetBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ProcessDefaultsBase(DataClassJsonMixin):
    definition: Optional[str] = None
    source: Optional[str] = None
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    system: Optional[str] = None
    process_owner: Optional[str] = None

# END DatasetDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Process(
    ProcessDefaultsBase,
    ProcessBase,
    ToAtlasConvertible[GenericProcess]
):
    def convert_to_atlas(self) -> GenericProcess:
        """
        Returns a corresponding Atlas `GenericProcess` instance.
        """

        attributes = GenericProcessAttributes(
          description=self.definition,
          name=self.name,
          qualified_name=self.qualified_name
        )

        if bool(self.process_owner):
          attributes.process_owner = [
            ObjectId(
              type_name="m4i_person",
              unique_attributes=M4IAttributes(qualified_name=self.process_owner)
            )
          ]
        # END IF

        if bool(self.system):
          attributes.system = [
            ObjectId(
              type_name="m4i_system",
              unique_attributes=M4IAttributes(qualified_name=self.system)
            )
          ]
        # END IF

        if bool(self.inputs):
          attributes.inputs = [
            ObjectId(
              type_name="m4i_dataset",
              unique_attributes=M4IAttributes(qualified_name=input_name)
            )
            for input_name in self.inputs if input_name
          ]
        # END IF

        if bool(self.outputs):
          attributes.outputs = [
            ObjectId(
              type_name="m4i_dataset",
              unique_attributes=M4IAttributes(qualified_name=output_name)
            )
            for output_name in self.outputs if output_name
          ]
        # END IF

        entity = GenericProcess(attributes=attributes)

        return entity
    # END convert_to_atlas
# END Dataset
