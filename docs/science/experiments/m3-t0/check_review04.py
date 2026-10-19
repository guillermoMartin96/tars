"""Regression checks for the M3 T0 Review 04 finding M3T0-R4-F1 (research only).

R4-F1: the Review 03 drag envelope assumed the relative rounding model fl(x op y) = (x op
y)(1 + d) for every result. It fails for subnormal results. Above about 181 890 km the
table density is subnormal, and at 190 681 km the model's computed drag is 2.01 times the
envelope: the coefficient's last division rounds 0.51 x 2^-1074 up to 2^-1074. The
correction (`t0_termination.rounding_allowances`, E1-E6) carries the absolute errors of
underflowing results (<= 2^-1075 per * or /, <= LIBM_ULP 2^-1074 per libm call) and adds
an absolute part to the envelope, bounded over every selection height at which the
computed density can be nonzero (h_zero, above which it is exactly 0).

Expected values come from `t0_oracle` (exact heights and decimal table densities), never
from the model. Each check states the defect it detects:
- the reviewer's counterexample: the absolute part is missing or too small;
- the normal-to-subnormal transition scan, and the binary64 neighbours of the smallest-
  normal and rounding-to-zero boundaries: the absolute part is missing, too small, or not
  maximised over the right heights;
- the zero-density height: h_zero placed below the true onset of zero density;
- every band base, both sides, binary64 neighbours: a band candidate missing or the wrong
  band at a base (all 27 bases, not only the 12 downward jumps of `check_review03.py`);
- the height-error bound at high altitude: the selection uncertainty (alpha h) too small;
- RK4 stages from high-altitude retrograde, near-escape and straight-down bound states:
  a stage force above the bound the stage condition uses;
- the three floors and the libm sensitivity by a second implementation, the floors
  unchanged against the values reviewed in Review 04, and the 2-decimal quotation;
- the derived underflow constants recomputed by a second implementation;
- the platform's IEEE gradual underflow (A-FP-1) on the model's own operations, and its
  exp accuracy for subnormal results (A-FP-2; a measurement, not a proof);
- a static guard that the stage condition uses the corrected envelope.

`mutation_check_review02.py` runs these checks (with those of Reviews 01 to 03) on
corrupted copies of the scripts. Not collected by the project test suite. Run explicitly:
  uv run --no-sync pytest -q docs/science/experiments/m3-t0/check_review04.py
"""

from __future__ import annotations

import inspect
import json
import math
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
getcontext().prec = 60
ROOT = HERE.parents[3]
DT = 10.0
CD, AREA = 2.2, 15.0
DRAG = m.Drag(cd=CD, area_m2=AREA)
J2_DRAG = m.Config(j2=m.J2_FROM_C20, drag=DRAG)
VEHICLES = {"B25.8": 850.0 / (CD * AREA), "B100": 100.0, "drag-free limit": math.inf}
MASSES = {"B25.8": 850.0, "B100": 100.0 * CD * AREA}
TINY = D(math.ulp(0.0))  # 2^-1074 exactly
R4_R = np.array([197_059_137.0, 0.0, 0.0])
# The floors reviewed in Review 04 (`44260ef`, t0_termination_results.json), typed from
# that record: the correction must not move them.
REVIEWED_FLOORS = {
    "B25.8": 124456.68544510857,
    "B100": 118633.50894662621,
    "drag-free limit": 111511.96182508787,
}


def results(name: str) -> dict:
    return json.loads((HERE / f"t0_{name}_results.json").read_text())


def record(name: str) -> str:
    paths = {
        "DR-0029": ROOT / "docs/decisions/requests/DR-0029-m3-t0-proposals.md",
        "report": ROOT / "docs/milestones/M3-T0-report.md",
        "README": HERE / "README.md",
        "review04": ROOT / "docs/reviews/M3-T0-review-04.md",
    }
    if name == "VAL-0019":
        text = (ROOT / "docs/science/validation.md").read_text()
        text = text[text.index("## VAL-0019") :]
        nxt = text.find("\n## VAL-", 10)
        text = text if nxt < 0 else text[:nxt]
    else:
        text = paths[name].read_text()
    return text


# ------------------------------------------------------------- independent helpers
def model_height(r) -> float:
    return m.geodetic_iterative(r)[1]


def model_density(r) -> float:
    return m.density(model_height(r))


def model_drag_norm(r, v, mass: float) -> D:
    """Exact norm of the model's binary64 drag vector (mu = 0 and J2 off make gravity 0)."""
    vec = m.acceleration(m.Config(mu=0.0, drag=DRAG), 0.0, r, v, mass)
    with localcontext() as c:
        c.prec = 60
        return sum(D(float(x)) ** 2 for x in vec).sqrt()


def up(x: float) -> float:
    return x if x == 0.0 else math.nextafter(x, math.inf)


def east(lon: float) -> np.ndarray:
    return np.array([-math.sin(lon), math.cos(lon), 0.0])


def relative_only_reference(r, v, mass: float) -> D:
    """A reference copy of the R4-F1 defect, written here: the exact drag at the true height
    (oracle) times 1 + 1e-12, i.e. any purely relative enclosure of the force. The model's
    subnormal arithmetic exceeds it where the R4-F1 defect matters."""
    return o.drag(r, v, mass, CD, AREA) * (1 + D("1e-12"))


