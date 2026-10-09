from pathlib import Path

import pytest
from aurelius_atlas_parity.cli import build_parser, main
from aurelius_atlas_parity.pytest_support import ParityLog, check_results, deviation_ids, unknown_deviations
from aurelius_atlas_parity.results import ParityResult, read_parity, write_parity
from aurelius_atlas_parity.scenario import load_scenarios
from tests.conftest import atlas_like, client_for


def _result(status: str, step: str = "a") -> ParityResult:
    return ParityResult(scenario="s", step=step, endpoint="GET /x", status=status, detail="why")  # type: ignore[arg-type]


@pytest.mark.covers("aurelius_atlas_parity.pytest_support.ParityLog.add")
@pytest.mark.covers("aurelius_atlas_parity.pytest_support.ParityLog.write")
@pytest.mark.covers("aurelius_atlas_parity.results.write_parity")
@pytest.mark.covers("aurelius_atlas_parity.results.read_parity")
def test__parity_log_writes_results(tmp_path: Path) -> None:
    """Collected results are written in the report's format."""
    log = ParityLog("apps/aurelius-atlas-server", "Apache Atlas 2.4.0")
    log.add([_result("match")])
    log.add([_result("mismatch", "b")])

    log.write(tmp_path / "parity-results.json")

    (run,) = read_parity([tmp_path / "parity-results.json"])
    assert run.reference == "Apache Atlas 2.4.0"
    assert [r.status for r in run.results] == ["match", "mismatch"]
    write_parity(tmp_path / "deep/x.json", run)
    assert (tmp_path / "deep/x.json").is_file()


@pytest.mark.covers("aurelius_atlas_parity.pytest_support.check_results", rules=["PAR-06"])
def test__check_results() -> None:
    """Matches and deviations pass; unrecorded scenarios skip; anything else fails naming the steps."""
    check_results([_result("match"), _result("deviation", "b")])
    with pytest.raises(pytest.skip.Exception, match="no recorded fixture"):
        check_results([_result("not recorded")])
    with pytest.raises(AssertionError, match=r"b \(GET /x\): error: why"):
        check_results([_result("match"), _result("error", "b")])


@pytest.mark.covers("aurelius_atlas_parity.pytest_support.deviation_ids", rules=["PAR-08"])
@pytest.mark.covers("aurelius_atlas_parity.pytest_support.unknown_deviations", rules=["PAR-08"])
def test__unknown_deviations(scenario_dir: Path) -> None:
    """Allowances must cite ids that deviations.md defines."""
    markdown = "| #     | Area |\n| ----- | ---- |\n| DV-01 | x    |\n| DV-02 | y |\nDV-03 in prose\n"
    scenarios = load_scenarios(scenario_dir)

    assert deviation_ids(markdown) == {"DV-01", "DV-02"}
    assert unknown_deviations(scenarios, {"DV-01"}) == []
    assert unknown_deviations(scenarios, set()) == ["entity-roundtrip/read: DV-01"]


@pytest.mark.covers("aurelius_atlas_parity.pytest_support.deviation_ids", rules=["PAR-08"])
def test__repository_deviations_are_parsed(workspace_root: Path) -> None:
    """The real deviations page defines DV-01 and DV-02."""
    text = (workspace_root / "docs/architecture/conversion/deviations.md").read_text()

    assert {"DV-01", "DV-02"} <= deviation_ids(text)


@pytest.mark.covers("aurelius_atlas_parity.cli.build_parser")
def test__build_parser_defaults() -> None:
    """The record command defaults to the local reference Atlas and its dev credentials."""
    args = build_parser().parse_args(["record", "--scenarios", "s", "--fixtures", "f", "--rules", "r"])

    assert (args.base_url, args.user, args.reference) == ("http://localhost:21000", "admin", "Apache Atlas 2.4.0")


@pytest.mark.covers("aurelius_atlas_parity.cli.main", rules=["PAR-04"])
def test__main_records_fixtures(scenario_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Every selected scenario is recorded; failures are reported and exit 1."""
    rules = tmp_path / "rules.yaml"
    rules.write_text("")
    args = ["record", "--scenarios", str(scenario_dir), "--fixtures", str(tmp_path / "fx"), "--rules", str(rules)]

    assert main(args, client=client_for(atlas_like())) == 0
    assert (tmp_path / "fx/entity-roundtrip.json").is_file()
    assert "entity-roundtrip: recorded" in capsys.readouterr().out

    assert (
        main([*args, "--only", "entity-roundtrip"], client=client_for(lambda _: __import__("httpx").Response(500))) == 1
    )
    assert "not recorded" in capsys.readouterr().err
