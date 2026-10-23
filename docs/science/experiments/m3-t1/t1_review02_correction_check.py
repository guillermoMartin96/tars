"""M3 T1: evidence that the Review 02 corrections (I-20) hold and change no valid result.

1. Re-runs each Review 02 reproduction (M3T1-R2-F1, F2) and the coefficient-chain case
   found while correcting R2-F1, against the pre-correction component (``b1566ae``, loaded
   from OLD_SRC) and the corrected one, with exactly rounded reference values.
2. Exact zeros, exact subnormal intermediates and subnormal final components: returned.
3. The numerical domain for the canonical constants (equatorial bisection, as in
   ``t1_review01_correction_check.py``), and the smallest coefficient and factor products
   the canonical constants can produce inside it.
4. Bit identity with OLD_SRC: the 200 004 states of ``t1_review01_correction_check.py``
   (same seed and generator) and three RK4 trajectories (point mass + J2, perigee 300 km,
   apogee 1000 km, inclinations 28.5, 51.6 and 97 deg, dt 10 s, 6 000 steps).

Usage (from the repository root; OLD_SRC is a checkout of src/ at b1566ae):
    uv run python docs/science/experiments/m3-t1/t1_review02_correction_check.py OLD_SRC OUT.json
"""

from __future__ import annotations

import importlib.util
import json
import math
import random
import struct
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

from tars.astro.elements import elements_to_rv
from tars.sim.constants import WGS84_EGM2008_TIDE_FREE as K
from tars.sim.forces import CompositeForceModel, PointMassGravity, ZonalJ2Gravity
from tars.sim.integrators import RK4

MU, A, J2 = K.mu, K.equatorial_radius, K.j2
Z3 = np.zeros(3)
MIN_NORMAL = sys.float_info.min


