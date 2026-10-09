import pytest
from aurelius_atlas_testing.markers import Coverage, InvalidCoversError, merge, parse_covers

PARSE = "aurelius_atlas_testing.markers.parse_covers"


@pytest.mark.covers(PARSE, rules=["TRC-01"])
def test__parse_covers_accepts_target_and_rules() -> None:
    """A dotted target with rule ids is accepted as declared."""
    coverage = parse_covers(("pkg.module.func",), {"rules": ["ABC-01", "ABCDEF-123"]})

    assert coverage == Coverage(targets=("pkg.module.func",), rules=("ABC-01", "ABCDEF-123"))


@pytest.mark.covers(PARSE, rules=["TRC-01"])
def test__parse_covers_rules_are_optional() -> None:
    """Without rules only the target is declared."""
    assert parse_covers(("pkg.func",), {}) == Coverage(targets=("pkg.func",))


@pytest.mark.covers(PARSE, rules=["TRC-01"])
@pytest.mark.parametrize(
    ("args", "kwargs", "message"),
    [
        ((), {}, "exactly one dotted target"),
        (("a.b", "c.d"), {}, "exactly one dotted target"),
        ((42,), {}, "exactly one dotted target"),
        (("func",), {}, "not a dotted path"),
        (("pkg.1func",), {}, "not a dotted path"),
        (("pkg.func",), {"rule": ["ABC-01"]}, "unexpected arguments: rule"),
        (("pkg.func",), {"rules": "ABC-01"}, "must be a list"),
        (("pkg.func",), {"rules": 7}, "must be a list"),
        (("pkg.func",), {"rules": ["abc-01"]}, "must look like 'ABC-01': abc-01"),
        (("pkg.func",), {"rules": ["ABC-1"]}, "must look like"),
    ],
    ids=["none", "two", "not-str", "no-dot", "bad-name", "unknown-kw", "rules-str", "rules-int", "lowercase", "short"],
)
def test__parse_covers_rejects_malformed_markers(
    args: tuple[object, ...], kwargs: dict[str, object], message: str
) -> None:
    """Malformed declarations are refused with a message saying what is wrong."""
    with pytest.raises(InvalidCoversError, match=message):
        parse_covers(args, kwargs)


@pytest.mark.covers("aurelius_atlas_testing.markers.merge", rules=["TRC-01"])
def test__merge_combines_markers_without_duplicates() -> None:
    """Several markers on one test add up, first-seen order kept."""
    merged = merge(
        [
            Coverage(targets=("a.b",), rules=("ABC-01",)),
            Coverage(targets=("a.c",), rules=("ABC-01", "ABC-02")),
            Coverage(targets=("a.b",)),
        ]
    )

    assert merged == Coverage(targets=("a.b", "a.c"), rules=("ABC-01", "ABC-02"))
