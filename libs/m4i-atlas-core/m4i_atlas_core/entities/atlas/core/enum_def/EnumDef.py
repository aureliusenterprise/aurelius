from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..base_type_def import BaseTypeDef
from ..enum_element_def import EnumElementDef

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EnumDef(BaseTypeDef):

    default_value: Optional[str] = None
    element_defs: List[EnumElementDef] = field(default_factory=list)

# END EnumDef
