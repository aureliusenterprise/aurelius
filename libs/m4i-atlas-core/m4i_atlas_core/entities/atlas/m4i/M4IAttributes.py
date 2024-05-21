from dataclasses import dataclass

from dataclasses_json import (DataClassJsonMixin, LetterCase, Undefined,
                              dataclass_json)
from ..core import Attributes as AtlasAttributes


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class M4IAttributesBase(DataClassJsonMixin):
    qualified_name: str

# END AttributesBase


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.INCLUDE)
@dataclass
class M4IAttributes(AtlasAttributes, M4IAttributesBase):
    pass

# END Attributes
