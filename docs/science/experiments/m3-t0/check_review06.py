"""Regression checks for the M3 T0 Review 06 findings M3T0-R6-F1 ... F3 (research only).

R6-F1: under C1, b = fl(mass / fl(cd area)), a positive mass can round to b = 0 (mass k x
2^-1074 with k <= 16 and cd area = 33). The model's drag is finite and nonzero; the E4a
bound assumed b >= 2 eta0 and divided by b, so the envelope raised ZeroDivisionError. The
correction (`t0_termination.inverse_ballistic_bound`) bounds cd area / mass at b = 0 by the
positive-mass fact mass >= 2^-1074: R(0) = max(cd area / 2^-1074, R(2^-1074)).

R6-F2: `_up` and `_dn` raised on, or mis-rounded, infinite and out-of-range inputs, and an
unbounded stage enclosure ended in an incidental exception instead of a non-certification.

R6-F3: E4b's cap c0 = fl(0.5 rho^) <= 5/8 uses the density allowance, so it depends on
A-FP-2 (LIBM_ULP); the Review 05 record classified it as derived under A-FP-1 only.

Records: the 5 287-point random search quoted in the Review 04 record is marked
UNREPRODUCED; the switch point b* is quoted for the stored and for the exact phi_B.

Expected values come from exact rational arithmetic on the binary64 inputs and from
`t0_oracle` heights, never from the envelope implementation. Each check states the defect
it detects. `mutation_check_review02.py` runs these checks on corrupted copies. Not
collected by the project test suite. Run:
  uv run --no-sync pytest -q docs/science/experiments/m3-t0/check_review06.py
"""

from __future__ import annotations

import math
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_review04 as c4  # noqa: E402
import check_review05 as c5  # noqa: E402
import t0_model as m  # noqa: E402
import t0_oracle as o  # noqa: E402
import t0_termination as tt  # noqa: E402

D = Decimal
TINY = 2.0**-1074  # the smallest positive binary64
ETA0 = Fraction(1, 2**1075)
U = Fraction(1, 2**53)
MAX = sys.float_info.max
CD, AREA = c4.CD, c4.AREA
PHI = c5.PHI  # the stored (binary64, rounded up) phi_B the envelope uses
PHI_EXACT = (1 + U) / (1 - U) ** 2  # phi_B as the derivation defines it
R5_R, R5_LOW = c5.R5_R, c5.R5_LOW
ROOT = HERE.parents[3]


# ------------------------------------------------------------- independent helpers
def r_zero_second(cd: float, area: float) -> Fraction:
    """E4a at b = 0, written out again: every positive binary64 mass is >= 2^-1074, so cd
    area / mass <= cd area / 2^-1074; the max with the b = 2^-1074 bound keeps R
    non-increasing in b."""
    return max(Fraction(cd) * Fraction(area) / (2 * ETA0), c5.ratio_second(TINY, cd, area))


def ratio_second(b: float, cd: float, area: float) -> Fraction:
    return r_zero_second(cd, area) if b == 0.0 else c5.ratio_second(b, cd, area)


def largest_zero_mass(p: float) -> float | None:
    """The largest binary64 mass with fl(mass / p) = 0 (C1 gives b = 0), by exact rational
    comparison with the rounding boundary eta0 (ties to even give 0)."""
    if p < 2.0:
        return None  # 2^-1074 / p > eta0: even the smallest mass gives b >= 2^-1074
    x = float(ETA0 * Fraction(p))
    while x / p != 0.0:
        x = math.nextafter(x, 0.0)
    while math.nextafter(x, math.inf) / p == 0.0:
        x = math.nextafter(x, math.inf)
    return x


# shapes: V1 (P = 33), P exactly 2 (the tie), just below 2 (b = 0 unreachable), small and
# large normal P, P near the largest binary64, subnormal cd with a huge area
SHAPES = [
    (CD, AREA),
    (1.0, 2.0),
    (1.0, math.nextafter(2.0, 0.0)),
    (1.0, 4.0),
    (0.5, 3.0),
    (2.2, 1e3),
    (1e154, 1e154),
    (MAX, 1.0),
    (math.nextafter(2.0**-1022, 0.0), 1.75 * 2.0**1023),
    (2.0**-1000, 2.0**1001),
]


