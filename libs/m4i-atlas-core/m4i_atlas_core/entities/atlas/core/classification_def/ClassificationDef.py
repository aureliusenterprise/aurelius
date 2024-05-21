from dataclasses import dataclass, field
from typing import List

from dataclasses_json import LetterCase, dataclass_json

from ..struct_def import StructDef


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ClassificationDef(StructDef):

    entity_types: List[str] = field(default_factory=list)
    sub_types: List[str] = field(default_factory=list)
    super_types: List[str] = field(default_factory=list)

# END ClassificationDef
