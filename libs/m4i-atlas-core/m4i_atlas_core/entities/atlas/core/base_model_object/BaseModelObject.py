from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BaseModelObject(DataClassJsonMixin):

    guid: str

# END BaseModelObject
