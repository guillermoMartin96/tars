"""Regression checks for the M3 T0 Review 07 findings M3T0-R7-F1 and R7-F2 (research only).

Both findings are documentation defects; the correction changes docstrings and records
only, and no executable statement or value. These checks therefore have two kinds:

- contract checks pin the behaviour the corrected documentation states. They pass on the
  unmodified implementation too (it did not change); they detect a change of semantics;
- record checks detect the stale statements. They fail on the uncorrected tree.

R7-F1: the stage condition's docstring said an envelope of +inf always gives need(h0) =
+inf. When M2 <= 0, `stage_lower_heights` returns before M4 and `stage_need` returns -M2,
finite and >= 0, even when A0 = +inf (h0 = 1, b = 2^-1074: need = 55 992.318990613036 m).
Both paths are non-certifications: a step is certified only when need < 0.

R7-F2: two summaries kept "b_R <= b" without b > 0. At b = 0 (Review 06 M3T0-R6-F1),
b_R = phi_B / R(0) > 0 = b: envelope_ballistic_coefficient(0, 2.2, 15) = 1.497e-325.

Expected values come from exact rational or independent decimal arithmetic on the
binary64 inputs and from the reviewer's report, never from the implementation under test.
Each check states the defect it detects. `mutation_check_review02.py` runs these checks on
corrupted copies. Not collected by the project test suite. Run:
  uv run --no-sync pytest -q docs/science/experiments/m3-t0/check_review07.py
"""

from __future__ import annotations

import math
import re
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_review04 as c4  # noqa: E402
import check_review06 as c6  # noqa: E402
import t0_model as m  # noqa: E402
import t0_termination as tt  # noqa: E402

D = Decimal
TINY = 2.0**-1074  # the smallest positive binary64
MAX = sys.float_info.max
CD, AREA = c4.CD, c4.AREA
B_V1 = c4.VEHICLES["B25.8"]
ROOT = HERE.parents[3]
# Review 07's counterexample (raw review: h0 = 1.0, b = 2^-1074)
R7_NEED = 55992.318990613036
# M2 <= 0 exactly up to this computed height with the published constants (FP)
M2_EDGE = 55749.393
VEHICLES = (0.0, TINY, 2 * TINY, 1e-310, 1e-300, B_V1, 100.0, 1e300, MAX, math.inf)


def m2_second(h0: float, fp: dict) -> Decimal:
    """M2 written out again from the stage_lower_heights docstring without the outward pads
    (E1, E6): M2 = (1 - alpha) L2 - beta, L2 = H0 - 5 (1 + u)^2 V - u R0 - 2 eta0. The
    implementation subtracts pads, so its M2 is <= this value and within 1e-9 m of it."""
    with localcontext() as ctx:
        ctx.prec = 80
        u = D(fp["u"])
        al, be = D(fp["alpha"]), D(fp["beta_m"])
        h = D(h0)
        big_h0 = (h - be) / (1 + al)
        r0 = D(m.A_WGS84) + (h + be) / (1 - al)
        v = (2 * D(m.MU) / (D(fp["b_lower_m"]) + big_h0)).sqrt()
        l2 = big_h0 - 5 * (1 + u) ** 2 * v - u * r0 - D(TINY)  # 2 eta0 = 2^-1074
        return (1 - al) * l2 - be


def certified(need: float) -> bool:
    """The consumers' rule (the floor bisection, `libm_sensitivity`): need < 0 only."""
    return need < 0.0


# ------------------------------------------------------------------- R7-F1
@pytest.mark.parametrize("b", [TINY, 0.0])
def test_r7f1_review07_counterexample_has_finite_positive_need(b):
    """Detects: the early-return path (M2 <= 0) changed, for example normalised to +inf or
    removed. The reviewer's case, b = 2^-1074 (and b = 0), h0 = 1: A0 = +inf, M3 = -inf,
    M4 = None and need = -M2 = 55 992.318990613036 m, finite and > 0 (not certified)."""
    s = tt.stage_lower_heights(1.0, b)
    assert s["A0"] == math.inf and s["M3"] == -math.inf
    assert s["A2"] is None and s["s3"] is None and s["L4"] is None and s["M4"] is None
    need = tt.stage_need(1.0, b)
    assert need == R7_NEED and need == -s["M2"]
    assert math.isfinite(need) and need > 0.0 and not certified(need)


@pytest.mark.parametrize("h0", [1.0, 1000.0, 2e4, 5e4, M2_EDGE])
def test_r7f1_early_return_need_is_minus_m2_for_every_vehicle(h0):
    """Detects: the early-return need depending on the vehicle or the envelope, or not equal
    to -M2. M2 is independent of b, and a second implementation of M2 (exact decimals, no
    pads) bounds it from above within 1e-9 m."""
    second = m2_second(h0, tt.FP)
    assert second <= 0
    m2s = set()
    for b in VEHICLES:
        s = tt.stage_lower_heights(h0, b)
        m2s.add(s["M2"])
        assert s["M4"] is None
        need = tt.stage_need(h0, b)
        assert need == -s["M2"] and math.isfinite(need) and need >= 0.0
        assert not certified(need)
    assert len(m2s) == 1
    (m2,) = m2s
    assert D(m2) <= second and second - D(m2) < D("1e-9")


