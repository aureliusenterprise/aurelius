from dataclasses import dataclass, field

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..attributes import Attributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class StructBase(DataClassJsonMixin):
    pass
# END StructBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class StructDefaultsBase(DataClassJsonMixin):
    type_name: str = field(default="m4i_struct")
    attributes: Attributes = field(default_factory=Attributes)
# END StructDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Struct(StructDefaultsBase, StructBase):
    pass
# END Struct
