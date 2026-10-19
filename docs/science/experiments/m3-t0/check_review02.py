"""Regression checks for the M3 T0 Review 02 findings M3T0-R2-F1 ... F3 and IM-1 (research only).

R2-F3 found that `check_review01.py` only read stored values: replacing the sweep and the
stage floors with zeros passed it. Every check here therefore recomputes the quantity it
protects, independently of the experiment scripts where a separate implementation is
possible, and compares it with what the result files and the records claim:
- the missed-crossing sweep: coverage of the declared matrix, the stored dip at its stored
  location, the stored dip as an upper envelope of other sampling phases, and the certified
  two-body bound by a second maximisation method;
- the between-sample extremum that makes the perturbed values estimates (R2-F1);
- the stage-domain floors: a second implementation of the derivation, the Review 02
  counterexample, adversarial drag points, and RK4 steps from bound states at the floors
  (near-escape, retrograde equatorial, straight down) in the fail-closed model (R2-F2);
- result provenance (a rerun of `t0_termination.py` must reproduce the committed JSON byte
  for byte) and units;
- the IM-1 axis-fit residual from the committed GMAT report.

`mutation_check_review02.py` corrupts the result files and the scripts and shows that these
checks fail for each corruption and pass on the unmodified tree.

Not collected by the project test suite (pytest `testpaths = ["tests"]`). Run explicitly:
  uv run --no-sync pytest -q docs/science/experiments/m3-t0/check_review02.py
Correction logs fenced by `<!-- review02-correction-log -->` ... `<!-- /review02-correction-log
-->` (and the Review 01 fences) describe superseded wording and are excluded from the wording
checks.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize_scalar

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t0_model as m  # noqa: E402
import t0_oracle as o  # noqa: E402

ROOT = HERE.parents[3]
DT = 10.0
MASS = 850.0
B_V1 = MASS / (2.2 * 15.0)
J2_DRAG = m.Config(j2=m.J2_FROM_C20, drag=m.Drag(cd=2.2, area_m2=15.0))
PHYSICS = {"kepler": m.Config(), "j2drag": J2_DRAG}
# The declared sweep (DR-0029 P2): spherical perigee/apogee km, inclination deg.
ORBITS = (
    (250.0, 250.0, 0.0),
    (250.0, 250.0, 51.6),
    (250.0, 250.0, 97.0),
    (180.0, 180.0, 51.6),
    (250.0, 400.0, 51.6),
    (250.0, 800.0, 51.6),
    (250.0, 800.0, 97.0),
    (180.0, 800.0, 51.6),
    (250.0, 2000.0, 51.6),
)
FENCES = re.compile(
    r"<!-- (review01|review02|review03)-correction-log -->.*?<!-- /\1-correction-log -->",
    re.DOTALL,
)


def record(name: str) -> str:
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
    return FENCES.sub("", text)


RECORDS = ("DR-0029", "VAL-0019", "report", "matrix", "README")


def results(name: str) -> dict:
    path = HERE / f"t0_{name}_results.json"
    return json.loads(path.read_text()) if path.exists() else {}


def sweep_rows() -> list[dict]:
    return results("termination").get("missed_crossing", {}).get("sweep", [])


def floors() -> dict[str, float]:
    rows = results("termination").get("sufficient_stage_condition", {}).get("rows", [])
    return {r["vehicle"]: r["h_f_sufficient_at_least_m"] for r in rows}


# ------------------------------------------------------- independent reimplementations
def solve(cfg: m.Config, y0: np.ndarray, t_end: float):
    sol = solve_ivp(
        m.rhs(cfg), (0.0, t_end), y0, method="DOP853", rtol=1e-13, atol=1e-9, dense_output=True
    )
    assert sol.status == 0, sol.message
    return sol.sol


def height(r: np.ndarray) -> float:
    return m.geodetic_iterative(r)[1]


def elements(hp_km: float, ha_km: float) -> tuple[float, float]:
    rp, ra = m.A_WGS84 + hp_km * 1e3, m.A_WGS84 + ha_km * 1e3
    return (rp + ra) / 2.0, (ra - rp) / (ra + rp)


def min_normal_cos() -> float:
    """cos of the largest normal-radius angle, by a dense scan of geodetic latitude (the
    angle is phi - atan((1 - e^2) tan phi), maximal near 45 deg; the scan is refined)."""
    f = 1.0 - m.E2_WGS84
    phis = np.linspace(0.0, math.pi / 2 - 1e-6, 200_001)
    ang = phis - np.arctan(f * np.tan(phis))
    k = int(ang.argmax())
    res = minimize_scalar(
        lambda p: -(p - math.atan(f * math.tan(p))),
        bounds=(phis[k - 1], phis[k + 1]),
        method="bounded",
        options={"xatol": 1e-15},
    )
    return math.cos(-res.fun)


def two_body_bound_independent(sma: float, ecc: float) -> float:
    """dt^2/8 max(0, max g) on [r_p, r_a], g as in the derivation, maximised by brentq on
    an analytic g' over sign changes on a 4001-point grid (not the cubic)."""
    rcurv = m.B_WGS84**2 / m.A_WGS84
    kk = min_normal_cos()

    def g(r: float) -> float:
        return m.MU * (2.0 / r - 1.0 / sma) / (r - m.A_WGS84 + rcurv) - m.MU * kk / r**2

    def dg(r: float) -> float:
        d = r - m.A_WGS84 + rcurv
        return m.MU * (-2.0 / r**2 / d - (2.0 / r - 1.0 / sma) / d**2) + 2.0 * m.MU * kk / r**3

    rp, ra = sma * (1 - ecc), sma * (1 + ecc)
    cands = [rp, ra]
    if ra > rp:
        grid = np.linspace(rp, ra, 4001)
        vals = [dg(float(x)) for x in grid]
        for i in range(len(grid) - 1):
            if vals[i] == 0.0:
                cands.append(float(grid[i]))
            elif vals[i] * vals[i + 1] < 0.0:
                cands.append(brentq(dg, float(grid[i]), float(grid[i + 1]), xtol=1e-6))
    return max(0.0, max(g(r) for r in cands)) * DT**2 / 8


