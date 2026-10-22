"""M3 T1 informational measurements for VAL-0020 (NOT gates; no tolerance is applied).

Uses the production components (PointMassGravity + ZonalJ2Gravity, RK4) to measure:
1. node and perigee drift rates against first-order secular J2 theory (DR-0025 Q1);
2. invariant drift (energy, h_z) against dt (DR-0025 Q2, characterization);
3. RK4 convergence on the J2 configuration (DR-0025 Q10, characterization);
4. margins of the two derived gates in tests/test_zonal_j2.py (how much of each bound
   is used), recorded so the reviewer can see the gates are not borderline.

First-order theory (SCI-0013 [CUR] section 10.7; Vallado section 9.6):
    dRAAN/dt = -(3/2) n J2 (R/p)^2 cos i,   dargp/dt = (3/4) n J2 (R/p)^2 (5 cos^2 i - 1)
with n = sqrt(mu / a^3), p = a (1 - e^2). It is first order in J2 and holds for mean
elements; the comparison below uses osculating elements (initial, and time-averaged),
so a discrepancy of order J2-relative is expected and no acceptance threshold exists.

Usage (from the repository root):
    uv run python docs/science/experiments/m3-t1/t1_j2_informational.py OUT.json
"""

from __future__ import annotations

import itertools
import json
import math
import platform
import sys

import numpy as np

from tars.astro.elements import elements_to_rv, rv_to_elements
from tars.sim.constants import WGS84_EGM2008_TIDE_FREE as K
from tars.sim.forces import CompositeForceModel, PointMassGravity, ZonalJ2Gravity
from tars.sim.integrators import RK4

MU, RE, J2 = K.mu, K.equatorial_radius, K.j2
RP, RA = RE + 300e3, RE + 1000e3
A0, E0 = 0.5 * (RP + RA), (RA - RP) / (RA + RP)
PERIOD = 2.0 * math.pi * math.sqrt(A0**3 / MU)
DAY = 86400.0


def model(j2: float = J2) -> CompositeForceModel:
    return CompositeForceModel([PointMassGravity(MU), ZonalJ2Gravity(MU, RE, j2)])


def propagate(m, y0, dt: float, steps: int) -> np.ndarray:
    def f(t, y):
        return np.concatenate([y[3:], m.acceleration(t, y[:3], y[3:])])

    rk4, y, out = RK4(), y0.copy(), [y0.copy()]
    for k in range(steps):
        y = rk4.step(f, k * dt, y, dt)
        out.append(y)
    return np.array(out)


def initial_state(inc_deg: float) -> np.ndarray:
    r, v = elements_to_rv(
        A0, E0, math.radians(inc_deg), math.radians(30.0), math.radians(40.0), 0.0, MU
    )
    return np.concatenate([r, v])


def rates(a: float, e: float, i: float) -> tuple[float, float]:
    n = math.sqrt(MU / a**3)
    f = n * J2 * (RE / (a * (1.0 - e * e))) ** 2
    return -1.5 * f * math.cos(i), 0.75 * f * (5.0 * math.cos(i) ** 2 - 1.0)


def drift_rates(inc_deg: float, orbits: int = 30, dt: float = 10.0) -> dict:
    steps = round(orbits * PERIOD / dt)
    ys = propagate(model(), initial_state(inc_deg), dt, steps)
    t = dt * np.arange(len(ys))
    el = [rv_to_elements(y[:3], y[3:], MU) for y in ys]
    raan = np.unwrap([x.raan for x in el])
    argp = np.unwrap([x.argp for x in el])
    fit_raan = float(np.polyfit(t, raan, 1)[0])
    fit_argp = float(np.polyfit(t, argp, 1)[0])
    th0 = rates(el[0].a, el[0].e, el[0].i)
    thm = rates(
        float(np.mean([x.a for x in el])),
        float(np.mean([x.e for x in el])),
        float(np.mean([x.i for x in el])),
    )
    deg_day = math.degrees(1.0) * DAY

    def rel(meas, th):
        return None if th == 0.0 else (meas - th) / abs(th)

    return {
        "inclination_deg": inc_deg,
        "horizon_s": float(t[-1]),
        "dt_s": dt,
        "raan_rate_deg_per_day": {
            "measured_fit": fit_raan * deg_day,
            "first_order_initial_osculating": th0[0] * deg_day,
            "first_order_mean_of_osculating": thm[0] * deg_day,
            "relative_discrepancy_vs_initial": rel(fit_raan, th0[0]),
            "relative_discrepancy_vs_mean": rel(fit_raan, thm[0]),
            "sign_agrees_with_theory": math.copysign(1, fit_raan) == math.copysign(1, th0[0]),
        },
        "argp_rate_deg_per_day": {
            "measured_fit": fit_argp * deg_day,
            "first_order_initial_osculating": th0[1] * deg_day,
            "first_order_mean_of_osculating": thm[1] * deg_day,
            "relative_discrepancy_vs_initial": rel(fit_argp, th0[1]),
            "relative_discrepancy_vs_mean": rel(fit_argp, thm[1]),
            "sign_agrees_with_theory": math.copysign(1, fit_argp) == math.copysign(1, th0[1]),
        },
    }


