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

def unpack_dataset_qualified_name(name):
    """ Unpacks the dataset name into its components and reconstructs the qualified name. """
    parts = name.split('--')
    system = parts[0]
    collection = parts[1]
    return '--'.join([system, collection, name])


def process_transform(data: DataFrame):
    data["inputs"] = data[["input_1", "input_2", "input_3", "input_4"]].apply(
        lambda row: [unpack_dataset_qualified_name(val) for val in row if val != ""], axis=1
    )
    data["outputs"] = data[["output_1", "output_2", "output_3", "output_4"]].apply(
        lambda row: [unpack_dataset_qualified_name(val) for val in row if val != ""], axis=1
    )
    data = data.drop(columns=[
        "input_1", "input_2", "input_3", "input_4",
        "output_1", "output_2", "output_3", "output_4"
    ])
    data["source"] = get_file_details()["qualifiedName"]
    return data


process_parser_config = ExcelParserConfig(
    column_mapping=processes_column_mapping,
    parser_class=processes_parser_class,
    sheet_name=processes_sheet_name,
    transform=process_transform
)