def dip_at(sol, ta: float) -> float:
    """Dip below the lower committed height on [ta, ta + dt], committed states taken on the
    numerical trajectory; the minimum is found by a 0.01 s scan plus bounded refinement."""
    tt = np.linspace(ta, ta + DT, 1001)
    hh = [height(sol(x)[:3]) for x in tt]
    k = int(np.argmin(hh))
    lo, hi = tt[max(k - 1, 0)], tt[min(k + 1, len(tt) - 1)]
    res = minimize_scalar(
        lambda x: height(sol(x)[:3]), bounds=(lo, hi), method="bounded", options={"xatol": 1e-9}
    )
    return min(hh[0], hh[-1]) - min(float(res.fun), min(hh))


def sampled_dips(sol, t_end: float, phase: float) -> float:
    """Largest dip over all steps at one sampling phase, h sampled every 0.05 s."""
    t = np.arange(0.0, t_end + 1e-9, 0.05)
    y = sol(t)[:3]
    hh = np.array([height(y[:, j]) for j in range(y.shape[1])])
    i0, per = round(phase / 0.05), 200
    n = (len(hh) - 1 - i0) // per
    best = 0.0
    for k in range(n):
        seg = hh[i0 + k * per : i0 + (k + 1) * per + 1]
        best = max(best, min(seg[0], seg[-1]) - seg.min())
    return best


SOLUTIONS: dict = {}


