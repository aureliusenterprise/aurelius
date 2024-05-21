from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..filter_criteria import FilterCriteria


class SortBy(Enum):
    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"
# END SortBy


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SearchParameters(DataClassJsonMixin):

    attributes: List[str] = field(default_factory=list)
    classification: Optional[str] = None
    entity_filters: Optional[FilterCriteria] = None
    exclude_deleted_entities: Optional[bool] = None
    include_classification_attributes: Optional[bool] = None
    include_sub_classifications: Optional[bool] = None
    include_sub_types: Optional[bool] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    query: Optional[str] = None
    sort_by: Optional[SortBy] = None
    tag_filters: Optional[FilterCriteria] = None
    term_name: Optional[str] = None
    type_name: Optional[str] = None

# END SearchParameters
