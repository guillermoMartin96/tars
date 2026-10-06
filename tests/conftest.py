from pathlib import Path

import pytest

from tars.sim.scenario import Scenario, load_scenario

REPO_ROOT = Path(__file__).resolve().parents[1]
M1_SCENARIO = REPO_ROOT / "scenarios" / "m1_leo_250km.json"


@pytest.fixture(scope="session")
def m1_scenario() -> Scenario:
    return load_scenario(M1_SCENARIO)