def orbit_solution(row: dict):
    key = (row["physics"], row["perigee_km"], row["apogee_km"], row["inclination_deg"])
    if key not in SOLUTIONS:
        sma, _ = elements(row["perigee_km"], row["apogee_km"])
        period = 2 * math.pi * math.sqrt(sma**3 / m.MU)
        r0, v0 = m.perigee_state(
            row["perigee_km"] * 1e3, row["apogee_km"] * 1e3, row["inclination_deg"]
        )
        t_end = 2 * period + 2 * DT
        SOLUTIONS[key] = (solve(PHYSICS[row["physics"]], np.r_[r0, v0, MASS], t_end), t_end)
    return SOLUTIONS[key]


G_BOUND = (1.0 + 3.0 * m.J2_FROM_C20 * (m.A_WGS84 / m.B_WGS84) ** 2) * m.MU / m.B_WGS84**2


def envelope(low: float, s: float, b: float) -> float:
    """sup over h >= low of rho(h) (s + omega (a + h))^2 / (2 b): written separately from
    `t0_termination.drag_envelope`. Every band is decreasing (checked by
    `test_r2f2_drag_factor_decreases_inside_every_band`), so the candidates are low and the
    band bases above it."""
    if math.isinf(b):
        return 0.0
    hs = [low] + [band.base_km * 1000.0 for band in m.TABLE if band.base_km * 1000.0 > low]
    return max(m.density(h) * (s + m.OMEGA_E * (m.A_WGS84 + h)) ** 2 for h in hs) / (2.0 * b)


def stage_bounds(h0: float, b: float) -> tuple[float, float, float]:
    v = math.sqrt(2.0 * m.MU / (m.B_WGS84 + h0))
    a0 = G_BOUND + envelope(h0, v, b)
    l2 = h0 - DT / 2 * v
    l3 = h0 - DT / 2 * (v + DT / 2 * a0)
    if l2 <= 0.0:
        return l2, l3, -math.inf
    a2 = G_BOUND + envelope(l2, v + DT / 2 * a0, b)
    return l2, l3, h0 - DT * (v + DT / 2 * a2)


def floor_independent(b: float) -> float:
    """The root of min(L2, L3, L4) = 0, by bisection (not brentq)."""
    lo, hi = 1.0, 2.0e6
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if min(stage_bounds(mid, b)) > 0.0:
            hi = mid
        else:
            lo = mid
    return hi


VEHICLES = {"B25.8": B_V1, "B100": 100.0, "drag-free limit": math.inf}


# --------------------------------------------------------------------------- R2-F1
def test_r2f1_sweep_covers_the_declared_matrix():
    mc = results("termination").get("missed_crossing", {})
    got = sorted(
        (r["physics"], r["perigee_km"], r["apogee_km"], r["inclination_deg"]) for r in sweep_rows()
    )
    want = sorted((p, *o) for o in ORBITS for p in PHYSICS)
    assert got == want
    assert mc["sweep_phases_s"] == [k * 0.25 for k in range(40)]
    assert mc["sweep_sample_s"] == 0.05 and mc["dt_s"] == DT
    for r in sweep_rows():
        assert r["phase_s"] in mc["sweep_phases_s"], r


@pytest.mark.parametrize("idx", range(len(ORBITS) * 2))
def test_r2f1_stored_dip_is_recomputed_at_its_location_and_bounds_other_phases(idx):
    rows = sweep_rows()
    assert len(rows) == len(ORBITS) * 2
    row = rows[idx]
    sol, t_end = orbit_solution(row)
    assert abs(dip_at(sol, row["step_start_s"]) - row["max_dip_m"]) < 1e-5, row
    assert (row["step_start_s"] - row["phase_s"]) / DT == pytest.approx(
        round((row["step_start_s"] - row["phase_s"]) / DT), abs=1e-9
    )
    for phase in (0.0, 2.5, 5.0, 7.5, row["phase_s"]):
        assert sampled_dips(sol, t_end, phase) <= row["max_dip_m"] + 1e-6, (row, phase)
    if row["physics"] == "kepler":
        sma, ecc = elements(row["perigee_km"], row["apogee_km"])
        assert row["bound_m"] == pytest.approx(two_body_bound_independent(sma, ecc), rel=1e-12)
        assert row["max_dip_m"] <= row["bound_m"]