def scan_points(rng, h_lo: float, h_hi: float, n: int):
    """(r, v) at heights uniform in [h_lo, h_hi]: equatorial, near-equatorial and global
    positions; zero, retrograde (near escape and 11 km/s), straight-down near-escape and
    random 11 km/s velocities."""
    out = []
    for k in range(n):
        h = rng.uniform(h_lo, h_hi)
        lon = rng.uniform(-math.pi, math.pi)
        lat = (0.0, rng.uniform(-1e-3, 1e-3), rng.uniform(-1.5, 1.5))[k % 3]
        r = m.geodetic_to_cartesian(lat, lon, h)
        vesc = math.sqrt(2.0 * m.MU / float(np.linalg.norm(r)))
        kind = k % 5
        if kind == 0:
            v = np.zeros(3)
        elif kind == 1:
            v = -vesc * (1.0 - 1e-6) * east(lon)
        elif kind == 2:
            v = -11_000.0 * east(lon)
        elif kind == 3:
            v = -vesc * (1.0 - 1e-6) * r / np.linalg.norm(r)
        else:
            d = rng.normal(size=3)
            v = 11_000.0 * d / np.linalg.norm(d)
        out.append((r, v))
    return out


def classify(rho: float) -> str:
    if rho == 0.0:
        return "zero"
    return "subnormal" if rho < 2.0**-1022 else "normal"


def coefficient_rounding_height(mass: float) -> float:
    """Height at which the exact coefficient 0.5 rho cd area / mass equals 0.5 x 2^-1074, so
    that the model's last division rounds it up to 2^-1074 just below (oracle density)."""
    return float(o.top_band_height(TINY * D(mass) / (D(CD) * D(AREA))))


def coefficient_flip_x(mass: float) -> float:
    """The largest equatorial x = |r| at which the model's computed drag coefficient
    0.5 rho cd area / mass is still nonzero (binary64 bisection on the model, used only to
    place test points: the intermediate subnormal roundings move it km away from the
    oracle's estimate)."""

    def coef(x: float) -> float:
        return 0.5 * model_density(np.array([x, 0.0, 0.0])) * CD * AREA / mass

    h = coefficient_rounding_height(mass)
    lo, hi = m.A_WGS84 + h - 5e4, m.A_WGS84 + h + 5e4
    assert coef(lo) > 0.0 == coef(hi)
    while math.nextafter(lo, math.inf) < hi:
        mid = lo + (hi - lo) / 2
        if mid in (lo, hi):
            break
        lo, hi = (mid, hi) if coef(mid) > 0.0 else (lo, mid)
    return lo


# ------------------------------------------------------------------ counterexample
def test_r4f1_reviewer_counterexample_is_reproduced_and_covered():
    """Detects: the envelope's absolute (underflow) part missing or too small."""
    ht = o.true_height(R4_R)
    assert ht == D(R4_R[0]) - o.A == D(190_681_000)  # exact: the foot point is (a, 0, 0)
    assert model_height(R4_R) == 190_681_000.0
    rho = o.density(ht)
    assert abs(rho - D("1.26316923236358804936e-322")) < D("1e-342")  # Review 04, decimal
    assert 0.0 < model_density(R4_R) < 2.0**-1022  # subnormal in binary64
    v = np.zeros(3)
    a = model_drag_norm(R4_R, v, MASSES["B25.8"])
    exact = o.drag(R4_R, v, MASSES["B25.8"], CD, AREA)
    assert D(2) < a / exact < D("2.015")  # the subnormal coefficient rounding (R4-F1)
    assert a > relative_only_reference(R4_R, v, MASSES["B25.8"])  # the defect
    old = D(tt.drag_envelope_relative_only(190_681_000.0, 0.0, VEHICLES["B25.8"]))
    assert abs(a / old - D("2.0149523474166813")) < D("1e-15")  # the reviewer's ratio
    assert a <= D(tt.drag_envelope(190_681_000.0, 0.0, VEHICLES["B25.8"]))  # the correction
    stored = results("termination")["sufficient_stage_condition"]["review04_counterexample"]
    assert stored["corrected_covers"] and not stored["superseded_covers"]


@pytest.mark.parametrize("vehicle", ["B25.8", "B100"])
def test_r4f1_normal_to_subnormal_transition_scan(vehicle):
    """Detects: the absolute part missing, too small, or not maximised over every height
    with nonzero computed density. Covers normal densities near 2^-1022, subnormal ones,
    the rounding-up height of the coefficient, values approaching 0 and density 0."""
    mass, b = MASSES[vehicle], VEHICLES[vehicle]
    h_n = float(o.top_band_height(D(2) ** -1022))  # exact density = smallest normal
    h_z = float(o.top_band_height(TINY / 2))  # exact density = 2^-1075
    h_c = coefficient_rounding_height(mass)
    rng = np.random.default_rng(4040 + int(b))
    pts = []
    for lo, hi, n in (
        (h_n - 3e5, h_n + 3e5, 60),
        (h_c - 5e5, h_c + 1e5, 90),
        (h_z - 3e5, h_z + 3e5, 60),
        (h_n - 1e6, h_z + 1e6, 90),
    ):
        pts += scan_points(rng, lo, hi, n)
    counts = {"normal": 0, "subnormal": 0, "zero": 0}
    near_normal = beyond = 0
    for r, v in pts:
        rho = model_density(r)
        counts[classify(rho)] += 1
        near_normal += 2.0**-1022 <= rho < 2.0**-1020
        a = model_drag_norm(r, v, mass)
        if rho == 0.0:
            assert a == 0
        low = tt._dn(o.true_height(r))
        assert a <= D(tt.drag_envelope(low, up(float(np.linalg.norm(v))), b)), (r, v)
        beyond += a > relative_only_reference(r, v, mass)
    assert min(counts.values()) >= 20, counts
    assert near_normal >= 5
    assert beyond >= 5  # the scan reproduces the R4-F1 defect


