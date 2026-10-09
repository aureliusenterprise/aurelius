"""Parity: the server answers like Apache Atlas 2.4.0 (ADR 048). Needs Docker."""

from pathlib import Path

import pytest
from aurelius_atlas_parity.normalise import load_rules
from aurelius_atlas_parity.pytest_support import ParityLog, check_results, deviation_ids, unknown_deviations
from aurelius_atlas_parity.runner import compare, load_fixture
from aurelius_atlas_parity.scenario import Scenario, load_scenarios
from fastapi.testclient import TestClient

PARITY = Path(__file__).parent
SCENARIOS = load_scenarios(PARITY / "scenarios")
RULES = load_rules(PARITY / "normalisation.yaml")
DEVIATIONS = PARITY.parents[3] / "docs/architecture/conversion/deviations.md"


@pytest.mark.component
@pytest.mark.covers("aurelius_atlas_server.routes.admin.version", rules=["ADM-01", "ADM-02"])
@pytest.mark.covers("aurelius_atlas_server.routes.admin.status", rules=["ADM-02", "ADM-03"])
@pytest.mark.covers("aurelius_atlas_server.routes.admin.liveness", rules=["ADM-02", "ADM-04"])
@pytest.mark.covers("aurelius_atlas_server.routes.admin.readiness", rules=["ADM-02", "ADM-05"])
@pytest.mark.parametrize("scenario", SCENARIOS, ids=[scenario.name for scenario in SCENARIOS])
def test__parity(scenario: Scenario, atlas: TestClient, parity_log: ParityLog) -> None:
    """Every scenario's answers equal the recorded reference answers, or differ only as a recorded deviation."""
    results = compare(atlas, scenario, load_fixture(PARITY / "fixtures", scenario), RULES)
    parity_log.add(results)
    check_results(results)


@pytest.mark.covers("aurelius_atlas_parity.pytest_support.unknown_deviations", rules=["PAR-08"])
def test__scenarios_cite_known_deviations() -> None:
    """Every deviation a scenario allows is recorded in deviations.md."""
    assert unknown_deviations(SCENARIOS, deviation_ids(DEVIATIONS.read_text(encoding="utf-8"))) == []