def energy(y: np.ndarray) -> float:
    x, yy, z = (float(c) for c in y[:3])
    r2 = x * x + yy * yy + z * z
    r = math.sqrt(r2)
    u2 = -0.5 * MU * J2 * RE * RE * (3.0 * z * z / (r2 * r2 * r) - 1.0 / (r2 * r))
    return 0.5 * float(y[3:] @ y[3:]) - MU / r - u2


def invariant_drift(inc_deg: float = 51.6, orbits: int = 10) -> list[dict]:
    out = []
    y0 = initial_state(inc_deg)
    e0, hz0 = energy(y0), float(y0[0] * y0[4] - y0[1] * y0[3])
    for dt in (40.0, 20.0, 10.0, 5.0, 2.5):
        ys = propagate(model(), y0, dt, round(orbits * PERIOD / dt))
        out.append(
            {
                "dt_s": dt,
                "max_rel_energy_drift": max(abs(energy(y) - e0) for y in ys) / abs(e0),
                "max_rel_hz_drift": max(abs(float(y[0] * y[4] - y[1] * y[3]) - hz0) for y in ys)
                / abs(hz0),
            }
        )
    for a, b in itertools.pairwise(out):
        b["energy_order_vs_previous"] = math.log2(
            a["max_rel_energy_drift"] / b["max_rel_energy_drift"]
        )
        b["hz_order_vs_previous"] = math.log2(a["max_rel_hz_drift"] / b["max_rel_hz_drift"])
    return out


def convergence(inc_deg: float = 51.6, orbits: int = 10) -> dict:
    """Successive-difference order estimate: |y(dt) - y(dt/2)| / |y(dt/2) - y(dt/4)| -> 2^p."""
    y0 = initial_state(inc_deg)
    horizon = 40.0 * round(orbits * PERIOD / 40.0)
    finals = {
        dt: propagate(model(), y0, dt, int(horizon / dt))[-1] for dt in (40.0, 20.0, 10.0, 5.0)
    }
    d = [
        float(np.linalg.norm(finals[a][:3] - finals[b][:3]))
        for a, b in ((40.0, 20.0), (20.0, 10.0), (10.0, 5.0))
    ]
    return {
        "horizon_s": horizon,
        "position_differences_m": {"40-20": d[0], "20-10": d[1], "10-5": d[2]},
        "observed_order": [math.log2(d[0] / d[1]), math.log2(d[1] / d[2])],
        "estimated_rk4_error_at_dt10_m": d[2] * 16.0 / 15.0,
    }


def gate_margins() -> dict:
    """Utilisation of the gradient bound and the invariant-drift ratios of the T1 gates."""
    sys.path.insert(0, ".")
    import tests.test_zonal_j2 as t  # the gate's own helpers, so the numbers match it

    m = t.j2_model()
    worst = 0.0
    for r in t.sample_points():
        grad = np.array(t.j2_potential(*t.seeds(r)).grad)
        grad_abs = np.array(t.j2_potential(*t.seeds(r, absolute=True)).grad)
        bound = t.gamma(64) * (t.acceleration_abs(r) + grad_abs)
        err = np.abs(m.acceleration(0.0, r, np.zeros(3)) - grad)
        worst = max(worst, max(float(e / b) for e, b in zip(err, bound, strict=True) if b > 0.0))
    ratios = {}
    for inc in (28.5, 51.6, 97.0):
        r0, v0 = t.eccentric_state(inc)
        both = CompositeForceModel([PointMassGravity(MU), m])
        period = 2.0 * math.pi * math.sqrt((0.5 * (2 * RE + 1300e3)) ** 3 / MU)
        d = {}
        for dt in (20.0, 5.0):
            ys = t.propagate(both, r0, v0, dt, round(10 * period / dt))
            e0, hz0 = t.specific_energy(r0, v0), t.h_z(r0, v0)
            d[dt] = (
                max(abs(t.specific_energy(y[:3], y[3:]) - e0) for y in ys) / abs(e0),
                max(abs(t.h_z(y[:3], y[3:]) - hz0) for y in ys) / abs(hz0),
            )
        ratios[str(inc)] = {
            "energy_drift_ratio_dt5_over_dt20": d[5.0][0] / d[20.0][0],
            "hz_drift_ratio_dt5_over_dt20": d[5.0][1] / d[20.0][1],
            "gate": 0.5,
        }
    return {"gradient_max_error_over_bound": worst, "invariant_drift_ratios": ratios}


def main(out_path: str) -> None:
    result = {
        "record": "VAL-0020 (informational; no gate, no threshold)",
        "constants": {"c20": K.c20, "j2": J2, "j2_hex": J2.hex(), "mu": MU, "re": RE},
        "orbit": {
            "perigee_alt_m": 300e3,
            "apogee_alt_m": 1000e3,
            "a_m": A0,
            "e": E0,
            "raan0_deg": 30.0,
            "argp0_deg": 40.0,
        },
        "host": {
            "python": sys.version.split()[0],
            "machine": platform.machine(),
            "system": platform.system(),
        },
        "drift_rates": [drift_rates(i) for i in (28.5, 51.6, 63.4349, 80.0, 100.0, 120.0, 150.0)],
        "invariant_drift_51_6deg": invariant_drift(),
        "rk4_convergence_51_6deg": convergence(),
        "gate_margins": gate_margins(),
    }
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")


if __name__ == "__main__":
    main(sys.argv[1])
