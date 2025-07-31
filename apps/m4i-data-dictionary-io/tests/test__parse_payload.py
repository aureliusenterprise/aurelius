from m4i_data_dictionary_io.sources.kafka.payload import parse_payload
from m4i_data_dictionary_io.sources.kafka.atlas import build_field


def test__parse_payload_empty():
    """Test parsing an empty payload."""
    payload = "{}"

    expected = []

    parsed_payload = parse_payload(payload, "example_dataset")

    actual = list(parsed_payload)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_payload_basic():
    """Test parsing a basic payload with simple fields."""
    payload = """
    {
        "name": "John Doe",
        "age": 30,
        "email": null
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
            type_name="null",
        ),
    ]

    parsed_payload = parse_payload(payload, "example_dataset")

    actual = list(parsed_payload)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_payload_with_complex_type():
    """Test parsing a payload with a complex type."""
    payload = """
    {
        "user": {
            "name": "Jane Doe",
            "age": 25,
            "email": "jane.doe@example.com"
        },
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
            parent_field="example_dataset--user",
            type_name="string",
        ),
        build_field(
            name="age",
            dataset_qualified_name="example_dataset",
            parent_field="example_dataset--user",
            type_name="int",
        ),
        build_field(
            name="email",
            dataset_qualified_name="example_dataset",
            parent_field="example_dataset--user",
            type_name="string",
        ),
    ]

    parsed_payload = parse_payload(payload, "example_dataset")

    actual = list(parsed_payload)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_payload_with_array():
    """Test parsing a payload with an array."""
    payload = """
    {
        "users": [
            {"name": "Alice", "age": 28},
            {"name": "Bob", "age": 32}
        ]
    }
    """

    expected = [
        build_field(
            name="users",
            dataset_qualified_name="example_dataset",
            type_name="array",
        ),
    ]

    parsed_payload = parse_payload(payload, "example_dataset")

    actual = list(parsed_payload)

    assert expected == actual, f"Expected {expected} but got {actual}"


def test__parse_payload_invalid_json():
    """Test parsing an invalid JSON payload."""
    payload = "{invalid_json}"

    expected = []

    parsed_payload = parse_payload(payload, "example_dataset")

    actual = list(parsed_payload)

    assert expected == actual, f"Expected {expected} but got {actual}"