# ------------------------------------------------------------------- R6-F1
@pytest.mark.parametrize("k", range(1, 18))
def test_r6f1_reviewer_counterexample_masses_are_covered(k):
    """Detects: the b = 0 case of C1 missing (ZeroDivisionError, the R6-F1 defect) or too
    small. mass = k x 2^-1074, cd 2.2, area 15 m^2 at r = (186 378 137, 0, 0) m (true height
    exactly 180 000 000 m), v = 0. k <= 16 gives b = 0 and k = 17 gives b = 2^-1074."""
    mass = k * TINY
    b = mass / (CD * AREA)
    assert b == (0.0 if k <= 16 else TINY)
    assert o.true_height(R5_R) == D(R5_LOW)
    a = c5.model_drag_norm(R5_R, np.zeros(3), mass, CD, AREA)
    assert 0 < a < D(MAX)  # finite, nonzero drag
    actual = Fraction(CD) * Fraction(AREA) / Fraction(mass)
    r = tt.inverse_ballistic_bound(b, CD, AREA, PHI)
    assert actual <= r and r == ratio_second(b, CD, AREA)
    env = tt.drag_envelope(R5_LOW, 0.0, b)
    assert math.isfinite(env) and a <= D(env), (k, a, env)


def test_r6f1_zero_b_bound_covers_every_c1_mass():
    """Detects: R(0) below the supremum of cd area / mass over the C1 masses that give b =
    0 (attained at the smallest mass 2^-1074 whenever fl(cd area) >= 2), or b = 0 rejected
    for a reachable shape."""
    reachable = 0
    for cd, area in SHAPES:
        p = cd * area
        prod = Fraction(cd) * Fraction(area)
        r0 = tt.inverse_ballistic_bound(0.0, cd, area, PHI)
        assert r0 == r_zero_second(cd, area), (cd, area)
        assert r0 >= prod / (2 * ETA0)  # mass >= 2^-1074
        top = largest_zero_mass(p)
        if top is None:
            assert TINY / p > 0.0  # b = 0 unreachable by C1
            continue
        reachable += 1
        assert TINY / p == 0.0 and top / p == 0.0 and math.nextafter(top, math.inf) / p > 0
        assert prod / Fraction(TINY) <= r0  # the supremum, at mass = 2^-1074
    assert reachable >= 7


def test_r6f1_exhaustive_small_masses_on_adversarial_shapes():
    """Detects: any C1 vehicle with mass k x 2^-1074 (k <= 20 000) whose cd area / mass
    exceeds R(b), b = 0 included (the Review 05 sweep filtered b > 0)."""
    zeros = 0
    for cd, area in SHAPES:
        p = cd * area
        prod = Fraction(cd) * Fraction(area)
        cache: dict[float, Fraction] = {}
        for k in range(1, 20_001):
            mass = k * TINY
            b = mass / p
            if not b < math.inf:
                continue
            if b not in cache:
                cache[b] = tt.inverse_ballistic_bound(b, cd, area, PHI)
            assert prod / Fraction(mass) <= cache[b], (cd, area, k)
            zeros += b == 0.0
    assert zeros >= 40_000, zeros


def test_r6f1_transition_from_zero_b_on_each_shape():
    """Detects: a gap or a decrease at the b = 0 / b = 2^-1074 transition: the largest mass
    giving b = 0 and its successor are covered, and R(0) >= R(2^-1074) >= R(2 x 2^-1074)."""
    for cd, area in SHAPES:
        prod = Fraction(cd) * Fraction(area)
        r = [tt.inverse_ballistic_bound(b, cd, area, PHI) for b in (0.0, TINY, 2 * TINY)]
        assert r[0] >= r[1] >= r[2], (cd, area)
        top = largest_zero_mass(cd * area)
        if top is None:
            continue
        nxt = math.nextafter(top, math.inf)
        for mass in (top, nxt, TINY, math.nextafter(TINY, 1.0)):
            b = mass / (cd * area)
            assert prod / Fraction(mass) <= tt.inverse_ballistic_bound(b, cd, area, PHI)


def test_r6f1_second_construction_never_gives_zero_b_with_positive_mass():
    """C2 (mass = fl(fl(b cd) area)) with b = 0 gives mass 0, so b = 0 is a C1 case only;
    near it, C2 vehicles stay within R."""
    for cd, area in SHAPES:
        assert (0.0 * cd) * area == 0.0
        for b in (TINY, 2 * TINY, 17 * TINY):
            mass = (b * cd) * area
            if 0.0 < mass < math.inf:
                actual = Fraction(cd) * Fraction(area) / Fraction(mass)
                assert actual <= tt.inverse_ballistic_bound(b, cd, area, PHI)


