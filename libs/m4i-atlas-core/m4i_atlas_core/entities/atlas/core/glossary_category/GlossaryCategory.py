from dataclasses import dataclass, field
from typing import List

from dataclasses_json import LetterCase, dataclass_json

from ..glossary_base_object import (GlossaryBaseObjectBase,
                                    GlossaryBaseObjectDefaultsBase)
from ..glossary_header import GlossaryHeader
from ..related_category_header import RelatedCategoryHeader
from ..related_term_header import RelatedTermHeader


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GlossaryCategoryBase(GlossaryBaseObjectBase):

    anchor: GlossaryHeader

# END GlossaryCategoryBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GlossaryCategoryDefaultsBase(GlossaryBaseObjectDefaultsBase):

    children_categories: List[RelatedCategoryHeader] = field(
        default_factory=list
    )
    parent_category: RelatedCategoryHeader = None
    terms: List[RelatedTermHeader] = field(default_factory=list)

# END GlossaryCategoryDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GlossaryCategory(GlossaryCategoryDefaultsBase, GlossaryCategoryBase):

    pass

# END GlossaryCategory
