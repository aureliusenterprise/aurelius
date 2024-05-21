from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import LetterCase, dataclass_json

from ..utils import create_placehoder_guid
from ..status import Status
from ..struct import Struct, StructBase, StructDefaultsBase
from ..time_boundary import TimeBoundary


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ClassificationBase(StructBase):

    pass

# END ClassificationBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ClassificationDefaultsBase(StructDefaultsBase):

    entity_status: Status = Status.ACTIVE
    propagate: bool = True
    remove_propagations_on_entity_delete: bool = True
    validity_periods: List[TimeBoundary] = field(default_factory=list)
    entity_guids: Optional[str] = None  # Used to request the classification
    entity_guid: Optional[str] = None  # Used to get the response of the classification

# END ClassificationDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Classification(Struct, ClassificationDefaultsBase, ClassificationBase):

    pass

# END Classification
