from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json


class Condition(Enum):
    AND = "AND"
    OR = "OR"
# END Condition


class Operator(Enum):
    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"
    EQ = "="
    NEQ = "NEQ"
    IN = "IN"
    LIKE = "LIKE"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    CONTAINS_ANY = "CONTAINS_ANY"
    CONTAINS_ALL = "CONTAINS_ALL"
    IS_NULL = "IS_NULL"
    NOT_NULL = "NOT_NULL"
# END Operator


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FilterCriteriaBase(DataClassJsonMixin):

    attribute_name: str
    attribute_value: str

# END FilterCriteriaBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FilterCriteriaDefaultsBase(DataClassJsonMixin):

    condition: Optional[Condition] = None
    criterion: List['FilterCriteria'] = field(default_factory=list)
    operator: Optional[Operator] = None

# END FilterCriteriaDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FilterCriteria(FilterCriteriaDefaultsBase, FilterCriteriaBase):

    pass

# END FilterCriteria
