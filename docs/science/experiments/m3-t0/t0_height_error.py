"""M3 T0: numerical evidence for the height-error bound of Review 03 M3T0-R3-F1 (research only).

`t0_termination.rounding_allowances` derives eps_h(h) = alpha h + beta, a worst-case bound
on |computed - true| geodetic height under assumptions A-FP-1 ... A-FP-3. This script is
the numerical side, kept separate from the proof:

1. A-FP-2 on this platform: the libm functions the model uses (sin, cos, atan2, hypot, exp,
   pow) against 50-digit decimal references, in ulps of the exact value. A measurement,
   not a proof: it covers the sampled arguments on the machine that ran it.
2. Observed height error: the model's `geodetic_iterative` against the exact height of the
   same binary64 point (`t0_oracle.true_height`, an independent foot-point method), over
   global, near-base, polar, low-height and equatorial points. The observed maximum is an
   empirical figure; the bound is the derivation.
3. Band crossings at the 12 bases where the density drops going up: points whose computed
   and true heights lie on opposite sides of the base, the superseded (exact-height)
   envelope's violations among them, and the corrected envelope's coverage.

Usage: uv run --no-sync python t0_height_error.py <out.json>
"""

from __future__ import annotations

import json
import math
import sys
from decimal import Decimal, localcontext

import numpy as np
import t0_model as m
import t0_oracle as o
import t0_termination as tt

D = Decimal
PREC = 50


# ------------------------------------------------------------ decimal references
def d_pi() -> D:
    """pi by the Python decimal-module recipe (Machin-free series), PREC + 5 digits."""
    with localcontext() as c:
        c.prec = PREC + 5
        three = D(3)
        lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
        while s != lasts:
            lasts = s
            n, na = n + na, na + 8
            d, da = d + da, da + 32
            t = (t * n) / d
            s += t
        return +s


PI = d_pi()


def d_sin(x: D) -> D:
    with localcontext() as c:
        c.prec = PREC + 5
        i, lasts, s, fact, num, sign = 1, 0, x, 1, x, 1
        while s != lasts:
            lasts = s
            i += 2
            fact *= i * (i - 1)
            num *= x * x
            sign *= -1
            s += num / fact * sign
        return +s


def d_cos(x: D) -> D:
    with localcontext() as c:
        c.prec = PREC + 5
        i, lasts, s, fact, num, sign = 0, 0, D(1), 1, D(1), 1
        while s != lasts:
            lasts = s
            i += 2
            fact *= i * (i - 1)
            num *= x * x
            sign *= -1
            s += num / fact * sign
        return +s


def d_atan(x: D) -> D:
    """|x| <= 1: three argument halvings, then the Taylor series."""
    with localcontext() as c:
        c.prec = PREC + 5
        for _ in range(3):
            x = x / (1 + (1 + x * x).sqrt())
        s, term, k, lasts = x, x, 1, None
        while s != lasts:
            lasts = s
            term *= -x * x
            k += 2
            s += term / k
        return s * 8


def d_atan2(y: D, x: D) -> D:
    """x >= 0 (the model's use)."""
    with localcontext() as c:
        c.prec = PREC + 5
        if x == 0:
            return PI / 2 if y > 0 else -PI / 2 if y < 0 else D(0)
        if abs(y) <= x:
            return d_atan(y / x)
        return (PI / 2 if y > 0 else -PI / 2) - d_atan(x / y)


def errors(got: float, ref: D) -> tuple[float, float]:
    """(error in ulps of the exact value's binade, relative error in units of 2^-52). A-FP-2
    is stated in the second unit, which is what the derivation uses (UF = LIBM_ULP 2^-52)."""
    with localcontext() as c:
        c.prec = PREC
        err = abs(D(got) - ref)
        e = math.frexp(float(ref))[1] - 1  # 2^e <= |float(ref)|
        if D(2) ** e > ref.copy_abs():
            e -= 1  # float(ref) rounded up to a power of two
        binade_ulp = D(2) ** (e - 52)
        return float(err / binade_ulp), float(err / (ref.copy_abs() * D(2) ** -52))


