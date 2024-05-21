from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelatedCategoryHeaderBase(DataClassJsonMixin):

    category_guid: str

# END RelatedCategoryHeaderBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelatedCategoryHeaderDefaultsBase(DataClassJsonMixin):

    description: Optional[str] = None
    display_text: Optional[str] = None
    parent_category_guid: Optional[str] = None
    relation_guid: Optional[str] = None

# END RelatedCategoryHeaderDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelatedCategoryHeader(RelatedCategoryHeaderDefaultsBase, RelatedCategoryHeaderBase):

    pass

# END RelatedCategoryHeader
