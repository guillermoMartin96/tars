# ruff: noqa  -- planning-experiment script kept as run; not project code.
"""M3 planning experiment (research only, not project code; no Proof gate).

Measures, for candidate M3 physics (J2 and atmospheric drag), the quantities the
G1/G2/G3 Decision Requests need before any threshold or design is proposed:

1. acceleration magnitudes at the M1/M2 reference orbit;
2. fixed-step RK4 error and convergence order against SciPy DOP853 (dt = 20, 10, 5, 2.5 s);
3. J2 secular node rate (fit) against the first-order analytic rate;
4. drag decay against the first-order analytic estimate;
5. sensitivity of the trajectory to candidate-constant and modelling choices
   (J2 value set, GM TT vs TCG, pole of the J2 axis, spherical vs geodetic altitude,
   atmosphere co-rotation);
6. density discontinuities at the band boundaries of the piecewise-exponential table.

Everything here is written independently of `src/tars` except the scenario loader and
the M1 initial state, so that it measures candidate physics, not production code.
Usage: uv run --no-sync python perturbation_experiment.py <repo>/src <repo>/scenarios/m1_leo_250km.json <out.json>
"""

from __future__ import annotations

import json
import math
import sys
import time

import numpy as np
from scipy.integrate import solve_ivp

SC = OUT = R0 = V0 = None  # set by load() (module importable by gmat_probe.py)


def load(src: str, scenario: str) -> None:
    global SC, R0, V0
    sys.path.insert(0, src)
    from tars.sim.runner import initial_state
    from tars.sim.scenario import load_scenario

    SC = load_scenario(scenario)
    R0, V0 = (np.array(x, dtype=float) for x in initial_state(SC))


# ----------------------------------------------------------------------- candidate constants
MU_WGS84 = 3.986004418e14  # NGA.STND.0036 Table 3.1; IERS TN36 Table 1.1 (TCG-compatible)
MU_TT = 3.986004415e14  # IERS TN36 §1.2 / ch. 6: TT-compatible value; EGM2008 scaling GM
RE_WGS84 = 6378137.0  # NGA.STND.0036 Table 3.1
RE_EGM2008 = 6378136.3  # IERS TN36 ch. 6 (EGM2008 scaling radius)
F_WGS84 = 1.0 / 298.257223563
OMEGA_E = 7.292115e-5  # NGA.STND.0036 Table 3.1 (nominal mean angular velocity)
SQRT5 = math.sqrt(5.0)
J2_SETS = {
    # J2 = -sqrt(5) * Cbar20
    "EGM2008_tide_free(NGA.STND.0036 T5.1)": -SQRT5 * -0.484165143790815e-3,
    "IERS2010_zero_tide(T1.1)": 1.0826359e-3,
    "IERS_conv_C20_zero_tide_2000(T6.2)": -SQRT5 * -0.48416948e-3,
    "IERS_conv_C20_tide_free_2000(§6.2.2)": -SQRT5 * -0.48416531e-3,
    "JGM3(GMAT JGM3.cof)": -SQRT5 * -4.84165374886470e-04,
    "EGM96(GMAT EGM96.cof)": -SQRT5 * -4.84165371736000e-04,
    "WGS84_normal_field(geometric; NOT dynamic)": -SQRT5 * -0.484166774985001e-3,
}
J2_REF = J2_SETS["EGM2008_tide_free(NGA.STND.0036 T5.1)"]

