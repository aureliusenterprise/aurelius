from dataclasses import dataclass, field
from typing import List

from dataclasses_json import LetterCase, dataclass_json

from ..attribute_def import AttributeDef
from ..base_type_def import BaseTypeDef


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class StructDef(BaseTypeDef):

    attribute_defs: List[AttributeDef] = field(default_factory=list)

# END StructDef
