"""Regression checks for the M3 T0 Review 03 finding M3T0-R3-F1 (research only).

R3-F1: the drag envelope bounded drag at the *exact* geodetic height, but the model
evaluates density at its *computed* height, and the table density is discontinuous. At the
12 bases where density drops going up, a computed height a few 1e-10 m below the base
selects the denser band while the true height is above it. Review 02's adversarial check
hid this by taking the envelope at `min(low, h_model)`, the implementation's own height.

The checks here take their expected values from `t0_oracle` (exact heights of the binary64
points by a foot-point method in 60-digit decimal arithmetic, and the table read as
decimals), which shares no altitude or band-selection code with the model; a second oracle
(H. Vermeille's closed form, also in decimal arithmetic) cross-validates it. They cover:
- the reviewer's 120 km counterexample, and constructed counterexamples at all 12 downward
  jumps (including 200 and 250 km): the superseded envelope is exceeded, the corrected one
  is not;
- boundary points at every downward jump: exactly representable base heights and their
  adjacent binary64 neighbours (equatorial points, where computed = true height), true
  heights just below and above the base, and points where the computed and true heights
  select different bands;
- the derived height-error bound against observed errors, and the derivation's constants
  recomputed by a second implementation;
- an oracle self-test: the oracle must detect the R3-F1 defect in a defective reference
  envelope written here (if it were replaced by the model's height it would not);
- static guards that the oracle does not use the model's height or band code and that the
  Review 02 adversarial check no longer adapts its bound to the model's height;
- RK4 steps from near-escape, retrograde and straight-down bound states at the floors and
  near the downward jumps, checked against the stage bounds with oracle heights;
- the floors recomputed by a second implementation of the corrected stage condition.

`mutation_check_review02.py` runs these checks (with those of Reviews 01 and 02) on
corrupted copies of the scripts. Not collected by the project test suite. Run explicitly:
  uv run --no-sync pytest -q docs/science/experiments/m3-t0/check_review03.py
"""

from __future__ import annotations

import ast
import json
import math
import re
import subprocess
import sys
from decimal import Decimal, getcontext, localcontext
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t0_model as m  # noqa: E402
import t0_oracle as o  # noqa: E402
import t0_termination as tt  # noqa: E402

D = Decimal
getcontext().prec = 60  # every decimal comparison below at the oracle's precision
ROOT = HERE.parents[3]
DT = 10.0
MASS = 850.0
B_V1 = MASS / (2.2 * 15.0)
DRAG = m.Drag(cd=2.2, area_m2=15.0)
J2_DRAG = m.Config(j2=m.J2_FROM_C20, drag=DRAG)
DOWNWARD_KM = (50, 90, 110, 120, 140, 200, 250, 450, 600, 700, 900, 1000)
SPEEDS = (7_800.0, 11_000.0)
FENCES = re.compile(
    r"<!-- (review01|review02|review03)-correction-log -->.*?<!-- /\1-correction-log -->",
    re.DOTALL,
)
REVIEWER_R = np.array([5420209.728043159, 3584286.6758661848, 1.8499824933775928])
REVIEWER_V = np.array([6067.454938935459, -9175.29239664793, 0.0])


def record(name: str) -> str:
    paths = {
        "DR-0029": ROOT / "docs/decisions/requests/DR-0029-m3-t0-proposals.md",
        "report": ROOT / "docs/milestones/M3-T0-report.md",
        "README": HERE / "README.md",
        "review03": ROOT / "docs/reviews/M3-T0-review-03.md",
    }
    if name == "VAL-0019":
        text = (ROOT / "docs/science/validation.md").read_text()
        text = text[text.index("## VAL-0019") :]
        nxt = text.find("\n## VAL-", 10)
        text = text if nxt < 0 else text[:nxt]
    else:
        text = paths[name].read_text()
    return FENCES.sub("", text)


def results(name: str) -> dict:
    return json.loads((HERE / f"t0_{name}_results.json").read_text())


