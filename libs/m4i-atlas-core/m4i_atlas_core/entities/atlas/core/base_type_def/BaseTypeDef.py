from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from dataclasses_json import DataClassJsonMixin, LetterCase, dataclass_json

from ..date_format import DateFormat
from ..utils import create_placehoder_guid


class TypeCategory(Enum):
    PRIMITIVE = "PRIMITIVE"
    OBJECT_ID_TYPE = "OBJECT_ID_TYPE"
    ENUM = "ENUM"
    STRUCT = "STRUCT"
    CLASSIFICATION = "CLASSIFICATION"
    ENTITY = "ENTITY"
    ARRAY = "ARRAY"
    MAP = "MAP"
    RELATIONSHIP = "RELATIONSHIP"
    BUSINESS_METADATA = "BUSINESS_METADATA"
# END TypeCategory


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BaseTypeDefBase(DataClassJsonMixin):

    category: TypeCategory
    name: str

# END BaseTypeDefBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BaseTypeDefDefaultsBase(DataClassJsonMixin):

    create_time: Optional[int] = None
    created_by: Optional[str] = None
    date_formatter: Optional[DateFormat] = None
    description: Optional[str] = None
    guid: str = field(default_factory=create_placehoder_guid)
    options: Dict[str, str] = field(default_factory=dict)
    service_type: Optional[str] = None
    type_version: Optional[str] = None
    update_type: Optional[int] = None
    updated_by: Optional[str] = None
    version: Optional[int] = None

# END BaseTypeDefDefaultsBase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BaseTypeDef(BaseTypeDefDefaultsBase, BaseTypeDefBase):

    pass

# END BaseTypeDef
