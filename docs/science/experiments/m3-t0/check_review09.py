"""Regression checks for the M3 T0 Review 09 findings M3T0-R9-F1 and M3T0-R9-F2
(research only).

R9-F1 is a verification gap: a mutant of `stage_need` that keeps M3 in the stage minimum
only when M3 = -inf (it returns -min(M2, M4) when M3 is finite) passed all 288 earlier
checks. The Review 08 regression made M3 the binding term only through M3 = -inf, and its
finite control always had M4 < M3. With an injected envelope (a propagation test, not a
physical force) of 1e8 at the first call (A0) and 0 after it, at h0 = 200 km and b = B_V1
(the Review 09 counterexample), M3 is finite, negative and the minimum: the committed code
returns need = -M3 > 0 (not certified) and the mutant returns -M4 < 0 (a false
certification). With the default envelope M4 is the minimum at every height checked here
(and in a sampled sweep of all three vehicles), and the published results regenerate byte
for byte with M3 dropped (Review 08), so no published value is decided by M3.

R9-F2 is a reference-precision defect: `check_review08.py` took A (1 - F) as the exact
polar radius of the model. The model's geodetic height (`geodetic_iterative`, a =
A_WGS84, e2 = E2_WGS84) is z - a sqrt(1 - e2) at the pole, and `t0_oracle` uses
B2 = a^2 (1 - e2): the model's ellipsoid is the one defined by the binary64 a and e2, with
polar radius b = a sqrt(1 - e2) (irrational; b^2 is exact). That radius exceeds A (1 - F)
by 2.4767e-13 m, so the mathematical height of [0, 0, fl(b)] is -2.0373635292484448e-10 m
(-2.04e-10 m), not -2.0348868076669469e-10 m. No classification, floor or certification
changes.

The checks call the production `stage_lower_heights` and `stage_need`, with the force bound
injected through their `envelope` argument (every consumer uses the same code path); they
never re-implement the stage minimum. Each need is classified as a certification (finite,
< 0), a finite non-certification (finite, >= 0) or the non-certification +inf. Expected
values come from the Review 09 report, from the signs of the stage bounds, and from exact
rational and 80-digit decimal arithmetic on the binary64 constants, never from the
implementation under test. `mutation_check_review02.py` runs these checks on corrupted
copies. Not collected by the project test suite. Run:
  uv run --no-sync pytest -q docs/science/experiments/m3-t0/check_review09.py
"""

from __future__ import annotations

import math
import re
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_review04 as c4  # noqa: E402
import check_review08 as c8  # noqa: E402
import t0_model as m  # noqa: E402
import t0_oracle as o  # noqa: E402
import t0_termination as tt  # noqa: E402

ROOT = HERE.parents[3]
B_V1 = c4.VEHICLES["B25.8"]
ULP = 2.0**-30  # the binary64 spacing at fl(b)


def first_call(value: float):
    """An injected envelope (a propagation test, not a physical force): `value` at the
    first call (A0) and 0 at every later call (A2)."""
    calls = []

    def env(low, s, b):
        calls.append(low)
        return value if len(calls) == 1 else 0.0

    return env


def classify(need: float) -> str:
    """The three outcomes of the stage condition (certified iff need < 0)."""
    if need == math.inf:
        return "infinite non-certification"
    assert math.isfinite(need), need
    return "certification" if need < 0.0 else "finite non-certification"


# ------------------------------------------------------------------- R9-F1
def test_r9f1_review09_counterexample():
    """Detects: M3 dropped from the minimum when it is finite. The Review 09 values (h0 =
    200 km, B_V1, envelope 1e8 then 0): M2 = 144 867.2696173568, M3 = -2 499 855 380.144757,
    M4 = 89 239.71048326683; the committed code returns need = +2 499 855 380.144757 and the
    finite-only mutant returns -89 239.71048326683, a false certification."""
    s = tt.stage_lower_heights(2e5, B_V1, envelope=first_call(1e8))
    assert s["M2"] == 144867.2696173568
    assert s["M3"] == -2499855380.144757
    assert s["M4"] == 89239.71048326683
    need = tt.stage_need(2e5, B_V1, envelope=first_call(1e8))
    assert need == 2499855380.144757 == -s["M3"], f"need = {need!r}"
    assert classify(need) == "finite non-certification", f"need = {need!r}"
    assert not need < 0.0
    # what an omitted M3 yields here: -M4 < 0 would certify a step whose k3 input may lie
    # 2.5e9 m below the edge (the regression above is what fails under that mutant)
    assert -min(s["M2"], s["M4"]) == -89239.71048326683 < 0.0