# ------------------------------------------------------------- independent helpers
def model_height(r) -> float:
    return m.geodetic_iterative(r)[1]


def model_drag_norm(r, v, mass: float = MASS) -> D:
    """Exact norm of the model's binary64 drag vector (mu = 0 and J2 off make gravity 0)."""
    vec = m.acceleration(m.Config(mu=0.0, drag=DRAG), 0.0, r, v, mass)
    with localcontext() as c:
        c.prec = 60
        return sum(D(float(x)) ** 2 for x in vec).sqrt()


def retrograde(lon: float, s: float) -> np.ndarray:
    """Horizontal velocity against the rotation: the largest |v_rel| for |v| = s."""
    return -s * np.array([-math.sin(lon), math.cos(lon), 0.0])


def defective_envelope(low: D, s: float, b: float) -> D:
    """A reference copy of the R3-F1 defect, written here: sup over EXACT heights h >= low of
    rho(h) (s + omega (a + h))^2 / (2 b) with oracle densities. Used only by the oracle
    self-test, which must find model drag above it at true heights >= low."""
    with localcontext() as c:
        c.prec = 60
        cands = [low] + [row[0] for row in o.TABLE if row[0] > low]
        return max(o.density(h) * (D(s) + o.OMEGA * (o.A + h)) ** 2 for h in cands) / (2 * D(b))


def vermeille_height(r) -> D:
    """Second oracle: H. Vermeille, J. Geodesy 76 (2002) 451-454, in 70-digit decimals."""
    with localcontext() as c:
        c.prec = 70
        x, y, z = (D(float(q)) for q in r)
        a2, e2 = o.A * o.A, o.E2
        e4 = e2 * e2
        pp = (x * x + y * y) / a2
        q = (1 - e2) / a2 * z * z
        rr = (pp + q - e4) / 6
        s = e4 * pp * q / (4 * rr**3)
        t = (1 + s + (s * (2 + s)).sqrt()) ** (D(1) / 3)
        u = rr * (1 + t + 1 / t)
        v = (u * u + e4 * q).sqrt()
        w = e2 * (u + v - q) / (2 * v)
        k = (u + v + w * w).sqrt() - w
        d = k * (x * x + y * y).sqrt() / (k + e2)
        return (k + e2 - 1) / k * (d * d + z * z).sqrt()


def crossing_cases(base_km: int, want: int = 2, tries: int = 4000) -> list[dict]:
    """Near-equatorial points constructed at the base whose computed height is below the base
    and whose oracle height is at or above it, with model drag above the superseded envelope
    at L = base (retrograde, s = 11 000 m/s). Deterministic per base."""
    base_d = D(base_km) * 1000
    base = float(base_d)
    rng = np.random.default_rng(base_km)
    found = []
    for _ in range(tries):
        lat, lon = rng.uniform(-0.01, 0.01), rng.uniform(-math.pi, math.pi)
        r = m.geodetic_to_cartesian(lat, lon, base + rng.uniform(-2e-9, 2e-9))
        if model_height(r) >= base:
            continue
        ht = o.true_height(r)
        if ht < base_d:
            continue
        v = retrograde(lon, 11_000.0)
        a = model_drag_norm(r, v)
        if a > defective_envelope(base_d, 11_000.0, B_V1):
            found.append({"r": r, "v": v, "true": ht, "drag": a})
            if len(found) == want:
                break
    return found


# ------------------------------------------------------------------ counterexamples
def test_r3f1_reviewer_counterexample_is_reproduced_and_covered():
    ht = o.true_height(REVIEWER_R)
    assert abs(ht - D("120000.0000000000233")) < D("1e-13")
    assert model_height(REVIEWER_R) == 119999.99999999907 < 120_000.0
    a = model_drag_norm(REVIEWER_R, REVIEWER_V)
    assert a > D(tt.drag_envelope_exact_height(120_000.0, 11_000.0, B_V1))  # the defect
    assert a > defective_envelope(D(120_000), 11_000.0, B_V1)
    assert a <= D(tt.drag_envelope(120_000.0, 11_000.0, B_V1))  # the correction
    stored = results("termination")["sufficient_stage_condition"]["review03_counterexample"]
    assert stored["corrected_covers"] and not stored["superseded_covers"]


