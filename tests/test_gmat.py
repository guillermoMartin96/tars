"""GMAT tooling tests using a synthetic report built from the exact Kepler solution."""

from dataclasses import replace

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


@pytest.mark.parametrize("column", range(len(gmat.REPORT_COLUMNS)))
@pytest.mark.parametrize("value", ["nan", "inf", "-inf"])
def test_parse_rejects_non_finite_report_fields(m1_scenario, column, value):
    lines = _synthetic_report(m1_scenario, n_rows=2).splitlines()
    fields = lines[2].split()  # Interior row, after a valid initial state.
    fields[column] = value
    lines[2] = " ".join(fields)
    with pytest.raises(ValueError, match="non-finite"):
        gmat.parse_report("\n".join(lines))


@pytest.mark.parametrize("width", [11, 13])
def test_parse_rejects_incorrect_row_width(m1_scenario, width):
    lines = _synthetic_report(m1_scenario, n_rows=2).splitlines()
    fields = lines[2].split()
    lines[2] = " ".join(fields[:width] if width < len(fields) else [*fields, "0"])
    with pytest.raises(ValueError, match="columns"):
        gmat.parse_report("\n".join(lines))


def test_parse_rejects_empty_report():
    with pytest.raises(ValueError, match="empty"):
        gmat.parse_report("\n  \n")


@pytest.fixture(scope="module")
def reference_comparison_inputs(m1_scenario):
    return gmat.parse_report(_synthetic_report(m1_scenario)), run_scenario(m1_scenario)


@pytest.mark.parametrize("field", ["r", "v", "sma", "ecc", "inc_deg", "period"])
@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_compare_rejects_non_finite_in_memory_rows(
    m1_scenario, reference_comparison_inputs, field, value
):
    original, run = reference_comparison_inputs
    rows = list(original)
    changed = np.full(3, value) if field in ("r", "v") else value
    rows[100] = replace(rows[100], **{field: changed})
    with pytest.raises(ValueError, match="non-finite"):
        gmat.compare(rows, run.samples, m1_scenario)


@pytest.mark.parametrize("field", ["r", "v"])
def test_compare_rejects_incorrect_vector_shape(m1_scenario, reference_comparison_inputs, field):
    original, run = reference_comparison_inputs
    rows = list(original)
    rows[100] = replace(rows[100], **{field: np.zeros(2)})
    with pytest.raises(ValueError, match="shape"):
        gmat.compare(rows, run.samples, m1_scenario)


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
    """GMAT's default mu (398600.4415 km^3/s^2) must be visible in the metrics (SCI-0005).

    Same Cartesian start, different mu: delta_a/a ~ -delta_mu/mu, so the period shifts
    by delta_T/T ~ -2 delta_mu/mu (8.1e-6 s/orbit), ~0.63 m along-track after 10 orbits
    (corrected per external review REV-001; the earlier 0.16 m figure assumed equal radii).
    """
    rows = gmat.parse_report(_synthetic_report(m1_scenario, mu_gmat=3.986004415e14))
    run = run_scenario(m1_scenario)
    m = gmat.compare(rows, run.samples, m1_scenario)
    assert m["initial_sma_difference_m"] == pytest.approx(
        6628137.0 * (3e5 / 3.986004415e14), rel=1e-2
    )
    assert m["period_difference_s"] == pytest.approx(8.08e-6, rel=1e-2)
    assert m["gmat_vs_kepler_position_error_max_m"] == pytest.approx(0.627, rel=1e-2)


def test_compare_rejects_off_grid_times(m1_scenario):
    text = _synthetic_report(m1_scenario, n_rows=2).replace("\n60 ", "\n61 ", 1)
    run = run_scenario(m1_scenario)
    with pytest.raises(ValueError):
        gmat.compare(gmat.parse_report(text), run.samples, m1_scenario)


@pytest.mark.parametrize("n_rows", [1, 89, 894])
def test_truncated_reference_is_rejected(m1_scenario, n_rows):
    """REV-002: a partial GMAT report must never pass."""
    rows = gmat.parse_report(_synthetic_report(m1_scenario, n_rows=n_rows))
    run = run_scenario(m1_scenario)
    with pytest.raises(ValueError, match="incomplete"):
        gmat.compare(rows, run.samples, m1_scenario)


def test_provenance_checks_are_exact(m1_scenario):
    """REV-001: constants and script must match the current scenario exactly."""
    script = gmat.m1_script(m1_scenario)
    good = {
        "scenario_hash": m1_scenario.config_hash(),
        "constants": {"name": "WGS84", "mu_km3_s2": 398600.4418, "equatorial_radius_km": 6378.137},
    }
    tol = (1e-4, 1e-7)
    assert gmat.provenance_problems(good, m1_scenario, script, *tol) == []
    wrong_mu = {**good, "constants": {**good["constants"], "mu_km3_s2": 398600.4415}}
    assert gmat.provenance_problems(wrong_mu, m1_scenario, script, *tol)
    edited = script.replace("398600.4418", "398600.4415")
    assert gmat.provenance_problems(good, m1_scenario, edited, *tol)
    # Last-bit differences in the initial state are tolerated; real changes are not.
    r0, _ = initial_state(m1_scenario)
    x_line = f"GMAT Sat.X = {float(r0[0]) / 1000.0!r};"
    nudged = script.replace(x_line, f"GMAT Sat.X = {float(r0[0]) / 1000.0 + 1e-12!r};")
    assert nudged != script and gmat.provenance_problems(good, m1_scenario, nudged, *tol) == []
    moved = script.replace(x_line, f"GMAT Sat.X = {float(r0[0]) / 1000.0 + 1e-3!r};")
    assert gmat.provenance_problems(good, m1_scenario, moved, *tol)


def test_committed_reference_passes_provenance_checks(m1_scenario):
    import json

    from tests.conftest import REPO_ROOT

    ref = REPO_ROOT / "toolbox" / "references" / "gmat"
    metadata = json.loads((ref / "m1_two_body_metadata.json").read_text())
    script = (ref / "m1_two_body.script").read_text()
    assert gmat.provenance_problems(metadata, m1_scenario, script, 1e-4, 1e-7) == []
    rows = gmat.parse_report((ref / "m1_two_body_report.txt").read_text())
    gmat.compare(rows, run_scenario(m1_scenario).samples, m1_scenario)  # complete


@pytest.mark.parametrize("mu_gmat", [3.986004415e14, 3.986004421e14, 3.986004418e14 * (1 + 1e-12)])
def test_approved_gates_reject_mu_mismatch_of_either_sign(m1_scenario, mu_gmat):
    """REV-001 / DR-0009: a mu mismatch must fail regardless of its sign.

    Before DR-0009, mu = 3.986004421e14 passed (ours vs GMAT 0.33 m < 0.6 m).
    """
    from tars.validation.thresholds import Check, load_thresholds

    rows = gmat.parse_report(_synthetic_report(m1_scenario, mu_gmat=mu_gmat))
    metrics = gmat.compare(rows, run_scenario(m1_scenario).samples, m1_scenario)
    th = load_thresholds()
    gates = {
        k: v for k, v in th.for_validator("gmat_reference").items() if not k.startswith("script_")
    }
    check = Check("gmat_reference", metrics, gates, th.status)
    assert not check.passed
    assert any("gmat_vs_kepler_position" in f for f in check.failures)