@pytest.mark.parametrize("vehicle", ["B25.8", "B100"])
def test_r4f1_binary64_neighbours_of_the_critical_boundaries(vehicle):
    """Detects the same defects at the exact boundaries: equatorial points (true height x - a
    exactly) at the binary64 neighbours of the heights where the exact density is 2^-1022
    (computed density normal or subnormal), where the model's coefficient flips between
    2^-1074 and 0 (the R4-F1 mechanism), and where the exact density is 2^-1075 (computed
    density 2^-1074 or 0)."""
    mass, b = MASSES[vehicle], VEHICLES[vehicle]
    seen = {"normal": 0, "subnormal": 0, "zero": 0}
    smallest = beyond = 0
    for x0 in (
        m.A_WGS84 + float(o.top_band_height(D(2) ** -1022)),
        coefficient_flip_x(mass),
        m.A_WGS84 + float(o.top_band_height(TINY / 2)),
    ):
        xs = [x0]
        for _ in range(40):
            xs = [math.nextafter(xs[0], 0.0), *xs, math.nextafter(xs[-1], math.inf)]
        for x in xs:
            r = np.array([x, 0.0, 0.0])
            ht = D(x) - o.A
            assert o.true_height(r) == ht or abs(o.true_height(r) - ht) < D("1e-40")
            rho = model_density(r)
            seen[classify(rho)] += 1
            smallest += rho == math.ulp(0.0)
            for s, v in ((0.0, np.zeros(3)), (11_000.0, -11_000.0 * east(0.0))):
                a = model_drag_norm(r, v, mass)
                assert a <= D(tt.drag_envelope(tt._dn(ht), s, b)), (x, s)
                beyond += a > relative_only_reference(r, v, mass)
    assert min(seen.values()) > 0 and smallest > 0, (seen, smallest)
    assert beyond > 0  # the neighbours of the coefficient flip reproduce the R4-F1 defect


def test_r4f1_zero_density_height():
    """Detects: h_zero placed below the true onset of zero density (the absolute part would
    then omit heights with nonzero force). The derived h_zero must not be below the oracle's
    exact onset, and every point whose computed selection height is above it must have
    computed density 0 and drag exactly 0."""
    h_zero = tt.FP["h_zero_m"]
    exact = o.top_band_height(TINY / 2)
    assert D(h_zero) >= exact and D(h_zero) - exact < 1, (h_zero, exact)
    rng = np.random.default_rng(4141)
    above = 0
    hs = [rng.uniform(h_zero - 2.5e6, h_zero + 2e6) for _ in range(200)]
    hs += [h_zero * f for f in (1.001, 1.5, 3.0, 10.0, 100.0)]
    for k, h in enumerate(hs):
        lat = 0.0 if k % 2 else rng.uniform(-1.5, 1.5)
        lon = rng.uniform(-math.pi, math.pi)
        r = m.geodetic_to_cartesian(lat, lon, h)
        hc = model_height(r)
        if Fraction(hc / 1000.0) * 1000 > Fraction(h_zero):  # the model's selection height
            above += 1
            assert m.density(hc) == 0.0, r
            for v in (np.zeros(3), -11_000.0 * east(lon)):
                assert model_drag_norm(r, v, MASSES["B25.8"]) == 0
    assert above >= 50
    assert (
        results("termination")["floating_point_enclosure"]["underflow"][
            "zero_density_selection_height_m"
        ]
        == h_zero
    )


