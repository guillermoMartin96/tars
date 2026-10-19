"""Regression checks for the M3 T0 Review 01 findings M3T0-F1 ... F4 (research only).

Each check recomputes the reviewer's counterexample independently of the experiment
scripts, then tests what the T0 records and result files claim against it. The checks were
written against the reviewed checkpoint (`bdcaacf`), where every one of them fails, before
any correction was made.

Not collected by the project test suite (pytest `testpaths = ["tests"]`, and the file name
does not match `test_*.py`), so the M1/M2 Proof is unaffected. Run explicitly:
  uv run --no-sync pytest -q docs/science/experiments/m3-t0/check_review01.py

Correction logs inside the records are fenced by `<!-- review01-correction-log -->` and
`<!-- /review01-correction-log -->`. They describe the superseded wording on purpose and are
excluded from the wording checks.

Amended for Review 02 M3T0-R2-F1: perturbed-motion (J2 + drag) values are sampled estimates,
not bounds, so the two F1 checks below test certified bounds where one is claimed and require
the perturbed values to be labelled as estimates. The checks of the new claims are in
`check_review02.py`.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t0_model as m  # noqa: E402

ROOT = HERE.parents[3]
DT = 10.0
B_V1 = 850.0 / (2.2 * 15.0)
J2_DRAG = m.Config(j2=m.J2_FROM_C20, drag=m.Drag(cd=2.2, area_m2=15.0))
LOG = re.compile(r"<!-- review01-correction-log -->.*?<!-- /review01-correction-log -->", re.DOTALL)


def record(name: str) -> str:
    """The text of a T0 record, without its Review 01 correction log."""
    paths = {
        "DR-0029": ROOT / "docs/decisions/requests/DR-0029-m3-t0-proposals.md",
        "report": ROOT / "docs/milestones/M3-T0-report.md",
        "matrix": ROOT / "docs/milestones/M3-T0-decision-matrix.md",
        "README": HERE / "README.md",
    }
    if name == "VAL-0019":
        text = (ROOT / "docs/science/validation.md").read_text()
        text = text[text.index("## VAL-0019") :]
        nxt = text.find("\n## VAL-", 10)
        text = text if nxt < 0 else text[:nxt]
    else:
        text = paths[name].read_text()
    return LOG.sub("", text)


RECORDS = ("DR-0029", "VAL-0019", "report", "matrix", "README")


def results(name: str) -> dict:
    path = HERE / f"t0_{name}_results.json"
    return json.loads(path.read_text()) if path.exists() else {}


def propagate(cfg: m.Config, y0: np.ndarray, t: float) -> np.ndarray:
    sol = solve_ivp(m.rhs(cfg), (0.0, t), y0, method="DOP853", rtol=1e-13, atol=1e-9)
    return sol.y[:, -1]


def midpoint_dip(cfg: m.Config, r0: np.ndarray, v0: np.ndarray) -> float:
    """The reviewer's construction: the lowest point at the middle of a dt step, committed
    states at -dt/2 and +dt/2. Returns how far h dips below the lower committed height."""
    y0 = np.concatenate([r0, v0, [850.0]])
    h = [m.geodetic_iterative(propagate(cfg, y0, s * DT / 2)[:3])[1] for s in (-1.0, 1.0)]
    return min(h) - m.geodetic_iterative(r0)[1]


# ------------------------------------------------------------------- M3T0-F1
DIP_CASES = {
    # case id in the records -> (physics, initial state at the lowest point)
    "kepler_250x800_i51.6_perigee_midstep": (m.Config(), m.perigee_state(250e3, 800e3, 51.6)),
    "j2drag_250x800_i51.6_perigee_midstep": (J2_DRAG, m.perigee_state(250e3, 800e3, 51.6)),
    "kepler_circular250_i51.6_equator_midstep": (m.Config(), m.circular_state(250e3, 51.6)),
}


def claimed_bounds(case: str) -> list[float]:
    """Every value the result files present as an upper bound on the missed-crossing dip
    for this configuration."""
    out = []
    old = results("decay").get("missed_crossing", {})
    if "analytic_estimate_m" in old and "250x800" in case:
        out.append(old["analytic_estimate_m"])  # presented as "the analytic bound"
    new = results("termination").get("missed_crossing", {}).get("cases", {})
    if case in new and "bound_m" in new[case]:
        out.append(new[case]["bound_m"])
    return out


@pytest.mark.parametrize("case", sorted(DIP_CASES))
def test_f1_every_claimed_missed_crossing_bound_holds_at_the_worst_phase(case):
    cfg, (r0, v0) = DIP_CASES[case]
    dip = midpoint_dip(cfg, r0, v0)
    bounds = claimed_bounds(case)
    assert bounds or cfg.drag is not None, f"no bound recorded for {case} (dip {dip:.5f} m)"
    for b in bounds:
        assert b >= dip, f"{case}: claimed bound {b:.5f} m < dip {dip:.5f} m"
    if cfg.drag is not None:  # perturbed: an estimate, labelled as one (M3T0-R2-F1)
        rec = results("termination")["missed_crossing"]["cases"][case]
        assert "not a bound" in rec["estimate_kind"]
        assert rec["sampled_estimate_m"] >= dip


def test_f1_measured_sweep_never_exceeds_the_derived_bound():
    sweep = results("termination").get("missed_crossing", {}).get("sweep")
    assert sweep, "no sampling-phase / eccentricity sweep recorded"
    for row in sweep:
        if "bound_m" in row:
            assert row["max_dip_m"] <= row["bound_m"], row
        else:
            assert "not a bound" in row["estimate_kind"], row


def test_f1_curvature_bound_is_an_upper_bound_on_hddot():
    """The pointwise bound U(r, v, a) >= d2h/dt2 along real trajectories (second
    difference of h on DOP853 states), including the worst cases above."""
    import t0_termination as tt

    for cfg, (r0, v0) in DIP_CASES.values():
        y0 = np.concatenate([r0, v0, [850.0]])
        for t in (0.0, 700.0, 1500.0, 2900.0):
            tau = 0.5
            ys = [y0 if s == t == 0.0 else propagate(cfg, y0, t + s) for s in (-tau, 0.0, tau)]
            h = [m.geodetic_iterative(y[:3])[1] for y in ys]
            hdd = (h[0] - 2 * h[1] + h[2]) / tau**2
            y = ys[1]
            acc = m.acceleration(cfg, t, y[:3], y[3:6], y[6])
            assert tt.hddot_upper(y[:3], y[3:6], acc) >= hdd - 1e-6, (t, hdd)


def test_f1_records_do_not_present_the_fixed_phase_formula_as_a_bound():
    pat = re.compile(r"a\s*e\s*n²\s*dt²\s*/\s*8")
    for name in RECORDS:
        assert not pat.search(record(name)), name
    assert "analytic_estimate_m" not in results("decay").get("missed_crossing", {})


# ------------------------------------------------------------------- M3T0-F2
def lam_dt_circular(h: float, b: float = B_V1) -> float:
    return m.density(h) * math.sqrt(m.MU / (m.A_WGS84 + h)) * DT / b


def test_f2_kappa_001_threshold_is_exact_and_recorded():
    h_star = brentq(lambda h: lam_dt_circular(h) - 0.01, 85e3, 95e3, xtol=1e-9)
    assert lam_dt_circular(90e3) > 0.01  # the rounded "90 km" fails the rule itself
    assert f"{h_star:,.2f}".replace(",", " ") == "90 185.09"
    rec = results("termination").get("stiffness_thresholds", {})
    got = rec.get("circular_speed", {}).get("B25.8", {}).get("0.01")
    assert got is not None and abs(got["threshold_m"] - h_star) < 1e-3
    text = record("DR-0029")
    assert "90 185.09 m" in text
    assert not re.search(r"κ = 0\.01 admits h_f ≥ 90 km", text)


def test_f2_p1_admissible_stress_input_leaves_the_domain():
    """The reviewer's input satisfies both P1 clauses yet puts a stage at -28 km."""
    hf, b = 21_500.0, 1e9
    r = np.array([m.A_WGS84 + 22_000.0, 0.0, 0.0])
    v = np.array([-10_000.0, 0.0, 0.0])
    assert m.A_WGS84 - m.B_WGS84 < hf < m.geodetic_iterative(r)[1]
    assert lam_dt_circular(hf, b) <= 0.01
    assert 0.5 * float(v @ v) - m.MU / float(np.linalg.norm(r)) < 0.0  # bound
    y0 = np.concatenate([r, v, [b * 2.2 * 15.0]])
    with pytest.raises(m.OutsideDomainError):
        m.rk4_step(m.rhs(J2_DRAG), 0.0, y0, DT)


