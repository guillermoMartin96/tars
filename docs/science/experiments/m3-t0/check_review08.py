"""Regression checks for the M3 T0 Review 08 finding M3T0-R8-F1 and the M3 coverage gap
(research only).

R8-F1 is a documentation defect: the stage condition's documentation stated a finite
need(h0) on the M2 <= 0 path and for the drag-free vehicle without the precondition
h0 > beta, and the Review 07 correction record said a computed h0 <= beta "is not the
computed height of a state in the domain (outside the ellipsoid)". Strictly exterior bound
states attain such heights: r = [nextafter(a, +inf), 0, 0] m, v = 0 has the mathematical
and the computed geodetic height 2^-30 m < beta, and `stage_need` raises ValueError there
for b = B_V1 and for b = +inf. The correction changes docstrings and records only.

The coverage gap (a Review 08 reviewer observation): replacing -min(M2, M3, M4) by
-min(M2, M4) passed all 261 earlier checks. With an envelope that is +inf at A0 only, M3 is
the only stage bound that is -inf, so dropping it turns need = +inf into a certification.

The checks distinguish four outcomes of the stage condition:
- a valid finite certification (need finite and < 0);
- the intended rejection (ValueError from the envelope's lower-edge check);
- the correct non-certification need = +inf (and the finite need >= 0 of the M2 <= 0 path);
- a false certification that omitting a required term would produce.

Contract checks pin the unchanged behaviour (they pass on the uncorrected tree too); record
checks detect the stale statements (they fail on it). Expected values come from exact
rational arithmetic on the binary64 inputs, from the binary64 grid (beta / 2^-30) and from
the reviewer's report, never from the implementation under test: the classification of each
state is decided from its computed height and beta alone. `mutation_check_review02.py` runs
these checks on corrupted copies. Not collected by the project test suite. Run:
  uv run --no-sync pytest -q docs/science/experiments/m3-t0/check_review08.py
"""

from __future__ import annotations

import decimal
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_review04 as c4  # noqa: E402
import t0_model as m  # noqa: E402
import t0_termination as tt  # noqa: E402

ROOT = HERE.parents[3]
B_V1 = c4.VEHICLES["B25.8"]
VEHICLES = (("B25.8", B_V1), ("drag-free", math.inf))
BETA = tt.FP["beta_m"]  # E1's absolute height-error term (derived and checked in Review 03)
ULP = 2.0**-30  # the binary64 spacing at a and at b: both lie in [2^22, 2^23)
EDGE_MSG = "the envelope is defined above the lower edge only"
# a binary64 h0 makes H0 = (h0 - beta)/(1 + alpha) - 1e-35 < 0 exactly when h0 <= beta, so
# along the equator the last raising point is k = floor(beta / 2^-30) = 9 (Review 08: k = 1)
K_LAST_RAISING = math.floor(Fraction(BETA) / Fraction(ULP))
A = Fraction(m.A_WGS84)
B_EXACT = A * (1 - Fraction(m.F_WGS84))  # the model's ellipsoid, in exact arithmetic


def computed_height(r: np.ndarray) -> float:
    return m.HEIGHTS["geodetic"](r)  # the height the simulator commits


def equator(k: int) -> tuple[np.ndarray, Fraction]:
    """r = [a + k 2^-30, 0, 0]; the mathematical geodetic height is exactly x - a."""
    x = m.A_WGS84 + k * ULP
    assert Fraction(x) == A + k * Fraction(ULP)  # exact: the grid spacing is 2^-30 here
    return np.array([x, 0.0, 0.0]), Fraction(x) - A


def pole(k: int) -> tuple[np.ndarray, Fraction]:
    """r = [0, 0, fl(b) + k 2^-30]; the mathematical geodetic height is exactly z - b."""
    z = m.B_WGS84 + k * ULP
    return np.array([0.0, 0.0, z]), Fraction(z) - B_EXACT


def bound_at_rest(r: np.ndarray) -> bool:
    """v = 0: the specific two-body energy -mu/|r| is negative."""
    return -m.MU / float(np.linalg.norm(r)) < 0.0


