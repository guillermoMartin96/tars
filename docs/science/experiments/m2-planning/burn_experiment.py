# ruff: noqa  -- planning-experiment script kept as run (VAL-0008/0009); not project code.
"""M2 planning experiment (research only, not project code).

Finite prograde burn from the M1 initial state. Model:
  r' = v
  v' = -mu r/|r|^3 + (F/m) u(r, v)         u = +v/|v| (VNB tracking) or fixed inertial
  m' = -F/(Isp g0)                         during the burn, 0 otherwise
Compares fixed-step RK4 (with/without step splitting at engine cutoff) against
SciPy DOP853 (rtol 1e-13) integrated segment-wise across the burn boundaries.
"""

from __future__ import annotations

import json
import math
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, sys.argv[1])  # repo src
from tars.astro import kepler
from tars.astro.elements import rv_to_elements
from tars.sim.runner import initial_state
from tars.sim.scenario import load_scenario

SC = load_scenario(sys.argv[2])
MU = SC.constants.mu
G0 = 9.80665
F, ISP = 490.0, 312.0
DRY, PROP = 1000.0, 300.0
MDOT = F / (ISP * G0)
T_IGN = 600.0
T_BURN = 77.3  # deliberately not a multiple of dt
T_END = 53_700.0


def rhs_factory(mode: str, u_fixed=None):
    def rhs(t, y, on):
        r, v, m = y[:3], y[3:6], y[6]
        a = -MU * r / np.linalg.norm(r) ** 3
        if on:
            u = v / np.linalg.norm(v) if mode == "track" else u_fixed
            a = a + (F / m) * u
        return np.concatenate([v, a, [-MDOT if on else 0.0]])

    return rhs


def dop(y0, mode, t_end=T_END, u_fixed=None):
    rhs = rhs_factory(mode, u_fixed)
    segs = [(0.0, T_IGN, False), (T_IGN, T_IGN + T_BURN, True), (T_IGN + T_BURN, t_end, False)]
    y = y0
    out = {}
    for a, b, on in segs:
        sol = solve_ivp(
            lambda t, y: rhs(t, y, on), (a, b), y, method="DOP853", rtol=1e-13, atol=1e-9
        )
        y = sol.y[:, -1]
        out[b] = y.copy()
    return out


