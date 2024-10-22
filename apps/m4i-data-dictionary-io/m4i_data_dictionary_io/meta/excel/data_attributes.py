from pandas import DataFrame

from ...entities import DataAttribute
from .ExcelParserConfig import ExcelParserConfig
from ..excel import get_file_details

data_attributes_column_mapping = {
    "Attribute Name": "name",
    "Attribute Qualified Name": "qualifiedName",
    "Definition": "definition",
    "Unique entity qualified name": "dataEntity",
    "Data Type": "attributeType",
    "Risk Classification": "risk_classification",
    "Has PII": "has_pii",
    "Is Key Data": "is_key_data",
    "Business Data Owner": "businessOwner",
    "Business Data Steward": "steward"
}

data_attributes_sheet_name = "3. L3 Data Attributes"
data_attributes_parser_class = DataAttribute


def data_attribute_transform(data: DataFrame):
    data["source"] = get_file_details()['qualifiedName']
    return data


# END data_attribute_transform

data_attributes_parser_config = ExcelParserConfig(
    column_mapping=data_attributes_column_mapping,
    parser_class=data_attributes_parser_class,
    sheet_name=data_attributes_sheet_name,
    transform=data_attribute_transform
)