# ------------------------------------------------------------- every band boundary
@pytest.mark.parametrize("base_km", [int(float(row[0]) / 1000) for row in o.TABLE])
def test_r4f1_every_band_base_both_sides_and_neighbours(base_km):
    """Detects: a band candidate missing from the envelope or the wrong band at a base
    (GMAT's rule: an exact base belongs to the band above), at every base, upward and
    downward jumps alike, and at the lower edge 0 m (true heights below 0 are outside the
    domain; a computed height below 0 must fail closed)."""
    base_d = D(base_km) * 1000
    base = float(base_d)
    x0 = m.A_WGS84 + base
    xs = [x0]
    for _ in range(3):
        xs = [math.nextafter(xs[0], 0.0), *xs, math.nextafter(xs[-1], math.inf)]
    for x in xs:  # equatorial: true height x - a exactly, equal to the computed height
        r = np.array([x, 0.0, 0.0])
        ht = D(x) - o.A
        assert D(model_height(r)) == ht
        if ht < 0:
            continue
        assert (o.band(ht) == o.band(base_d)) == (ht >= base_d)
        for s in (7_800.0, 11_000.0):
            a = model_drag_norm(r, -s * east(0.0), MASSES["B25.8"])
            assert a <= D(tt.drag_envelope(tt._dn(ht), s, VEHICLES["B25.8"])), (x, s)
            if ht >= base_d:
                assert a <= D(tt.drag_envelope(base, s, VEHICLES["B25.8"])), (x, s)
    rng = np.random.default_rng(4242 + base_km)
    below = above = 0
    for k in range(16):  # true heights just below and above the base, off the equator
        lat = rng.uniform(-0.01, 0.01) if k % 2 else rng.uniform(-1.5, 1.5)
        lon = rng.uniform(-math.pi, math.pi)
        for dh in (-1e-8, -1e-9, 0.0, 1e-9, 1e-8):
            r = m.geodetic_to_cartesian(lat, lon, base + dh)
            try:
                ht = o.true_height(r)
            except ValueError:  # at the lower edge: the binary64 point is inside the ellipsoid
                assert base == 0.0 and dh <= 0.0
                continue
            below += ht < base_d
            above += ht >= base_d
            if model_height(r) < 0.0:
                with pytest.raises(m.OutsideDomainError):
                    model_drag_norm(r, -11_000.0 * east(lon), MASSES["B25.8"])
                continue
            a = model_drag_norm(r, -11_000.0 * east(lon), MASSES["B25.8"])
            assert a <= D(tt.drag_envelope(tt._dn(ht), 11_000.0, VEHICLES["B25.8"])), r
            if ht >= base_d:
                assert a <= D(tt.drag_envelope(base, 11_000.0, VEHICLES["B25.8"])), r
    assert above and (below or base == 0.0)


def test_r4f1_height_error_bound_at_high_altitude():
    """Detects: the geodetic-height selection uncertainty (alpha h + beta, and the km
    conversion of E2) too small where alpha h dominates."""
    rng = np.random.default_rng(4343)
    worst = 0.0
    for k in range(400):
        lat = rng.uniform(-1.5707, 1.5707) if k % 4 else math.pi / 2 - 10.0 ** rng.uniform(-9, -3)
        h = 10.0 ** rng.uniform(7.0, 10.0)
        r = m.geodetic_to_cartesian(lat, rng.uniform(-math.pi, math.pi), h)
        ht, hc = o.true_height(r), model_height(r)
        err = abs(D(hc) - ht)
        assert err <= D(tt.height_error_bound(float(ht))), (r, err)
        sel = abs(D(hc / 1000.0) * 1000 - ht)  # the model's selection height, exactly
        eps_sel = tt.FPA["alpha_sel"] * Fraction(ht) + tt.FPA["beta_sel_m"]
        assert sel <= D(eps_sel.numerator) / D(eps_sel.denominator), (r, sel)
        worst = max(worst, float(err / D(tt.height_error_bound(float(ht)))))
    assert worst > 0.01


# ---------------------------------------------------------------- RK4 stages
@pytest.mark.parametrize("vehicle", ["B25.8", "B100"])
def test_r4f1_rk4_stages_at_high_altitude(vehicle):
    """Detects: a stage force above the bound the stage condition uses (A0, A2 and the drag
    envelopes at the stage's lower height and speed bounds), for retrograde, near-escape and
    straight-down bound states where the computed density is subnormal."""
    mass, b = MASSES[vehicle], VEHICLES[vehicle]
    h_c = coefficient_rounding_height(mass)
    rng = np.random.default_rng(4444 + int(b))
    beyond = 0
    for k in range(60):
        h0 = rng.uniform(h_c - 4e5, h_c + 4e4) if k % 2 else rng.uniform(1.8e8, 1.95e8)
        lat = 0.0 if k % 3 else rng.uniform(-1.5, 1.5)
        lon = rng.uniform(-math.pi, math.pi)
        r0 = m.geodetic_to_cartesian(lat, lon, h0)
        vesc = math.sqrt(2.0 * m.MU / float(np.linalg.norm(r0)))
        speed = vesc * (1.0 - 10.0 ** rng.uniform(-7.0, -3.0))
        d = (-east(lon), -r0 / np.linalg.norm(r0), rng.normal(size=3))[k % 3]
        v0 = speed * d / np.linalg.norm(d)
        assert 0.5 * float(v0 @ v0) - m.MU / float(np.linalg.norm(r0)) < 0.0
        y0 = np.r_[r0, v0, mass]
        lim = tt.stage_lower_heights(model_height(r0), b)
        assert o.true_height(r0) >= D(lim["H0"])
        stages: list = []
        m.rk4_step(m.rhs(J2_DRAG), 0.0, y0, DT, stages)
        for st, lk, mk in zip(stages, ("L2", "L3", "L4"), ("M2", "M3", "M4"), strict=True):
            assert o.true_height(st.r) >= D(lim[lk]), (vehicle, lk)
            assert model_height(st.r) >= lim[mk], (vehicle, mk)
        y2 = y0 + 0.5 * DT * m.rhs(J2_DRAG)(0.0, y0)
        for y, low, s, acc in ((y0, "H0", "V", "A0"), (y2, "L2", "s2", "A2")):
            drag = model_drag_norm(y[:3], y[3:6], mass)
            assert drag <= D(tt.drag_envelope(lim[low], lim[s], b)), (vehicle, low)
            assert (
                float(np.linalg.norm(m.acceleration(J2_DRAG, 0.0, y[:3], y[3:6], mass)))
                <= (lim[acc])
            )
            beyond += drag > relative_only_reference(y[:3], y[3:6], mass)
    assert beyond >= 3  # stage forces in this set exceed any relative-only enclosure