def test_r6f1_signed_zero_b_is_the_same_vehicle():
    for cd, area in SHAPES[:3]:
        assert tt.inverse_ballistic_bound(-0.0, cd, area, PHI) == r_zero_second(cd, area)
    assert tt.drag_envelope(R5_LOW, 0.0, -0.0) == tt.drag_envelope(R5_LOW, 0.0, 0.0)


STATES = c5.STATES + [(np.array([m.A_WGS84 + h, 0.0, 0.0]), 7_800.0) for h in (2e5, 1e6)]


def test_r6f1_model_drag_within_envelope_at_zero_b():
    """Detects: the b = 0 bound not applied to both parts of the envelope or too small in
    the force, for C1 vehicles with b = 0 on several shapes (states whose force overflows
    are outside the domain)."""
    checked = 0
    for cd, area in SHAPES:
        top = largest_zero_mass(cd * area)
        if top is None:
            continue
        for mass in sorted({x for x in (TINY, 3 * TINY, top) if x <= top}):
            assert mass / (cd * area) == 0.0
            for r, s in STATES:
                v = -s * c4.east(0.0)
                with np.errstate(over="ignore", invalid="ignore"):
                    vec = m.acceleration(
                        m.Config(mu=0.0, drag=m.Drag(cd=cd, area_m2=area)), 0.0, r, v, mass
                    )
                if not np.all(np.isfinite(vec)):
                    continue
                a = c5.model_drag_norm(r, v, mass, cd, area)
                low = tt._dn(o.true_height(r))
                env = tt.drag_envelope(low, c4.up(s) if s else 0.0, 0.0, cd=cd, area=area)
                assert a <= D(env), (cd, area, mass, r[0], s)
                checked += a > 0
    assert checked >= 60, checked


def test_r6f1_zero_b_envelope_recomputed_by_a_second_implementation():
    """Detects: b_R at b = 0 rounded the unsafe way, or the b = 0 bound applied to one part
    of the envelope only."""
    for cd, area in SHAPES[:6]:
        ratio = r_zero_second(cd, area)
        for low, s in ((R5_LOW, 0.0), (1.0e8, 11_000.0), (120_000.0, 7_800.0)):
            env = tt.drag_envelope(low, s, 0.0, cd=cd, area=area)
            ref = c5.env_second(Fraction(low), Fraction(s), ratio, cd, area, c5.CONST)
            if env == math.inf:
                assert ref > Fraction(MAX)
                continue
            assert Fraction(env) >= ref * (1 - Fraction(1, 10**30)), (cd, area, low)
            assert Fraction(env) <= ref * (1 + Fraction(1, 10**9)) + Fraction(TINY)


def test_r6f1_zero_b_ballistic_coefficient_is_positive_and_rounded_down():
    """b_R = phi_B / R(0), rounded down: positive (no division by zero downstream) and <= the
    exact quotient."""
    for cd, area in SHAPES:
        q = PHI / r_zero_second(cd, area)
        b_r = tt.envelope_ballistic_coefficient(0.0, cd, area, tt.FP)
        assert isinstance(b_r, D) and b_r > 0
        assert Fraction(b_r) <= q and Fraction(b_r) >= q * (1 - Fraction(1, 10**58))


def test_r6f1_stage_condition_is_defined_at_zero_b():
    """Detects: the stage enclosure failing on a b = 0 vehicle instead of returning bounds
    (finite or an explicit non-certification)."""
    for h0 in (1.2e5, 1e6, 1e7, 2e8):
        need = tt.stage_need(h0, 0.0)
        assert not math.isnan(need)


@pytest.mark.parametrize(
    "b, cd, area",
    [
        (math.nan, CD, AREA),
        (-TINY, CD, AREA),
        (-1.0, CD, AREA),
        (math.inf, CD, AREA),
        (1.0, 0.0, AREA),
        (1.0, -2.2, AREA),
        (1.0, math.nan, AREA),
        (1.0, math.inf, AREA),
        (1.0, CD, 0.0),
        (1.0, CD, math.inf),
    ],
)
def test_r6f1_invalid_vehicles_are_rejected_not_bounded(b, cd, area):
    """Detects: an input outside E4a's domain (b a non-negative finite binary64; cd and area
    positive finite) silently turned into a ratio bound."""
    with pytest.raises(ValueError):
        tt.inverse_ballistic_bound(b, cd, area, PHI)