def libm_accuracy(n: int = 20000) -> dict:
    rng = np.random.default_rng(20261019)
    half = math.pi / 2
    lats = np.r_[rng.uniform(-half, half, n), half - 10.0 ** rng.uniform(-9, -1, n // 4)]
    pts = [
        m.geodetic_to_cartesian(float(a), rng.uniform(-math.pi, math.pi), rng.uniform(0, 2e6))
        for a in lats[:n]
    ]
    xs = rng.uniform(-50.0, 0.0, n)
    rs = rng.uniform(6.3e6, 1.0e8, n)
    with localcontext() as c:
        c.prec = PREC
        cases = {
            "sin": [(math.sin(float(x)), d_sin(D(float(x)))) for x in lats],
            "cos": [(math.cos(float(x)), d_cos(D(float(x)))) for x in lats],
            "atan2": [
                (math.atan2(y, x), d_atan2(D(y), D(x)))
                for x, y in ((math.hypot(p[0], p[1]), float(p[2]) * 1.0068) for p in pts)
            ],
            "hypot": [
                (
                    math.hypot(float(p[0]), float(p[1])),
                    (D(float(p[0])) ** 2 + D(float(p[1])) ** 2).sqrt(),
                )
                for p in pts
            ],
            "exp": [(math.exp(float(x)), D(float(x)).exp()) for x in xs],
            "pow3": [(float(r) ** 3, D(float(r)) ** 3) for r in rs],
        }
    ulp_max, rel_max = {}, {}
    for name, pairs in cases.items():
        errs = [errors(g, r) for g, r in pairs]
        ulp_max[name] = max(e[0] for e in errs)
        rel_max[name] = max(e[1] for e in errs)
    sub = subnormal_results()
    return {
        "max_error_ulp": ulp_max,
        "max_relative_error_in_2^-52": rel_max,
        "samples_per_function": {k: len(v) for k, v in cases.items()},
        "assumed_relative_bound_in_2^-52": tt.LIBM_ULP,
        "within_assumption": max(rel_max.values()) <= tt.LIBM_ULP,
        "subnormal_results": sub,
        "kind": "measurement on this platform (sampled arguments), not a proof of A-FP-2",
    }


def subnormal_results(n: int = 4000) -> dict:
    """Review 04 M3T0-R4-F1: A-FP-2's absolute term. Functions whose exact value is subnormal
    (or below half the smallest subnormal, where 0 is the nearest binary64), against
    decimal references, in units of 2^-1074; plus IEEE gradual-underflow identities (A-FP-1:
    no flush-to-zero or denormals-are-zero mode)."""
    rng = np.random.default_rng(20261020)
    tiny = D(math.ulp(0.0))
    xs = np.r_[rng.uniform(-745.2, -708.39, n), np.linspace(-745.2, -708.39, 1001)]
    ys = 10.0 ** rng.uniform(-323.5, -308.0, n)
    ps = 10.0 ** rng.uniform(6.3, 8.5, n)
    with localcontext() as c:
        c.prec = PREC
        cases = {
            "exp": [(math.exp(float(x)), D(float(x)).exp()) for x in xs],
            "sin": [(math.sin(float(y)), d_sin(D(float(y)))) for y in ys],
            "atan2": [
                (math.atan2(float(y), float(p)), d_atan2(D(float(y)), D(float(p))))
                for y, p in zip(ys, ps, strict=True)
            ],
            "hypot": [
                (
                    math.hypot(float(y), float(y) / 3),
                    (D(float(y)) ** 2 + (D(float(y) / 3)) ** 2).sqrt(),
                )
                for y in ys
            ],
        }
    worst = {k: float(max(abs(D(g) - r) for g, r in v) / tiny) for k, v in cases.items()}
    probe = {
        "smallest_subnormal_positive": math.ulp(0.0) > 0.0,
        "halving_smallest_normal_is_exact": 2.0**-1022 / 2 == 2.0**-1023,
        "tie_rounds_to_even": (3 * math.ulp(0.0)) * 0.5 == 2 * math.ulp(0.0),
        "half_smallest_subnormal_rounds_to_zero": math.ulp(0.0) * 0.5 == 0.0,
        "numpy_subnormal_product": float(np.float64(2.0**-1022) * np.float64(0.5)) == 2.0**-1023,
    }
    return {
        "max_abs_error_in_2^-1074": worst,
        "samples_per_function": {k: len(v) for k, v in cases.items()},
        "assumed_abs_bound_in_2^-1074": tt.LIBM_ULP,
        "within_assumption": max(worst.values()) <= tt.LIBM_ULP,
        "gradual_underflow_probe": probe,
        "gradual_underflow": all(probe.values()),
    }


# ---------------------------------------------------------------- height errors
def height_errors() -> dict:
    rng = np.random.default_rng(20261020)
    cats: dict[str, list] = {"global": [], "near_bases": [], "polar": [], "low": [], "equator": []}
    for _ in range(6000):
        cats["global"].append((rng.uniform(-1.5707, 1.5707), rng.uniform(0.0, 2.0e6)))
    for bb in m.TABLE[1:]:  # the lower edge 0 m is covered by "low"
        for _ in range(150):
            cats["near_bases"].append(
                (rng.uniform(-1.5707, 1.5707), bb.base_km * 1e3 + rng.uniform(-1e-6, 1e-6))
            )
    for _ in range(1000):
        cats["polar"].append(
            (
                math.copysign(math.pi / 2 - 10.0 ** rng.uniform(-12, -3), rng.uniform(-1, 1)),
                rng.uniform(0.0, 2.0e6),
            )
        )
        cats["low"].append((rng.uniform(-1.5707, 1.5707), rng.uniform(1e-3, 10.0)))
        cats["equator"].append((0.0, rng.uniform(0.0, 2.0e6)))
    out = {}
    for name, items in cats.items():
        worst, ratio, arg, neg = 0.0, 0.0, None, 0
        for lat, h in items:
            r = m.geodetic_to_cartesian(lat, rng.uniform(-math.pi, math.pi), h)
            ht = o.true_height(r)
            err = float(D(m.geodetic_iterative(r)[1]) - ht)
            neg += err < 0
            rat = abs(err) / tt.height_error_bound(float(ht))
            if abs(err) > worst:
                worst, arg = abs(err), [float(x) for x in r]
            ratio = max(ratio, rat)
        out[name] = {
            "points": len(items),
            "max_abs_error_m": worst,
            "max_error_over_bound": ratio,
            "computed_below_true_fraction": neg / len(items),
            "worst_point_m": arg,
        }
    return {
        "categories": out,
        "max_abs_error_m": max(c["max_abs_error_m"] for c in out.values()),
        "max_error_over_bound": max(c["max_error_over_bound"] for c in out.values()),
        "bound_m_at_120km": tt.height_error_bound(120e3),
        "kind": "observed maximum over the sampled points (empirical); the bound is derived",
    }


# --------------------------------------------------------------- band crossings
def crossings(per_base: int = 400) -> dict:
    rng = np.random.default_rng(31)
    rows = []
    for base_d in o.downward_jumps():
        base = float(base_d)
        down = up = viol = 0
        worst_old, min_new_margin = 0.0, math.inf
        for _ in range(per_base):
            lat, lon = rng.uniform(-1.5, 1.5), rng.uniform(-math.pi, math.pi)
            r = m.geodetic_to_cartesian(lat, lon, base)
            hc, ht = m.geodetic_iterative(r)[1], o.true_height(r)
            if (hc < base) == (ht < base_d):
                continue
            if ht < base_d:
                up += 1
                continue
            down += 1
            east = np.array([-math.sin(lon), math.cos(lon), 0.0])
            for s in (7_800.0, 11_000.0):
                a = tt.model_drag(r, -s * east, tt.MASS)
                old = tt.drag_envelope_exact_height(base, s, tt.B_V1)
                new = tt.drag_envelope(base, s, tt.B_V1)
                if a > old:
                    viol += 1
                    worst_old = max(worst_old, a / old - 1)
                min_new_margin = min(min_new_margin, new / a - 1)
        rows.append(
            {
                "base_m": base,
                "points": per_base,
                "computed_below_true_at_or_above": down,
                "computed_at_or_above_true_below": up,
                "superseded_envelope_violations": viol,
                "superseded_worst_relative_excess": worst_old,
                "corrected_min_relative_margin": min_new_margin,
            }
        )
    return {
        "rows": rows,
        "corrected_covers_all": all(r["corrected_min_relative_margin"] >= 0 for r in rows),
        "velocity": "horizontal against the rotation (largest |v_rel|), s = 7800 and 11000 m/s",
    }


def main() -> None:
    out = {"libm": libm_accuracy(), "height_error": height_errors(), "crossings": crossings()}
    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