def rk4_step(f, t, y, h):
    k1 = f(t, y)
    k2 = f(t + h / 2, y + h / 2 * k1)
    k3 = f(t + h / 2, y + h / 2 * k2)
    k4 = f(t + h, y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def rk4(y0, dt, mode, split=True, t_end=T_END, u_fixed=None):
    rhs = rhs_factory(mode, u_fixed)
    t_off = T_IGN + T_BURN
    n = round(t_end / dt)
    y = y0.copy()
    at_cut = None
    for k in range(n):
        t0, t1 = k * dt, (k + 1) * dt
        bounds = sorted({t0, t1, *[b for b in (T_IGN, t_off) if t0 < b < t1]})
        if not split:
            bounds = [t0, t1]
        for a, b in zip(bounds[:-1], bounds[1:]):
            mid = 0.5 * (a + b)
            on_at = lambda t: T_IGN <= t < t_off  # noqa: E731
            if split:
                y = rk4_step(lambda t, yy: rhs(t, yy, on_at(mid)), a, y, b - a)
            else:
                y = rk4_step(lambda t, yy: rhs(t, yy, on_at(t)), a, y, b - a)
        if at_cut is None and t1 >= t_off:
            at_cut = (t1, y.copy())
    return y, at_cut


def main():
    r0, v0 = initial_state(SC)
    y0 = np.concatenate([r0, v0, [DRY + PROP]])
    res = {
        "config": dict(
            F=F,
            Isp=ISP,
            g0=G0,
            dry=DRY,
            prop=PROP,
            mdot=MDOT,
            t_ign=T_IGN,
            t_burn=T_BURN,
            t_end=T_END,
        )
    }
    ref = dop(y0, "track")
    yf_ref = ref[T_END]
    m_after = DRY + PROP - MDOT * T_BURN
    res["prop_used_analytic"] = MDOT * T_BURN
    res["dv_ideal_rocket_eq"] = ISP * G0 * math.log((DRY + PROP) / m_after)
    res["ref_mass_after_minus_analytic"] = float(ref[T_IGN + T_BURN][6] - m_after)

    # Post-burn coast vs Kepler (independent oracle for the coast arc)
    yb = ref[T_IGN + T_BURN]
    rk, vk = kepler.propagate(yb[:3], yb[3:6], T_END - (T_IGN + T_BURN), MU)
    res["dop_coast_vs_kepler_pos_m"] = float(np.linalg.norm(rk - yf_ref[:3]))

    el0 = rv_to_elements(r0, v0, MU)
    el1 = rv_to_elements(yb[:3], yb[3:6], MU)
    res["sma_before_m"] = el0.a if hasattr(el0, "a") else str(el0)
    res["sma_after_m"] = el1.a if hasattr(el1, "a") else str(el1)
    a1 = el1.a
    e1 = el1.e
    res["ecc_after"] = e1
    res["apoapsis_alt_after_m"] = a1 * (1 + e1) - SC.constants.equatorial_radius
    res["periapsis_alt_after_m"] = a1 * (1 - e1) - SC.constants.equatorial_radius

    # Impulsive equivalent at burn midpoint: ideal dv along velocity, on the unperturbed circle
    tm = T_IGN + T_BURN / 2
    rm, vm = kepler.propagate(r0, v0, tm, MU)
    vimp = vm + res["dv_ideal_rocket_eq"] * vm / np.linalg.norm(vm)
    eli = rv_to_elements(rm, vimp, MU)
    res["impulsive_sma_m"] = eli.a
    res["finite_minus_impulsive_sma_m"] = a1 - eli.a
    res["impulsive_apo_alt_m"] = eli.a * (1 + eli.e) - SC.constants.equatorial_radius

    # RK4 accuracy
    rows = []
    for dt in (20.0, 10.0, 5.0, 2.5, 1.0):
        y, cut = rk4(y0, dt, "track", split=True)
        rows.append(
            dict(
                dt=dt,
                pos_err_m=float(np.linalg.norm(y[:3] - yf_ref[:3])),
                vel_err_mps=float(np.linalg.norm(y[3:6] - yf_ref[3:6])),
                mass_err_kg=float(y[6] - yf_ref[6]),
            )
        )
    res["rk4_split_track"] = rows
    y, cut = rk4(y0, 10.0, "track", split=False)
    res["rk4_nosplit_dt10"] = dict(
        pos_err_m=float(np.linalg.norm(y[:3] - yf_ref[:3])),
        vel_err_mps=float(np.linalg.norm(y[3:6] - yf_ref[3:6])),
        mass_err_kg=float(y[6] - yf_ref[6]),
    )
    # error right after the burn (first tick at/after cutoff), dt=10 split
    y, (tc, ycut) = rk4(y0, 10.0, "track", split=True)
    refc = dop(y0, "track", t_end=tc)[tc] if tc > T_IGN + T_BURN else ref[T_IGN + T_BURN]
    res["rk4_split_dt10_at_cutoff_tick"] = dict(
        t=tc,
        pos_err_m=float(np.linalg.norm(ycut[:3] - refc[:3])),
        vel_err_mps=float(np.linalg.norm(ycut[3:6] - refc[3:6])),
        mass_err_kg=float(ycut[6] - refc[6]),
    )

    # No-burn baseline RK4 error over same span (M1-like)
    def coast(t, y):
        r, v = y[:3], y[3:6]
        return np.concatenate([v, -MU * r / np.linalg.norm(r) ** 3, [0.0]])

    yb0 = y0.copy()
    for k in range(round(T_END / 10)):
        yb0 = rk4_step(coast, k * 10.0, yb0, 10.0)
    rkk, _ = kepler.propagate(r0, v0, T_END, MU)
    res["rk4_noburn_dt10_pos_err_m"] = float(np.linalg.norm(yb0[:3] - rkk))

    # Fixed inertial direction (velocity direction frozen at ignition) vs tracking
    rI, vI = kepler.propagate(r0, v0, T_IGN, MU)
    u_fixed = vI / np.linalg.norm(vI)
    reff = dop(y0, "fixed", u_fixed=u_fixed)
    ybf = reff[T_IGN + T_BURN]
    elf = rv_to_elements(ybf[:3], ybf[3:6], MU)
    res["fixed_inertial_sma_m"] = elf.a
    res["fixed_minus_track_sma_m"] = elf.a - a1
    res["fixed_vs_track_final_pos_diff_m"] = float(np.linalg.norm(reff[T_END][:3] - yf_ref[:3]))

    res["ref_final_state"] = yf_ref.tolist()
    res["ref_cutoff_state"] = yb.tolist()
    print(json.dumps(res, indent=1, default=float))


main()
