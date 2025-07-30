from typing import Generator, Union

from avro.schema import RecordSchema
from confluent_kafka.avro import loads

from m4i_data_dictionary_io.entities.json import (
    DataField,
)

from .atlas import build_field


def _parse_avro_schema(
    schema: RecordSchema,
    dataset_qualified_name: str,
    parent_field: Union[str, None] = None,
) -> Generator[DataField, None, None]:
    """Parse an Avro schema and yield DataField instances."""
    for field in schema.fields:
        type_name = (
            " | ".join(schema.name for schema in field.type.schemas)
            if field.type.type == "union"
            else field.type.name
        )

        result = build_field(
            name=field.name,
            dataset_qualified_name=dataset_qualified_name,
            definition=field.doc,
            parent_field=parent_field,
            type_name=type_name,
        )

        yield result

        if field.type.type == "record":
            # Recursively parse nested records
            yield from _parse_avro_schema(
                schema=field.type,
                dataset_qualified_name=dataset_qualified_name,
                parent_field=result.qualified_name,
            )
        elif field.type.type == "array":
            # If the field is an array, parse its items
            items = field.type.items
            if items.type == "record":
                yield from _parse_avro_schema(
                    schema=items,
                    dataset_qualified_name=dataset_qualified_name,
                    parent_field=result.qualified_name,
                )
            else:
                # For non-record items, just yield the field
                yield build_field(
                    name=f"{field.name}_item",
                    dataset_qualified_name=dataset_qualified_name,
                    type_name=items.name,
                    parent_field=result.qualified_name,
                )


def parse_avro_schema(
    schema: str,
    dataset_qualified_name: str,
) -> Generator[DataField, None, None]:
    """Parse an Avro schema and yield DataField instances."""
    yield from _parse_avro_schema(
        schema=loads(schema),
        dataset_qualified_name=dataset_qualified_name,
    )
