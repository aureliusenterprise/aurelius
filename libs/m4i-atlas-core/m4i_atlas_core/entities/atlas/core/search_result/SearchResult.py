from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..attribute_search_result import AttributeSearchResult
from ..entity_header import EntityHeader
from ..full_text_result import FullTextResult
from ..search_parameters import SearchParameters


class QueryType(Enum):
    DSL = "DSL"
    FULL_TEXT = "FULL_TEXT"
    GREMLIN = "GREMLIN"
    BASIC = "BASIC"
    ATTRIBUTE = "ATTRIBUTE"
    RELATIONSHIP = "RELATIONSHIP"


# END QueryType


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SearchResultBase(DataClassJsonMixin):

    approximate_count: int
    query_type: QueryType


# END SearchResultBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SearchResultDefaultsBase(DataClassJsonMixin):

    attributes: Optional[AttributeSearchResult] = None
    classification: Optional[str] = None
    entities: List[EntityHeader] = field(default_factory=list)
    full_text_result: List[FullTextResult] = field(default_factory=list)
    query_text: Optional[str] = None
    referred_entities: Dict[str, EntityHeader] = field(default_factory=dict)
    search_parameters: SearchParameters = None
    type: Optional[str] = None


# END SearchResultDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SearchResult(SearchResultDefaultsBase, SearchResultBase):

    pass

# END SearchResult
