from m4i_data_dictionary_io.sources.kafka.atlas import build_field
from m4i_data_dictionary_io.sources.kafka.json_schema import parse_json_schema


def test__parse_json_schema_empty():
    """Test parsing an empty JSON schema."""
    json_schema = """
    {
        "type": "object",
        "properties": {}
    }
    """

    expected = []

    parsed_schema = parse_json_schema(json_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_json_schema_basic():
    """Test parsing a basic JSON schema with simple fields."""
    json_schema = """
    {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {
                "anyOf": [
                    {"type": "null"}, 
                    {"type": "string"}
                ],
                "default": null
            }
        }
    }
    """

    expected = [
        build_field(
            name="name",
            dataset_qualified_name="example_dataset",
            type_name="string",
        ),
        build_field(
            name="age",
            dataset_qualified_name="example_dataset",
            type_name="integer",
        ),
        build_field(
            name="email",
            dataset_qualified_name="example_dataset",
            type_name="null | string",
        ),
    ]

    parsed_schema = parse_json_schema(json_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_json_schema_with_nested_fields():
    """Test parsing a JSON schema with nested fields."""
    json_schema = """
    {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                }
            },
            "preferences": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string"},
                    "notifications": {"type": "boolean"}
                }
            }
        }
    }
    """

    expected = [
        build_field(
            name="user",
            dataset_qualified_name="example_dataset",
            type_name="object",
        ),
        build_field(
            name="name",
            dataset_qualified_name="example_dataset",
            type_name="string",
            parent_field="example_dataset--user",
        ),
        build_field(
            name="age",
            dataset_qualified_name="example_dataset",
            type_name="integer",
            parent_field="example_dataset--user",
        ),
        build_field(
            name="preferences",
            dataset_qualified_name="example_dataset",
            type_name="object",
        ),
        build_field(
            name="theme",
            dataset_qualified_name="example_dataset",
            type_name="string",
            parent_field="example_dataset--preferences",
        ),
        build_field(
            name="notifications",
            dataset_qualified_name="example_dataset",
            type_name="boolean",
            parent_field="example_dataset--preferences",
        ),
    ]

    parsed_schema = parse_json_schema(json_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_json_schema_with_array():
    """Test parsing a JSON schema with array types."""
    json_schema = """
    {
        "type": "object",
        "properties": {
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            },
            "metadata": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": "string"}
                    }
                }
            }
        }
    }
    """

    expected = [
        build_field(
            name="tags",
            dataset_qualified_name="example_dataset",
            type_name="array<string>",
        ),
        build_field(
            name="tags_item",
            dataset_qualified_name="example_dataset",
            type_name="string",
            parent_field="example_dataset--tags",
        ),
        build_field(
            name="metadata",
            dataset_qualified_name="example_dataset",
            type_name="array<object>",
        ),
        build_field(
            name="key",
            dataset_qualified_name="example_dataset",
            type_name="string",
            parent_field="example_dataset--metadata",
        ),
        build_field(
            name="value",
            dataset_qualified_name="example_dataset",
            type_name="string",
            parent_field="example_dataset--metadata",
        ),
    ]

    parsed_schema = parse_json_schema(json_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_json_schema_with_anyOf():
    """Test parsing a JSON schema with anyOf."""
    json_schema = """
    {
        "type": "object",
        "properties": {
            "data": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "integer"}
                ]
            }
        }
    }
    """

    expected = [
        build_field(
            name="data",
            dataset_qualified_name="example_dataset",
            type_name="string | integer",
        ),
    ]

    parsed_schema = parse_json_schema(json_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_json_schema_with_allOf():
    """Test parsing a JSON schema with allOf."""
    json_schema = """
    {
        "type": "object",
        "properties": {
            "data": {
                "allOf": [
                    {"type": "string"},
                    {"minLength": 5}
                ]
            }
        }
    }
    """

    expected = [
        build_field(
            name="data",
            dataset_qualified_name="example_dataset",
            type_name="string & minLength(5)",
        ),
    ]

    parsed_schema = parse_json_schema(json_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_json_schema_with_oneOf():
    """Test parsing a JSON schema with oneOf."""
    json_schema = """
    {
        "type": "object",
        "properties": {
            "data": {
                "oneOf": [
                    {"type": "string"},
                    {"type": "null"}
                ]
            }
        }
    }
    """

    expected = [
        build_field(
            name="data",
            dataset_qualified_name="example_dataset",
            type_name="string ^ null",
        ),
    ]

    parsed_schema = parse_json_schema(json_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_json_schema_with_definitions():
    """Test parsing a JSON schema with definitions."""
    json_schema = """
    {
        "$defs": {
            "User": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                }
            }
        },
        "type": "object",
        "properties": {
            "user": {"$ref": "#/$defs/User"}
        }
    }
    """

    expected = [
        build_field(
            name="user",
            dataset_qualified_name="example_dataset",
            type_name="object",
        ),
        build_field(
            name="name",
            dataset_qualified_name="example_dataset",
            type_name="string",
            parent_field="example_dataset--user",
        ),
        build_field(
            name="age",
            dataset_qualified_name="example_dataset",
            type_name="integer",
            parent_field="example_dataset--user",
        ),
    ]

    parsed_schema = parse_json_schema(json_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"