from pathlib import Path

import pytest
from aurelius_atlas_parity.normalise import TIMESTAMP, GuidMap, NormalisationRules, load_rules, normalise
from aurelius_atlas_parity.scenario import Request, Step
from tests.conftest import GUID_A, GUID_B

STEP = Step(
    name="read",
    request=Request(method="GET", path="/x"),
    ignore=("$.entity.version",),
    unordered=("$.entity.labels", "$.entity.refs"),
)


@pytest.mark.covers("aurelius_atlas_parity.normalise.load_rules", rules=["PAR-03"])
def test__load_rules(tmp_path: Path) -> None:
    """Rules are read from YAML; an empty file gives the defaults."""
    (tmp_path / "rules.yaml").write_text("ignore: ['$..version']\ntimestamps: [createTime, lastModifiedTS]\n")
    (tmp_path / "empty.yaml").write_text("")

    assert load_rules(tmp_path / "rules.yaml") == NormalisationRules(
        ignore=("$..version",), timestamps=("createTime", "lastModifiedTS")
    )
    assert load_rules(tmp_path / "empty.yaml") == NormalisationRules()


@pytest.mark.covers("aurelius_atlas_parity.normalise.GuidMap.name", rules=["PAR-03"])
def test__guid_map_numbers_by_first_appearance() -> None:
    """Each GUID gets a stable number; letter case does not matter."""
    guids = GuidMap()

    assert [guids.name(GUID_A), guids.name(GUID_B), guids.name(GUID_A.upper())] == ["<guid-1>", "<guid-2>", "<guid-1>"]


@pytest.mark.covers("aurelius_atlas_parity.normalise.normalise", rules=["PAR-03"])
def test__normalise_applies_every_rule() -> None:
    """Ignored paths go, timestamps are masked, unordered lists sorted, GUIDs numbered in values and keys."""
    document = {
        "entity": {
            "guid": GUID_A,
            "version": 3,
            "updateTime": 99,
            "labels": ["b", "a"],
            "refs": [{"guid": GUID_B, "n": 2}, {"guid": GUID_A, "n": 1}],
        },
        "referredEntities": {GUID_B: {"createTime": 5}},
        "global": "drop me",
    }
    rules = NormalisationRules(ignore=("$.global",))

    result = normalise(document, rules, STEP, GuidMap())

    assert result == {
        "entity": {
            "guid": "<guid-1>",
            "updateTime": TIMESTAMP,
            "labels": ["a", "b"],
            "refs": [{"guid": "<guid-1>", "n": 1}, {"guid": "<guid-2>", "n": 2}],
        },
        "referredEntities": {"<guid-2>": {"createTime": TIMESTAMP}},
    }
    assert document["entity"]["version"] == 3  # the input is not changed


@pytest.mark.covers("aurelius_atlas_parity.normalise.normalise", rules=["PAR-03"])
def test__normalise_shares_numbering_across_steps() -> None:
    """The same GUID in two answers of a scenario gets the same placeholder."""
    guids = GuidMap()
    plain = Step(name="s", request=Request(method="GET", path="/x"))

    first = normalise({"guid": GUID_B}, NormalisationRules(), plain, guids)
    second = normalise({"other": GUID_A, "again": GUID_B}, NormalisationRules(), plain, guids)

    assert first == {"guid": "<guid-1>"}
    assert second == {"again": "<guid-1>", "other": "<guid-2>"}


@pytest.mark.covers("aurelius_atlas_parity.normalise.normalise", rules=["PAR-03"])
def test__normalise_leaves_text_and_scalars() -> None:
    """Non-JSON bodies and scalars pass through."""
    plain = Step(name="s", request=Request(method="GET", path="/x"))

    assert normalise("plain text", NormalisationRules(), plain, GuidMap()) == "plain text"
    assert normalise(None, NormalisationRules(), plain, GuidMap()) is None
