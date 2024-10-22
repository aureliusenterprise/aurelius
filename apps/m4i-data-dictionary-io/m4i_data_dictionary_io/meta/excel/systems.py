from pandas import DataFrame

from ...entities import System
from .ExcelParserConfig import ExcelParserConfig
from ..excel import get_file_details

systems_column_mapping = {
    "System Name": "name",
    "Intermediate Qualified System Name": "qualifiedName"
}

systems_sheet_name = "4. L4 Fields"
systems_parser_class = System


def systems_transform(data: DataFrame):
    data["source"] = get_file_details()['qualifiedName']
    return data.drop_duplicates()

# END systems_transform


systems_parser_config = ExcelParserConfig(
    column_mapping=systems_column_mapping,
    parser_class=systems_parser_class,
    sheet_name=systems_sheet_name,
    transform=systems_transform
)
