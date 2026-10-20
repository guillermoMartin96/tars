"""Regression checks for the M3 T0 Review 05 findings M3T0-R5-F1 and R5-F2 (research only).

R5-F1: the drag envelope took the vehicle as a ballistic coefficient b and bounded cd area
/ mass by phi_B / b, a relative-only rounding of the conversion between b and the mass the
model uses. With a subnormal b the conversion's rounding is absolute: b = 2^-1074 =
fl(17 x 2^-1074 / 33) gave drag 1.94 times the envelope at 180 000 km, and mass = fl(fl(b
2.2) 15) = 30 x 2^-1074 gave 1.10 times. The correction (`t0_termination.
inverse_ballistic_bound`, E4a) bounds cd area / mass for either construction with the
absolute error of every underflowing rounding; the envelope uses b_R = phi_B / R <= b.
E4b: a vehicle with cd area <= 2^-1075 (C1 then gives b = +inf) has exactly zero force.

R5-F2: 0.983 was described as the largest observed ratio of model drag to envelope "in the
subnormal regime". It is the maximum over the coefficient-rounding subset only; the
committed transition scan reaches 0.99999999999886 at subnormal densities.

Expected values come from exact rational arithmetic on the binary64 inputs (the rounding
intervals of round-to-nearest) and from `t0_oracle` heights, never from the envelope
implementation. Each check states the defect it detects. `mutation_check_review02.py`
runs these checks on corrupted copies. Not collected by the project test suite. Run:
  uv run --no-sync pytest -q docs/science/experiments/m3-t0/check_review05.py
"""

from __future__ import annotations

import math
import re
import sys
from decimal import Decimal, getcontext, localcontext
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_review04 as c4  # noqa: E402
import t0_model as m  # noqa: E402
import t0_oracle as o  # noqa: E402
import t0_termination as tt  # noqa: E402

D = Decimal
getcontext().prec = 60
TINY = 2.0**-1074  # the smallest positive binary64
ETA0 = Fraction(1, 2**1075)
U = Fraction(1, 2**53)
CD, AREA = c4.CD, c4.AREA
R5_R = np.array([186_378_137.0, 0.0, 0.0])  # true height exactly 180 000 000 m
R5_LOW = 180_000_000.0
PHI = Fraction(tt.FP["phi_B"])  # the published relative factor (checked in check_review04)


# ------------------------------------------------------------- independent helpers
def model_drag_norm(r, v, mass: float, cd: float, area: float) -> D:
    """Exact norm of the model's binary64 drag vector for any vehicle (mu = 0, J2 off)."""
    cfg = m.Config(mu=0.0, drag=m.Drag(cd=cd, area_m2=area))
    vec = m.acceleration(cfg, 0.0, r, v, mass)
    with localcontext() as c:
        c.prec = 60
        return sum(D(float(x)) ** 2 for x in vec).sqrt()


def pred(x: float) -> float:
    return math.nextafter(x, 0.0)


def lower_rounding_end(b: float) -> Fraction:
    """Every real that rounds to the positive binary64 b is >= (pred(b) + b) / 2."""
    return (Fraction(pred(b)) + Fraction(b)) / 2


def c1_tight(b: float, cd: float, area: float) -> Fraction | None:
    """sup of cd area / mass over masses with fl(mass / fl(cd area)) = b (C1): the exact
    product over the host's binary64 P (IEEE, A-FP-1) and the lower end of b's rounding
    interval. None if fl(cd area) = 0 (C1 then cannot give a finite b)."""
    p = cd * area
    if p == 0.0:
        return None
    return Fraction(cd) * Fraction(area) / Fraction(p) / lower_rounding_end(b)


def c2_exact(b: float, cd: float, area: float) -> tuple[float, Fraction] | None:
    """The C2 vehicle mass = fl(fl(b cd) area) and its exact cd area / mass."""
    mass = (b * cd) * area
    if not 0.0 < mass < math.inf:
        return None
    return mass, Fraction(cd) * Fraction(area) / Fraction(mass)


