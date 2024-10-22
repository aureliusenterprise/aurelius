from pandas import DataFrame

from ...entities import Person
from .ExcelParserConfig import ExcelParserConfig
from ..excel import get_file_details

persons_column_mapping = {
    "Person Name": "name",
    "Email address": "email"
}

persons_sheet_name = "9. Person Table"
persons_parser_class = Person


def persons_transform(data: DataFrame):
    data["qualifiedName"] = data["email"]
    data["source"] = get_file_details()['qualifiedName']
    return data
# END persons_transform


persons_parser_config = ExcelParserConfig(
    column_mapping=persons_column_mapping,
    parser_class=persons_parser_class,
    sheet_name=persons_sheet_name,
    transform=persons_transform
)
