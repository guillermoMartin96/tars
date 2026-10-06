"""Validators used as Proof must themselves be tested (toolbox/README.md)."""

import json
import math

import numpy as np
import pytest

from tars.astro import kepler
from tars.astro.elements import circular_orbit_state, keplerian_period
from tars.sim.constants import WGS84
from tars.sim.state import StateSnapshot
from tars.validation import architecture, determinism, orbit
from tars.validation.convergence import ConvergencePoint, fitted_order, propagation_error
from tars.validation.thresholds import M1_THRESHOLDS, Check, load_thresholds

MU = WGS84.mu
RADIUS = WGS84.equatorial_radius + 250e3
PERIOD = keplerian_period(RADIUS, MU)


def _exact_samples(n=50, span=3 * PERIOD):
    r0, v0 = circular_orbit_state(RADIUS, math.radians(51.6), 0.0, 0.0, MU)
    out = []
    for k in range(n + 1):
        t = span * k / n
        r, v = kepler.propagate(r0, v0, t, MU)
        out.append(StateSnapshot(tick=k, t=t, r=r, v=v))
    return out


def test_check_gates_only_thresholded_metrics():
    c = Check("x", {"a": 1.0, "b": 100.0}, {"a": 2.0}, "provisional")
    assert c.passed
    c = Check("x", {"a": 3.0, "b": 0.0}, {"a": 2.0}, "provisional")
    assert not c.passed and "a=3" in c.failures[0]
    assert Check("x", {"a": math.nan}, {"a": 1.0}, "approved").passed is False
    with pytest.raises(KeyError):
        Check("x", {"a": 1.0}, {"missing": 1.0}, "approved")
    event = c.to_event()
    assert event.passed is False and event.threshold_status == "provisional"


def test_threshold_file_is_valid_and_honest_about_status():
    data = json.loads(M1_THRESHOLDS.read_text())
    th = load_thresholds()
    assert th.status in ("provisional", "approved")
    if th.status == "approved":
        assert data["approved_by"] and data["approved_on"]
    assert all(v > 0 for name in th.limits for v in th.for_validator(name).values())


def test_invariants_are_zero_for_exact_two_body_motion():
    metrics = orbit.invariant_metrics(_exact_samples(), MU)
    assert metrics["energy_rel_drift_max"] < 1e-14
    assert metrics["angular_momentum_rel_drift_max"] < 1e-14
    assert metrics["eccentricity_vector_drift_max"] < 1e-12
    assert metrics["sma_drift_max_m"] < 1e-6


def test_invariants_detect_injected_energy_error():
    samples = _exact_samples()
    last = samples[-1]
    samples[-1] = StateSnapshot(tick=last.tick, t=last.t, r=last.r, v=last.v * (1 + 1e-6))
    metrics = orbit.invariant_metrics(samples, MU)
    # |dE/E| for a 1e-6 relative speed error on a circular orbit is ~2e-6.
    assert metrics["energy_rel_drift_max"] == pytest.approx(2e-6, rel=1e-3)


def test_trajectory_error_is_zero_against_itself_and_detects_offset():
    samples = _exact_samples()
    ref = orbit.kepler_reference(samples[0], MU)
    assert orbit.trajectory_error_metrics(samples, ref)["position_error_max_m"] < 1e-6

    def shifted(t):
        r, v = ref(t)
        return r + np.array([0.0, 0.0, 5.0]), v

    m = orbit.trajectory_error_metrics(samples, shifted)
    assert m["position_error_max_m"] == pytest.approx(5.0, abs=1e-6)


def test_period_metrics_on_exact_crossings():
    initial = _exact_samples(n=1)[0]
    m = orbit.period_metrics([k * PERIOD for k in range(1, 11)], initial, MU)
    assert m["analytic_period_s"] == pytest.approx(PERIOD, rel=1e-15)
    assert m["period_error_max_s"] < 1e-9
    assert m["node_crossing_time_error_max_s"] < 1e-9
    m = orbit.period_metrics([k * (PERIOD + 0.01) for k in range(1, 11)], initial, MU)
    assert m["node_crossing_time_error_max_s"] == pytest.approx(0.1, rel=1e-6)


def test_fitted_order_recovers_synthetic_power_law():
    points = [ConvergencePoint(dt, 1, 3.0 * dt**4, 0.0, 0.0) for dt in (20.0, 10.0, 5.0)]
    assert fitted_order(points) == pytest.approx(4.0, abs=1e-12)


def test_propagation_error_requires_whole_steps(m1_scenario):
    with pytest.raises(ValueError):
        propagation_error(m1_scenario, 7.0, 100.0)


def test_architecture_scan_flags_forbidden_imports(tmp_path):
    pkg = tmp_path / "tars"
    (pkg / "sim").mkdir(parents=True)
    (pkg / "agents").mkdir()
    (pkg / "sim" / "bad.py").write_text("import random\nfrom time import time\nimport numpy\n")
    (pkg / "sim" / "worse.py").write_text("from tars.validation import orbit\n")
    (pkg / "agents" / "crew.py").write_text(
        "import anthropic\nimport random\nimport pygame.display\n"
    )
    found = {(v.path, v.module, v.rule) for v in architecture.scan(pkg)}
    assert ("sim/bad.py", "random", "physics_core_nondeterminism") in found
    assert ("sim/bad.py", "time", "physics_core_nondeterminism") in found
    assert ("sim/worse.py", "tars.validation", "physics_core_nondeterminism") in found
    assert ("agents/crew.py", "anthropic", "llm_or_3d_dependency") in found
    assert ("agents/crew.py", "pygame.display", "llm_or_3d_dependency") in found
    assert not any(m == "numpy" for _, m, _ in found)
    assert not any(p == "agents/crew.py" and m == "random" for p, m, _ in found)


def test_repository_passes_architecture_scan():
    from tests.conftest import REPO_ROOT

    assert architecture.scan(REPO_ROOT / "src" / "tars") == []


def test_in_process_determinism(m1_scenario):
    hashes = determinism.repeat_hashes(m1_scenario, runs=2)
    assert hashes[0] == hashes[1]