def test_r2f1_certified_bound_function_matches_a_second_maximisation():
    import t0_termination as tt

    for hp in (80.0, 150.0, 250.0):
        for ecc in (0.0, 0.005, 0.01, 0.04, 0.1, 0.3):
            rp = m.A_WGS84 + hp * 1e3
            sma = rp / (1 - ecc)
            assert tt.two_body_domain_bound(sma, ecc)["bound_m"] == pytest.approx(
                two_body_bound_independent(sma, ecc), rel=1e-12
            )
    table = results("termination")["missed_crossing"]["two_body_domain_bound_table"]
    assert len(table) == 18
    for row in table:
        sma = (m.A_WGS84 + row["perigee_km"] * 1e3) / (1 - row["eccentricity"])
        assert row["bound_m"] == pytest.approx(
            two_body_bound_independent(sma, row["eccentricity"]), rel=1e-12
        )


def test_r2f1_two_body_maximum_is_at_an_endpoint_on_a_domain_scan():
    """Why dropping the stationary points from `two_body_domain_bound` is an equivalent
    mutant (mutation_check_review02.py): on a 60 x 60 scan of bound orbits (perigee height
    1 m ... 5000 km, e 0 ... 0.99) no interior stationary point of g exceeds both endpoints.
    The certified maximisation keeps the stationary points; this is an observation, not a
    proof that g has no interior maximum."""
    import t0_termination as tt

    c, k = m.A_WGS84 - m.B_WGS84**2 / m.A_WGS84, math.cos(tt.DELTA_MAX)
    for hp in np.linspace(1.0, 5.0e6, 60):
        for ecc in np.linspace(0.0, 0.99, 60):
            rp = m.A_WGS84 + hp
            sma = rp / (1 - ecc)
            ra = sma * (1 + ecc)

            def g(r: float, sma: float = sma) -> float:
                return m.MU * (2 / r - 1 / sma) / (r - c) - m.MU * k / r**2

            best = tt.two_body_domain_bound(sma, ecc)["sup_hddot_mps2"]
            ends = max(g(sma * (1 - ecc)), g(ra))  # r_p as the module computes it
            assert best == pytest.approx(ends, rel=1e-12, abs=1e-15), (hp, ecc)


def test_r2f1_between_sample_extremum_exceeds_the_sampled_maximum():
    """The reviewer's case: 180 km circular, 51.6 deg, J2 + drag. U refined between the
    0.25 s samples exceeds their maximum, so dt^2/8 x (sampled max) is not a bound."""
    import t0_termination as tt

    row = next(
        r
        for r in sweep_rows()
        if r["physics"] == "j2drag" and r["perigee_km"] == r["apogee_km"] == 180.0
    )
    sol, t_end = orbit_solution(row)

    def u(t: float) -> float:
        y = sol(t)
        return tt.hddot_upper(y[:3], y[3:6], m.acceleration(J2_DRAG, t, y[:3], y[3:6], y[6]))

    ts = np.arange(0.0, t_end + 1e-9, 0.25)
    us = np.array([u(float(t)) for t in ts])
    assert float(us.max()) == pytest.approx(row["sampled_max_hddot_upper_mps2"], rel=1e-9)
    fine = np.linspace(2645.0, 2645.5, 5001)
    assert max(u(float(t)) for t in fine) > float(us.max())
    assert row["refined_max_hddot_upper_mps2"] > row["sampled_max_hddot_upper_mps2"]


