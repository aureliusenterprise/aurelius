from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..number_format import NumberFormat
from ..time_zone import TimeZone


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DateFormat(DataClassJsonMixin):

    available_locales: List[str] = field(default_factory=list)
    calendar: Optional[int] = None
    date_instance: Optional['DateFormat'] = None
    date_time_instance: Optional['DateFormat'] = None
    instance: Optional['DateFormat'] = None
    lenient: Optional[bool] = None
    number_format: Optional[NumberFormat] = None
    time_instance: Optional['DateFormat'] = None
    time_zone: Optional[TimeZone] = None

# END DateFormat