# Piecewise-exponential table as distributed with GMAT R2026a
# (data/atmosphere/earth/EarthExponentialAtmosphereData.txt; GMAT cites Vallado, Fundamentals
# of Astrodynamics and Applications, 5th ed. (2022) §8.6). Columns: base altitude [km],
# base density [kg/m^3], scale height [km].
EXP_TABLE = [
    (0.0, 1.225, 7.249),
    (25.0, 3.899e-2, 6.349),
    (30.0, 1.774e-2, 6.682),
    (40.0, 3.972e-3, 7.554),
    (50.0, 1.057e-3, 8.382),
    (60.0, 3.206e-4, 7.714),
    (70.0, 8.770e-5, 6.549),
    (80.0, 1.905e-5, 5.799),
    (90.0, 3.396e-6, 5.382),
    (100.0, 5.297e-7, 5.877),
    (110.0, 9.661e-8, 7.263),
    (120.0, 2.438e-8, 9.473),
    (130.0, 8.484e-9, 12.636),
    (140.0, 3.845e-9, 16.149),
    (150.0, 2.070e-9, 22.523),
    (180.0, 5.464e-10, 29.740),
    (200.0, 2.789e-10, 37.105),
    (250.0, 7.248e-11, 45.546),
    (300.0, 2.418e-11, 53.628),
    (350.0, 9.518e-12, 53.298),
    (400.0, 3.725e-12, 58.515),
    (450.0, 1.585e-12, 60.828),
    (500.0, 6.967e-13, 63.822),
    (600.0, 1.454e-13, 71.835),
    (700.0, 3.614e-14, 88.667),
    (800.0, 1.170e-14, 124.64),
    (900.0, 5.245e-15, 181.05),
    (1000.0, 3.019e-15, 268.00),
]

# Illustrative ballistic coefficients only (no project spacecraft drag parameters exist):
# VAL-0007 used GMAT defaults (850 kg, 15 m^2, Cd 2.2) -> m/(Cd A) = 25.8 kg/m^2.
BALLISTIC = {"B25.8": 850.0 / (2.2 * 15.0), "B100": 100.0}

T_END = 53_700.0  # the M1/M2 horizon (10 orbits)


def density(h_m: float) -> float:
    hk = h_m / 1000.0
    base = EXP_TABLE[0]
    for row in EXP_TABLE:
        if hk >= row[0]:
            base = row
        else:
            break
    h0, rho0, H = base
    return rho0 * math.exp(-(hk - h0) / H)


def geodetic_height(r: np.ndarray, a: float = RE_WGS84, f: float = F_WGS84) -> float:
    """Height above the ellipsoid (iterative; axis = frame z). Sufficient for a sensitivity study."""
    x, y, z = r
    p = math.hypot(x, y)
    e2 = f * (2 - f)
    lat = math.atan2(z, p * (1 - e2))
    for _ in range(8):
        n = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
        h = p / math.cos(lat) - n
        lat = math.atan2(z, p * (1 - e2 * n / (n + h)))
    n = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    return p / math.cos(lat) - n


