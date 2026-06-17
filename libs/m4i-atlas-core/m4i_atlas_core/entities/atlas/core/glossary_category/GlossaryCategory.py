from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..glossary_base_object import GlossaryBaseObjectBase, GlossaryBaseObjectDefaultsBase
from ..glossary_header import GlossaryHeader
from ..related_category_header import RelatedCategoryHeader
from ..related_term_header import RelatedTermHeader


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class GlossaryCategoryBase(GlossaryBaseObjectBase):
    anchor: GlossaryHeader


# END GlossaryCategoryBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class GlossaryCategoryDefaultsBase(GlossaryBaseObjectDefaultsBase):
    children_categories: List[RelatedCategoryHeader] = field(default_factory=list)
    parent_category: Optional[RelatedCategoryHeader] = None
    terms: List[RelatedTermHeader] = field(default_factory=list)


# END GlossaryCategoryDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)  # type: ignore[argument-type]
@dataclass
class GlossaryCategory(GlossaryCategoryDefaultsBase, GlossaryCategoryBase):
    pass


# END GlossaryCategory