def load_old(old_src: str):
    spec = importlib.util.spec_from_file_location(
        "old_forces", Path(old_src) / "tars/sim/forces.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def outcome(make, r):
    try:
        a = make().acceleration(0.0, np.array(r), Z3)
        return {"result": [repr(float(c)) for c in a], "dtype": str(a.dtype)}
    except (ValueError, TypeError, OverflowError) as e:
        return {"raises": type(e).__name__, "message": str(e)}


def exact(r, mu, radius, j2):
    """Correctly rounded acceleration from exact rationals; |r| bracketed by isqrt."""
    x, y, z = (Fraction(float(c)) for c in r)
    r2 = x * x + y * y + z * z
    scale = 2**1200
    lo = Fraction(math.isqrt(int(r2 * scale * scale)), scale)
    k0 = Fraction(-3, 2) * Fraction(j2) * Fraction(mu) * Fraction(radius) ** 2
    s2 = z * z / r2
    ends = [
        [
            repr(float(k0 / (r2 * r2 * n) * f))
            for f in (x * (1 - 5 * s2), y * (1 - 5 * s2), z * (3 - 5 * s2))
        ]
        for n in (lo, lo + Fraction(1, scale))
    ]
    assert ends[0] == ends[1]
    return ends[0]


def before_after(old, params, r):
    return {
        "exact": exact(r, *params),
        "reviewed_b1566ae": outcome(lambda: old.ZonalJ2Gravity(*params), r),
        "corrected": outcome(lambda: ZonalJ2Gravity(*params), r),
    }


def accepted(x: float) -> bool:
    return "result" in outcome(lambda: ZonalJ2Gravity(MU, A, J2), [x, 0.0, 0.0])


def boundary(good_x: float, bad_x: float) -> float:
    assert accepted(good_x) and not accepted(bad_x)
    g, b = (struct.unpack("<q", struct.pack("<d", v))[0] for v in (good_x, bad_x))
    while abs(b - g) > 1:
        m = (g + b) // 2
        if accepted(struct.unpack("<d", struct.pack("<q", m))[0]):
            g = m
        else:
            b = m
    return struct.unpack("<d", struct.pack("<q", g))[0]


def propagate(model, r0, v0, dt: float, steps: int) -> bytes:
    def f(t, y):
        return np.concatenate([y[3:], model.acceleration(t, y[:3], y[3:])])

    y = np.concatenate([r0, v0])
    rk4, out = RK4(), [y]
    for k in range(steps):
        y = rk4.step(f, k * dt, y, dt)
        out.append(y)
    return np.array(out).tobytes()


def main(old_src: str, out_path: str) -> None:
    old = load_old(old_src)
    out: dict = {"reference": "OLD_SRC = src/ at b1566ae (forces.py as at a27f288)"}

    # R2-F1: component products (Review 02's case, the y variant, the (3 - 5 s^2) factor)
    f1 = {
        "x_factor_review02": (
            (5.1827254193540115e-108, 1.0, 0.5),
            [1e40, 0.0, 4.9999999999999995e39],
        ),
        "y_factor": ((5.1827254193540115e-108, 1.0, 0.5), [0.0, 1e40, 4.9999999999999995e39]),
        "z_factor": ((1.3 * 2.931792231242491e-107, 1.0, 0.5), [1e40, 0.0, 1.224744871391589e40]),
        "coefficient_chain": ((2.0**1000, 1.0, 3 * 2.0**-1074), [2.0**10, 0.0, 0.0]),
    }
    out["R2-F1_underflow"] = {k: before_after(old, p, r) for k, (p, r) in f1.items()}
    legit = {
        "exact_zero_factor_and_coordinate": (
            (5.1827254193540115e-106, 1.0, 0.5),
            [2.0**134, 0.0, 2.0**133],
        ),
        "j2_zero": ((5.1827254193540115e-108, 1.0, 0.0), [1e40, 0.0, 5e39]),
        "exact_subnormal_intermediate": ((2.0**1000, 1.0, 2 * 2.0**-1074), [2.0**10, 0.0, 0.0]),
        "subnormal_final_component": ((1.0, 1.0, 0.5), [2.0**200, 2.0**-50, 0.0]),
    }
    out["R2-F1_legitimate_results"] = {k: before_after(old, p, r) for k, (p, r) in legit.items()}

    # R2-F2: caller-owned arrays, float32, unsupported types
    pos = [A, 0.0, 0.0]
    f2: dict = {}
    for tag, cls in (("reviewed_b1566ae", old.ZonalJ2Gravity), ("corrected", ZonalJ2Gravity)):
        row = {}
        mu_arr = np.array(MU)
        try:
            m = cls(mu_arr, A, J2)
            mu_arr[...] = -1.0
            row["mu_array_set_to_-1_after_construction"] = outcome(lambda m=m: m, pos)
        except (ValueError, TypeError) as e:
            row["mu_array_set_to_-1_after_construction"] = {"raises": type(e).__name__}
        row["float32_parameters"] = outcome(
            lambda cls=cls: cls(np.float32(MU), np.float32(A), np.float32(J2)), pos
        )
        row["str_mu"] = outcome(lambda cls=cls: cls("398600441800000.0", A, J2), pos)
        row["list_mu"] = outcome(lambda cls=cls: cls([MU], A, J2), pos)
        row["bool_j2"] = outcome(lambda cls=cls: cls(MU, A, True), pos)
        row["int_mu_10**400"] = outcome(lambda cls=cls: cls(10**400, A, J2), pos)
        f2[tag] = row
    f2["float_conversion_of_float32_values"] = outcome(
        lambda: ZonalJ2Gravity(*(float(np.float32(v)) for v in (MU, A, J2))), pos
    )
    f2["canonical_python_floats"] = outcome(lambda: ZonalJ2Gravity(MU, A, J2), pos)
    out["R2-F2"] = f2

    # Domain and the canonical constants' smallest products
    k0 = -1.5 * J2 * MU * A * A
    out["numerical_domain_equatorial_canonical"] = {
        "largest_accepted_x_m": boundary(1e61, 1e62),
        "smallest_accepted_x_m": boundary(1e-50, 1e-60),
        "review01_values": [4.476546622757235e61, 3.3773820261812166e-57],
    }
    out["canonical_reach"] = {
        "k0": k0,
        "smallest_abs_k_in_domain": abs(k0) / sys.float_info.max,
        "times_2^-53": abs(k0) / sys.float_info.max * 2.0**-53,
        "is_normal": abs(k0) / sys.float_info.max * 2.0**-53 >= MIN_NORMAL,
        "coefficient_chain": [-1.5 * J2, -1.5 * J2 * MU, -1.5 * J2 * MU * A],
    }

    # Bit identity: the Review 01 state set
    new, ref = ZonalJ2Gravity(MU, A, J2), old.ZonalJ2Gravity(MU, A, J2)
    rng = random.Random(20261023)
    n, diff = 0, 0
    for _ in range(200_000):
        rad = A + rng.random() * (1.0e8 - A)
        lat = math.asin(2.0 * rng.random() - 1.0)
        lon = 2.0 * math.pi * rng.random()
        r = np.array(
            [
                rad * math.cos(lat) * math.cos(lon),
                rad * math.cos(lat) * math.sin(lon),
                rad * math.sin(lat),
            ]
        )
        n += 1
        diff += new.acceleration(0.0, r, Z3).tobytes() != ref.acceleration(0.0, r, Z3).tobytes()
    for pole in ([0.0, 0.0, A], [0.0, 0.0, -A], [A, 0.0, 0.0], [0.0, -A, 0.0]):
        n += 1
        diff += (
            new.acceleration(0.0, np.array(pole), Z3).tobytes()
            != ref.acceleration(0.0, np.array(pole), Z3).tobytes()
        )
    out["bit_identity_valid_states"] = {"states": n, "differing": diff, "seed": 20261023}

    rp, ra = A + 300e3, A + 1000e3
    trajectories = []
    for inc in (28.5, 51.6, 97.0):
        r0, v0 = elements_to_rv(
            0.5 * (rp + ra),
            (ra - rp) / (ra + rp),
            math.radians(inc),
            math.radians(30.0),
            math.radians(40.0),
            0.0,
            MU,
        )
        a = propagate(CompositeForceModel([PointMassGravity(MU), new]), r0, v0, 10.0, 6000)
        b = propagate(CompositeForceModel([PointMassGravity(MU), ref]), r0, v0, 10.0, 6000)
        trajectories.append({"inclination_deg": inc, "states": 6001, "bit_identical": a == b})
    out["bit_identity_rk4_trajectories"] = trajectories
    Path(out_path).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
