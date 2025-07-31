import json
from typing import Generator, Union

from m4i_data_dictionary_io.entities.json import DataField

from .atlas import build_field


def _get_json_schema_definition(ref: str, defs: dict) -> Union[dict, None]:
    """Retrieve a JSON schema definition by reference."""
    return defs.get(ref.replace("#/$defs/", ""))


def _find_json_schema_references(
    schema: dict,
    defs: dict,
) -> Generator[dict, None, None]:
    """Find all JSON schema references in the given schema."""

    if "$ref" in schema:
        if definition := _get_json_schema_definition(schema["$ref"], defs):
            yield definition

    dependencies = [
        *schema.get("anyOf", []),
        *schema.get("allOf", []),
        *schema.get("oneOf", []),
    ]

    if items := schema.get("items"):
        dependencies.append(items)

    for dep in dependencies:
        if ref := dep.get("$ref"):
            if definition := _get_json_schema_definition(ref, defs):
                yield definition


def _parse_constraint(schema: dict) -> str:
    """Parse a constraint from a JSON schema."""
    return " & ".join(f"{key}({value})" for key, value in schema.items())


def _parse_json_schema_type(schema: dict, defs: dict) -> str:
    """Parse the type from a JSON schema."""
    if ref := schema.get("$ref"):
        if definition := _get_json_schema_definition(ref, defs):
            return _parse_json_schema_type(definition, defs)

    type_name = schema.get("type", "object")

    if "anyOf" in schema:
        return " | ".join(
            _parse_json_schema_type(item, defs) for item in schema["anyOf"]
        )

    if "allOf" in schema:
        return " & ".join(
            _parse_json_schema_type(item, defs)
            if "type" in item or "$ref" in item
            else _parse_constraint(item)
            for item in schema["allOf"]
        )

    if "oneOf" in schema:
        return " ^ ".join(
            _parse_json_schema_type(item, defs) for item in schema["oneOf"]
        )

    if type_name == "array":
        items = schema.get("items", {})
        if isinstance(items, dict):
            return f"array<{_parse_json_schema_type(items, defs)}>"
        return "array"

    if type_name == "object":
        return schema.get("title", "object")

    return type_name


def _parse_json_schema(
    schema: dict,
    dataset_qualified_name: str,
    defs: dict,
    parent_field: Union[str, None] = None,
) -> Generator[DataField, None, None]:
    """Parse a JSON schema and yield DataField instances."""
    for key, metadata in schema.get("properties", {}).items():
        type_name = _parse_json_schema_type(metadata, defs)

        field = build_field(
            name=key,
            dataset_qualified_name=dataset_qualified_name,
            definition=metadata.get("description"),
            parent_field=parent_field,
            type_name=type_name,
        )

        yield field

        if type_name == "object":
            # Recursively parse nested objects
            yield from _parse_json_schema(
                schema=metadata,
                dataset_qualified_name=dataset_qualified_name,
                defs=defs,
                parent_field=field.qualified_name,
            )

        elif type_name.startswith("array") and "items" in metadata:
            items = metadata["items"]

            if items["type"] == "object":
                # Handle array of objects
                yield from _parse_json_schema(
                    schema=items,
                    dataset_qualified_name=dataset_qualified_name,
                    defs=defs,
                    parent_field=field.qualified_name,
                )
            else:
                # Handle array of primitive types
                item_type = _parse_json_schema_type(items, defs)
                yield build_field(
                    name=f"{key}_item",
                    dataset_qualified_name=dataset_qualified_name,
                    type_name=item_type,
                    parent_field=field.qualified_name,
                )

        for definition in _find_json_schema_references(metadata, defs):
            yield from _parse_json_schema(
                schema=definition,
                dataset_qualified_name=dataset_qualified_name,
                defs=defs,
                parent_field=field.qualified_name,
            )


def parse_json_schema(
    schema: str,
    dataset_qualified_name: str,
) -> Generator[DataField, None, None]:
    """Parse a JSON schema and yield DataField instances."""
    schema_dict = json.loads(schema)

    yield from _parse_json_schema(
        schema=schema_dict,
        dataset_qualified_name=dataset_qualified_name,
        defs=schema_dict.get("$defs", {}),
    )
