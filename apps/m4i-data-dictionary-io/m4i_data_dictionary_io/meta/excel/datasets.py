from pandas import DataFrame

from ...entities import Dataset
from .ExcelParserConfig import ExcelParserConfig
from ..excel import get_file_details

datasets_column_mapping = {
    "Dataset Name": "name",
    "Intermediate Physical Qualified Name": "simpleDataset",
    "Intermediate Qualified System Name": "simpleSystem",
    "Collection Intermediate Qualified Name": "simpleCollection",
}

datasets_sheet_name = "4. L4 Fields"
datasets_parser_class = Dataset


def datasets_transform(data: DataFrame):
    data["collection"] = data["simpleSystem"] + "--" + data["simpleCollection"]
    data["qualifiedName"] = data["simpleDataset"]
    data = data.drop(columns=["simpleSystem", "simpleCollection", "simpleDataset"])
    data["source"] = get_file_details()['qualifiedName']
    return data.drop_duplicates()
# END datasets_transform


datasets_parser_config = ExcelParserConfig(
    column_mapping=datasets_column_mapping,
    parser_class=datasets_parser_class,
    sheet_name=datasets_sheet_name,
    transform=datasets_transform
)