def rot_x(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def make_accel(
    mu, re, j2=None, drag=None, pole=None, altitude="spherical", corotate=True, re_alt=RE_WGS84
):
    """a(r, v). re: J2 reference radius; re_alt: spherical altitude datum for density (SCI-0006).
    pole: optional rotation matrix taking frame vectors into the J2/atmosphere body axes."""
    P = np.eye(3) if pole is None else pole
    PT = P.T
    w_body = np.array([0.0, 0.0, OMEGA_E])

    def accel(r, v):
        rn = math.sqrt(r @ r)
        a = -mu / rn**3 * r
        if j2 is not None:
            rb = P @ r
            x, y, z = rb
            k = -1.5 * j2 * mu * re**2 / rn**5
            zz = 5.0 * z * z / (rn * rn)
            ab = k * np.array([x * (1 - zz), y * (1 - zz), z * (3 - zz)])
            a = a + PT @ ab
        if drag is not None:
            h = (rn - re_alt) if altitude == "spherical" else geodetic_height(P @ r)
            rho = density(h)
            w = PT @ w_body if corotate else np.zeros(3)
            vrel = v - np.cross(w, r)
            a = a - 0.5 * rho / drag * math.sqrt(vrel @ vrel) * vrel
        return a

    return accel


def rk4(accel, r, v, dt, t_end):
    y = np.concatenate([r, v])
    f = lambda y: np.concatenate([y[3:], accel(y[:3], y[3:])])
    n = round(t_end / dt)
    for _ in range(n):
        k1 = f(y)
        k2 = f(y + 0.5 * dt * k1)
        k3 = f(y + 0.5 * dt * k2)
        k4 = f(y + dt * k3)
        y = y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    return y


def dop(accel, r, v, t_end, t_eval=None):
    sol = solve_ivp(
        lambda t, y: np.concatenate([y[3:], accel(y[:3], y[3:])]),
        (0.0, t_end),
        np.concatenate([r, v]),
        method="DOP853",
        rtol=1e-13,
        atol=1e-9,
        t_eval=t_eval,
        dense_output=False,
    )
    assert sol.success, sol.message
    return sol


def raan(r, v):
    h = np.cross(r, v)
    return math.atan2(h[0], -h[1])


def sma(r, v, mu):
    return 1.0 / (2.0 / math.sqrt(r @ r) - (v @ v) / mu)


def main():
    out = {
        "inputs": {
            "r0": R0.tolist(),
            "v0": V0.tolist(),
            "t_end_s": T_END,
            "J2_sets": J2_SETS,
            "ballistic_kg_m2": BALLISTIC,
        }
    }
    started = time.time()
    rn = math.sqrt(R0 @ R0)
    h0 = rn - RE_WGS84

    # 1. magnitudes at the initial state
    a_pm = MU_WGS84 / rn**2
    a_j2 = np.linalg.norm(
        make_accel(MU_WGS84, RE_WGS84, j2=J2_REF)(R0, V0) - make_accel(MU_WGS84, RE_WGS84)(R0, V0)
    )
    mags = {
        "point_mass_mps2": a_pm,
        "j2_mps2_at_r0": float(a_j2),
        "j2_max_mps2_equator": 1.5 * J2_REF * MU_WGS84 * RE_WGS84**2 / rn**4 * 1.0,
        "j2_max_mps2_pole": 3.0 * J2_REF * MU_WGS84 * RE_WGS84**2 / rn**4,
    }
    for name, b in BALLISTIC.items():
        vrel = V0 - np.cross([0, 0, OMEGA_E], R0)
        mags[f"drag_{name}_mps2_at_250km"] = 0.5 * density(h0) / b * float(vrel @ vrel)
    mags["density_at_250km_spherical"] = density(h0)
    out["magnitudes"] = mags

    # 6. band-boundary density jumps (left limit vs table value)
    jumps = []
    for (h_a, rho_a, H_a), (h_b, rho_b, _) in zip(EXP_TABLE, EXP_TABLE[1:]):
        left = rho_a * math.exp(-(h_b - h_a) / H_a)
        jumps.append(
            {"boundary_km": h_b, "left_limit": left, "table": rho_b, "rel_jump": rho_b / left - 1.0}
        )
    out["band_boundary_jumps"] = jumps

    # 2. RK4 vs DOP853, convergence
    cases = {
        "point_mass": dict(),
        "j2": dict(j2=J2_REF),
        "drag_B25.8": dict(drag=BALLISTIC["B25.8"]),
        "j2_drag_B25.8": dict(j2=J2_REF, drag=BALLISTIC["B25.8"]),
        "j2_drag_B100": dict(j2=J2_REF, drag=BALLISTIC["B100"]),
    }
    conv = {}
    refs = {}
    for name, kw in cases.items():
        acc = make_accel(MU_WGS84, RE_WGS84, **kw)
        ref = dop(acc, R0, V0, T_END).y[:, -1]
        refs[name] = ref
        rows = []
        for dt in (20.0, 10.0, 5.0, 2.5):
            y = rk4(acc, R0, V0, dt, T_END)
            rows.append(
                {
                    "dt": dt,
                    "pos_err_m": float(np.linalg.norm(y[:3] - ref[:3])),
                    "vel_err_mps": float(np.linalg.norm(y[3:] - ref[3:])),
                }
            )
        for a, b in zip(rows, rows[1:]):
            b["ratio_vs_prev"] = a["pos_err_m"] / b["pos_err_m"] if b["pos_err_m"] else None
        conv[name] = rows
    out["rk4_vs_dop853"] = conv
    out["final_displacement_vs_point_mass_m"] = {
        name: float(np.linalg.norm(refs[name][:3] - refs["point_mass"][:3]))
        for name in refs
        if name != "point_mass"
    }

    # 3. J2 node rate: fit vs first-order analytic (osculating initial elements)
    acc = make_accel(MU_WGS84, RE_WGS84, j2=J2_REF)
    t_eval = np.arange(0.0, T_END + 1.0, 60.0)
    sol = dop(acc, R0, V0, T_END, t_eval=t_eval)
    node = np.unwrap([raan(sol.y[:3, k], sol.y[3:, k]) for k in range(sol.y.shape[1])])
    fit = np.polyfit(sol.t, node, 1)[0]
    a0 = sma(R0, V0, MU_WGS84)
    n0 = math.sqrt(MU_WGS84 / a0**3)
    inc = math.radians(SC.initial_orbit.inclination_deg)
    analytic = -1.5 * n0 * J2_REF * (RE_WGS84 / a0) ** 2 * math.cos(inc)
    out["j2_node_rate"] = {
        "fit_deg_per_day": math.degrees(fit) * 86400,
        "analytic_first_order_deg_per_day": math.degrees(analytic) * 86400,
        "rel_diff": fit / analytic - 1.0,
        "note": "osculating a0 used in the analytic rate; mean-element theory differs at O(J2)",
    }

    # 4. drag decay: mean SMA over the run vs first-order estimate
    decay = {}
    for name, b in BALLISTIC.items():
        acc = make_accel(MU_WGS84, RE_WGS84, drag=b)
        sol = dop(acc, R0, V0, T_END, t_eval=t_eval)
        a_series = np.array(
            [sma(sol.y[:3, k], sol.y[3:, k], MU_WGS84) for k in range(sol.y.shape[1])]
        )
        da_dt = np.polyfit(sol.t, a_series, 1)[0]
        rho = density(h0)
        v = math.sqrt(MU_WGS84 / a0)
        Fwind = (1 - a0 * OMEGA_E * math.cos(inc) / v) ** 2
        est = -rho / b * math.sqrt(MU_WGS84 * a0)
        decay[name] = {
            "fit_m_per_s": da_dt,
            "fit_km_per_day": da_dt * 86.4,
            "first_order_no_rotation_m_per_s": est,
            "first_order_with_rotation_factor_m_per_s": est * Fwind,
            "rotation_factor": Fwind,
            "rel_diff_vs_rotation_estimate": da_dt / (est * Fwind) - 1.0,
            "total_sma_change_m": float(a_series[-1] - a_series[0]),
        }
    out["drag_decay"] = decay

    # 5. sensitivities (final-state position differences at T_END, DOP853)
    sens = {}
    base = make_accel(MU_WGS84, RE_WGS84, j2=J2_REF, drag=BALLISTIC["B25.8"])
    yb = dop(base, R0, V0, T_END).y[:, -1]

    def diff(acc, label):
        y = dop(acc, R0, V0, T_END).y[:, -1]
        sens[label] = float(np.linalg.norm(y[:3] - yb[:3]))

    for label, j2 in J2_SETS.items():
        if j2 != J2_REF:
            diff(make_accel(MU_WGS84, RE_WGS84, j2=j2, drag=BALLISTIC["B25.8"]), f"J2 = {label}")
    diff(
        make_accel(MU_TT, RE_WGS84, j2=J2_REF, drag=BALLISTIC["B25.8"]),
        "GM TT-compatible (3.986004415e14)",
    )
    diff(
        make_accel(MU_WGS84, RE_EGM2008, j2=J2_REF, drag=BALLISTIC["B25.8"]),
        "J2 reference radius 6378136.3 m (EGM2008); altitude datum unchanged",
    )
    diff(
        make_accel(MU_WGS84, RE_WGS84, j2=J2_REF, drag=BALLISTIC["B25.8"], re_alt=RE_WGS84 - 0.7),
        "altitude datum 0.7 m lower (6378136.3 m)",
    )
    # J2 only (no drag): constant-set sensitivities without drag amplification.
    j2_base = dop(make_accel(MU_WGS84, RE_WGS84, j2=J2_REF), R0, V0, T_END).y[:, -1]
    for label, j2 in J2_SETS.items():
        if j2 != J2_REF:
            yj = dop(make_accel(MU_WGS84, RE_WGS84, j2=j2), R0, V0, T_END).y[:, -1]
            sens[f"J2 only: J2 = {label}"] = float(np.linalg.norm(yj[:3] - j2_base[:3]))
    yj = dop(make_accel(MU_WGS84, RE_EGM2008, j2=J2_REF), R0, V0, T_END).y[:, -1]
    sens["J2 only: reference radius 6378136.3 m"] = float(np.linalg.norm(yj[:3] - j2_base[:3]))
    yj = dop(make_accel(MU_TT, RE_WGS84, j2=J2_REF), R0, V0, T_END).y[:, -1]
    sens["J2 only: GM TT-compatible"] = float(np.linalg.norm(yj[:3] - j2_base[:3]))
    # Precession of the pole between J2000.0 and 2026-01-01: about 20.04"/yr in declination
    # (general precession; approximate, rotation modelled as a tilt about the frame x axis).
    tilt = math.radians(20.04 / 3600.0 * 26.0)
    diff(
        make_accel(MU_WGS84, RE_WGS84, j2=J2_REF, drag=BALLISTIC["B25.8"], pole=rot_x(tilt)),
        "J2+atmosphere axis tilted 0.145 deg (approx. precession J2000->2026)",
    )
    diff(
        make_accel(
            MU_WGS84,
            RE_WGS84,
            j2=J2_REF,
            drag=BALLISTIC["B25.8"],
            pole=rot_x(math.radians(10 / 3600)),
        ),
        "J2+atmosphere axis tilted 10 arcsec (nutation-scale)",
    )
    diff(
        make_accel(MU_WGS84, RE_WGS84, j2=J2_REF, drag=BALLISTIC["B25.8"], altitude="geodetic"),
        "geodetic (WGS 84 ellipsoid) instead of spherical altitude",
    )
    diff(
        make_accel(MU_WGS84, RE_WGS84, j2=J2_REF, drag=BALLISTIC["B25.8"], corotate=False),
        "non-rotating atmosphere",
    )
    diff(
        make_accel(MU_WGS84, RE_WGS84, j2=J2_REF, drag=BALLISTIC["B25.8"] * 1.01),
        "ballistic coefficient +1%",
    )
    # J2 only: axis tilted by the IAU 1976 precession angle theta_A over 26 years
    # (2004.1917"/century; Lieske et al. 1977), rotation about the frame y axis (the mean pole
    # moves towards the equinox direction). Compare with GMAT case j2_custom_2026 (gmat_probe.py).
    j2_only = dop(make_accel(MU_WGS84, RE_WGS84, j2=J2_REF), R0, V0, T_END).y[:, -1]
    th = math.radians(2004.1917 * 0.26 / 3600.0)
    c, s = math.cos(th), math.sin(th)
    roty = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])
    y = dop(make_accel(MU_WGS84, RE_WGS84, j2=J2_REF, pole=roty), R0, V0, T_END).y[:, -1]
    sens["J2 only: axis tilted theta_A(2026) = 521 arcsec about y"] = float(
        np.linalg.norm(y[:3] - j2_only[:3])
    )
    out["sensitivity_final_position_diff_m"] = sens
    out["runtime_s"] = time.time() - started
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    load(sys.argv[1], sys.argv[2])
    OUT = sys.argv[3]
    main()