# ------------------------------------------------------------ second implementation
def sqrt_hi(q: Fraction) -> Fraction:
    x = Fraction(math.isqrt(math.ceil(q * 10**60)) + 1, 10**30)
    for _ in range(4):
        x = (x + q / x) / 2
        x = Fraction(math.ceil(x * 10**45), 10**45)
    return x


def sqrt_lo(q: Fraction) -> Fraction:
    return q / sqrt_hi(q)


def frac(x: D) -> Fraction:
    return Fraction(x)


def constants_second(libm_ulp: int) -> dict:
    """E1-E6 with the underflow terms, written out again from the derivation."""
    u = Fraction(1, 2**53)
    uf, nu, eta0 = Fraction(libm_ulp, 2**52), Fraction(libm_ulp, 2**1074), Fraction(1, 2**1075)
    a, e2 = Fraction(m.A_WGS84), Fraction(m.E2_WGS84)
    root = sqrt_lo(1 - e2)
    b = a * root
    g3 = 3 * u / (1 - 3 * u)
    t1 = (1 + uf) ** 2 * (1 + u) - 1
    lin = t1 + u * (1 + t1)
    t3 = (1 + uf) ** 2 * (1 + u) ** 2 - 1
    rel_w = (e2 * t3 + u * (1 + e2 * t3)) / (1 - e2)
    rel_sqrt = rel_w / (2 - rel_w)
    t4 = (1 + rel_sqrt) * (1 + u) ** 2 - 1
    qq, qd = e2 * a / root, e2 * a / root**3
    kk = qd / (b - qq)
    nu1 = (1 + u) / (2 - (1 + rel_sqrt) * (1 + u)) - 1
    t5 = (1 + nu1) * (1 + uf) * (1 + u) ** 2 - 1
    gap = b - qq
    step = Fraction(355, 226) * ((uf * b + (t5 + u * (1 + t5)) * qq) / gap + uf)
    # underflow: p's and Y's absolute errors over |v| >= b - Q, and atan2's own
    y_abs = (1 + u) ** 2 * e2 * (a / root * Fraction(1001, 1000)) * nu + (1 + u) * eta0
    eta_uf = Fraction(355, 226) * (nu + y_abs) / gap + nu
    step += eta_uf
    tail = max(kk * Fraction(1e-15) / (1 - kk), Fraction(7, 1000) ** 60 * Fraction(355, 113))
    dphi = step / (1 - kk) + tail
    lat2 = dphi**2 / 2
    f_r = (1 + u) ** 3 * nu
    f_c = (1 + u) ** 3 * (1 + uf) * nu + 2 * (1 + u) ** 2 * eta0
    f_c += a * (1 + u) ** 6 * (3 * e2 * (1 + uf) * nu + 2 * eta0) / (2 * root * (1 - rel_w))
    alpha = (1 + u) * (lin + lat2) + u + f_r
    beta = (1 + u) * ((lin + t4) * a + (2 * a + a / root) * lat2) + f_r * a + f_c
    q3, r3 = sqrt_hi(1 + g3), sqrt_lo(1 - g3)
    phi_b = (1 + u) / (1 - u) ** 2
    s_min = Fraction(m.OMEGA_E) * b
    tau = 3 * eta0 / s_min + 2 * eta0 / s_min**2 + 2 * eta0**2 / s_min**2
    zeta = (1 + u) ** 3 / (1 - g3) - 1
    f_k = (1 + u) ** 5 / ((1 - g3) ** 2 * (1 - u) ** 3 * r3)
    f_g = (1 + u) ** 2 / ((1 - uf) * (r3 * (1 - u)) ** 3)
    f_j = f_k * (1 + u) ** 3 * (1 + 5 * zeta / 2)
    j2, mu = Fraction(m.J2_FROM_C20), Fraction(m.MU)
    theta = (1 + u) ** 2 / (1 - u) - 1
    rho0_max = max(frac(row[1]) for row in o.TABLE)
    # zero-density height (top band): (1 + u) rho0 ((1 + UF)(1 + 2 eta0) e^{-(1 - theta) X}
    # + nu) < eta0 for X > X0
    rho0 = frac(o.TABLE[-1][1])
    e0 = (eta0 / ((1 + u) * rho0) - nu) / ((1 + uf) * (1 + 2 * eta0))
    with localcontext() as c:
        c.prec = 70
        th = D(theta.numerator) / D(theta.denominator)
        x0 = -(D(e0.numerator) / D(e0.denominator)).ln() / (1 - th)
        h_zero = frac(o.TABLE[-1][0] + o.TABLE[-1][2] * x0) * (1 + Fraction(1, 10**50))
    return {
        "alpha": alpha,
        "beta_m": beta,
        "alpha_sel": alpha * (1 + u) + u,
        "beta_sel_m": beta * (1 + u) + 1000 * eta0,
        "theta_x": theta,
        "F_D": (1 + uf) * (1 + u) ** 12 * q3 * phi_b * (1 + 2 * eta0) * (1 + tau),
        "F_A": (1 + u) ** 10 * q3 * phi_b * (1 + tau),
        "K_W": (1 + u) ** 7 * q3 * (1 + tau),
        "N_rho": (1 + u) ** 2 * rho0_max * nu + eta0,
        "phi_B": phi_b,
        "h_zero_m": h_zero,
        "gravity_hat_mps2": (1 + u) * max(f_g, f_j) * (mu / b**2 + 3 * j2 * mu * a**2 / b**4)
        + 4 * eta0,
        "stage_abs": 2 * eta0,
        "eta0": eta0,
        "alpha_uf": f_r,
        "beta_uf": f_r * a + f_c,
        "eta_uf": eta_uf,
        "b": b,
    }


