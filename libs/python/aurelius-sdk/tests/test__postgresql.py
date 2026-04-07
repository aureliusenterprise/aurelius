import pytest
from aurelius_sdk.postgresql import sanitize_tsquery


@pytest.mark.parametrize(
    "input_value",
    [None, "", "   ", "\t", "\n"],
    ids=["none", "empty_string", "spaces", "tab", "newline"],
)
def test_empty_inputs_return_none(input_value: str | None) -> None:
    """None, empty, and whitespace-only inputs should return None."""
    assert sanitize_tsquery(input_value) is None


# Tests for individual special character escaping
@pytest.mark.parametrize(
    ("input_str", "expected"),
    [
        ("foo & bar", r"foo \& bar"),
        ("foo | bar", r"foo \| bar"),
        ("foo ! bar", r"foo \! bar"),
        ("foo:bar", r"foo\:bar"),
        ('foo "bar" baz', r"foo \"bar\" baz"),
        ("(foo)", r"\(foo\)"),
    ],
    ids=["ampersand", "pipe", "exclamation", "colon", "double_quote", "parentheses"],
)
def test_escapes_special_characters(input_str: str, expected: str) -> None:
    """Special characters should be properly escaped."""
    assert sanitize_tsquery(input_str) == expected


# Tests for control character removal
@pytest.mark.parametrize(
    ("input_str", "expected"),
    [
        ("foo\x00bar", "foobar"),
        ("foo\x09bar", "foobar"),  # tab (0x09)
        ("foo\x0abar", "foobar"),  # newline (0x0a)
        ("foo\x0dbar", "foobar"),  # carriage return (0x0d)
    ],
    ids=["null_byte", "tab", "newline", "carriage_return"],
)
def test_removes_control_characters(input_str: str, expected: str) -> None:
    """Control characters (0x00-0x1F) should be removed."""
    assert sanitize_tsquery(input_str) == expected


# Tests for normal strings
@pytest.mark.parametrize(
    "input_str",
    [
        "simple query",
        "hello world 123",
        "foo-bar_baz",
    ],
    ids=["simple", "with_numbers", "with_hyphens_and_underscores"],
)
def test_normal_text_unchanged(input_str: str) -> None:
    """Normal text without special characters should remain unchanged."""
    assert sanitize_tsquery(input_str) == input_str


# Tests for combinations and complex scenarios
@pytest.mark.parametrize(
    ("input_str", "expected"),
    [
        ("(query & more) | filter", r"\(query \& more\) \| filter"),
        ('"advanced" && (search | filter)', r"\"advanced\" \&\& \(search \| filter\)"),
        ('foo&bar\x00baz"qux', r"foo\&barbaz\"qux"),
        ("foo&&&bar", r"foo\&\&\&bar"),
        ("&|()", r"\&\|\(\)"),
        ('search for "users & groups" | (admin)', r"search for \"users \& groups\" \| \(admin\)"),
    ],
    ids=[
        "mixed_operators",
        "quotes_and_operators",
        "special_with_control",
        "consecutive_operators",
        "only_special_chars",
        "full_text_search",
    ],
)
def test_complex_scenarios(input_str: str, expected: str) -> None:
    """Complex queries with multiple operators and edge cases."""
    assert sanitize_tsquery(input_str) == expected


# Edge cases
@pytest.mark.parametrize(
    "input_value",
    [
        "\x00\x01\x1f",
        "\x00 \x01",
    ],
    ids=["only_control_characters", "control_and_whitespace"],
)
def test_only_control_and_whitespace_returns_none(input_value: str) -> None:
    """Strings with only control characters or control+whitespace should return None."""
    assert sanitize_tsquery(input_value) is None


# Real-world scenarios with assertions on content preservation
def test_injection_attempt_neutralized() -> None:
    """Attempt to inject tsquery operators should be neutralized."""
    injection = "user' OR '1'='1"
    result = sanitize_tsquery(injection)
    # Single quotes are not special, should remain; content should be preserved
    assert result is not None
    assert "user" in result
    assert "OR" in result


def test_preserves_meaningful_content() -> None:
    """Content should be preserved even when special chars are escaped."""
    original = "search for users & teams"
    result = sanitize_tsquery(original)
    # Content should still be in result, just with escaped operators
    assert result is not None
    assert "search" in result
    assert "users" in result
    assert "teams" in result