@pytest.mark.parametrize("base_km", DOWNWARD_KM)
def test_r3f1_counterexamples_at_every_downward_jump_are_covered(base_km):
    """Includes the 200 km and 250 km cases of Review 03."""
    cases = crossing_cases(base_km)
    assert len(cases) == 2, base_km
    base = base_km * 1000.0
    for case in cases:
        assert case["drag"] > D(tt.drag_envelope_exact_height(base, 11_000.0, B_V1))
        assert case["drag"] <= D(tt.drag_envelope(base, 11_000.0, B_V1))
        assert case["drag"] <= D(tt.drag_envelope(tt._dn(case["true"]), 11_000.0, B_V1))


# ------------------------------------------------------------------- boundary points
def test_the_twelve_downward_jumps_are_identified_from_the_decimal_table():
    assert [int(b / 1000) for b in o.downward_jumps()] == list(DOWNWARD_KM)


@pytest.mark.parametrize("base_km", DOWNWARD_KM)
def test_r3f1_boundary_points(base_km):
    base_d = D(base_km) * 1000
    base = float(base_d)
    i_up = o.band(base_d)
    # (a) exactly representable base heights and adjacent binary64 values: equatorial
    #     points, where the true height is x - a exactly.
    x0 = m.A_WGS84 + base
    xs = [x0]
    for _ in range(3):
        xs = [math.nextafter(xs[0], 0.0), *xs, math.nextafter(xs[-1], math.inf)]
    for x in xs:
        r = np.array([x, 0.0, 0.0])
        ht = D(x) - o.A  # exact: the foot point is (a, 0, 0)
        assert abs(o.true_height(r) - ht) < D("1e-40")
        hc = model_height(r)
        assert D(hc) == ht  # exact at the equator
        rho = m.density(hc)
        assert abs(D(rho) / o.density(ht) - 1) < D("1e-14"), (x, hc)
        assert (o.band(ht) == i_up) == (ht >= base_d)  # GMAT: the base belongs above
        for s in SPEEDS:
            a = model_drag_norm(r, retrograde(0.0, s))
            assert abs(
                a
                / (
                    o.density(ht)
                    * (D(s) + o.OMEGA * D(x)) ** 2
                    * D(DRAG.cd)
                    * D(DRAG.area_m2)
                    / (2 * D(MASS))
                )
                - 1
            ) < D("1e-13")
            for low in (hc, base):
                if ht >= D(low):
                    assert a <= D(tt.drag_envelope(low, s, B_V1)), (x, s, low)
    # (b) true heights just below and above the base off the equator, and (c) points
    #     whose computed and true heights select different bands.
    rng = np.random.default_rng(1000 + base_km)
    eps_sel = tt._up(tt.FPA["alpha_sel"] * Fraction(base) + tt.FPA["beta_sel_m"])
    env = {s: D(tt.drag_envelope(base, s, B_V1)) for s in SPEEDS}
    down = up = below = above = 0
    for k in range(120):
        lat = rng.uniform(-0.01, 0.01) if k % 2 else rng.uniform(-1.5, 1.5)
        lon = rng.uniform(-math.pi, math.pi)
        for dh in (-1e-8, -3e-9, -1e-9, 0.0, 1e-9, 3e-9, 1e-8):
            r = m.geodetic_to_cartesian(lat, lon, base + dh)
            ht, hc = o.true_height(r), model_height(r)
            below += ht < base_d
            above += ht >= base_d
            assert abs(D(hc) - ht) <= D(tt.height_error_bound(float(ht))), (r, hc, ht)
            rho = D(m.density(hc))
            if abs(ht - base_d) > D(eps_sel):
                assert abs(rho / o.density(ht) - 1) < D("1e-11"), (r, hc, ht)
            else:  # either band may be selected; its formula must hold at the computed height
                assert abs(rho / o.density(D(hc)) - 1) < D("1e-11")
            if ht >= base_d and hc < base:
                down += 1
            if ht < base_d and hc >= base:
                up += 1
            for s in SPEEDS:
                a = model_drag_norm(r, retrograde(lon, s))
                if ht >= base_d:
                    assert a <= env[s], (r, s)
                low = tt._dn(ht)
                if (ht >= base_d) != (hc >= base) and low >= 0:
                    assert a <= D(tt.drag_envelope(low, s, B_V1)), (r, s, low)
    assert below and above and down and up, (below, above, down, up)