def env_second(low: Fraction, s: Fraction, bb: float, c: dict) -> Fraction:
    """Second implementation of the corrected envelope: the relative part over the oracle's
    table and band rule, plus the absolute part at S_max."""
    if math.isinf(bb):
        return Fraction(0)
    ell = max((1 - c["alpha_sel"]) * low - c["beta_sel_m"], Fraction(0))
    best = Fraction(0)
    with localcontext() as ctx:
        ctx.prec = 70
        for h in [ell] + [frac(row[0]) for row in o.TABLE if frac(row[0]) > ell]:
            base, rho0, scale = o.TABLE[o.band(D(h.numerator) / D(h.denominator))]
            x = (h - frac(base)) / frac(scale) * (1 - c["theta_x"])
            ex = frac((-(D(x.numerator) / D(x.denominator))).exp()) * (1 + Fraction(1, 10**50))
            rad = Fraction(m.A_WGS84) + (h + c["beta_sel_m"]) / (1 - c["alpha_sel"])
            vr = s + Fraction(m.OMEGA_E) * rad
            best = max(best, frac(rho0) * ex * vr * vr)
    b = Fraction(bb)
    eta0 = c["eta0"]
    u = Fraction(1, 2**53)
    smax = s + Fraction(m.OMEGA_E) * (
        Fraction(m.A_WGS84) + (c["h_zero_m"] + c["beta_sel_m"]) / (1 - c["alpha_sel"])
    )
    cd, area = Fraction(CD), Fraction(AREA)
    w = eta0 * (1 + c["phi_B"] / b * ((1 + u) ** 3 + (1 + u) ** 2 / cd + (1 + u) / (cd * area)))
    absolute = (c["F_A"] * c["N_rho"] / (2 * b) + c["K_W"] * w) * smax**2
    absolute += (1 + u) ** 3 * eta0 * smax + 2 * eta0
    return best * c["F_D"] / (2 * b) + absolute


def need_second(h0: float, bb: float, c: dict) -> Fraction:
    u = Fraction(1, 2**53)
    h = Fraction(h0)
    big = (h - c["beta_m"]) / (1 + c["alpha"])
    r0 = Fraction(m.A_WGS84) + (h + c["beta_m"]) / (1 - c["alpha"])
    v = sqrt_hi(2 * Fraction(m.MU) / (c["b"] + big))
    g, e6 = c["gravity_hat_mps2"], c["stage_abs"]
    a0 = (1 + u) * (g + env_second(big, v, bb, c))
    l2 = big - 5 * (1 + u) ** 2 * v - u * r0 - e6
    s2 = (1 + u) * v + 5 * (1 + u) ** 2 * a0 + e6
    l3 = big - 5 * (1 + u) ** 2 * s2 - u * r0 - e6
    m2 = (1 - c["alpha"]) * l2 - c["beta_m"]
    m3 = (1 - c["alpha"]) * l3 - c["beta_m"]
    if m2 <= 0:
        return -m2
    a2 = (1 + u) * (g + env_second(l2, s2, bb, c))
    l4 = big - 10 * (1 + u) ** 2 * ((1 + u) * v + 5 * (1 + u) ** 2 * a2 + e6) - u * r0 - e6
    return -min(m2, m3, (1 - c["alpha"]) * l4 - c["beta_m"])


