from dict_hash import sha256
from pandas import Series


def calculate_hash_for_row(row: Series) -> str:

    cleaned = row.dropna().apply(str)

    row_dict = cleaned.to_dict()

    row_hash = sha256(row_dict)

    return str(row_hash)
# END calculate_hash_for_row
