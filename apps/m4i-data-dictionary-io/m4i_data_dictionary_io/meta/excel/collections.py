from pandas import DataFrame

from ...entities import Collection
from .ExcelParserConfig import ExcelParserConfig
from ..excel.source import get_file_details

collections_column_mapping = {
    "Collection Name": "name",
    "Intermediate Qualified System Name": "system",
    "Collection Intermediate Qualified Name": "simpleCollection",
}

collections_sheet_name = "4. L4 Fields"
collections_parser_class = Collection


def collections_transform(data: DataFrame):
    data["qualifiedName"] = data["system"] + \
        "--" + data["simpleCollection"]
    data = data.drop(columns=["simpleCollection"])
    data["source"] = get_file_details()['qualifiedName']
    return data.drop_duplicates()
# END collections_transform


collections_parser_config = ExcelParserConfig(
    column_mapping=collections_column_mapping,
    parser_class=collections_parser_class,
    sheet_name=collections_sheet_name,
    transform=collections_transform
)