def c1_smallest_mass(b: float, cd: float, area: float) -> float | None:
    """The smallest binary64 mass with fl(mass / fl(cd area)) = b: the C1 vehicle with the
    largest cd area / mass for this b."""
    p = cd * area
    if p == 0.0:
        return None
    x = float(lower_rounding_end(b) * Fraction(p))
    while x / p < b:
        x = math.nextafter(x, math.inf)
    while x > TINY and pred(x) / p == b:
        x = pred(x)
    if x / p != b or not 0.0 < x < math.inf:
        return None
    return x


def ratio_second(b: float, cd: float, area: float) -> Fraction:
    """E4a written out again from the derivation (second implementation)."""
    bq, cq, aq = Fraction(b), Fraction(cd), Fraction(area)
    two = 2 * ETA0
    prod = cq * aq
    r1 = Fraction(0)
    if prod > ETA0:
        over_p = max(1 / (1 - U), prod / (prod - ETA0))
        over_p = min(over_p, prod / two)
        r1 = over_p * max((1 + U) / bq, 1 / (bq - ETA0))
    q = max(two, min(bq * cq * (1 - U), bq * cq - ETA0))
    mm = max(two, min(q * aq * (1 - U), q * aq - ETA0))
    return max(PHI / bq, r1, prod / mm)


def env_second(low: Fraction, s: Fraction, ratio: Fraction, cd: float, area: float, c: dict):
    """The corrected envelope with cd area / mass <= ratio (relative part over the oracle's
    table and band rule, plus the absolute part at S_max), from `check_review04`'s
    constants. ratio = phi_B / b is the superseded Review 04 envelope."""
    ell = max((1 - c["alpha_sel"]) * low - c["beta_sel_m"], Fraction(0))
    best = Fraction(0)
    with localcontext() as ctx:
        ctx.prec = 70
        for h in [ell] + [Fraction(row[0]) for row in o.TABLE if Fraction(row[0]) > ell]:
            base, rho0, scale = o.TABLE[o.band(D(h.numerator) / D(h.denominator))]
            x = (h - Fraction(base)) / Fraction(scale) * (1 - c["theta_x"])
            ex = Fraction((-(D(x.numerator) / D(x.denominator))).exp()) * (1 + Fraction(1, 10**50))
            rad = Fraction(m.A_WGS84) + (h + c["beta_sel_m"]) / (1 - c["alpha_sel"])
            vr = s + Fraction(m.OMEGA_E) * rad
            best = max(best, Fraction(rho0) * ex * vr * vr)
    phi, eta0 = c["phi_B"], c["eta0"]
    smax = s + Fraction(m.OMEGA_E) * (
        Fraction(m.A_WGS84) + (c["h_zero_m"] + c["beta_sel_m"]) / (1 - c["alpha_sel"])
    )
    cq, aq = Fraction(cd), Fraction(area)
    w = eta0 * (1 + ratio * ((1 + U) ** 3 + (1 + U) ** 2 / cq + (1 + U) / (cq * aq)))
    absolute = (c["F_A"] / phi * ratio * c["N_rho"] / 2 + c["K_W"] * w) * smax**2
    absolute += (1 + U) ** 3 * eta0 * smax + 2 * eta0
    return best * c["F_D"] / phi * ratio / 2 + absolute


CONST = c4.constants_second(tt.LIBM_ULP)
SUBNORMAL_B = [k * TINY for k in (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 1000, 2**30, 2**51 + 1)]
NORMAL_B = [2.0**-1022, 1e-300, 1e-10, 1.0, tt.B_V1, 100.0, 1e10, 1e300]
SHAPES = [(CD, AREA), (1.0, 1.0), (0.5, 3.0), (2.2, 1e-3)]
# products, intermediate products and masses that are subnormal for a normal b
SUBNORMAL_PRODUCTS = [(2.2, 2 * TINY), (2.2, 7 * TINY), (1e-160, 1e-160), (1e-300, 1e-15)]
SUBNORMAL_Q = [(1e-300, 100.0)]  # b cd subnormal for b <= 2e-8


