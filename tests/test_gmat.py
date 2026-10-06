"""GMAT tooling tests using a synthetic report built from the exact Kepler solution."""

import math

import numpy as np
import pytest

from tars.astro import kepler
from tars.astro.elements import keplerian_period
from tars.sim.runner import initial_state, run_scenario
from tars.validation import gmat


def _synthetic_report(scenario, mu_gmat=None, n_rows=None):
    """Emulate GMAT output: exact two-body states in km, 16 significant digits."""
    mu = scenario.constants.mu
    mu_gmat = mu if mu_gmat is None else mu_gmat
    r0, v0 = initial_state(scenario)
    interval, count = gmat.report_schedule(scenario)
    lines = [" ".join(gmat.REPORT_COLUMNS)]
    a0 = 1.0 / (2.0 / np.linalg.norm(r0) - np.dot(v0, v0) / mu_gmat)
    for k in range((n_rows or count) + 1):
        t = interval * k
        r, v = kepler.propagate(r0, v0, t, mu_gmat)
        values = [t, 61041.0 + t / 86400, *(r / 1e3), *(v / 1e3), a0 / 1e3, 0.0, 51.6,
                  keplerian_period(a0, mu_gmat)]  # fmt: skip
        lines.append(" ".join(f"{x:.16g}" for x in values))
    return "\n".join(lines) + "\n"


def test_script_is_deterministic_and_carries_project_configuration(m1_scenario):
    script = gmat.m1_script(m1_scenario)
    assert script == gmat.m1_script(m1_scenario)
    assert m1_scenario.config_hash() in script
    assert "GMAT Earth.Mu = 398600.4418;" in script
    assert "GMAT Earth.EquatorialRadius = 6378.137;" in script
    assert "GMAT TwoBodyFM.PointMasses = {Earth};" in script
    assert "GMAT TwoBodyFM.Drag = None;" in script
    assert "GMAT Sat.Epoch = '01 Jan 2026 00:00:00.000';" in script
    assert "For I = 1:895;" in script  # 895 x 60 s = 53 700 s <= 10 periods
    r0, _ = initial_state(m1_scenario)
    assert f"GMAT Sat.X = {float(r0[0]) / 1000.0!r};" in script
    # Every assignment must be a GMAT literal (catches e.g. numpy's 'np.float64(...)' repr).
    assert "np." not in script and "float64" not in script
    for line in script.splitlines():
        if line.startswith("GMAT Sat.") and line.split("=")[0].strip()[-1] in "XYZ":
            float(line.split("=")[1].strip().rstrip(";"))


def test_report_schedule_matches_telemetry(m1_scenario):
    interval, count = gmat.report_schedule(m1_scenario)
    assert interval == m1_scenario.telemetry.sample_interval_s
    assert count * interval <= 10 * keplerian_period(6628137.0, m1_scenario.constants.mu)


def test_parse_skips_repeated_header_lines(m1_scenario):
    """Observed in GMAT R2026a output: the header is written again inside the loop."""
    text = _synthetic_report(m1_scenario, n_rows=3)
    lines = text.splitlines()
    repeated = "\n".join([lines[0], lines[1], lines[0], *lines[2:]]) + "\n"
    assert len(gmat.parse_report(repeated)) == len(gmat.parse_report(text)) == 4


def test_parse_rejects_unexpected_columns():
    with pytest.raises(ValueError):
        gmat.parse_report("A B C\n1 2 3\n")


def test_compare_against_exact_reference(m1_scenario):
    rows = gmat.parse_report(_synthetic_report(m1_scenario))
    run = run_scenario(m1_scenario)
    m = gmat.compare(rows, run.samples, m1_scenario)
    # Synthetic "GMAT" is exact, so ours-vs-GMAT equals our RK4 error vs Kepler.
    assert m["gmat_vs_kepler_position_error_max_m"] < 1e-5
    assert m["position_error_max_m"] == pytest.approx(
        m["ours_vs_kepler_position_error_max_m"], abs=1e-5
    )
    assert m["initial_sma_difference_m"] < 1e-5
    assert m["initial_state_difference_m"] < 1e-6
    assert m["rows_compared"] == 896


def test_compare_detects_mismatched_mu(m1_scenario):
    """GMAT's default mu (398600.4415 km^3/s^2) must be caught (SCI-0005)."""
    rows = gmat.parse_report(_synthetic_report(m1_scenario, mu_gmat=3.986004415e14, n_rows=10))
    run = run_scenario(m1_scenario)
    m = gmat.compare(rows, run.samples, m1_scenario)
    # Circular orbit: delta_a ~ r * delta_mu / mu ~ 6.6e6 m * 7.5e-10 ~ 5 mm.
    assert m["initial_sma_difference_m"] == pytest.approx(
        6628137.0 * (3e5 / 3.986004415e14), rel=1e-2
    )
    assert math.isfinite(m["period_difference_s"]) and m["period_difference_s"] > 1e-6


def test_compare_rejects_off_grid_times(m1_scenario):
    text = _synthetic_report(m1_scenario, n_rows=2).replace("\n60 ", "\n61 ", 1)
    run = run_scenario(m1_scenario)
    with pytest.raises(ValueError):
        gmat.compare(gmat.parse_report(text), run.samples, m1_scenario)
