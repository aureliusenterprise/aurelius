from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..base_model_object import BaseModelObject
from ..classification import Classification


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GlossaryBaseObjectBase(BaseModelObject):

    name: str
    qualified_name: str

# END GlossaryBaseObjectBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GlossaryBaseObjectDefaultsBase(DataClassJsonMixin):

    additional_attributes: Dict[str, Any] = field(default_factory=dict)
    classifications: List[Classification] = field(default_factory=list)
    long_description: Optional[str] = None
    short_description: Optional[str] = None

# END GlossaryBaseObjectDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GlossaryBaseObject(GlossaryBaseObjectDefaultsBase, GlossaryBaseObjectBase):

    pass

# END GlossaryBaseObject