def test_r2f1_perturbed_values_are_labelled_estimates_not_bounds():
    mc = results("termination")["missed_crossing"]
    perturbed = [r for r in sweep_rows() if r["physics"] == "j2drag"]
    perturbed += [c for k, c in mc["cases"].items() if k.startswith("j2drag")]
    assert len(perturbed) == len(ORBITS) + 2
    for r in perturbed:
        assert "bound_m" not in r and "bound_holds" not in r, r
        assert "not a bound" in r["estimate_kind"], r
    for r in [*sweep_rows(), *mc["cases"].values()]:
        if "bound_m" in r:
            assert r["bound_kind"].startswith("certified: two-body"), r
    assert "all_bounds_hold" not in mc


def test_r2f1_records_distinguish_certified_bounds_from_estimates():
    for name in RECORDS:
        text = record(name)
        assert not re.search(r"It never exceeds the bound", text), name
        assert not re.search(r"J2 \+ drag; bound 5\.11 m", text), name
    for name in ("DR-0029", "VAL-0019"):
        assert "sampled estimate" in record(name), name
        assert "no certified bound" in record(name), name


# --------------------------------------------------------------------------- R2-F2
def test_r2f2_review02_counterexample_is_covered():
    import t0_termination as tt

    low, s, h = 79_999.9, 11_000.0, 80_000.0
    r = np.array([m.A_WGS84 + h, 0.0, 0.0])
    v = np.array([0.0, -s, 0.0])
    nodrag = m.Config(j2=m.J2_FROM_C20)
    actual = float(
        np.linalg.norm(
            m.acceleration(J2_DRAG, 0, r, v, MASS) - m.acceleration(nodrag, 0, r, v, MASS)
        )
    )
    assert actual == pytest.approx(48.65837703993666, rel=1e-12)
    for env in (envelope(low, s, B_V1), tt.drag_envelope(low, s, B_V1)):
        assert env >= actual * (1 - 1e-13)  # rounding allowance only
    stored = results("termination")["sufficient_stage_condition"]["review02_counterexample"]
    assert stored["corrected_covers"] and not stored["superseded_covers"]


def test_r2f2_drag_factor_decreases_inside_every_band():
    """Premise of both envelope implementations: rho(h) (s + omega (a + h))^2 decreases
    inside every band, for every speed (checked on a 1 m grid near each band's start and
    proved for a > 2 H; here a / (2 H) >= 11.9)."""
    assert all(2.0 * band.scale_km * 1e3 < m.A_WGS84 / 10 for band in m.TABLE)
    for i, band in enumerate(m.TABLE):
        lo = band.base_km * 1e3
        hi = m.TABLE[i + 1].base_km * 1e3 if i + 1 < len(m.TABLE) else lo + 3.0e6
        for s in (0.0, 8_000.0, 11_200.0, 20_000.0):
            hs = np.concatenate([lo + np.arange(0.0, 50.0), np.linspace(lo, hi, 2001)[:-1]])
            hs.sort()
            f = [m.density(h) * (s + m.OMEGA_E * (m.A_WGS84 + h)) ** 2 for h in hs]
            assert all(x >= y for x, y in itertools.pairwise(f)), (band, s)