def test_r3f1_height_error_bound_holds_on_global_polar_and_low_points():
    rng = np.random.default_rng(303)
    worst = 0.0
    for k in range(1500):
        if k % 3 == 0:
            lat = math.copysign(math.pi / 2 - 10.0 ** rng.uniform(-12, -2), rng.uniform(-1, 1))
        else:
            lat = rng.uniform(-1.5707, 1.5707)
        h = rng.uniform(1e-3, 10.0) if k % 5 == 0 else rng.uniform(0.0, 2.0e6)
        r = m.geodetic_to_cartesian(lat, rng.uniform(-math.pi, math.pi), h)
        ht = o.true_height(r)
        err = abs(D(model_height(r)) - ht)
        bound = D(tt.height_error_bound(float(ht)))
        assert err <= bound, (r, err, bound)
        worst = max(worst, float(err / bound))
    assert worst > 0.05  # the sample is not trivially far from the bound's scale


def test_r3f1_committed_height_error_evidence():
    res = results("height_error")
    assert res["height_error"]["max_error_over_bound"] < 1.0
    assert res["crossings"]["corrected_covers_all"]
    assert [r["base_m"] for r in res["crossings"]["rows"]] == [k * 1000.0 for k in DOWNWARD_KM]
    libm = res["libm"]
    assert libm["within_assumption"]
    assert libm["assumed_relative_bound_in_2^-52"] == tt.LIBM_ULP == 2


# ------------------------------------------------------------ derivation recomputed
def sqrt_hi(q: Fraction) -> Fraction:
    """A rational upper bound of sqrt(q) by Newton from above (independent of the module)."""
    x = Fraction(math.isqrt(math.ceil(q * 10**60)) + 1, 10**30)
    for _ in range(4):
        x = (x + q / x) / 2  # stays >= sqrt(q) (AM-GM)
        x = Fraction(math.ceil(x * 10**45), 10**45)
    return x


def sqrt_lo(q: Fraction) -> Fraction:
    return q / sqrt_hi(q)


