from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class EnumElementDef(DataClassJsonMixin):
    description: Optional[str] = None
    ordinal: Optional[int] = None
    value: Optional[str] = None


# END EnumElementDef
