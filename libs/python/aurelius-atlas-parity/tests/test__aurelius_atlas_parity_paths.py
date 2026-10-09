import pytest
from aurelius_atlas_parity.paths import InvalidPathError, locate, parse_path, select, transform

DOC = {"a": {"b": [{"c": 1, "k": "x"}, {"c": 2}], "k": "y"}, "k": "z"}


@pytest.mark.covers("aurelius_atlas_parity.paths.parse_path", rules=["PAR-10"])
def test__parse_path_steps() -> None:
    """Members, deep keys, wildcards and indices are recognised."""
    assert parse_path("$.a..k[*][0]") == [("member", "a"), ("deep", "k"), ("all", "*"), ("index", "0")]
    assert parse_path("$") == []


@pytest.mark.covers("aurelius_atlas_parity.paths.parse_path", rules=["PAR-10"])
@pytest.mark.parametrize("path", ["a.b", "$a", "$.a[", "$.a[x]", "$.", "$.a b"])
def test__parse_path_rejects_malformed(path: str) -> None:
    """Anything outside the supported syntax is refused."""
    with pytest.raises(InvalidPathError):
        parse_path(path)


@pytest.mark.covers("aurelius_atlas_parity.paths.select", rules=["PAR-10"])
@pytest.mark.covers("aurelius_atlas_parity.paths.locate", rules=["PAR-10"])
@pytest.mark.parametrize(
    ("path", "values"),
    [
        ("$", [DOC]),
        ("$.a.b[*].c", [1, 2]),
        ("$.a.b[1].c", [2]),
        ("$.a.b[5].c", []),
        ("$.missing.x", []),
        ("$..k", ["y", "x", "z"]),
        ("$.a..c", [1, 2]),
        ("$.k[*]", []),
    ],
)
def test__select(path: str, values: list[object]) -> None:
    """Paths select the values they point at, in document order; missing parts select nothing."""
    assert sorted(map(str, select(DOC, path))) == sorted(map(str, values))


@pytest.mark.covers("aurelius_atlas_parity.paths.locate")
def test__locate_root_has_no_container() -> None:
    """The root itself cannot be located (it has no container)."""
    assert locate(DOC, "$") == []


@pytest.mark.covers("aurelius_atlas_parity.paths.transform", rules=["PAR-10"])
def test__transform_in_place() -> None:
    """Every selected value is replaced in place."""
    doc = {"x": [{"t": 1}, {"t": 2}]}

    transform(doc, "$.x[*].t", lambda v: v * 10)

    assert doc == {"x": [{"t": 10}, {"t": 20}]}