def test_r7f1_early_return_edge_quoted_in_the_docstring():
    """Detects: a wrong quoted edge of the early-return path (55 749.393 m with FP): M2 <= 0
    at and below it, M2 > 0 from 55 749.394 m."""
    assert m2_second(M2_EDGE, tt.FP) < 0 < m2_second(55749.394, tt.FP)
    for b in (0.0, TINY, B_V1, math.inf):
        assert tt.stage_lower_heights(M2_EDGE, b)["M4"] is None
        assert tt.stage_lower_heights(55749.394, b)["M4"] is not None


@pytest.mark.parametrize("h0, b", [(55749.394, TINY), (6e4, TINY), (1e5, 0.0), (1e7, TINY)])
def test_r7f1_unbounded_envelope_with_m2_positive_gives_infinite_need(h0, b):
    """Detects: the M2 > 0 path losing the +inf of an unbounded envelope (need clamped or
    made finite)."""
    s = tt.stage_lower_heights(h0, b)
    assert s["M2"] > 0.0 and s["M4"] == -math.inf
    assert math.inf in (s["A0"], s["A2"])
    assert tt.stage_need(h0, b) == math.inf and not certified(tt.stage_need(h0, b))


def test_r7f1_stage_value_outside_the_binary64_range_gives_infinite_need():
    """Detects: an overflow of a stage value (with a finite envelope) not rounded outward to
    +-inf. The injected envelope returns the largest binary64: A0 exceeds it, so the speeds
    after it are +inf and M3 = M4 = -inf."""
    s = tt.stage_lower_heights(1e7, B_V1, envelope=lambda low, sp, b: MAX)
    assert s["M2"] > 0.0 and s["A0"] == math.inf and s["s2"] == math.inf
    assert s["M3"] == -math.inf and s["M4"] == -math.inf
    assert tt.stage_need(1e7, B_V1, envelope=lambda low, sp, b: MAX) == math.inf


def test_r7f1_drag_free_vehicle_has_finite_need_on_both_paths():
    """Detects: b = +inf (the drag-free vehicle, envelope 0) reported as unbounded."""
    for h0 in (1.0, 5e4, 6e4, 1e7):
        s = tt.stage_lower_heights(h0, math.inf)
        values = [x for x in s.values() if x is not None]
        assert all(math.isfinite(x) for x in values)
        assert math.isfinite(tt.stage_need(h0, math.inf))
    assert tt.stage_need(1e7, math.inf) < 0.0  # certified far above the floors


@pytest.mark.parametrize("h0", [1.0, 1e7])
def test_r7f1_invalid_inputs_raise_on_both_paths(h0):
    """Detects: an invalid input certified or returned as a need on either path (b is
    validated by the envelope for A0, before the M2 test)."""
    for b in (math.nan, -1.0, -TINY):
        with pytest.raises(ValueError):
            tt.stage_need(h0, b)
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError):
            tt.stage_need(bad, B_V1)


def test_r7f1_no_finite_bound_is_ever_certified():
    """Detects: a false certification. Over both paths and every vehicle, an infinite A0 or
    A2 never comes with need < 0."""
    for h0 in (1.0, 5e4, M2_EDGE, 55749.394, 6e4, 1.2e5, 1e6, 1e7, 2e8):
        for b in VEHICLES:
            s = tt.stage_lower_heights(h0, b)
            need = tt.stage_need(h0, b)
            assert not math.isnan(need)
            if math.inf in (s["A0"], s["A2"]):
                assert need >= 0.0 and not certified(need), (h0, b)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def test_r7f1_docstring_states_both_non_certification_paths():
    """Detects: the universal "need(h0) = +inf" claim restored, or either path undocumented."""
    doc = norm(tt.stage_lower_heights.__doc__)
    assert "so need(h0) = +inf: the step is not certified at h0" not in doc  # the R7-F1 text
    for phrase in (
        "certified at h0 only when need(h0) < 0",
        "need(h0) >= 0 is a non-certification",
        "M2 <= 0",
        "need(h0) = -M2, finite and >= 0",
        "M2 depends on h0 and fp only, not on b or the envelope",
        "M2 <= 0 up to h0 = 55 749.393 m",
        "need(h0) = 55 992.32 m",
        "M2 > 0: need(h0) = -min(M2, M3, M4)",
        "so need(h0) = +inf",
        "outside the binary64 range",
        "b = +inf is drag-free (envelope 0) and has a finite need on both paths",
        "raises ValueError on both paths",
        "no value changed",
    ):
        assert phrase in doc, phrase
    assert "Review 07 M3T0-R7-F1" in doc