def outcome(h0: float, b: float, envelope=None):
    """("rejected", None) for the lower-edge ValueError, otherwise ("returned", need)."""
    try:
        return "returned", tt.stage_need(h0, b, envelope=envelope)
    except ValueError as exc:
        assert str(exc) == EDGE_MSG, exc  # not another ValueError
        return "rejected", None


# ------------------------------------------------------------- R8-F1 contract
def test_r8f1_beta_grid_transition_is_k9_to_k10():
    """Detects: a misread beta or grid. The transition quoted in the records (raises for
    k <= 9, returns for k >= 10) follows from beta and 2^-30 alone."""
    assert K_LAST_RAISING == 9
    assert 9 * ULP <= BETA < 10 * ULP


@pytest.mark.parametrize("vehicle", VEHICLES, ids=[v[0] for v in VEHICLES])
def test_r8f1_ellipsoid_surface_raises(vehicle):
    """Detects: the lower-edge rejection removed or hidden (for example the envelope clamped
    at 0, or the drag-free vehicle skipping the envelope). [a, 0, 0] lies on the ellipsoid
    (mathematical height 0); its computed height is 0 <= beta."""
    _, b = vehicle
    r, h_math = equator(0)
    assert h_math == 0
    h0 = computed_height(r)
    assert h0 == 0.0 and h0 <= BETA
    assert outcome(h0, b) == ("rejected", None)
    for h0 in (0.0, -0.0):
        assert outcome(h0, b) == ("rejected", None)


@pytest.mark.parametrize("vehicle", VEHICLES, ids=[v[0] for v in VEHICLES])
def test_r8f1_successive_floats_above_the_equatorial_radius(vehicle):
    """Detects: the rejection removed, or moved off h0 <= beta. For k = 1 ... 16 the states
    r = [a + k 2^-30, 0, 0], v = 0 are strictly exterior and bound; the computed height is
    checked against the exact one, and the outcome is decided from the computed height."""
    _, b = vehicle
    seen = []
    for k in range(1, 17):
        r, h_math = equator(k)
        assert h_math > 0 and bound_at_rest(r)  # strictly exterior, negative energy
        h0 = computed_height(r)
        assert Fraction(h0) == h_math  # on the equator the computed height is exact here
        kind, need = outcome(h0, b)
        if h0 <= BETA:
            assert kind == "rejected", (k, h0)
        else:
            assert kind == "returned" and math.isfinite(need) and need >= 0.0, (k, need)
            assert need == -tt.stage_lower_heights(h0, b)["M2"]  # path 1: need = -M2
        seen.append(kind)
    assert seen == ["rejected"] * K_LAST_RAISING + ["returned"] * (16 - K_LAST_RAISING)


@pytest.mark.parametrize("vehicle", VEHICLES, ids=[v[0] for v in VEHICLES])
def test_r8f1_review08_counterexample(vehicle):
    """Detects: the reviewer's state no longer rejected. r = [nextafter(a, +inf), 0, 0],
    v = 0: mathematical and computed height 2^-30 = 9.313225746154785e-10 m."""
    _, b = vehicle
    r = np.array([math.nextafter(m.A_WGS84, math.inf), 0.0, 0.0])
    h0 = computed_height(r)
    assert h0 == 2.0**-30 == 9.313225746154785e-10 and bound_at_rest(r)
    with pytest.raises(ValueError, match="the envelope is defined above the lower edge only"):
        tt.stage_need(h0, b)


@pytest.mark.parametrize("vehicle", VEHICLES, ids=[v[0] for v in VEHICLES])
def test_r8f1_computed_height_differs_from_mathematical_at_the_pole(vehicle):
    """Detects: the outcome decided by the mathematical instead of the computed height. At
    the pole the computed height of [0, 0, fl(b) + k 2^-30] is k 2^-30 while the
    mathematical height is k 2^-30 - (b - fl(b)): at k = 0 the point is inside the
    ellipsoid (mathematical height -2.03e-10 m) with computed height 0, and at k = 10 the
    mathematical height is 9.11e-9 m."""
    _, b = vehicle
    shift = Fraction(m.B_WGS84) - B_EXACT
    assert -2.04e-10 < shift < -2.03e-10  # fl(b) lies below the exact b
    for k in range(0, 13):
        r, h_math = pole(k)
        assert h_math == k * Fraction(ULP) + shift
        h0 = computed_height(r)
        assert h0 == k * ULP, (k, h0)
        assert abs(Fraction(h0) - h_math) <= Fraction(BETA)  # within E1
        kind, _ = outcome(h0, b)
        assert kind == ("rejected" if k <= K_LAST_RAISING else "returned"), k
    assert pole(0)[1] < 0  # inside, yet computed height 0