def test_f2_records_do_not_claim_p1_is_sufficient():
    claims = (
        r"leaves every valid run unchanged",
        r"termination always precedes `impact`",
        r"`reentry` and `impact` cannot both hold at one tick",
        r"it can never fire first for a committed state",
    )
    for name in RECORDS:
        for c in claims:
            assert not re.search(c, record(name)), (name, c)
    assert re.search(r"necessary,? (but )?not sufficient", record("DR-0029"))


def test_f2_bound_speed_covers_the_eccentric_retrograde_counterexample():
    import t0_termination as tt

    h = 90_185.09
    rn = m.A_WGS84 + h
    vrel = math.sqrt(m.MU / rn) * math.sqrt(1.9) + m.OMEGA_E * rn  # e 0.9, retrograde
    assert m.density(h) * vrel * DT / B_V1 > 0.01  # the circular proxy admits it
    assert tt.vrel_bound(h) >= vrel


# ------------------------------------------------------------------- M3T0-F3
def test_f3_inward_stage_is_the_input_of_k3():
    r, v = m.circular_state(180e3, 51.6)
    stages: list = []
    m.rk4_step(m.rhs(J2_DRAG), 0.0, np.r_[r, v, 850.0], DT, stages)
    dh = [m.geodetic_iterative(s.r)[1] - 180e3 for s in stages]  # inputs of k2, k3, k4
    assert dh[0] > 100.0 and dh[1] < -100.0 and abs(dh[2]) < 2.0
    for name in RECORDS:
        assert not re.search(r"second (RK4 )?stage", record(name), re.IGNORECASE), name
    for name in ("DR-0029", "VAL-0019"):
        assert "k3" in record(name), name


# ------------------------------------------------------------------- M3T0-F4
def test_f4_quoted_m3_form_residual_matches_the_committed_result():
    value = results("gmat")["regression_m3_form"]["metrics"]["gmat_vs_kepler_position_error_max_m"]
    quoted = f"{value:.2e}".replace("e-06", "e-6")
    assert quoted == "6.95e-6"
    for name in ("DR-0029", "VAL-0019"):
        text = record(name)
        assert "4.86e-6" not in text, name
        assert quoted in text, name
