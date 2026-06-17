from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class GlossaryHeaderBase(DataClassJsonMixin):
    glossary_guid: str


# END GlossaryHeaderBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class GlossaryHeaderDefaultsBase(DataClassJsonMixin):
    display_text: Optional[str] = None
    relation_guid: Optional[str] = None


# END GlossaryHeaderDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class GlossaryHeader(GlossaryHeaderDefaultsBase, GlossaryHeaderBase):
    pass


# END GlossaryHeader
