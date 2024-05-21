from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json


class RoundingMode(Enum):
    UP = "UP"
    DOWN = "DOWN"
    CEILING = "CEILING"
    FLOOR = "FLOOR"
    HALF_UP = "HALF_UP"
    HALF_DOWN = "HALF_DOWN"
    HALF_EVEN = "HALF_EVEN"
    UNNECESSARY = "UNNECESSARY"
# END RoundingMode


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class NumberFormat(DataClassJsonMixin):

    available_locales: List[str] = field(default_factory=list)
    currency: Optional[str] = None
    currency_instance: Optional['NumberFormat'] = None
    grouping_used: bool = False
    instance: Optional['NumberFormat'] = None
    integer_instance: Optional['NumberFormat'] = None
    maximum_fraction_digits: Optional[int] = None
    maximum_integer_digits: Optional[int] = None
    minimum_fraction_digits: Optional[int] = None
    minimum_integer_digits: Optional[int] = None
    number_instance: Optional['NumberFormat'] = None
    parse_integer_only: bool = False
    percent_instance: Optional['NumberFormat'] = None
    rounding_mode: RoundingMode = RoundingMode.UNNECESSARY

# END NumberFormat
