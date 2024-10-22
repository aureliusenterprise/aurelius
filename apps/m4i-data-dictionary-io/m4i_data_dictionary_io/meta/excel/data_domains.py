from pandas import DataFrame

from ...entities import DataDomain
from .ExcelParserConfig import ExcelParserConfig
from ..excel import get_file_details

data_domains_column_mapping = {
    "Domain name": "name",
    "Domain Qualified Name": "qualifiedName",
    "Definition": "definition",
    "Data Domain Lead": "domainLead"
}

data_domains_sheet_name = "1. L1 Data Domains"
data_domains_parser_class = DataDomain


def domain_transform(data: DataFrame):
    data["source"] = get_file_details()['qualifiedName']
    return data


# END domain_transform

data_domains_parser_config = ExcelParserConfig(
    column_mapping=data_domains_column_mapping,
    parser_class=data_domains_parser_class,
    sheet_name=data_domains_sheet_name,
    transform=domain_transform
)