def test_r4f1_underflow_constants_recomputed_by_a_second_implementation():
    """Detects: an underflow term of E1-E6 removed or reduced (the density, coefficient,
    libm, gravity or stage terms, or h_zero)."""
    c = constants_second(tt.LIBM_ULP)
    tiny = Fraction(1, 2**1074)
    pairs = {
        "alpha": tt.FPA["alpha"],
        "beta_m": tt.FPA["beta_m"],
        "alpha_sel": tt.FPA["alpha_sel"],
        "beta_sel_m": tt.FPA["beta_sel_m"],
        "F_D": tt.FPA["F_D"],
        "F_A": tt.FPA["F_A"],
        "K_W": tt.FPA["K_W"],
        "N_rho": tt.FPA["N_rho_in_2^-1074"] * tiny,
        "gravity_hat_mps2": tt.FPA["gravity_hat_mps2"],
        "stage_abs": tt.FPA["stage_abs_in_2^-1074"] * tiny,
    }
    for key, got in pairs.items():
        ref = c[key]
        assert got >= ref * (1 - Fraction(1, 10**14)), key  # not below the derivation
        assert got <= ref * (1 + Fraction(1, 10**9)), key  # no padding
    # the underflow parts themselves, not only their sums with larger terms
    assert tt.FPA["N_rho_in_2^-1074"] >= Fraction(295, 100) - Fraction(1, 10**12)
    assert tt.FPA["nu_in_2^-1074"] == tt.LIBM_ULP
    assert abs(Fraction(tt.FP["h_zero_m"]) - c["h_zero_m"]) < Fraction(1, 10**6)
    assert Fraction(tt.FP["h_zero_m"]) >= c["h_zero_m"] - Fraction(1, 10**7)
    # the underflow parts themselves (far below the totals' 1e-14 agreement), exactly
    f = tt.FPA
    assert f["alpha"] == f["alpha_relative_part"] + f["alpha_underflow_part"]
    assert f["beta_m"] == f["beta_relative_part_m"] + f["beta_underflow_part_m"]
    assert (
        f["gravity_hat_mps2"] == f["gravity_relative_part_mps2"] + f["gravity_underflow_part_mps2"]
    )
    assert f["beta_sel_m"] == f["beta_m"] * (1 + f["u"]) + 1000 * c["eta0"]
    for key, ref in (
        ("alpha_underflow_part", c["alpha_uf"]),
        ("beta_underflow_part_m", c["beta_uf"]),
        ("lat_step_underflow_rad", c["eta_uf"]),
        ("gravity_underflow_part_mps2", 4 * c["eta0"]),
    ):
        assert f[key] >= ref * (1 - Fraction(1, 10**12)), key
        assert f[key] <= ref * (1 + Fraction(1, 10**9)), key


def test_r4f1_envelope_recomputed_by_a_second_implementation():
    """Detects: a term of the corrected envelope removed or reduced in its evaluation (the
    absolute part, its density, coefficient and product terms, h_zero, or the relative
    part), including terms too small for any constructed point to expose."""
    c = constants_second(tt.LIBM_ULP)
    h_zero = tt.FP["h_zero_m"]
    cases = [
        (190_681_000.0, 0.0, "B25.8"),
        (185_000_000.0, 11_000.0, "B100"),
        (h_zero - 1e5, 2_000.0, "B25.8"),
        (h_zero + 1e6, 0.0, "B25.8"),
        (120_000.0, 11_000.0, "B25.8"),
        (450_000.0, 7_800.0, "B100"),
        (0.0, 7_800.0, "B25.8"),
    ]
    for low, s, vehicle in cases:
        b = VEHICLES[vehicle]
        got = Fraction(tt.drag_envelope(low, s, b))
        ref = env_second(Fraction(low), Fraction(s), b, c)
        assert got >= ref * (1 - Fraction(1, 10**30)), (low, s, vehicle)
        assert got <= ref * (1 + Fraction(1, 10**9)) + 2 * Fraction(1, 2**1074), (low, s)


@pytest.mark.parametrize("vehicle", sorted(VEHICLES))
def test_r4f1_floors_by_a_second_implementation_and_unchanged(vehicle):
    """Detects: a floor that moved, or that no longer satisfies the corrected condition."""
    c = constants_second(tt.LIBM_ULP)
    b = VEHICLES[vehicle]
    rows = {r["vehicle"]: r for r in results("termination")["sufficient_stage_condition"]["rows"]}
    got = rows[vehicle]["h_f_sufficient_at_least_m"]
    assert got == REVIEWED_FLOORS[vehicle]  # the correction does not move the floor
    assert need_second(got, b, c) < 0
    lo, hi = got - 1.0, got
    assert need_second(lo, b, c) > 0
    while hi - lo > 1e-6:
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if need_second(mid, b, c) < 0 else (mid, hi)
    assert abs(hi - got) <= 3e-6, (vehicle, hi, got)
    cmp = {r["vehicle"]: r for r in results("termination")["floor_comparison"]["rows"]}[vehicle]
    before, after = cmp["root_bracket_review03_correction_m"], cmp["root_bracket_corrected_m"]
    assert after[1] - after[0] <= 1e-9 and lo - 1e-6 <= after[0] <= after[1] <= got
    assert abs(after[0] - before[0]) <= 1e-9 and cmp["published_unchanged"]
    nearest = round(got, 2)
    assert (need_second(nearest, b, c) < 0) == cmp["two_decimals_nearest_is_sufficient"]


def test_r4f1_two_decimal_quotation_of_the_drag_free_floor_is_below_it():
    """Disclosure check (I-5 section 3): 111 511.96 m, the drag-free floor rounded to
    nearest, is below the sufficient bound; 111 511.97 m (rounded up) satisfies it."""
    c = constants_second(tt.LIBM_ULP)
    assert need_second(111511.96, math.inf, c) > 0
    assert need_second(111511.97, math.inf, c) < 0


