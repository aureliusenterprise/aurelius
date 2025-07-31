from m4i_data_dictionary_io.sources.kafka.avro import parse_avro_schema
from m4i_data_dictionary_io.sources.kafka.atlas import build_field


def test__parse_avro_schema_empty():
    """Test parsing an empty Avro schema."""
    avro_schema = """
    {
        "type": "record",
        "name": "EmptyRecord",
        "fields": []
    }
    """

    expected = []

    parsed_schema = parse_avro_schema(avro_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_avro_schema_basic():
    """Test parsing a basic Avro schema with simple fields."""
    avro_schema = """
    {
        "type": "record",
        "name": "User",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "age", "type": "int"},
            {"name": "email", "type": ["null", "string"], "default": null}
        ]
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
            type_name="int",
        ),
        build_field(
            name="email",
            dataset_qualified_name="example_dataset",
            type_name="null | string",
        ),
    ]

    parsed_schema = parse_avro_schema(avro_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_avro_schema_with_nested_fields():
    """Test parsing an Avro schema with nested fields."""
    avro_schema = """
    {
        "type": "record",
        "name": "User",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "age", "type": "int"},
            {
                "name": "address",
                "type": {
                    "type": "record",
                    "name": "Address",
                    "fields": [
                        {"name": "street", "type": "string"},
                        {"name": "city", "type": "string"}
                    ]
                }
            }
        ]
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
            type_name="int",
        ),
        build_field(
            name="address",
            dataset_qualified_name="example_dataset",
            type_name="Address",
        ),
        build_field(
            name="street",
            dataset_qualified_name="example_dataset",
            type_name="string",
            parent_field="example_dataset--address",
        ),
        build_field(
            name="city",
            dataset_qualified_name="example_dataset",
            type_name="string",
            parent_field="example_dataset--address",
        ),
    ]

    parsed_schema = parse_avro_schema(avro_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_avro_schema_with_union_types():
    """Test parsing an Avro schema with union types."""
    avro_schema = """
    {
        "type": "record",
        "name": "User",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "age", "type": ["null", "int"], "default": null},
            {"name": "preferences", "type": {
                "type": "map",
                "values": ["null", "string"]
            }}
        ]
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
            type_name="null | int",
        ),
        build_field(
            name="preferences",
            dataset_qualified_name="example_dataset",
            type_name="map<null | string>",
        ),
        build_field(
            name="preferences_value",
            dataset_qualified_name="example_dataset",
            type_name="null | string",
            parent_field="example_dataset--preferences",
        ),
    ]

    parsed_schema = parse_avro_schema(avro_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_avro_schema_with_array_types():
    """Test parsing an Avro schema with array types."""
    avro_schema = """
    {
        "type": "record",
        "name": "User",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "tags", "type": {
                "type": "array",
                "items": "string"
            }}
        ]
    }
    """

    expected = [
        build_field(
            name="name",
            dataset_qualified_name="example_dataset",
            type_name="string",
        ),
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
    ]

    parsed_schema = parse_avro_schema(avro_schema, "example_dataset")

    actual = list(parsed_schema)

    assert expected == actual, f"Expected {expected} but got {actual}"