def test_r7f1_records_state_both_paths():
    """Detects: the records keeping need = +inf as the only non-certification, or the
    Review 06 record rewritten instead of amended."""
    rev = (ROOT / "docs/reviews/M3-T0-review-06.md").read_text()
    amend = rev.index("### Amendment (Authorization I-10, Review 07 M3T0-R7-F1)")
    old = "so need(h0) = +∞: the step is **not certified** at h0."
    assert rev[:amend].count(old) == 1  # preserved above the amendment
    tail = rev[amend:]
    for phrase in ("need = −M2", "finite and ≥ 0", "55 749.393", "need < 0"):
        assert phrase in tail, phrase
    for name in ("DR-0029", "VAL-0019"):
        text = c4.record(name)
        assert "need = −M2, finite and ≥ 0" in text, name
        assert "M3T0-R7-F1" in text, name
        log = re.search(
            r"<!-- review06-correction-log -->.*<!-- /review07-correction-log -->", text, re.S
        )
        body = text[: log.start()] + text[log.end() :]  # the logs keep or quote the old text
        assert "need = +∞" in log.group(0), name
        assert not re.search(
            r"certifies nothing \((?:the stage condition then reports )?need = \+∞", body
        ), name
    for name in ("report", "README"):
        assert "R7-F1" in c4.record(name), name
    assert "check_review07.py" in c4.record("VAL-0019")
    assert "check_review07.py" in c4.record("README")


# ------------------------------------------------------------------- R7-F2
def test_r7f2_review07_counterexample_b_r_positive_at_zero_b():
    """Detects: b_R at b = 0 made equal to b (0) or non-positive. The reviewer's case:
    envelope_ballistic_coefficient(0, 2.2, 15) = phi_B / R(0) = 1.497e-325, rounded down,
    with R(0) recomputed independently (`check_review06.r_zero_second`)."""
    b_r = tt.envelope_ballistic_coefficient(0.0, 2.2, 15.0, tt.FP)
    q = c6.PHI / c6.r_zero_second(2.2, 15.0)
    assert isinstance(b_r, D) and b_r > 0 and not b_r <= 0.0
    assert f"{b_r:.4g}" == "1.497e-325"
    assert Fraction(b_r) <= q and Fraction(b_r) >= q * (1 - Fraction(1, 10**58))
    for cd, area in c6.SHAPES:
        b_r = tt.envelope_ballistic_coefficient(0.0, cd, area, tt.FP)
        assert b_r > 0  # b_R <= b fails at b = 0 on every shape


def test_r7f2_b_r_at_most_b_for_positive_b():
    """Detects: the qualified claim b_R <= b (b > 0) failing, or b_R not the same binary64 b
    where the conversion is normal."""
    for cd, area in [(CD, AREA), *c6.SHAPES]:
        for b in (TINY, 2 * TINY, 3 * TINY, 1e-320, 1e-310, 2.0**-1022, 1e-300, 1.0, 1e300):
            b_r = tt.envelope_ballistic_coefficient(b, cd, area, tt.FP)
            assert Fraction(b_r) <= Fraction(b), (b, cd, area)
    for b in (B_V1, 100.0, 1.0):
        assert tt.envelope_ballistic_coefficient(b, CD, AREA, tt.FP) is b


def test_r7f2_docstrings_qualify_b_r_at_most_b():
    """Detects: "b_R <= b" stated without b > 0 in t0_termination.py, or the b = 0 case
    dropped beside either qualified summary."""
    src = norm((HERE / "t0_termination.py").read_text())
    assert "phi_B / R <= b" not in src  # the stale drag_envelope summary
    for hit in re.finditer(r"b_R <= b", src):
        after, before = src[hit.end() : hit.end() + 10], src[hit.start() - 4 : hit.start()]
        assert after == " for b > 0" or before == "not ", src[hit.start() - 60 : hit.end() + 20]
    e4 = "b_R <= b for b > 0, and b_R = b wherever the conversion is normal; at b = 0, b_R = "
    assert e4 + "phi_B / R(0) > 0, Review 07 M3T0-R7-F2" in src  # the E4 summary
    env = norm(tt.drag_envelope.__doc__)
    assert "b_R <= b for b > 0" in env and "at b = 0, b_R = phi_B / R(0) > 0" in env
    assert "Review 07 M3T0-R7-F2" in env


def test_r7_correction_is_documentation_only():
    """Detects: an executable change hidden in the documentation correction. Every published
    floor, bracket and need is re-derived bit for bit from the committed results."""
    res = c4.results("termination")["sufficient_stage_condition"]
    for row in res["rows"]:
        b = dict(tt.VEHICLES)[row["vehicle"]]
        floor = row["h_f_sufficient_at_least_m"]
        assert tt.stage_need(floor, b) == row["need_at_floor_m"] < 0.0
        assert tt.stage_lower_heights(floor, b) == row["at_floor"]