# ------------------------------------------------------------------- R6-F2
NEXT_MAX = Fraction(2) ** 1024  # the first real above which binary64 rounding overflows


@pytest.mark.parametrize(
    "q, up, dn",
    [
        (Fraction(2**1024), math.inf, MAX),
        (-(D(2) ** 1024), -MAX, -math.inf),
        (D(2) ** 1024, math.inf, MAX),
        (Fraction(MAX), MAX, MAX),
        (-Fraction(MAX), -MAX, -MAX),
        (Fraction(MAX) + Fraction(1, 2), math.inf, MAX),
        (-Fraction(MAX) - Fraction(1, 2), -MAX, -math.inf),
        (D("Infinity"), math.inf, math.inf),
        (D("-Infinity"), -math.inf, -math.inf),
        (math.inf, math.inf, math.inf),
        (-math.inf, -math.inf, -math.inf),
        (Fraction(1, 2**1076), TINY, 0.0),
        (-Fraction(1, 2**1076), 0.0, -TINY),
        (ETA0, TINY, 0.0),
        (Fraction(0), 0.0, 0.0),
        (D("-0"), 0.0, 0.0),
        (-0.0, 0.0, 0.0),
        (Fraction(1, 3), math.nextafter(1 / 3, 1.0), 1 / 3),
        (10**400, math.inf, MAX),
        (D("1e-400"), TINY, 0.0),
    ],
)
def test_r6f2_up_and_dn_at_extremes(q, up, dn):
    """Detects: OverflowError on a finite rational beyond the binary64 range, -inf for a
    negative one (not an upper bound's smallest binary64 >= q), an exception on an infinite
    Decimal, or -0.0 escaping. Expected values from exact comparison."""
    got_up, got_dn = tt._up(q), tt._dn(q)
    assert got_up == up and got_dn == dn, (q, got_up, got_dn)
    for got in (got_up, got_dn):
        assert math.copysign(1.0, got) == 1.0 or got != 0.0  # no -0.0


def test_r6f2_up_and_dn_bracket_random_rationals():
    """_dn(q) <= q <= _up(q), each the nearest binary64 on its side, over 20 000 rationals
    from below the subnormal range to beyond the largest binary64, both signs."""
    rng = np.random.default_rng(606)
    for _ in range(20_000):
        e = int(rng.integers(-1100, 1030))
        q = Fraction(int(rng.integers(1, 2**62)), 2**62) * Fraction(2) ** e
        q = -q if rng.random() < 0.5 else q
        for v in (q, D(q.numerator) / D(q.denominator) if abs(e) < 300 else q):
            hi, lo = tt._up(v), tt._dn(v)
            x = Fraction(v)
            assert lo <= hi
            if math.isfinite(hi):
                assert Fraction(hi) >= x
                assert math.nextafter(hi, -math.inf) == -math.inf or (
                    Fraction(math.nextafter(hi, -math.inf)) < x
                )
            else:
                assert x > Fraction(MAX)
            if math.isfinite(lo):
                assert Fraction(lo) <= x
                assert lo == MAX or Fraction(math.nextafter(lo, math.inf)) > x
            else:
                assert x < -Fraction(MAX)


@pytest.mark.parametrize("q", [math.nan, D("NaN"), D("sNaN"), -math.nan])
def test_r6f2_nan_is_rejected(q):
    """Detects: a NaN silently rounded into a bound."""
    for fn in (tt._up, tt._dn):
        with pytest.raises(ValueError):
            fn(q)


def test_r6f2_float_nan_is_rejected_even_without_the_explicit_guard():
    """Why removing `_exact`'s float NaN guard is an equivalent mutant: the exact conversion
    itself rejects NaN with ValueError, so the guard only states the semantics."""
    for q in (math.nan, -math.nan):
        with pytest.raises(ValueError):
            Fraction(q)


@pytest.mark.parametrize("q", ["1.0", None, 1j, [1.0]])
def test_r6f2_unsupported_types_are_rejected(q):
    for fn in (tt._up, tt._dn):
        with pytest.raises(TypeError):
            fn(q)


