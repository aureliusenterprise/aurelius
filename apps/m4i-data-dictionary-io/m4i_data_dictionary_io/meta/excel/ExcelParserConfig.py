from dataclasses import dataclass
from typing import Callable, Dict, Type

from pandas import DataFrame

from ...entities import ToAtlasConvertible


@dataclass
class ExcelParserConfig:
    column_mapping: Dict[str, str]
    parser_class: Type[ToAtlasConvertible]
    sheet_name: str
    transform: Callable[[DataFrame], DataFrame] = lambda data: data
# END ExcelParserConfig