def vehicles():
    """(label, construction, b, mass, cd, area): C1 with the smallest mass for b, and C2."""
    out = []
    for cd, area in SHAPES + SUBNORMAL_PRODUCTS + SUBNORMAL_Q:
        bs = SUBNORMAL_B + NORMAL_B
        if (cd, area) in SUBNORMAL_Q:
            bs = bs + [(k + 0.45) * 2.0**-1074 / cd for k in range(1, 40)]
        for b in bs:
            mass = c1_smallest_mass(b, cd, area)
            if mass is not None:
                out.append((f"C1 b={b:.3e} cd={cd:g} A={area:g}", "C1", b, mass, cd, area))
            two = c2_exact(b, cd, area)
            if two is not None:
                out.append((f"C2 b={b:.3e} cd={cd:g} A={area:g}", "C2", b, two[0], cd, area))
    return out


VEHICLE_GRID = vehicles()


# ------------------------------------------------------------- R5-F1 counterexamples
@pytest.mark.parametrize(
    "mass_units, construction, reviewer_ratio",
    [(17, "C1", D("1.94117647058593")), (30, "C2", D("1.09999999999869"))],
)
def test_r5f1_review05_counterexamples_are_covered(mass_units, construction, reviewer_ratio):
    """Detects: the conversion between b and mass bounded by a relative factor only (the
    R5-F1 defect), or its absolute term missing or too small."""
    mass = mass_units * TINY
    b = mass / (CD * AREA) if construction == "C1" else TINY
    assert b == TINY
    if construction == "C2":
        assert (b * CD) * AREA == mass  # the second construction gives the same pair
    assert o.true_height(R5_R) == D(R5_LOW)  # exact: the foot point is (a, 0, 0)
    assert m.geodetic_iterative(R5_R)[1] == R5_LOW
    v = np.zeros(3)
    a = model_drag_norm(R5_R, v, mass, CD, AREA)
    exact_ratio = Fraction(CD) * Fraction(AREA) / Fraction(mass)
    assert exact_ratio > PHI / Fraction(b)  # the superseded prerequisite fails
    old = env_second(Fraction(R5_LOW), Fraction(0), PHI / Fraction(b), CD, AREA, CONST)
    assert abs(a / D(old.numerator) * D(old.denominator) - reviewer_ratio) < D("1e-9")
    assert a <= D(tt.drag_envelope(R5_LOW, 0.0, b))  # the correction
    stored = c4.results("termination")["sufficient_stage_condition"]["review05_counterexamples"]
    row = next(x for x in stored if x["construction"] == construction)
    assert row["corrected_covers"] and not row["superseded_covers"]


# ------------------------------------------------------------------ the E4a lemma
def test_r5f1_conversion_bound_holds_for_both_constructions():
    """Detects: an absolute term of E4a missing or too small (the quotient's for subnormal
    b, the product's for subnormal cd area, or C2's for subnormal b cd or mass). Expected
    values: the exact cd area / mass of each constructed vehicle (C2) and the supremum over
    b's rounding interval (C1)."""
    kinds = {"subnormal b": 0, "subnormal P": 0, "subnormal b cd": 0, "beyond phi_B / b": 0}
    for label, kind, b, mass, cd, area in VEHICLE_GRID:
        r = tt.inverse_ballistic_bound(b, cd, area, PHI)
        actual = Fraction(cd) * Fraction(area) / Fraction(mass)
        assert actual <= r, label
        tight = c1_tight(b, cd, area) if kind == "C1" else actual
        assert tight <= r, label
        kinds["subnormal b"] += b < 2.0**-1022
        kinds["subnormal P"] += 0.0 < cd * area < 2.0**-1022
        kinds["subnormal b cd"] += 0.0 < b * cd < 2.0**-1022 <= b
        kinds["beyond phi_B / b"] += actual > PHI / Fraction(b)
    assert min(kinds.values()) >= 10, kinds


