from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TimeBoundary(DataClassJsonMixin):

    end_time: str
    start_time: str
    time_zone: str

# END TimeBoundary
