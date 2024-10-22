from pandas import DataFrame

from ...entities import DataEntity
from .ExcelParserConfig import ExcelParserConfig
from ..excel import get_file_details

data_entities_column_mapping = {
    "Entity name": "name",
    "Entity Qualified Name": "qualifiedName",
    "Definition": "definition",
    "Unique Domain Qualified Name": "dataDomain",
    "Parent entity Qualified name": "parentEntity",
    "Business Data Owner": "businessOwner",
    "Business Data Steward": "steward",
    "Direct Relation to Domain": "domainLink"
}

data_entities_sheet_name = "2. L2 Data Entities"
data_entities_parser_class = DataEntity


def data_entity_transform(data: DataFrame):
    data["source"] = get_file_details()['qualifiedName']
    return data


data_entities_parser_config = ExcelParserConfig(
    column_mapping=data_entities_column_mapping,
    parser_class=data_entities_parser_class,
    sheet_name=data_entities_sheet_name,
    transform=data_entity_transform
)