def test_r5f1_conversion_bound_recomputed_by_a_second_implementation():
    """Detects: a term of E4a removed, reduced or applied to the wrong construction,
    including terms too small for a force comparison to expose."""
    for label, _, b, _, cd, area in VEHICLE_GRID:
        assert tt.inverse_ballistic_bound(b, cd, area, PHI) == ratio_second(b, cd, area), label


def test_r5f1_dominance_switch_between_relative_and_absolute_terms():
    """Detects: the quotient's absolute term missing, or taking over at the wrong b. For
    the V1 shape (P normal), R1 = (1 / (1 - u)) max((1 + u) / b, 1 / (b - eta0)) exceeds
    phi_B / b exactly when b < b* = c eta0 / (c - 1), c = phi_B (1 - u) (derived here)."""
    c = PHI * (1 - U)
    b_star = c * ETA0 / (c - 1)
    above = tt._up(b_star)
    below = tt._dn(b_star)
    assert below < above
    assert 2.0**-1024 < above < 2.0**-1022  # about 2^-1023: subnormal b
    assert tt.inverse_ballistic_bound(above, CD, AREA, PHI) == PHI / Fraction(above)
    assert tt.envelope_ballistic_coefficient(above, CD, AREA, tt.FP) is above
    assert tt.inverse_ballistic_bound(below, CD, AREA, PHI) > PHI / Fraction(below)
    for b in (below, above, pred(below), math.nextafter(above, 1.0)):
        assert c1_tight(b, CD, AREA) <= tt.inverse_ballistic_bound(b, CD, AREA, PHI)


def test_r5f1_normal_ballistic_coefficients_are_unchanged():
    """Detects: the correction changing the envelope where the conversion is normal (the
    published B 25.8 and B 100 vehicles included), which would move the floors."""
    for b in NORMAL_B[1:]:
        for cd, area in SHAPES:
            assert tt.inverse_ballistic_bound(b, cd, area, PHI) == PHI / Fraction(b), (b, cd)
            assert tt.envelope_ballistic_coefficient(b, cd, area, tt.FP) is b
    for name in ("B25.8", "B100"):
        b = c4.VEHICLES[name]
        assert tt.envelope_ballistic_coefficient(b, CD, AREA, tt.FP) is b
        mass = c4.MASSES[name]
        assert Fraction(CD) * Fraction(AREA) / Fraction(mass) <= PHI / Fraction(b)


# ------------------------------------------------------------ the force comparison
STATES = [
    (np.array([m.A_WGS84 + h, 0.0, 0.0]), s)
    for h in (1.0e8, 1.5e8, 1.8e8, 1.85e8, 1.9e8, 1.917e8)
    for s in (0.0, 2_000.0, 11_000.0)
]


def test_r5f1_model_drag_within_envelope_for_subnormal_conversions():
    """Detects: the corrected bound not applied to both parts of the envelope, or too small
    in the force (vehicles with subnormal b, P or b cd, at normal, subnormal and zero
    computed densities; states whose force overflows are outside the domain)."""
    checked = beyond = overflow = 0
    for label, _, b, mass, cd, area in VEHICLE_GRID:
        if b >= 2.0**-1022 and cd * area >= 2.0**-1022 and b * cd >= 2.0**-1022:
            continue
        for r, s in STATES:
            v = -s * c4.east(0.0)
            with np.errstate(over="ignore", invalid="ignore"):
                vec = m.acceleration(
                    m.Config(mu=0.0, drag=m.Drag(cd=cd, area_m2=area)), 0.0, r, v, mass
                )
            if not np.all(np.isfinite(vec)):
                overflow += 1
                continue
            a = model_drag_norm(r, v, mass, cd, area)
            low = tt._dn(o.true_height(r))
            env = tt.drag_envelope(low, c4.up(s) if s else 0.0, b, cd=cd, area=area)
            assert a <= D(env), (label, r[0], s)
            checked += 1
            if a > 0 and checked % 7 == 0:
                old = env_second(Fraction(low), Fraction(s), PHI / Fraction(b), cd, area, CONST)
                beyond += a > D(old.numerator) / D(old.denominator)
    assert checked >= 300 and beyond >= 5, (checked, beyond, overflow)


