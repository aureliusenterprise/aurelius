from ...entities import DataQuality
from .ExcelParserConfig import ExcelParserConfig
from pandas import DataFrame
from ..excel import get_file_details

data_qualities_column_mapping = {
    "ID": "id",
    "Business Rule Description": "businessRuleDescription",
    "Data Quality Rule Description": "ruleDescription",
    "Data Quality Dimension": "qualityDimension",
    "Filter Required": "filterRequired",
    "Expression": "expression",
    "Active": "active",
    "Expression_version": "expressionVersion",
    "Field Qualified Name": "dataField"
}

data_qualities_sheet_name = "6. Data Quality Rulebook"
data_qualities_parser_class = DataQuality


def qualities_transform(data: DataFrame):
    data["qualifiedName"] = data["dataField"] + \
                            "--" + data["id"].astype(str)
    data["id"] = data["id"].astype(str)
    data["source"] = get_file_details()['qualifiedName']
    return data.drop_duplicates()


# END qualities_transform

data_qualities_parser_config = ExcelParserConfig(
    column_mapping=data_qualities_column_mapping,
    parser_class=data_qualities_parser_class,
    sheet_name=data_qualities_sheet_name,
    transform=qualities_transform
)
