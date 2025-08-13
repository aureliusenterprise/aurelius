import json
import logging
from typing import Generator, Union

from m4i_data_dictionary_io.entities.json import DataField

from .atlas import build_field

# Inverted index of data types to standardized names
DATA_TYPE_MAPPING = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "dict": "object",
    "list": "array",
    "bytes": "binary",
    "NoneType": "null",
}


def _parse_payload(
    payload: dict,
    dataset_qualified_name: str,
    parent_field: Union[str, None] = None,
) -> Generator[DataField, None, None]:
    """Parse a JSON payload and yield DataField instances."""
    for key, value in payload.items():
        print(f"Parsing field: {key} with value: {value} ", isinstance(value, dict), " ",  type(value).__name__)
        type_name = (
            value.get("type", "object")
            if isinstance(value, dict)
            else type(value).__name__
        )

        field = build_field(
            name=key,
            dataset_qualified_name=dataset_qualified_name,
            type_name=DATA_TYPE_MAPPING.get(type_name, type_name),
            parent_field=parent_field,
        )

        yield field

        if isinstance(value, dict):
            # Recursively parse nested objects
            print(f"Recursively parsing nested object for field: {key}")
            yield from _parse_payload(
                payload=value,
                dataset_qualified_name=dataset_qualified_name,
                parent_field=field.qualified_name,
            )


def parse_payload(
    payload: str,
    dataset_qualified_name: str,
) -> Generator[DataField, None, None]:
    """Attempt to parse the given payload as JSON and yield DataField instances."""
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        logging.error("Invalid JSON payload")
        return

    if not isinstance(data, dict):
        logging.error("JSON payload is not a dictionary")
        return

    yield from _parse_payload(
        payload=data,
        dataset_qualified_name=dataset_qualified_name,
    )