@pytest.mark.parametrize("vehicle", VEHICLES, ids=[v[0] for v in VEHICLES])
def test_r8f1_binary64_transition_at_beta(vehicle):
    """Detects: the rejection threshold moved. h0 = beta and every h0 below it down to
    -6e6 m raise ValueError; the next binary64 above beta returns a finite need >= 0."""
    _, b = vehicle
    for h0 in (BETA, math.nextafter(BETA, 0.0), BETA / 2, 2.0**-1074, -(2.0**-1074), -BETA):
        assert outcome(h0, b) == ("rejected", None), h0
    for h0 in (-1.0, -1e3, -6e6):
        assert outcome(h0, b) == ("rejected", None), h0
    kind, need = outcome(math.nextafter(BETA, math.inf), b)
    assert kind == "returned" and math.isfinite(need) and need >= 0.0


def test_r8f1_very_negative_height_raises_decimal_error():
    """Detects: the separately documented exception path changed. For b_lower + H0 <= 0
    the Decimal square root in V raises before the envelope (no exterior state: by E1 its
    computed height exceeds -beta)."""
    for b in (B_V1, math.inf):
        with pytest.raises(decimal.InvalidOperation):
            tt.stage_need(-6.4e6, b)


@pytest.mark.parametrize("vehicle", VEHICLES, ids=[v[0] for v in VEHICLES])
def test_r8f1_valid_finite_certification_still_returned(vehicle):
    """Detects: a valid certification lost (the rejection widened). At the published floors
    and at 200 km the stage condition returns a finite need < 0."""
    name, b = vehicle
    res = c4.results("termination")["sufficient_stage_condition"]
    floor = {
        row["vehicle"]: row["h_f_sufficient_at_least_m"]
        for row in res["rows"]
        if row["vehicle"] in ("B25.8", "drag-free limit")
    }["B25.8" if name == "B25.8" else "drag-free limit"]
    for h0 in (floor, 2e5):
        kind, need = outcome(h0, b)
        assert kind == "returned" and math.isfinite(need) and need < 0.0, (h0, need)


# ----------------------------------------------- first-stage-infinity regression
def first_stage_infinite(after: float):
    """An injected envelope (a propagation test, not a physical force): +inf at the first
    call (A0) and `after` at every later call (A2)."""
    calls = []

    def env(low, s, b):
        calls.append((low, s))
        return math.inf if len(calls) == 1 else after

    return env, calls


@pytest.mark.parametrize("after", [0.0, 1.0, 100.0])
@pytest.mark.parametrize("h0", [2e5, 1e6, 1e7])
def test_r8_first_stage_infinite_envelope_gives_infinite_need(h0, after):
    """Detects: M3 dropped from the stage minimum (`-min(M2, M4)`), or an infinite stage
    bound otherwise lost. A0 = +inf makes s2 = +inf and M3 = -inf; the injected A2 is finite,
    so M2 and M4 are finite and positive and M3 is the only term that forbids certification."""
    env, calls = first_stage_infinite(after)
    s = tt.stage_lower_heights(h0, B_V1, envelope=env)
    assert len(calls) == 2 and calls[1][1] == math.inf  # A2 was evaluated at s2 = +inf
    assert s["A0"] == math.inf and s["s2"] == math.inf and s["M3"] == -math.inf
    assert math.isfinite(s["A2"]) and math.isfinite(s["M4"]) and s["M4"] > 0.0
    assert math.isfinite(s["M2"]) and s["M2"] > 0.0
    need = tt.stage_need(h0, B_V1, envelope=first_stage_infinite(after)[0])
    assert need == math.inf and not need < 0.0  # the correct non-certification
    omitted = -min(s["M2"], s["M4"])  # what the M3-dropped mutant returns
    assert math.isfinite(omitted) and omitted < 0.0  # a false certification