def test_r4f1_libm_sensitivity_by_a_second_implementation():
    """Detects: a misreported weakening of A-FP-2. At the stored largest LIBM_ULP = 2^j the
    published floor holds, and at 2^(j + 1) it fails."""
    sens = results("termination")["libm_sensitivity"]
    assert sens["assumed_libm_ulp"] == tt.LIBM_ULP == 2
    for row in sens["rows"]:
        b = VEHICLES[row["vehicle"]]
        for key in ("published_bracket_end", "two_decimals_rounded_up"):
            h, j = row[key]["height_m"], row[key]["largest_log2_libm_ulp"]
            assert j is not None and j >= 1  # holds at the assumed LIBM_ULP = 2
            assert need_second(h, b, constants_second(2**j)) < 0, (row["vehicle"], key, j)
            if j < sens["max_log2_tested"]:
                assert need_second(h, b, constants_second(2 ** (j + 1))) >= 0, (row, key)


# --------------------------------------------------------- platform assumptions
def ieee(q: Fraction) -> float:
    """Round an exact rational to binary64 by IEEE 754 round-to-nearest-even with gradual
    underflow (written here; the platform's result must equal it)."""
    if q == 0:
        return 0.0
    sign, q = (-1 if q < 0 else 1), abs(q)
    e = q.numerator.bit_length() - q.denominator.bit_length()
    if Fraction(2) ** e > q:
        e -= 1
    quantum = Fraction(2) ** max(e - 52, -1074)
    n = q / quantum
    k = math.floor(n)
    rem = n - k
    if rem > Fraction(1, 2) or (rem == Fraction(1, 2) and k % 2 == 1):
        k += 1
    return sign * float(k * quantum)


def test_platform_gradual_underflow_on_the_model_operations():
    """A-FP-1 on the running platform: the drag coefficient chain and the force products at
    the R4-F1 point (all subnormal) equal IEEE round-to-nearest with gradual underflow, and
    no flush-to-zero mode is active (Python floats and numpy)."""
    rho = model_density(R4_R)
    assert rho == ieee(
        Fraction(m.TABLE[-1].rho0)
        * Fraction(
            math.exp(-((model_height(R4_R) / 1000.0 - m.TABLE[-1].base_km) / m.TABLE[-1].scale_km))
        )
    )
    c1 = 0.5 * rho
    c2 = c1 * CD
    c3 = c2 * AREA
    k = c3 / MASSES["B25.8"]
    for got, exact in (
        (c1, Fraction(1, 2) * Fraction(rho)),
        (c2, Fraction(c1) * Fraction(CD)),
        (c3, Fraction(c2) * Fraction(AREA)),
        (k, Fraction(c3) / Fraction(MASSES["B25.8"])),
    ):
        assert got == ieee(exact)
    assert k == math.ulp(0.0)  # 0.51 x 2^-1074 rounded up: the R4-F1 mechanism
    vrel = np.array([0.0, m.OMEGA_E * R4_R[0], 0.0])
    kn = k * math.sqrt(float(vrel @ vrel))
    prod = kn * vrel
    assert kn == ieee(Fraction(k) * Fraction(math.sqrt(float(vrel @ vrel))))
    assert float(prod[1]) == ieee(Fraction(kn) * Fraction(vrel[1]))
    assert math.ulp(0.0) * 0.5 == 0.0 and 2.0**-1022 / 2 == 2.0**-1023
    assert float(np.float64(2.0**-1022) * np.float64(0.5)) == 2.0**-1023
    assert float(np.array([3 * math.ulp(0.0)]) @ np.array([0.5])) == 2 * math.ulp(0.0)


def test_platform_exp_accuracy_for_subnormal_results():
    """A-FP-2's absolute term on the running platform, sampled (a measurement, not a proof):
    |exp(x) - exact| <= LIBM_ULP 2^-1074 where the exact value is subnormal or rounds to 0;
    and the committed measurement of `t0_height_error.py`."""
    rng = np.random.default_rng(4545)
    worst = D(0)
    for x in np.r_[rng.uniform(-745.2, -708.39, 1500), np.linspace(-745.2, -708.39, 301)]:
        x = float(x)
        worst = max(worst, abs(D(math.exp(x)) - D(x).exp()) / TINY)
    assert worst <= tt.LIBM_ULP, worst
    sub = results("height_error")["libm"]["subnormal_results"]
    assert sub["within_assumption"] and sub["gradual_underflow"]
    assert sub["assumed_abs_bound_in_2^-1074"] == tt.LIBM_ULP


def test_stage_condition_uses_the_corrected_envelope():
    """Static guard (the superseded envelope gives the same floors to the last bit, since
    the absolute part is about 1e-315 m/s^2 against G ~ 9.9 m/s^2, so no numerical check can
    see it): stage_lower_heights defaults to `drag_envelope`, and the floors are computed
    with that default."""
    src = inspect.getsource(tt.stage_lower_heights)
    assert "drag_envelope(low, s, b, fp=fp)) if envelope is None" in src
    assert "relative_only" not in src
    body = inspect.getsource(tt.sufficient_stage_condition)
    assert "return stage_need(h0, b)\n" in body and "envelope=" not in body


# ------------------------------------------------------------------------ records
def test_records_state_the_r4f1_correction_and_its_assumptions():
    for name in ("DR-0029", "VAL-0019", "report", "README", "review04"):
        assert "R4-F1" in record(name), name
    dr = record("DR-0029")
    for phrase in ("2^-1075", "subnormal", "gradual underflow", "LIBM_ULP", "111 511.97"):
        assert phrase in dr, phrase
    val = record("VAL-0019")
    for phrase in ("check_review04.py", "2^-1074"):
        assert phrase in val, phrase