def test_r2f2_envelope_bounds_adversarial_drag_points():
    """Points above the lower bound, at band bases, just below upward jumps, at the equator
    against the rotation (the largest |v_rel|), and above h0. Corrected after Review 03
    M3T0-R3-F1: the expected bound is taken at the point's true height from the
    independent oracle (`t0_oracle`), never at the model's own computed height, and the
    measured drag is the model's drag vector itself (no difference of accelerations, so
    no measurement allowance)."""
    import t0_termination as tt

    rng = np.random.default_rng(7)
    bases = [band.base_km * 1e3 for band in m.TABLE]
    lows = [x - d for x in bases[1:12] for d in (1e-6, 0.1, 50.0)] + list(
        rng.uniform(0.0, 300e3, 60)
    )
    for low in lows:
        for s in (100.0, 7_800.0, 11_100.0):
            env = tt.drag_envelope(low, s, B_V1)
            # the corrected envelope includes the exact-height one and widens it only by
            # the height-error allowance (< 1e-8 m) and the rounding factor F_D
            assert envelope(low, s, B_V1) <= env
            assert env <= envelope(max(low - 1e-8, 0.0), s, B_V1) * (1 + 1e-12)
            hs = [low, *[x for x in bases if low < x < low + 60e3], low + rng.uniform(0, 60e3)]
            for h in hs:
                for lat, sign in ((0.0, -1.0), (rng.uniform(-1.4, 1.4), rng.choice([-1, 1]))):
                    lon = rng.uniform(-math.pi, math.pi)
                    r = m.geodetic_to_cartesian(lat, lon, h)
                    east = np.array([-math.sin(lon), math.cos(lon), 0.0])
                    v = sign * s * east
                    a = tt.model_drag(r, v, MASS)
                    true_h = tt._dn(o.true_height(r))
                    bound = tt.drag_envelope(min(low, true_h), s, B_V1)
                    assert a <= bound, (low, s, h, true_h, lat)


@pytest.mark.parametrize("vehicle", sorted(VEHICLES))
def test_r2f2_floors_recomputed_by_a_second_implementation(vehicle):
    got = floors()
    assert set(got) == set(VEHICLES)
    ref = floor_independent(VEHICLES[vehicle])
    assert got[vehicle] == pytest.approx(ref, abs=1e-3)
    assert 1.0e5 < got[vehicle] < 2.0e5  # metres, not km
    assert min(stage_bounds(got[vehicle] + 1.0, VEHICLES[vehicle])) > 0.0
    assert min(stage_bounds(got[vehicle] - 1.0, VEHICLES[vehicle])) < 0.0
    hs = np.linspace(got[vehicle] - 50e3, got[vehicle] + 500e3, 400)
    need = [-min(stage_bounds(float(h), VEHICLES[vehicle])) for h in hs]
    assert all(x > y for x, y in itertools.pairwise(need))  # monotone (proved)


@pytest.mark.parametrize("vehicle", sorted(VEHICLES))
def test_r2f2_rk4_steps_from_bound_states_at_the_floor_stay_in_the_domain(vehicle):
    """Fail-closed model: any stage below 0 m raises OutsideDomainError."""
    b = VEHICLES[vehicle]
    floor = floors()[vehicle]
    cfg = m.Config(j2=m.J2_FROM_C20) if math.isinf(b) else J2_DRAG
    mass = MASS if math.isinf(b) else b * 2.2 * 15.0
    rng = np.random.default_rng(99)
    lowest = math.inf
    for i in range(300):
        h0 = floor * (1 + 1e-12) + (0.0 if i < 30 else rng.uniform(0.0, 5_000.0))
        lat = 0.0 if i % 3 == 1 else rng.uniform(-1.5, 1.5)
        lon = rng.uniform(-math.pi, math.pi)
        r0 = m.geodetic_to_cartesian(lat, lon, h0)
        vesc = math.sqrt(2.0 * m.MU / float(np.linalg.norm(r0)))
        speed = vesc * (1.0 - 10.0 ** rng.uniform(-7.0, -2.0))
        if i % 3 == 0:
            d = rng.normal(size=3)
        elif i % 3 == 1:
            d = np.array([math.sin(lon), -math.cos(lon), 0.0])
        else:
            d = -np.array(
                [math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat)]
            )
        v0 = speed * d / np.linalg.norm(d)
        assert 0.5 * float(v0 @ v0) - m.MU / float(np.linalg.norm(r0)) < 0.0
        stages: list = []
        m.rk4_step(m.rhs(cfg), 0.0, np.r_[r0, v0, mass], DT, stages)
        lowest = min(lowest, *(height(st.r) for st in stages))
    assert lowest > 0.0