def recomputed_constants() -> dict:
    """E1-E5 written out again from the derivation (same assumptions A-FP-1 ... A-FP-3)."""
    u = Fraction(1, 2**53)
    uf = Fraction(tt.LIBM_ULP, 2**52)
    a, e2 = Fraction(m.A_WGS84), Fraction(m.E2_WGS84)
    root = sqrt_lo(1 - e2)
    b = a * root
    g3 = 3 * u / (1 - 3 * u)
    # E1: final height formula at the returned latitude
    t1 = (1 + uf) ** 2 * (1 + u) - 1  # fl(hypot) fl(cos) and the product
    lin = t1 + u * (1 + t1)  # plus the sum with fl(z sin)
    t3 = (1 + uf) ** 2 * (1 + u) ** 2 - 1  # e2 s s
    rel_w = (e2 * t3 + u * (1 + e2 * t3)) / (1 - e2)  # 1 - e2 s s, relative
    rel_sqrt = rel_w / (2 - rel_w)
    t4 = (1 + rel_sqrt) * (1 + u) ** 2 - 1  # a sqrt(.)
    # latitude iteration
    qq, qd = e2 * a / root, e2 * a / root**3
    kk = qd / (b - qq)
    nu = (1 + u) / (2 - (1 + rel_sqrt) * (1 + u)) - 1
    t5 = (1 + nu) * (1 + uf) * (1 + u) ** 2 - 1
    step = Fraction(355, 226) * ((uf * b + (t5 + u * (1 + t5)) * qq) / (b - qq) + uf)
    tail = max(kk * Fraction(1e-15) / (1 - kk), Fraction(7, 1000) ** 60 * Fraction(355, 113))
    dphi = step / (1 - kk) + tail
    lat2 = dphi**2 / 2
    alpha = (1 + u) * (lin + lat2) + u
    beta = (1 + u) * ((lin + t4) * a + (2 * a + a / root) * lat2)
    # E3-E5
    q3 = sqrt_hi(1 + g3)
    r3 = sqrt_lo(1 - g3)
    zeta = (1 + u) ** 3 / (1 - g3) - 1
    f_k = (1 + u) ** 5 / ((1 - g3) ** 2 * (1 - u) ** 3 * r3)
    f_g = (1 + u) ** 2 / ((1 - uf) * (r3 * (1 - u)) ** 3)
    f_j = f_k * (1 + u) ** 3 * (1 + 5 * zeta / 2)
    j2, mu = Fraction(m.J2_FROM_C20), Fraction(m.MU)
    return {
        "alpha": alpha,
        "beta_m": beta,
        "alpha_sel": alpha * (1 + u) + u,
        "beta_sel_m": beta * (1 + u),
        "theta_x": (1 + u) ** 2 / (1 - u) - 1,
        "F_D": (1 + uf) * (1 + u) ** 12 * q3 * (1 + u) / (1 - u) ** 2,
        "F_g": f_g,
        "F_J": f_j,
        "gravity_hat_mps2": (1 + u) * max(f_g, f_j) * (mu / b**2 + 3 * j2 * mu * a**2 / b**4),
        "contraction_k": kk,
        "lat_error_rad": dphi,
    }


def test_r3f1_derivation_constants_are_recomputed_by_a_second_implementation():
    ref = recomputed_constants()
    for key, val in ref.items():
        got = Fraction(tt.FP[key])
        assert got >= val * (1 - Fraction(1, 10**12)), key  # not below the derivation
        assert got <= val * (1 + Fraction(1, 10**9)) + Fraction(1, 10**300), key  # no padding
    assert 5e-9 < tt.FP["beta_m"] < 2e-8  # metres: dominated by about 13 u a
    assert tt.FP["contraction_k"] < 0.0069


# ------------------------------------------------------------- oracle independence
def test_oracles_agree():
    rng = np.random.default_rng(404)
    pts = [np.array([m.A_WGS84 + 1.0, 0.0, 0.0]), np.array([0.0, 0.0, m.B_WGS84 + 5.0e5])]
    pts.append(REVIEWER_R)
    for k in range(200):
        lat = rng.uniform(-1.57, 1.57) if k % 4 else math.pi / 2 - 10.0 ** rng.uniform(-10, -3)
        pts.append(m.geodetic_to_cartesian(lat, rng.uniform(-3.1, 3.1), rng.uniform(1.0, 2.0e6)))
    for r in pts:
        assert abs(o.true_height(r) - vermeille_height(r)) < D("1e-25"), r


def test_oracle_detects_the_r3f1_defect():
    """Self-test: with oracle heights the defective reference envelope is exceeded at true
    heights above its lower limit (120 km reviewer point, 200 km, 250 km). An oracle that
    returned the model's height would place these points below the limit and miss it."""
    hits = 0
    pts = [(REVIEWER_R, REVIEWER_V, 120_000)]
    for km in (200, 250):
        pts += [(c["r"], c["v"], km * 1000) for c in crossing_cases(km, want=1)]
    for r, v, low in pts:
        if o.true_height(r) >= D(low) and model_drag_norm(r, v) > defective_envelope(
            D(low), 11_000.0, B_V1
        ):
            hits += 1
    assert hits == 3


