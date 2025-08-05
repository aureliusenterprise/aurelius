def zigzag_decode(n: int) -> int:
    """
    Decode an integer from zigzag encoding.

    Zigzag encoding is a method of encoding signed integers into unsigned integers.

    See <https://gist.github.com/mfuerstenau/ba870a29e16536fdbaba> for more details.

    Args:
        n (int): The zigzag encoded integer

    Returns:
        int: The decoded integer
    """
    return (n >> 1) ^ -(n & 1)


def zigzag_encode(n: int) -> int:
    """
    Encode an integer to zigzag encoding.

    Zigzag encoding is a method of encoding signed integers into unsigned integers.

    See <https://gist.github.com/mfuerstenau/ba870a29e16536fdbaba> for more details.

    Args:
        n (int): The integer to encode

    Returns:
        int: The zigzag encoded integer
    """
    return (n << 1) ^ (n >> 31)
