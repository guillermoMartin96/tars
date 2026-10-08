"""Mission-level checks: the M1 scenario as a whole, judged by deterministic logic."""

import numpy as np
import pytest

from tars.astro.elements import keplerian_period
from tars.events import read_jsonl, to_jsonl
from tars.sim import runner


@pytest.fixture(scope="module")
def m1_run(m1_scenario):
    return runner.run_scenario(m1_scenario)


def test_m1_completes_ten_orbits_successfully(m1_run):
    types = [e.type for e in m1_run.events]
    assert types[0] == "SimulationStarted" and types[-1] == "SimulationCompleted"
    orbits = [e for e in m1_run.events if e.type == "OrbitCompleted"]
    assert [e.orbit_number for e in orbits] == list(range(1, 11))
    done = m1_run.completed
    assert done.status == "success" and done.failure_cause is None
    assert done.orbits_completed == 10


def test_m1_event_log_is_valid_jsonl(m1_run):
    text = to_jsonl(m1_run.events)
    assert read_jsonl(text) == m1_run.events


def test_m1_start_event_records_configuration(m1_run, m1_scenario):
    start = m1_run.events[0]
    assert start.scenario_hash == m1_scenario.config_hash()
    assert start.earth_constants["name"] == "WGS84"
    assert start.integrator == "rk4" and start.dt == 10.0 and start.seed == 0


def test_m1_crossings_are_one_period_apart(m1_run, m1_scenario):
    c = m1_scenario.constants
    period = keplerian_period(c.equatorial_radius + m1_scenario.initial_orbit.altitude_m, c.mu)
    # Coarse sanity bound; precise period error is a Proof metric (validators).
    assert np.max(np.abs(np.diff([0.0, *m1_run.crossing_times]) - period)) < 1e-3


def _run_with_extra_force(monkeypatch, scenario, accel):
    class Extra:
        name = "test_extra"

        def acceleration(self, t, r, v):
            return accel(r, v)

    original = runner.build_force_model

    def patched(s):
        from tars.sim.forces import CompositeForceModel

        return CompositeForceModel([*original(s).models, Extra()])

    monkeypatch.setattr(runner, "build_force_model", patched)
    return runner.run_scenario(scenario, record_samples=False)


def test_impact_is_detected_as_failure(monkeypatch, m1_scenario):
    result = _run_with_extra_force(
        monkeypatch, m1_scenario, lambda r, v: -0.5 * v / np.linalg.norm(v)
    )
    assert result.completed.status == "failure" and result.completed.failure_cause == "impact"


def test_escape_is_detected_as_failure(monkeypatch, m1_scenario):
    result = _run_with_extra_force(
        monkeypatch, m1_scenario, lambda r, v: 5.0 * v / np.linalg.norm(v)
    )
    assert result.completed.failure_cause == "escape"


def test_timeout_guard(monkeypatch, m1_scenario):
    # Strong prograde push raises the orbit so 10 orbits cannot finish in 1.1 nominal periods.
    result = _run_with_extra_force(
        monkeypatch, m1_scenario, lambda r, v: 2e-2 * v / np.linalg.norm(v)
    )
    assert result.completed.failure_cause == "timeout"


def test_final_state_is_sampled_and_validated(m1_run):
    """REV-009: the final (off-cadence) state must be in samples and telemetry."""
    assert m1_run.samples[-1].tick == m1_run.final.tick == m1_run.completed.tick
    sampled = [e for e in m1_run.events if e.type == "StateSampled"]
    assert sampled[-1].tick == m1_run.final.tick


@pytest.mark.parametrize("phase", [90.0, 180.0, 270.0])
def test_non_node_start_counts_passages_not_full_revolutions(m1_scenario, phase):
    """F3: retain the existing node-passage semantics for nonzero starting phase."""
    data = m1_scenario.model_dump()
    data["initial_orbit"]["arg_latitude_deg"] = phase
    scenario = type(m1_scenario).model_validate(data)
    result = runner.run_scenario(scenario)
    c = scenario.constants
    period = keplerian_period(c.equatorial_radius + scenario.initial_orbit.altitude_m, c.mu)
    assert result.status == "success"
    assert result.completed.orbits_completed == scenario.stop.orbits
    assert len(result.crossing_times) == scenario.stop.orbits
    # The first passage completes a partial revolution; later ones complete full ones.
    assert 0.0 < result.crossing_times[0] < period
    assert (scenario.stop.orbits - 1) * period < result.final.t < scenario.stop.orbits * period