@pytest.mark.parametrize("h0", [2e5, 1e7])
def test_r8_finite_injected_envelope_certifies(h0):
    """Detects: the finite path broken. With a finite injected envelope every stage bound is
    finite, need = -min(M2, M3, M4) < 0 and M3 enters the minimum."""
    s = tt.stage_lower_heights(h0, B_V1, envelope=lambda low, sp, b: 1.0)
    need = tt.stage_need(h0, B_V1, envelope=lambda low, sp, b: 1.0)
    assert all(math.isfinite(s[k]) for k in ("A0", "A2", "M2", "M3", "M4"))
    assert need == -min(s["M2"], s["M3"], s["M4"]) < 0.0
    assert s["M4"] < s["M3"] < s["M2"]  # each later stage starts from a larger speed bound


# --------------------------------------------------------- R8-F1 documentation
def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def test_r8f1_docstring_states_the_lower_edge_rejection():
    """Detects: the rejection undocumented, its threshold or vehicle scope misstated, or a
    finite need claimed for every exterior state."""
    doc = norm(tt.stage_lower_heights.__doc__)
    for phrase in (
        "Review 08 M3T0-R8-F1",
        "Every returned value needs a computed h0 > beta",
        "a computed h0 <= beta (H0 < 0) raises ValueError",
        "before the M2 test, for b = B_V1 and for the drag-free b = +inf alike",
        "the computed height is not the mathematical height",
        "r = [a + k 2^-30, 0, 0] m for k = 1 ... 9",
        "does not return a finite need for every state outside the ellipsoid",
        "certifies only under the premises above and A-FP-1 to A-FP-3",
        "decimal.InvalidOperation",
        "For h0 > beta, need(h0) >= 0 is a non-certification",
        "has a finite need on both paths for h0 > beta",
    ):
        assert phrase in doc, phrase
    assert f"beta = {BETA!r} m" in doc


def test_r8f1_records_amended():
    """Detects: the false exclusion left unqualified, or a historical record rewritten
    instead of amended."""
    rev7 = (ROOT / "docs/reviews/M3-T0-review-07.md").read_text()
    amend7 = rev7.index("### Amendment (Authorization I-11, Review 08 M3T0-R8-F1)")
    old7 = "Such an h0 is not the computed height of a state in the domain (outside the ellipsoid)"
    assert rev7[:amend7].count(old7) == 1  # preserved above the amendment
    tail7 = rev7[amend7:]
    for phrase in ("is false", "h0 ≤ β", "2^-30", "B_V1", "drag-free", "computed height"):
        assert phrase in tail7, phrase
    rev6 = (ROOT / "docs/reviews/M3-T0-review-06.md").read_text()
    amend6 = rev6.index("### Amendment 2 (Authorization I-11, Review 08 M3T0-R8-F1)")
    assert rev6.index("### Amendment (Authorization I-10, Review 07 M3T0-R7-F1)") < amend6
    assert "h0 ≤ β" in rev6[amend6:] and "ValueError" in rev6[amend6:]
    for name in ("DR-0029", "VAL-0019"):
        text = c4.record(name)
        assert "M3T0-R8-F1" in text, name
        log = re.search(
            r"<!-- review08-correction-log -->.*<!-- /review08-correction-log -->", text, re.S
        )
        assert log and "h0 ≤ β" in log.group(0), name
        body = text[: log.start()] + text[log.end() :]
        assert "Qualified after Review 08 M3T0-R8-F1" in body, name
        assert "computed h0 > β" in body, name
    rep = c4.record("report")
    assert "R8-F1: every value the stage condition returns needs a computed h0 > β" in rep
    assert "check_review08.py" in c4.record("VAL-0019")
    assert "check_review08.py" in c4.record("README")
