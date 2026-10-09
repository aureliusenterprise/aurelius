from pathlib import Path

import pytest
from aurelius_atlas_testing.records import TestRecord, TraceabilityFile, read_traceability, write_traceability


@pytest.mark.covers("aurelius_atlas_testing.records.write_traceability", rules=["TRC-02"])
@pytest.mark.covers("aurelius_atlas_testing.records.read_traceability", rules=["TRC-02"])
def test__traceability_round_trip(tmp_path: Path) -> None:
    """A written file reads back equal; missing files are skipped."""
    data = TraceabilityFile(project="p", tests=(TestRecord(nodeid="t::a", targets=("a.b",), outcome="passed"),))
    path = tmp_path / "deep" / "traceability.json"

    write_traceability(path, data)

    assert read_traceability([path, tmp_path / "missing.json"]) == [data]


@pytest.mark.covers("aurelius_atlas_testing.records.read_traceability")
def test__read_traceability_rejects_invalid_file(tmp_path: Path) -> None:
    """A file that exists but is not a traceability file is an error naming it."""
    path = tmp_path / "bad.json"
    path.write_text('{"tests": 3}')

    with pytest.raises(ValueError, match=r"bad\.json is not a valid traceability file"):
        read_traceability([path])