def test_oracle_does_not_use_the_model_height_or_band_code():
    tree = ast.parse((HERE / "t0_oracle.py").read_text())
    used = {
        n.attr
        for n in ast.walk(tree)
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "m"
    }
    assert used <= {"A_WGS84", "E2_WGS84", "OMEGA_E", "TABLE_COPY", "TABLE_SHA256", "sha256"}
    assert used >= {"A_WGS84", "E2_WGS84"}


def test_review02_adversarial_check_no_longer_adapts_its_bound_to_the_model_height():
    src = (HERE / "check_review02.py").read_text()
    body = src[src.index("def test_r2f2_envelope_bounds_adversarial_drag_points") :]
    body = body[: body.index("\ndef ", 10)]
    assert "h_model" not in body and not re.search(r"(?<![\w.])height\(r\)", body)
    assert "o.true_height(r)" in body


# --------------------------------------------------------------- stage condition
def floors() -> dict[str, float]:
    rows = results("termination")["sufficient_stage_condition"]["rows"]
    return {r["vehicle"]: r["h_f_sufficient_at_least_m"] for r in rows}


VEHICLES = {"B25.8": B_V1, "B100": 100.0, "drag-free limit": math.inf}


def env_second(low: Fraction, s: Fraction, b: float, c: dict) -> Fraction:
    """Second implementation of the corrected envelope (oracle table and band rule)."""
    if math.isinf(b):
        return Fraction(0)
    one = Fraction(1)
    ell = max((one - c["alpha_sel"]) * low - c["beta_sel_m"], Fraction(0))
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
    return best * c["F_D"] / (2 * Fraction(b))


def need_second(h0: float, b: float, c: dict) -> Fraction:
    u = Fraction(1, 2**53)
    h = Fraction(h0)
    big = (h - c["beta_m"]) / (1 + c["alpha"])
    r0 = Fraction(m.A_WGS84) + (h + c["beta_m"]) / (1 - c["alpha"])
    vv = 2 * Fraction(m.MU) / (Fraction(m.A_WGS84) * sqrt_lo(1 - Fraction(m.E2_WGS84)) + big)
    v = sqrt_hi(vv)
    g = c["gravity_hat_mps2"]
    a0 = (1 + u) * (g + env_second(big, v, b, c))
    l2 = big - 5 * (1 + u) ** 2 * v - u * r0
    s2 = (1 + u) * v + 5 * (1 + u) ** 2 * a0
    l3 = big - 5 * (1 + u) ** 2 * s2 - u * r0
    m2 = (1 - c["alpha"]) * l2 - c["beta_m"]
    m3 = (1 - c["alpha"]) * l3 - c["beta_m"]
    if m2 <= 0:
        return -m2
    a2 = (1 + u) * (g + env_second(l2, s2, b, c))
    l4 = big - 10 * (1 + u) ** 2 * ((1 + u) * v + 5 * (1 + u) ** 2 * a2) - u * r0
    return -min(m2, m3, (1 - c["alpha"]) * l4 - c["beta_m"])


@pytest.mark.parametrize("vehicle", sorted(VEHICLES))
def test_r3f1_floors_recomputed_by_a_second_implementation(vehicle):
    c = recomputed_constants()
    b = VEHICLES[vehicle]
    got = floors()[vehicle]
    assert need_second(got, b, c) < 0  # the published floor satisfies the condition
    lo, hi = got - 1.0, got
    assert need_second(lo, b, c) > 0
    while hi - lo > 1e-6:
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if need_second(mid, b, c) < 0 else (mid, hi)
    assert abs(hi - got) <= 3e-6, (vehicle, hi, got)


def test_r3f1_floors_are_unchanged_at_the_quoted_precision():
    quoted = {"B25.8": "124 456.69", "B100": "118 633.51", "drag-free limit": "111 511.96"}
    for vehicle, text in quoted.items():
        assert f"{floors()[vehicle]:,.2f}".replace(",", " ") == text


