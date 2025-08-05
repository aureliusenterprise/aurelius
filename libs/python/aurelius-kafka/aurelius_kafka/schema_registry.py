from aurelius_sdk import zigzag_encode

MAGIC_BYTE = b"\x00"


def build_schema_registry_header(
    schema_id: int,
    *,
    is_protobuf: bool = False,
    message_indexes: list[int] | None = None,
) -> bytes:
    r"""
    Builds a message header compatible with the Confluent Schema Registry wire format.

    The header consists of a magic byte (0) and the schema ID encoded as 4 big-endian bytes. For Protobuf messages, the
    header also includes the message indexes as zigzag-encoded integers.

    [See the Confluent documentation for more details](https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html#wire-format).

    Args:
        schema_id (int): Schema registry ID for the message schema.
        is_protobuf (bool): Whether or not the header is for a Protobuf message.
        message_indexes (list[int] | None): An array of indexes that corresponds to the message type.

    Returns:
        bytes: The schema registry header.
    """
    header = MAGIC_BYTE + schema_id.to_bytes(4, "big")

    if not is_protobuf:
        return header

    if message_indexes is None or not (length := len(message_indexes)) or (length == 1 and message_indexes[0] == 0):
        return header + b"\x00"

    encoded_length = zigzag_encode(length).to_bytes()
    encoded_message_indexes = b"".join(zigzag_encode(n).to_bytes() for n in message_indexes)

    return header + encoded_length + encoded_message_indexes
