from dataclasses import dataclass, field
from typing import Any, List

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AttributeSearchResult(DataClassJsonMixin):

    name: List[str] = field(default_factory=list)
    values: List[Any] = field(default_factory=list)

# END AttributeSearchResult