def test_r5f1_envelope_recomputed_by_a_second_implementation():
    """Detects: b_R applied to one part of the envelope only, or the envelope's use of the
    E4a bound reduced, at vehicles whose conversion is subnormal."""
    cases = [(R5_LOW, 0.0), (1.9e8, 2_000.0), (1.0e8, 11_000.0), (120_000.0, 7_800.0)]
    for label, _, b, _, cd, area in VEHICLE_GRID[::9]:
        ratio = ratio_second(b, cd, area)
        for low, s in cases:
            env = tt.drag_envelope(low, s, b, cd=cd, area=area)
            ref = env_second(Fraction(low), Fraction(s), ratio, cd, area, CONST)
            if env == math.inf:  # rounded up past the largest binary64: still a bound
                assert ref > Fraction(sys.float_info.max), (label, low, s)
                continue
            got = Fraction(env)
            assert got >= ref * (1 - Fraction(1, 10**30)), (label, low, s)
            assert got <= ref * (1 + Fraction(1, 10**9)) + Fraction(1, 2**1074), (label, low)


@pytest.mark.parametrize(
    "cd, area, mass",
    [
        (TINY, 0.5, 1.0),
        (TINY, 0.25, 17 * TINY),
        (0.4, TINY, 1e-300),
        (1e-200, 1e-124, 1.0),
        (1e-200, 1e-124, 17 * TINY),
    ],
)
def test_r5f1_no_area_vehicles_have_zero_force(cd, area, mass):
    """E4b. Detects: a vehicle with cd area <= 2^-1075, which C1 maps to b = +inf (envelope
    0), receiving a nonzero force anywhere, including at the largest density (sea level)."""
    assert Fraction(cd) * Fraction(area) <= ETA0
    assert cd * area == 0.0  # P = 0
    with np.errstate(divide="ignore"):
        assert np.float64(mass) / np.float64(cd * area) == math.inf  # C1 gives b = +inf
    assert tt.FPA["zero_force_c0_max"] <= Fraction(5, 8)
    for h in (1.0, 120_000.0, 1.0e8):
        for s in (0.0, 11_000.0):
            r = np.array([m.A_WGS84 + h, 0.0, 0.0])
            vec = m.acceleration(
                m.Config(mu=0.0, drag=m.Drag(cd=cd, area_m2=area)),
                0.0,
                r,
                -s * c4.east(0.0),
                mass,
            )
            assert np.all(vec == 0.0), (h, s)
    assert tt.drag_envelope(0.0, 11_000.0, math.inf) == 0.0


# --------------------------------------------------------------------------- R5-F2
def transition_scan_maximum(vehicle: str) -> float:
    """The largest model-drag-to-envelope ratio over the subnormal-density points of the
    committed transition scan (`check_review04.py`, same seeds and points)."""
    mass, b = c4.MASSES[vehicle], c4.VEHICLES[vehicle]
    h_n = float(o.top_band_height(D(2) ** -1022))
    h_z = float(o.top_band_height(c4.TINY / 2))
    h_c = c4.coefficient_rounding_height(mass)
    rng = np.random.default_rng(4040 + int(b))
    pts = []
    for lo, hi, n in (
        (h_n - 3e5, h_n + 3e5, 60),
        (h_c - 5e5, h_c + 1e5, 90),
        (h_z - 3e5, h_z + 3e5, 60),
        (h_n - 1e6, h_z + 1e6, 90),
    ):
        pts += c4.scan_points(rng, lo, hi, n)
    best = D(0)
    for r, v in pts:
        if c4.classify(c4.model_density(r)) != "subnormal":
            continue
        a = c4.model_drag_norm(r, v, mass)
        low = tt._dn(o.true_height(r))
        best = max(best, a / D(tt.drag_envelope(low, c4.up(float(np.linalg.norm(v))), b)))
    return float(best)


