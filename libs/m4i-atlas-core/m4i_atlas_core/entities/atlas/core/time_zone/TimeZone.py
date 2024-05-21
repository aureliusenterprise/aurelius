from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json, config


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TimeZone(DataClassJsonMixin):

    dst_savings: Optional[int] = field(
        metadata=config(field_name="DSTSavings")
    )
    id: Optional[str] = field(
        metadata=config(field_name="ID")
    )
    available_ids: List[str] = field(
        default_factory=list,
        metadata=config(field_name="availableIDs")
    )
    default: Optional['TimeZone'] = None
    display_name: Optional[str] = None
    raw_offset: Optional[int] = None

# END TimeZone