def stress_states(vehicle: str, b: float):
    """Near-escape, retrograde equatorial and straight-down bound states (computed height
    >= floor), plus straight-down states whose k2 input lands near a downward jump."""
    floor = floors()[vehicle]
    rng = np.random.default_rng(505)
    out = []
    for i in range(90):
        h0 = floor + rng.uniform(1e-6, 2_000.0)
        lat = 0.0 if i % 3 == 1 else rng.uniform(-1.5, 1.5)
        lon = rng.uniform(-math.pi, math.pi)
        out.append((lat, lon, h0, ("random", "retrograde", "down")[i % 3]))
    for km in (200, 250, 450, 600):  # k2 input of a straight-down near-escape step ~ at km
        h0 = km * 1000.0 + 5.0 * math.sqrt(2 * m.MU / (m.A_WGS84 + km * 1000.0))
        for _ in range(3):
            out.append((rng.uniform(-0.01, 0.01), rng.uniform(-math.pi, math.pi), h0, "down"))
    return out, rng


@pytest.mark.parametrize("vehicle", sorted(VEHICLES))
def test_r3f1_rk4_stages_satisfy_the_corrected_bounds_with_oracle_heights(vehicle):
    b = VEHICLES[vehicle]
    cfg = m.Config(j2=m.J2_FROM_C20) if math.isinf(b) else J2_DRAG
    mass = MASS if math.isinf(b) else b * 2.2 * 15.0
    states, rng = stress_states(vehicle, b)
    for lat, lon, h0, kind in states:
        r0 = m.geodetic_to_cartesian(lat, lon, h0)
        vesc = math.sqrt(2.0 * m.MU / float(np.linalg.norm(r0)))
        speed = vesc * (1.0 - 10.0 ** rng.uniform(-7.0, -3.0))
        if kind == "random":
            d = rng.normal(size=3)
        elif kind == "retrograde":
            d = np.array([math.sin(lon), -math.cos(lon), 0.0])
        else:
            d = -np.array(
                [math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat)]
            )
        v0 = speed * d / np.linalg.norm(d)
        assert 0.5 * float(v0 @ v0) - m.MU / float(np.linalg.norm(r0)) < 0.0
        y0 = np.r_[r0, v0, mass]
        h0c = model_height(r0)
        lim = tt.stage_lower_heights(h0c, b)
        assert o.true_height(r0) >= D(lim["H0"])
        stages: list = []
        m.rk4_step(m.rhs(cfg), 0.0, y0, DT, stages)  # raises if a stage leaves the domain
        for st, lk, mk in zip(stages, ("L2", "L3", "L4"), ("M2", "M3", "M4"), strict=True):
            assert o.true_height(st.r) >= D(lim[lk]), (vehicle, kind, lk)
            assert model_height(st.r) >= lim[mk], (vehicle, kind, mk)
        a0 = float(np.linalg.norm(m.acceleration(cfg, 0.0, r0, v0, mass)))
        y2 = y0 + 0.5 * DT * m.rhs(cfg)(0.0, y0)
        a2 = float(np.linalg.norm(m.acceleration(cfg, 0.0, y2[:3], y2[3:6], mass)))
        assert a0 <= lim["A0"] and a2 <= lim["A2"]
        assert float(np.linalg.norm(y2[3:6])) <= lim["s2"]


# -------------------------------------------------------------- provenance, records
def test_provenance_rerun_reproduces_the_committed_height_error_results(tmp_path):
    out = tmp_path / "t0_height_error_results.json"
    subprocess.run(
        [sys.executable, str(HERE / "t0_height_error.py"), str(out)],
        cwd=HERE,
        check=True,
        capture_output=True,
    )
    assert out.read_bytes() == (HERE / "t0_height_error_results.json").read_bytes()


def test_records_state_the_correction_and_its_assumptions():
    for name in ("DR-0029", "VAL-0019", "report", "README", "review03"):
        text = record(name)
        assert "R3-F1" in text, name
    dr = record("DR-0029")
    for phrase in ("computed height", "A-FP-2", "2^-52", "ε_h"):
        assert phrase in dr, phrase
    assert "the supremum is attained at L or at a band base above L" not in dr
