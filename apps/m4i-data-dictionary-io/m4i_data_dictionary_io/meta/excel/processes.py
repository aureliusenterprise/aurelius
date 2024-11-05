from pandas import DataFrame

from ...entities import Process
from .ExcelParserConfig import ExcelParserConfig
from . import get_file_details

processes_column_mapping = {
    "Input 1": "input_1",
    "Input 2": "input_2",
    "Input 3": "input_3",
    "Input 4": "input_4",
    "Output 1": "output_1",
    "Output 2": "output_2",
    "Output 3": "output_3",
    "Output 4": "output_4",
    "Process Name": "name",
    "Process Qualified Name": "qualifiedName",
    "System Intermediate Qualified Name": "system",
    "Process Owner": "processOwner"
}

processes_sheet_name = "12. Process"
processes_parser_class = Process


def process_transform(data: DataFrame):
    data["source"] = get_file_details()['qualifiedName']
    return data


process_parser_config = ExcelParserConfig(
    column_mapping=processes_column_mapping,
    parser_class=processes_parser_class,
    sheet_name=processes_sheet_name,
    transform=process_transform
)