def coefficient_rounding_subset_maximum(vehicle: str) -> float:
    """The measurement behind 0.983: equatorial points at the 200 binary64 neighbours on
    each side of the model's coefficient-rounding position (`coefficient_flip_x`) and 400
    uniform positions from 300 km below to 10 km above it, retrograde speeds 0, 2 and 11
    km/s (seed 1)."""
    mass, b = c4.MASSES[vehicle], c4.VEHICLES[vehicle]
    x0 = c4.coefficient_flip_x(mass)
    xs = [x0]
    for _ in range(200):
        xs = [math.nextafter(xs[0], 0.0), *xs, math.nextafter(xs[-1], math.inf)]
    rng = np.random.default_rng(1)
    pts = [(np.array([x, 0.0, 0.0]), s) for x in xs for s in (0.0, 11_000.0)]
    for x in rng.uniform(x0 - 3e5, x0 + 1e4, 400):
        pts.append((np.array([x, 0.0, 0.0]), float(rng.choice([0.0, 2000.0, 11000.0]))))
    best = D(0)
    for r, s in pts:
        a = c4.model_drag_norm(r, -s * c4.east(0.0), mass)
        if a == 0:
            continue
        env = D(tt.drag_envelope(tt._dn(D(r[0]) - o.A), s, b))
        best = max(best, a / env)
    return float(best)


def live_dr0029() -> str:
    return c4.record("DR-0029")


def test_r5f2_transition_scan_maximum_is_quoted_and_near_one():
    """Detects: the records quoting a subnormal-regime maximum other than the transition
    scan's, or hiding it."""
    dr = live_dr0029()
    start = dr.index("Over the subnormal-density points of the committed transition scan")
    sentence = dr[start : dr.index(".", dr.index("(B 100)", start))]  # P1 itself, not the log
    for vehicle, quoted in (("B25.8", "0.99999999999886"), ("B100", "0.99999999999885")):
        got = transition_scan_maximum(vehicle)
        assert 0.9999999999 < got <= 1.0, vehicle
        assert f"{got:.14f}" == quoted, (vehicle, got)
        assert f"{quoted} ({vehicle[0]} {vehicle[1:]})" in sentence, vehicle


def test_r5f2_coefficient_rounding_subset_maximum_is_quoted_with_its_scope():
    """Detects: 0.983 quoted without its subset, or a misquoted subset maximum."""
    dr = live_dr0029()
    got = {v: coefficient_rounding_subset_maximum(v) for v in ("B25.8", "B100")}
    assert f"{got['B100']:.3f}" == "0.983" and f"{got['B25.8']:.3f}" == "0.953", got
    assert "0.983 (B 100; 0.953 for B 25.8)" in dr
    sentence = dr[dr.index("0.983 (B 100") - 400 : dr.index("0.983 (B 100")]
    assert "coefficient-rounding subset" in sentence


def test_r5f2_records_no_longer_scope_0983_to_the_subnormal_regime():
    """Detects: a return to the superseded characterisation in the live records, or the
    historical Review 04 statement rewritten instead of amended."""
    for name in ("DR-0029", "VAL-0019", "README", "report"):
        text = c4.record(name)
        assert "The tightest observed case is where the coefficient rounds" not in text, name
        assert not re.search(r"subnormal regime is 0\.983", text), name
    rev = c4.record("review04")
    old = "The largest observed ratio of model drag to envelope in the subnormal regime is 0.983"
    assert rev.count(old) == 1  # preserved, append-only
    amend = rev.index("### Amendment (Authorization I-6, Review 05 M3T0-R5-F2)")
    assert amend > rev.index(old)
    tail = rev[amend:]
    for phrase in ("coefficient-rounding subset", "0.99999999999886", "0.99999999999885"):
        assert phrase in tail, phrase


def test_records_state_the_r5f1_correction():
    for name in ("DR-0029", "VAL-0019", "report", "README"):
        assert "R5-F1" in c4.record(name), name
    dr = live_dr0029()
    for phrase in ("E4a", "b = fl(mass/fl(cd·area))", "mass = fl(fl(b·cd)·area)", "E4b"):
        assert phrase in dr, phrase
    assert "check_review05.py" in c4.record("VAL-0019")