def test_r2f2_records_quote_the_recomputed_floors_and_the_corrected_derivation():
    text = record("DR-0029")
    for vehicle in VEHICLES:
        quoted = f"{floors()[vehicle]:,.2f}".replace(",", " ")
        assert quoted + " m" in text, (vehicle, quoted)
    for name in RECORDS:
        assert "drag at each stage's lower height bound" not in record(name), name


# ---------------------------------------------------------------- provenance and units
def test_provenance_rerun_reproduces_the_committed_termination_results(tmp_path):
    out = tmp_path / "t0_termination_results.json"
    subprocess.run(
        [sys.executable, str(HERE / "t0_termination.py"), str(out)],
        cwd=HERE,
        check=True,
        capture_output=True,
    )
    assert out.read_bytes() == (HERE / "t0_termination_results.json").read_bytes()


def test_units_and_declared_constants():
    d = results("termination")
    sc = d["sufficient_stage_condition"]
    assert sc["dt_s"] == DT and sc["lower_edge_m"] == 0.0
    assert sc["gravity_bound_mps2"] == pytest.approx(G_BOUND, rel=1e-15)
    assert {r["vehicle"]: r["B_kg_per_m2"] for r in sc["rows"]} == {
        "B25.8": B_V1,
        "B100": 100.0,
        "drag-free limit": None,
    }
    assert d["missed_crossing"]["b2_over_a_m"] == pytest.approx(m.B_WGS84**2 / m.A_WGS84, rel=1e-15)
    for r in sweep_rows():
        assert 0.0 <= r["max_dip_m"] < 20.0, r  # metres


# --------------------------------------------------------------------------------- IM-1
def axis_fit_rms(cols: tuple[int, ...]) -> float:
    """Written separately from t0_axis_ablation.py: z_EF = u(t) . r_TOE least squares."""
    data = []
    path = HERE / "gmat_runs/axis_probe__m1_two_body_report.txt"
    for line in path.read_text().splitlines():
        if line and not line.startswith("ElapsedS"):
            data.append([float(x) for x in line.split()])
    d = np.array(data)
    t = np.r_[d[:, 0], d[:, 0]]
    r = np.r_[d[:, 1:4], d[:, 5:8]]
    z = np.r_[d[:, 4], d[:, 8]]
    s, th = t / d[-1, 0], m.OMEGA_E * t
    basis = [np.ones_like(t), s, s * s, np.cos(th), np.sin(th)]
    a = np.column_stack([r[:, j] * basis[k] for k in cols for j in range(3)])
    x, *_ = np.linalg.lstsq(a, z, rcond=None)
    return float(np.sqrt(np.mean(((z - a @ x) * 1000.0) ** 2)))


def test_im1_axis_fit_residual_is_reproduced_from_the_committed_gmat_report():
    res = results("axis_ablation")
    tol = res["tolerance_m"]
    assert tol == 1e-6
    report = HERE / res["data_file"]
    meta = json.loads((HERE / "gmat_runs/axis_probe__metadata.json").read_text())
    digest = hashlib.sha256(report.read_bytes()).hexdigest()
    assert digest == res["data_sha256"] == meta["reports_sha256"]["m1_two_body_report.txt"]
    full, quad = axis_fit_rms((0, 1, 2, 3, 4)), axis_fit_rms((0, 1, 2))
    assert abs(full - results("gmat")["axis"]["fit_rms_residual_m"]) <= tol
    assert abs(full - res["fits"]["full"]["rms_residual_m"]) <= tol
    assert abs(quad - res["fits"]["quadratic_only"]["rms_residual_m"]) <= tol
    assert quad == pytest.approx(0.9856650955520649, abs=tol)
    assert res["fits"]["quadratic_only"]["equations"] == 1792


def test_im1_records_name_the_quantity_and_the_procedure():
    text = record("DR-0029")
    assert "t0_axis_ablation.py" in text
    assert re.search(r"0\.986 m RMS", text)
    assert "DR-0028" in text
