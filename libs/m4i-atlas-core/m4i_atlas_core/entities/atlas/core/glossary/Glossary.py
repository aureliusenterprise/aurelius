from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..glossary_base_object import GlossaryBaseObjectBase, GlossaryBaseObjectDefaultsBase
from ..related_category_header import RelatedCategoryHeader
from ..related_term_header import RelatedTermHeader


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class GlossaryBase(GlossaryBaseObjectBase):
    pass


# END GlossaryBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class GlossaryDefaultsBase(GlossaryBaseObjectDefaultsBase):
    categories: List[RelatedCategoryHeader] = field(default_factory=list)
    language: Optional[str] = None
    terms: List[RelatedTermHeader] = field(default_factory=list)
    usage: Optional[str] = None


# END GlossaryDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class Glossary(GlossaryDefaultsBase, GlossaryBase):
    pass


# END Glossary