def test_r6f2_unbounded_stage_enclosure_is_an_explicit_non_certification():
    """Detects: the reviewer's stage_lower_heights(1e7, 2^-1074) ending in an incidental
    OverflowError instead of bounds whose infinite parts make need(h0) = +inf (the step is
    not certified at that height)."""
    lim = tt.stage_lower_heights(1e7, TINY)
    values = [x for x in lim.values() if x is not None]
    assert not any(math.isnan(x) for x in values)
    assert any(math.isinf(x) for x in values)
    assert tt.stage_need(1e7, TINY) == math.inf
    assert tt.drag_envelope(1e7, math.inf, TINY) == math.inf
    assert tt.drag_envelope(1e7, math.inf, math.inf) == 0.0  # drag-free: exactly 0 (E4b)
    assert tt.drag_envelope(1e9, math.inf, 1.0) == math.inf  # above h_zero: no 0 x inf
    # far above h_zero the decimal table density underflows to 0: 0 x inf must not arise
    assert tt.drag_envelope(1e12, math.inf, 1.0) == math.inf


@pytest.mark.parametrize(
    "low, s, b",
    [
        (math.nan, 0.0, 1.0),
        (-1.0, 0.0, 1.0),
        (0.0, math.nan, 1.0),
        (0.0, -1.0, 1.0),
        (0.0, 0.0, math.nan),
        (0.0, 0.0, -1.0),
        (math.inf, 0.0, 1.0),
    ],
)
def test_r6f2_invalid_envelope_inputs_are_rejected(low, s, b):
    """Detects: an invalid input silently transformed into an envelope value."""
    with pytest.raises(ValueError):
        tt.drag_envelope(low, s, b)


def test_r6f2_invalid_stage_input_is_not_certified():
    for h0, b in ((math.nan, 1.0), (1e6, math.nan), (1e6, -1.0)):
        with pytest.raises(ValueError):
            tt.stage_need(h0, b)


def test_r6f2_published_vehicles_unchanged():
    """The helpers' new cases leave the published floors and their brackets bit-identical."""
    rows = c4.results("termination")["sufficient_stage_condition"]["rows"]
    floors = {r["vehicle"]: r["h_f_sufficient_at_least_m"] for r in rows}
    assert floors == {
        "B25.8": 124456.68544510857,
        "B100": 118633.50894662621,
        "drag-free limit": 111511.96182508787,
    }
    for name, b in c4.VEHICLES.items():
        assert tt.stage_need(floors[name], b) < 0.0


# ------------------------------------------------------------------- R6-F3
def c0_cap(libm_ulp: int) -> Fraction:
    """E4b's c0 bound written out again: fl(0.5 rho^) <= (F_rho e^eta0 rho0_max + N_rho) / 2
    + eta0, F_rho = (1 + UF)(1 + u)^2, UF = LIBM_ULP 2^-52, N_rho = (1 + u)^2 rho0_max nu +
    eta0, nu = LIBM_ULP 2^-1074 (A-FP-2 enters through UF and nu)."""
    rho0_max = max(c4.frac(row[1]) for row in o.TABLE)
    uf, nu = Fraction(libm_ulp, 2**52), Fraction(libm_ulp, 2**1074)
    n_rho = (1 + U) ** 2 * rho0_max * nu + ETA0
    return ((1 + uf) * (1 + U) ** 2 * (1 + 2 * ETA0) * rho0_max + n_rho) / 2 + ETA0


def largest_libm_ulp_for_cap() -> int:
    """c0_cap is affine in LIBM_ULP: the largest integer LIBM_ULP with c0 <= 5/8."""
    a, slope = c0_cap(0), c0_cap(1) - c0_cap(0)
    return math.floor((Fraction(5, 8) - a) / slope)


def test_r6f3_e4b_cap_depends_on_libm_ulp():
    """Detects: the cap computed without the density (libm) allowance, i.e. claimed
    independent of A-FP-2. The derived constant equals the second implementation at every
    LIBM_ULP, grows with it, and fails just above the largest LIBM_ULP computed here."""
    assert tt.FPA["zero_force_c0_max"] == c0_cap(tt.LIBM_ULP) <= Fraction(5, 8)
    caps = [tt.rounding_allowances(2**j)["zero_force_c0_max"] for j in (0, 1, 8, 20, 40)]
    assert caps == [c0_cap(2**j) for j in (0, 1, 8, 20, 40)]
    assert caps == sorted(caps) and caps[0] < caps[-1]
    top = largest_libm_ulp_for_cap()
    assert 2**46 < top < 2**47, top
    assert tt.rounding_allowances(top)["zero_force_c0_max"] <= Fraction(5, 8)
    for libm in (top + 1, 2**47, 2**48):
        with pytest.raises(ValueError, match="E4b"):
            tt.rounding_allowances(libm)