# (h0, first-call envelope) cases in which a finite M3 is the strict minimum
M3_BINDING = [
    (h0, first)
    for h0 in (2e5, 1e6, 1e7)
    for first in (1e4, 1e5, 1e6, 1e7, 1e8)
    if not (h0 == 2e5 and first == 1e8)  # the counterexample above
]


@pytest.mark.parametrize(("h0", "first"), M3_BINDING)
def test_r9f1_finite_m3_minimum_decides_need(h0, first):
    """Detects: a finite M3 dropped or ignored. When a finite M3 is the strict minimum,
    need = -M3 exactly. If M3 < 0 the step is not certified (the omission would certify
    it); if M3 > 0 it is certified with the M3 margin (the omission would overstate it)."""
    s = tt.stage_lower_heights(h0, B_V1, envelope=first_call(first))
    assert math.isfinite(s["M3"]) and s["M3"] < s["M2"] and s["M3"] < s["M4"], s
    need = tt.stage_need(h0, B_V1, envelope=first_call(first))
    assert need == -s["M3"], f"need = {need!r}, -M3 = {-s['M3']!r}"
    expected = "finite non-certification" if s["M3"] < 0.0 else "certification"
    assert classify(need) == expected, f"need = {need!r}"
    assert need != -min(s["M2"], s["M4"])  # the omission gives a different value here


def test_r9f1_m3_minimum_cases_cover_both_signs():
    """Detects: the case grid losing either sign of the binding finite M3."""
    signs = set()
    for h0, first in M3_BINDING:
        m3 = tt.stage_lower_heights(h0, B_V1, envelope=first_call(first))["M3"]
        signs.add(m3 > 0.0)
    assert signs == {True, False}


def test_r9_three_outcomes_distinguished():
    """Detects: +inf, a finite positive need and a certification confused. At h0 = 200 km
    and B_V1: an envelope +inf at A0 gives need = +inf; 1e8 at A0 gives a finite need > 0
    (= -M3); a constant envelope of 1 gives need < 0 (= -M4)."""
    inf_need = tt.stage_need(2e5, B_V1, envelope=first_call(math.inf))
    fin_need = tt.stage_need(2e5, B_V1, envelope=first_call(1e8))
    cert = tt.stage_need(2e5, B_V1, envelope=lambda low, sp, b: 1.0)
    assert classify(inf_need) == "infinite non-certification"
    assert classify(fin_need) == "finite non-certification" and fin_need > 0.0
    assert classify(cert) == "certification" and cert < 0.0
    s = tt.stage_lower_heights(2e5, B_V1, envelope=lambda low, sp, b: 1.0)
    assert cert == -s["M4"] and s["M4"] < s["M3"]


@pytest.mark.parametrize("h0", [124456.68544510857, 1.3e5, 2e5, 1e6, 1e7])
def test_r9f1_default_envelope_m4_is_the_minimum(h0):
    """Records why no committed check saw R9-F1: with the default envelope, M4 < M3 < M2
    at the B25.8 floor and above, so M3 never decides a published need."""
    s = tt.stage_lower_heights(h0, B_V1)
    assert s["M4"] < s["M3"] < s["M2"], s


# ------------------------------------------------------------------- R9-F2
def model_polar_radius() -> Decimal:
    """b = a sqrt(1 - e2) of the binary64 a and e2, to 80 digits."""
    with localcontext() as ctx:
        ctx.prec = 80
        return (Decimal(m.A_WGS84) * Decimal(m.A_WGS84) * (1 - Decimal(m.E2_WGS84))).sqrt()


def test_r9f2_model_polar_radius_is_a_sqrt_1_minus_e2():
    """Detects: a misidentified model ellipsoid. At the pole `geodetic_iterative` returns
    z - fl(a sqrt(1 - e2)) (latitude pi/2, sin = 1), and fl(a sqrt(1 - e2)) = fl(b); the
    flattening-defined radius A (1 - F) is a different ellipsoid, 2.4767e-13 m smaller."""
    b64 = m.A_WGS84 * math.sqrt(1.0 - m.E2_WGS84)
    assert b64 == m.B_WGS84
    for z in (m.B_WGS84, m.B_WGS84 + 10 * ULP, m.B_WGS84 + 1e5, m.B_WGS84 + 1e6):
        lat, h = m.geodetic_iterative(np.array([0.0, 0.0, z]))
        assert lat == math.pi / 2 and h == z - b64, (z, h)
    assert m.E2_WGS84 == m.F_WGS84 * (2.0 - m.F_WGS84)
    with localcontext() as ctx:
        ctx.prec = 80
        b_f = Decimal(m.A_WGS84) * (1 - Decimal(m.F_WGS84))
        diff = model_polar_radius() - b_f
    assert Decimal("2.47672e-13") < diff < Decimal("2.47673e-13"), diff


