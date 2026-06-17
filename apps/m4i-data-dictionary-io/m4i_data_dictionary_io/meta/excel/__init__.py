from .collections import collections_parser_config
from .data_attributes import data_attributes_parser_config
from .data_domains import data_domains_parser_config
from .data_entities import data_entities_parser_config
from .data_fields import data_fields_parser_config
from .data_qualities import data_qualities_parser_config
from .datasets import datasets_parser_config
from .ExcelParserConfig import ExcelParserConfig as ExcelParserConfig
from .persons import persons_parser_config
from .systems import systems_parser_config
from .source import get_file_details as get_file_details, get_source as get_source
from .processes import process_parser_config

excel_parser_configs = (
    persons_parser_config,
    systems_parser_config,
    collections_parser_config,
    datasets_parser_config,
    data_domains_parser_config,
    data_entities_parser_config,
    data_attributes_parser_config,
    data_fields_parser_config,
    data_qualities_parser_config,
    process_parser_config,
)
