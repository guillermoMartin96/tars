# ruff: noqa  -- planning-experiment script kept as run (VAL-0008/0009); not project code.
"""Impulsive-limit order and sensed-dv (rocket equation) accuracy. Research only."""

import json
import math
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, sys.argv[1])
from tars.astro import kepler
from tars.astro.elements import rv_to_elements
from tars.sim.runner import initial_state
from tars.sim.scenario import load_scenario

SC = load_scenario(sys.argv[2])
MU = SC.constants.mu
G0 = 9.80665
ISP, M0 = 312.0, 1300.0
r0, v0 = initial_state(SC)
T_IGN = 600.0


def run(F, T):
    mdot = F / (ISP * G0)

    def rhs(t, y):
        r, v, m = y[:3], y[3:6], y[6]
        u = v / np.linalg.norm(v)
        return np.concatenate([v, -MU * r / np.linalg.norm(r) ** 3 + F / m * u, [-mdot, F / m]])

    rI, vI = kepler.propagate(r0, v0, T_IGN, MU)
    sol = solve_ivp(
        rhs, (0, T), np.concatenate([rI, vI, [M0, 0.0]]), method="DOP853", rtol=1e-13, atol=1e-10
    )
    y = sol.y[:, -1]
    a_fin = rv_to_elements(y[:3], y[3:6], MU).a
    dv_ideal = ISP * G0 * math.log(M0 / (M0 - mdot * T))
    rm, vm = kepler.propagate(rI, vI, T / 2, MU)
    a_imp = rv_to_elements(rm, vm + dv_ideal * vm / np.linalg.norm(vm), MU).a
    return dict(
        F=F, T=T, a_fin_minus_imp=a_fin - a_imp, sensed_minus_rocket_eq=y[7] - dv_ideal, dv=dv_ideal
    )


rows = [run(490.0 * k, 77.3 / k) for k in (0.25, 0.5, 1, 2, 4, 8)]
for a, b in zip(rows, rows[1:]):
    b["ratio_prev"] = a["a_fin_minus_imp"] / b["a_fin_minus_imp"]


# RK4 dt=10 sensed dv error, burn aligned to grid start, cutoff mid-step (split)
def rk4(f, t, y, h):
    k1 = f(t, y)
    k2 = f(t + h / 2, y + h / 2 * k1)
    k3 = f(t + h / 2, y + h / 2 * k2)
    k4 = f(t + h, y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


F = 490.0
T = 77.3
mdot = F / (ISP * G0)


def rhs(t, y):
    r, v, m = y[:3], y[3:6], y[6]
    u = v / np.linalg.norm(v)
    return np.concatenate([v, -MU * r / np.linalg.norm(r) ** 3 + F / m * u, [-mdot, F / m]])


rI, vI = kepler.propagate(r0, v0, T_IGN, MU)
y = np.concatenate([rI, vI, [M0, 0.0]])
t = 0.0
for h in [10.0] * 7 + [7.3]:
    y = rk4(rhs, t, y, h)
    t += h
dv_ideal = ISP * G0 * math.log(M0 / (M0 - mdot * T))
print(
    json.dumps(
        dict(
            impulsive_limit=rows,
            rk4_dt10_sensed_dv_err=y[7] - dv_ideal,
            rk4_mass_err=y[6] - (M0 - mdot * T),
        ),
        indent=1,
    )
)
