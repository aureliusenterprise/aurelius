from pandas import DataFrame

from ...entities import DataField
from .ExcelParserConfig import ExcelParserConfig
from ..excel import get_file_details

data_fields_column_mapping = {
    "Field Name": "name",
    "Field Qualified Name": "qualifiedName",
    "Attribute Qualified Name": "attribute",
    "Intermediate Physical Qualified Name": "simpleDataset",
    "Intermediate Qualified System Name": "simpleSystem",
    "Collection Intermediate Qualified Name": "simpleCollection",
    "Field Type": "fieldType"
}

data_fields_sheet_name = "4. L4 Fields"
data_fields_parser_class = DataField


def data_fields_transform(data: DataFrame):
    data["dataset"] = data["simpleSystem"] + "--" + data["simpleCollection"] + "--" + data["simpleDataset"]
    data = data.drop(
        columns=["simpleSystem", "simpleCollection", "simpleDataset"]
    )
    data["source"] = get_file_details()['qualifiedName']
    return data.drop_duplicates()
# END data_fields_transform


data_fields_parser_config = ExcelParserConfig(
    column_mapping=data_fields_column_mapping,
    parser_class=data_fields_parser_class,
    sheet_name=data_fields_sheet_name,
    transform=data_fields_transform
)
