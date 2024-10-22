from typing import Iterable

from m4i_atlas_core import ConfigStore
from pandas import DataFrame, read_excel

from ..meta import ExcelParserConfig

store = ConfigStore.get_instance()


def read_data_from_dictionary(config: ExcelParserConfig) -> Iterable[dict]:

    data_path = store.get("data.dictionary.path")

    sheet: DataFrame = read_excel(
        data_path,
        sheet_name=config.sheet_name,
        usecols=config.column_mapping,
        keep_default_na=False,
    )

    data: DataFrame = (
        sheet
        .pipe(DataFrame.rename, columns=config.column_mapping)
        .pipe(config.transform)
    )

    return data.to_dict(orient="records")
# END read_data_from_dictionary