def test_r6f3_records_classify_e4b_under_a_fp_2():
    """Detects: E4b still classified as derived under A-FP-1 only, or the Review 05 record
    rewritten instead of amended."""
    rev = (ROOT / "docs/reviews/M3-T0-review-05.md").read_text()
    amend = rev.index("### Amendment (Authorization I-8, Review 06 M3T0-R6-F3)")
    for old in ("E4a and E4b use no libm call.", "| **Derived under A-FP-1** | E4a (R1, R2, R)"):
        assert rev[:amend].count(old) == 1, old  # preserved above the amendment
    tail = rev[amend:]
    assert "c₀ ≤ 5/8 depends on A-FP-2" in tail
    assert f"{largest_libm_ulp_for_cap()}" in tail
    for name in ("DR-0029", "VAL-0019"):
        assert "c₀ ≤ 5/8 depends on A-FP-2" in c4.record(name), name
    src = (HERE / "t0_termination.py").read_text()
    assert "E4b depends on A-FP-2" in src


# ------------------------------------------------------- provenance and switch point
def b_star(phi: Fraction) -> Fraction:
    c = phi * (1 - U)
    return c * ETA0 / (c - 1)


def test_switch_point_stored_and_exact_phi_are_distinguished():
    """Detects: b* quoted without the phi_B it uses. With the stored phi_B (what the
    envelope uses) b* ~ 7.42e-309; with the exact phi_B, b* = (1 + u) 2^-1023 ~ 1.11e-308."""
    stored, exact = b_star(PHI), b_star(PHI_EXACT)
    assert exact == (1 + U) * Fraction(1, 2**1023)
    assert repr(float(stored)) == "7.416912861690675e-309"
    assert repr(float(exact)) == "1.1125369292536007e-308"
    above, below = tt._up(exact), tt._dn(exact)
    r_exact = tt.inverse_ballistic_bound(above, CD, AREA, PHI_EXACT)
    assert r_exact == PHI_EXACT / Fraction(above)  # switch at the exact b* with exact phi_B
    assert tt.inverse_ballistic_bound(below, CD, AREA, PHI_EXACT) > PHI_EXACT / Fraction(below)
    rev = (ROOT / "docs/reviews/M3-T0-review-05.md").read_text()
    amend = rev.index("### Amendment (Authorization I-8, switch point b*)")
    assert rev[:amend].count("b* ≈ 7.42e-309, two thirds of 2^-1023") == 1  # preserved
    tail = rev[amend:]
    for phrase in ("7.416912861690675e-309", "stored", "1.1125369292536007e-308", "exact"):
        assert phrase in tail, phrase


def test_random_search_is_marked_unreproduced():
    """Detects: the 5 287-point random search presented as reproduced evidence, or the
    Review 04 record rewritten instead of amended."""
    rev = c4.record("review04")
    old = "A random search of 5 287 points found no violation"
    amend = rev.index("### Amendment (Authorization I-8, provenance of the random search)")
    assert rev[:amend].count(old) == 1  # preserved above the amendment
    assert "UNREPRODUCED" in rev[amend:]
    assert "UNREPRODUCED" in c4.record("report")


def test_records_state_the_r6_corrections():
    for name in ("DR-0029", "VAL-0019", "report", "README"):
        assert "R6-F1" in c4.record(name), name
    for name in ("DR-0029", "VAL-0019"):
        assert "mass ≥ 2^-1074" in c4.record(name), name
    assert "check_review06.py" in c4.record("VAL-0019")
    assert "check_review06.py" in c4.record("README")
    with localcontext() as ctx:  # the published B 25.8 conversion is still normal
        ctx.prec = 60
        assert (
            tt.envelope_ballistic_coefficient(c4.VEHICLES["B25.8"], CD, AREA, tt.FP)
            is (c4.VEHICLES["B25.8"])
        )