def test_r9f2_pole_reference_matches_the_model_ellipsoid():
    """Detects: the pole reference of `check_review08.py` off the model's ellipsoid (for
    example A (1 - F) restored). Its exact b^2 equals a^2 (1 - e2), agrees with the
    oracle's B2, and its heights equal the 80-digit model heights and the oracle's."""
    assert Fraction(m.A_WGS84) ** 2 * (1 - Fraction(m.E2_WGS84)) == c8.B2_EXACT
    with localcontext() as ctx:
        ctx.prec = 80
        b2 = Decimal(c8.B2_EXACT.numerator) / Decimal(c8.B2_EXACT.denominator)
        assert abs(b2 - o.B2) <= o.B2 * Decimal("1e-58")
    b = model_polar_radius()
    for k in range(0, 13):
        r, h_math = c8.pole(k)
        with localcontext() as ctx:
            ctx.prec = 80
            expect = Decimal(float(r[2])) - b
        assert abs(h_math - expect) <= Decimal("1e-40"), (k, h_math, expect)
        if k >= 1:
            assert abs(o.true_height(r) - expect) <= Decimal("1e-30"), k  # oracle: 60 digits
    shift = c8.pole(0)[1]
    assert Decimal("-2.03737e-10") < shift < Decimal("-2.03736e-10"), shift
    assert f"{shift:.2e}" == "-2.04e-10"
    with pytest.raises(ValueError, match="inside the ellipsoid"):
        o.true_height(c8.pole(0)[0])  # [0, 0, fl(b)] is inside on the oracle's ellipsoid too


def test_r9f2_docstrings_quote_the_model_ellipsoid():
    """Detects: the -2.03e-10 m (A (1 - F)) quotation restored in the stage-condition or
    pole-check docstring."""
    doc = c8.norm(tt.stage_lower_heights.__doc__)
    assert "(mathematical height -2.04e-10 m on the model ellipsoid, polar radius" in doc
    assert "a sqrt(1 - e2); corrected after Review 09 M3T0-R9-F2" in doc
    assert "-2.03e-10" not in doc
    pole_doc = c8.norm(c8.test_r8f1_computed_height_differs_from_mathematical_at_the_pole.__doc__)
    assert "-2.04e-10 m" in pole_doc and "-2.03e-10" not in pole_doc


def test_r9_records_amended():
    """Detects: R9-F1 or R9-F2 unrecorded, or a historical record rewritten instead of
    amended."""
    old = "(mathematical height −2.03e-10 m)"
    for name, header in (
        ("M3-T0-review-07.md", "### Amendment 2 (Authorization I-12, Review 09 M3T0-R9-F2)"),
        ("M3-T0-review-08.md", "### Amendment (Authorization I-12, Review 09 M3T0-R9-F2)"),
    ):
        text = (ROOT / "docs/reviews" / name).read_text()
        at = text.index(header)
        assert text[:at].count(old) == 1, name  # the original sentence, preserved above
        tail = text[at:]
        for phrase in ("−2.04e-10 m", "a·√(1 − e2)", "A·(1 − F)", "2.48e-13 m"):
            assert phrase in tail, (name, phrase)
    rev9 = (ROOT / "docs/reviews/M3-T0-review-09.md").read_text()
    corr = rev9.index("## Correction pass (Authorization I-12")
    assert "**Verdict:** **`VERDICT: PASS (unconditional)`**" in rev9[:corr]
    for fid in ("M3T0-R9-F1", "M3T0-R9-F2"):
        assert fid in rev9[corr:], fid
    val = c4.record("VAL-0019")
    log = re.search(
        r"<!-- review09-correction-log -->.*<!-- /review09-correction-log -->", val, re.S
    )
    assert log and "M3T0-R9-F1" in log.group(0) and "M3T0-R9-F2" in log.group(0)
    body = val[: log.start()] + val[log.end() :]
    amended = body.index("Amended after Review 09 M3T0-R9-F2")
    assert body[:amended].count(old) == 1  # the Review 08 qualification kept as written
    assert "−2.04e-10 m" in body[amended:] and "a·√(1 − e2)" in body[amended:]
    assert "check_review09.py" in val and "check_review09.py" in c4.record("README")
    rep = c4.record("report")
    assert "R9-F1: a finite M3 that is the minimum decides need" in rep
