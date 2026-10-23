"""M3 T1: evidence that the Review 01 corrections (I-19) hold and change no valid result.

1. Re-runs each Review 01 reproduction (M3T1-R1-F1, F2) against the corrected component.
2. Bit-identity: the corrected acceleration equals the reviewed one (``97b69ef``, loaded
   from OLD_SRC) bit for bit on 200 000 deterministic pseudo-random states from 6 378 km
   to 100 000 km, at every latitude, and on four axis states (M3T1-R2-F3: no trajectory
   is checked here).
3. The numerical domain for the canonical constants: the smallest and largest equatorial
   radius accepted, found by bisection on binary64 values.

Usage (from the repository root; OLD_SRC is a checkout of src/ at 97b69ef):
    uv run python docs/science/experiments/m3-t1/t1_review01_correction_check.py OLD_SRC OUT.json
"""

from __future__ import annotations

import importlib.util
import json
import math
import random
import struct
import sys
from pathlib import Path

import numpy as np

from tars.sim.constants import WGS84_EGM2008_TIDE_FREE as K
from tars.sim.forces import ZonalJ2Gravity

MU, A, J2 = K.mu, K.equatorial_radius, K.j2
Z3 = np.zeros(3)


def load_old(old_src: str):
    spec = importlib.util.spec_from_file_location(
        "old_forces", Path(old_src) / "tars/sim/forces.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ZonalJ2Gravity


def outcome(model, r):
    try:
        return {"result": [repr(float(c)) for c in model.acceleration(0.0, np.array(r), Z3)]}
    except (ValueError, ZeroDivisionError) as e:
        return {"raises": type(e).__name__, "message": str(e)}


def accepted(x: float) -> bool:
    return "result" in outcome(ZonalJ2Gravity(MU, A, J2), [x, 0.0, 0.0])


def boundary(good_x: float, bad_x: float) -> float:
    """The accepted radius adjacent to the rejected side, by bisection on the binary64
    bit patterns (positive doubles order like their bit patterns)."""
    assert accepted(good_x) and not accepted(bad_x)
    g, b = (struct.unpack("<q", struct.pack("<d", v))[0] for v in (good_x, bad_x))
    while abs(b - g) > 1:
        m = (g + b) // 2
        if accepted(struct.unpack("<d", struct.pack("<q", m))[0]):
            g = m
        else:
            b = m
    return struct.unpack("<d", struct.pack("<q", g))[0]


def main(old_src: str, out_path: str) -> None:
    old_cls = load_old(old_src)
    new, old = ZonalJ2Gravity(MU, A, J2), old_cls(MU, A, J2)
    out: dict = {}

    # F1
    f1 = {}
    for name in ("mu", "equatorial_radius", "j2", "name", "extra"):
        try:
            setattr(new, name, 0.0)
            f1[f"set_{name}"] = "allowed"
        except AttributeError as e:
            f1[f"set_{name}"] = f"AttributeError: {e}"
        try:
            delattr(new, name)
            f1[f"del_{name}"] = "allowed"
        except AttributeError as e:
            f1[f"del_{name}"] = f"AttributeError: {e}"
    f1["has_instance_dict"] = hasattr(new, "__dict__")
    out["F1"] = f1

    # F2: the Review 01 reproduction inputs, before and after
    cases = {
        "x=1e62": [1e62, 0.0, 0.0],
        "x=1e70": [1e70, 0.0, 0.0],
        "x=1e200": [1e200, 0.0, 0.0],
        "x=1e-100": [1e-100, 0.0, 0.0],
        "x=5e-324": [5e-324, 0.0, 0.0],
        "origin": [0.0, 0.0, 0.0],
        "x=inf": [math.inf, 0.0, 0.0],
        "x=nan": [math.nan, 0.0, 0.0],
    }
    out["F2_states"] = {
        k: {"reviewed": outcome(old, r), "corrected": outcome(new, r)} for k, r in cases.items()
    }
    params = {}
    for label, args in (("mu=inf", (math.inf, A, J2)), ("a=inf", (MU, math.inf, J2))):
        row = {}
        for tag, cls in (("reviewed", old_cls), ("corrected", ZonalJ2Gravity)):
            try:
                row[tag] = {"accepted": True, **outcome(cls(*args), [A, 0.0, 0.0])}
            except ValueError as e:
                row[tag] = {"accepted": False, "message": str(e)}
        params[label] = row
    out["F2_parameters"] = params
    out["numerical_domain_equatorial_canonical"] = {
        "largest_accepted_x_m": boundary(1e61, 1e62),
        "smallest_accepted_x_m": boundary(1e-50, 1e-60),
    }

    # Bit identity on valid states
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
        diff += new.acceleration(0.0, r, Z3).tobytes() != old.acceleration(0.0, r, Z3).tobytes()
    for pole in ([0.0, 0.0, A], [0.0, 0.0, -A], [A, 0.0, 0.0], [0.0, -A, 0.0]):
        n += 1
        diff += (
            new.acceleration(0.0, np.array(pole), Z3).tobytes()
            != old.acceleration(0.0, np.array(pole), Z3).tobytes()
        )
    out["bit_identity_valid_states"] = {"states": n, "differing": diff, "seed": 20261023}
    zero_new, zero_old = ZonalJ2Gravity(MU, A, 0.0), old_cls(MU, A, 0.0)
    r = np.array([4.1e6, -2.7e6, 5.0e6])
    out["bit_identity_j2_zero"] = (
        zero_new.acceleration(0.0, r, Z3).tobytes() == zero_old.acceleration(0.0, r, Z3).tobytes()
    )
    Path(out_path).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
