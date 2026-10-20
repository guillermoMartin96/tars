"""M3 T0: termination-domain analysis (corrections for Review 01 M3T0-F1, F2, F3).

Evidence for DR-0029 P1-P4 that replaces three generalisations the review disproved:

1. Missed crossings (F1). Between two committed states a trajectory can dip below the lower
   committed height. For a C2 height history h(t) on a step of length dt,
       dip <= (dt^2 / 8) * sup over the step of max(h'', 0)
   (g = h - chord has g(0) = g(dt) = 0 and g'' <= M, so g >= -M t (dt - t) / 2). Outside the
   ellipsoid, h is the distance to a convex surface, so
       h'' = n.a + v^T H v,   H <= |v_t|^2 / (h + b^2/a)
   where n is the geodetic normal, v_t the velocity component tangent to the level surface
   and b^2/a the smallest radius of curvature of the WGS 84 ellipsoid (meridian, equator):
   the eigenvalues of the distance Hessian are k_i / (1 + k_i h) <= 1 / (h + 1/k_max).
   `hddot_upper` is this pointwise bound U(r, v, a). For two-body motion on a bound orbit it
   is bounded over the whole orbit by a function of |r| alone, maximised in closed form
   over [r_p, r_a] (endpoints and the real roots of a cubic; `two_body_domain_bound`).
   That is the only certified orbit bound here. For perturbed motion (J2 + drag) no orbit
   bound is derived: the maximum of U over samples of a numerical trajectory is reported as
   a sampled estimate (Review 02 M3T0-R2-F1), and refinement between samples can exceed it.
   Dips are measured over sampling-phase, eccentricity and inclination sweeps.

2. Stiffness thresholds and admissibility (F2). Exact heights (not a 5 km grid) at which
   rho(h) |v| dt / B reaches kappa, for the circular-speed proxy used in DR-0029 P1 and for
   a speed bound valid for every bound state at geodetic height h:
       |v_rel| <= sqrt(2 mu / (b + h)) + omega_E (a + h)
   (negative two-body energy gives |v|^2 < 2 mu / |r|; b + h <= |r| <= a + h outside the
   ellipsoid). The reviewer's P1-admissible counterexamples are reproduced, and a derived
   sufficient condition for RK4 stages to stay above the lower edge is evaluated: geodetic
   height is 1-Lipschitz (signed distance to a convex body), so every stage of a step from
   y0 has h >= h(r0) - dt (|v0| + dt A / 2) with A >= |a| over the stages. The drag part
   of A is maximised over every height above the stage's lower bound (corrected after
   Review 02 M3T0-R2-F2; see `drag_envelope`).

3. RK4 stage order (F3): which stage input lies inside the arc.

Research only; no threshold, kappa or admissible domain is chosen here (DR-0029 stays OPEN).
Usage: uv run --no-sync python t0_termination.py <out.json>
"""

from __future__ import annotations

import json
import math
import sys
from decimal import ROUND_FLOOR, Decimal, localcontext
from fractions import Fraction

import numpy as np
import t0_model as m
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize_scalar

DT = 10.0
MASS = 850.0
B_V1 = MASS / (2.2 * 15.0)  # 25.76 kg/m^2, the spike's illustrative vehicle
RK4_REAL_STABILITY = 2.785293563405282  # as in t0_atmosphere.py
KAPPAS = (RK4_REAL_STABILITY, 1.0, 0.1, 0.01)
R_CURV_MIN = m.B_WGS84**2 / m.A_WGS84  # smallest radius of curvature of the ellipsoid
J2_DRAG = m.Config(j2=m.J2_FROM_C20, drag=m.Drag(cd=2.2, area_m2=15.0))
KEPLER = m.Config()
SAMPLE = 0.05  # s, dense-output sampling of h(t) in the sweeps
PHASES = tuple(k * 0.25 for k in range(40))  # step-grid offsets 0 ... 9.75 s
CERTIFIED = "certified: two-body orbit bound, maximised in closed form"
SAMPLED = "sampled estimate of dt^2/8 sup U on a numerical trajectory; not a bound"


# ---------------------------------------------------------------- geometry helpers
def normal(lat: float, lon: float) -> np.ndarray:
    return np.array([math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat)])


def hddot_upper(r: np.ndarray, v: np.ndarray, acc: np.ndarray) -> float:
    """Upper bound U(r, v, a) on d2h/dt2 for geodetic height h outside the ellipsoid."""
    lat, h = m.geodetic_iterative(r)
    n = normal(lat, math.atan2(r[1], r[0]))
    vn = float(n @ v)
    vt2 = max(float(v @ v) - vn * vn, 0.0)
    return float(n @ acc) + vt2 / (h + R_CURV_MIN)


def max_normal_angle() -> float:
    """Largest angle between the geodetic normal and the radius vector on the surface (it
    only decreases above the surface, since r = r_s + h n)."""
    one_m_e2 = 1.0 - m.E2_WGS84
    res = minimize_scalar(
        lambda p: -(p - math.atan(one_m_e2 * math.tan(p))),
        bounds=(0.1, 1.4),
        method="bounded",
        options={"xatol": 1e-14},
    )
    return -float(res.fun)


DELTA_MAX = max_normal_angle()


def two_body_domain_bound(sma: float, ecc: float) -> dict:
    """sup U over a two-body bound orbit (perigee radius > a): with |v|^2 = mu (2/r - 1/sma),
    h >= r - a and n.r_hat >= cos(DELTA_MAX),
        U <= g(r) = mu (2/r - 1/sma) / (r - a + b^2/a) - mu cos(DELTA_MAX) / r^2.
    g is smooth on [r_p, r_a], so its maximum is at an endpoint or a stationary point. With
    c = a - b^2/a, K = cos(DELTA_MAX) and s = sma, g'(r) = 0 is the cubic
        r^3 + (2 K s - 4 s) r^2 + (2 s c - 4 K s c) r + 2 K s c^2 = 0,
    so the maximum is exact up to floating-point rounding (no sampling)."""
    rp, ra = sma * (1.0 - ecc), sma * (1.0 + ecc)
    c, k = m.A_WGS84 - R_CURV_MIN, math.cos(DELTA_MAX)

    def g(r: float) -> float:
        return m.MU * (2.0 / r - 1.0 / sma) / (r - c) - m.MU * k / (r * r)

    cands = [rp, ra]
    if ra > rp:
        coeffs = [1.0, 2 * k * sma - 4 * sma, 2 * sma * c - 4 * k * sma * c, 2 * k * sma * c * c]
        cands += [float(z.real) for z in np.roots(coeffs) if abs(z.imag) < 1e-9 * abs(z)]
        cands = [r for r in cands if rp <= r <= ra]
    best_r = max(cands, key=g)
    best = g(best_r)
    return {"sup_hddot_mps2": best, "at_radius_m": best_r, "bound_m": max(best, 0.0) * DT**2 / 8}


# ------------------------------------------------------------- dense trajectories
def geodetic_heights(rr: np.ndarray) -> np.ndarray:
    """Vectorised form of m.geodetic_iterative (same fixed point, 12 iterations; the
    contraction factor is ~e^2, so 12 iterations converge far below round-off)."""
    x, y, z = rr
    p = np.hypot(x, y)
    a, e2 = m.A_WGS84, m.E2_WGS84
    lat = np.arctan2(z, p * (1.0 - e2))
    for _ in range(12):
        s = np.sin(lat)
        n = a / np.sqrt(1.0 - e2 * s * s)
        lat = np.arctan2(z + e2 * n * s, p)
    s, c = np.sin(lat), np.cos(lat)
    return p * c + z * s - a * np.sqrt(1.0 - e2 * s * s)


def dense(cfg: m.Config, y0: np.ndarray, t_end: float):
    sol = solve_ivp(
        m.rhs(cfg), (0.0, t_end), y0, method="DOP853", rtol=1e-13, atol=1e-9, dense_output=True
    )
    if sol.status < 0:
        raise RuntimeError(sol.message)
    return sol.sol


def phase_sweep(cfg: m.Config, y0: np.ndarray, t_end: float) -> dict:
    """Worst dip below the lower committed height over all steps and all 40 grid phases,
    with committed states taken on the exact (DOP853) trajectory."""
    sol = dense(cfg, y0, t_end)
    t = np.arange(0.0, t_end + 1e-9, SAMPLE)
    h = geodetic_heights(sol(t)[:3])
    per = round(DT / SAMPLE)
    cands = []
    for phase in PHASES:
        i0 = round(phase / SAMPLE)
        nsteps = (len(h) - 1 - i0) // per
        seg = h[i0 : i0 + nsteps * per + 1]
        ends = np.minimum(seg[:-1:per][:nsteps], seg[per::per][:nsteps])
        inner = np.lib.stride_tricks.sliding_window_view(seg, per + 1)[::per][:nsteps]
        dips = ends - inner.min(axis=1)
        for k in np.argsort(dips)[-3:]:
            cands.append((float(dips[k]), phase, i0 + int(k) * per))
    cands.sort(reverse=True)

    def h_at(tt: float) -> float:
        return m.geodetic_iterative(sol(tt)[:3])[1]

    best = {"max_dip_m": -math.inf}
    for _, phase, i in cands[:12]:  # refine the leading candidates exactly
        ta, tb = t[i], t[i + per]
        jm = i + int(np.argmin(h[i : i + per + 1]))
        lo, hi = max(t[jm] - SAMPLE, ta), min(t[jm] + SAMPLE, tb)
        res = minimize_scalar(h_at, bounds=(lo, hi), method="bounded", options={"xatol": 1e-9})
        dip = min(h_at(ta), h_at(tb)) - min(float(res.fun), h_at(lo), h_at(hi))
        if dip > best["max_dip_m"]:
            best = {"max_dip_m": dip, "phase_s": phase, "step_start_s": float(ta)}
    # Maximum of the pointwise bound U over 0.25 s samples of the numerical trajectory, then
    # refined between samples around the leading samples. Both are estimates of sup U, not
    # bounds (M3T0-R2-F1): the refinement exists to show that the sampled value can be
    # exceeded between samples.
    ts = np.arange(0.0, t_end + 1e-9, 0.25)
    ys = sol(ts)

    def u_at(tt: float) -> float:
        y = sol(tt)
        return hddot_upper(y[:3], y[3:6], m.acceleration(cfg, tt, y[:3], y[3:6], y[6]))

    us = np.array(
        [
            hddot_upper(
                ys[:3, j], ys[3:6, j], m.acceleration(cfg, ts[j], ys[:3, j], ys[3:6, j], ys[6, j])
            )
            for j in range(len(ts))
        ]
    )
    refined = float(us.max())
    for j in np.argsort(us)[-5:]:
        lo, hi = float(ts[max(j - 1, 0)]), float(ts[min(j + 1, len(ts) - 1)])
        res = minimize_scalar(lambda tt: -u_at(tt), bounds=(lo, hi), method="bounded")
        refined = max(refined, float(-res.fun))
    best["sampled_max_hddot_upper_mps2"] = float(us.max())
    best["refined_max_hddot_upper_mps2"] = refined
    best["sampled_estimate_m"] = max(float(us.max()), 0.0) * DT**2 / 8
    best["height_range_m"] = [float(h.min()), float(h.max())]
    return best


def midpoint_dip(cfg: m.Config, r0: np.ndarray, v0: np.ndarray) -> dict:
    """Review 01 construction: the lowest point at the middle of a step (committed states at
    -dt/2 and +dt/2), plus the maximum of U over 101 samples of that step (an estimate)."""
    y0 = np.concatenate([r0, v0, [MASS]])
    sol_b = dense(cfg, y0, -DT / 2)
    sol_f = dense(cfg, y0, DT / 2)
    h_ends = [m.geodetic_iterative(s(e)[:3])[1] for s, e in ((sol_b, -DT / 2), (sol_f, DT / 2))]
    h_mid = m.geodetic_iterative(r0)[1]
    sup_u = -math.inf
    for s, sign in ((sol_b, -1.0), (sol_f, 1.0)):
        for tt in np.linspace(0.0, sign * DT / 2, 101):
            y = s(tt)
            acc = m.acceleration(cfg, float(tt), y[:3], y[3:6], y[6])
            sup_u = max(sup_u, hddot_upper(y[:3], y[3:6], acc))
    return {
        "dip_m": min(h_ends) - h_mid,
        "sampled_max_hddot_upper_over_step_mps2": sup_u,
        "sampled_estimate_m": max(sup_u, 0.0) * DT**2 / 8,
    }


def orbit_elements(hp: float, ha: float) -> tuple[float, float]:
    rp, ra = m.A_WGS84 + hp, m.A_WGS84 + ha
    return 0.5 * (rp + ra), (ra - rp) / (ra + rp)


SWEEP_ORBITS = (
    # (perigee km, apogee km, inclination deg) - spherical altitudes, perigee at the node
    (250.0, 250.0, 0.0),
    (250.0, 250.0, 51.6),
    (250.0, 250.0, 97.0),
    (180.0, 180.0, 51.6),
    (250.0, 400.0, 51.6),
    (250.0, 800.0, 51.6),
    (250.0, 800.0, 97.0),
    (180.0, 800.0, 51.6),
    (250.0, 2000.0, 51.6),
)


def missed_crossing() -> dict:
    cases = {}
    ecc_state = m.perigee_state(250e3, 800e3, 51.6)
    circ_state = m.circular_state(250e3, 51.6)
    for name, (cfg, label), (r0, v0) in (
        ("kepler_250x800_i51.6_perigee_midstep", (KEPLER, "kepler"), ecc_state),
        ("j2drag_250x800_i51.6_perigee_midstep", (J2_DRAG, "j2drag"), ecc_state),
        ("kepler_circular250_i51.6_equator_midstep", (KEPLER, "kepler"), circ_state),
        ("j2drag_circular250_i51.6_equator_midstep", (J2_DRAG, "j2drag"), circ_state),
    ):
        rec = midpoint_dip(cfg, r0, v0)
        if label == "kepler":
            sma = m.sma(r0, v0)
            ecc = 1.0 - float(np.linalg.norm(r0)) / sma if "800" in name else 0.0
            dom = two_body_domain_bound(sma, ecc)
            rec["two_body_domain_bound_m"] = dom["bound_m"]
            rec["bound_m"] = dom["bound_m"]
            rec["bound_kind"] = CERTIFIED
            rec["bound_holds"] = rec["bound_m"] >= rec["dip_m"]
        else:
            rec["estimate_kind"] = SAMPLED
            rec["dip_within_sampled_estimate"] = rec["sampled_estimate_m"] >= rec["dip_m"]
        cases[name] = rec
    sweep = []
    for hp, ha, inc in SWEEP_ORBITS:
        sma, ecc = orbit_elements(hp * 1e3, ha * 1e3)
        period = 2 * math.pi * math.sqrt(sma**3 / m.MU)
        r0, v0 = m.perigee_state(hp * 1e3, ha * 1e3, inc)
        y0 = np.concatenate([r0, v0, [MASS]])
        for label, cfg in (("kepler", KEPLER), ("j2drag", J2_DRAG)):
            row = {
                "physics": label,
                "perigee_km": hp,
                "apogee_km": ha,
                "inclination_deg": inc,
                "eccentricity": ecc,
                **phase_sweep(cfg, y0, 2 * period + 2 * DT),
            }
            # The two-body bound of the initial osculating orbit is certified only for the
            # two-body rows; for J2 + drag it is a reference value, not a bound.
            row["two_body_domain_bound_m"] = two_body_domain_bound(sma, ecc)["bound_m"]
            if label == "kepler":
                row["bound_m"] = row["two_body_domain_bound_m"]
                row["bound_kind"] = CERTIFIED
                row["bound_holds"] = row["max_dip_m"] <= row["bound_m"]
            else:
                row["estimate_kind"] = SAMPLED
                row["dip_within_sampled_estimate"] = row["max_dip_m"] <= row["sampled_estimate_m"]
            sweep.append(row)
    table = []
    for hp in (80.0, 150.0, 250.0):
        for ecc in (0.0, 0.005, 0.01, 0.02, 0.04, 0.1):
            rp = m.A_WGS84 + hp * 1e3
            sma = rp / (1.0 - ecc)
            table.append(
                {
                    "perigee_km": hp,
                    "eccentricity": ecc,
                    "bound_m": two_body_domain_bound(sma, ecc)["bound_m"],
                    "sup_hddot_mps2": two_body_domain_bound(sma, ecc)["sup_hddot_mps2"],
                }
            )
    certified = [r for r in (*cases.values(), *sweep) if "bound_holds" in r]
    sampled = [r for r in (*cases.values(), *sweep) if "estimate_kind" in r]
    return {
        "theorem": "dip <= dt^2/8 * sup max(h'', 0); h'' <= n.a + |v_t|^2 / (h + b^2/a)",
        "dt_s": DT,
        "b2_over_a_m": R_CURV_MIN,
        "max_normal_angle_rad": DELTA_MAX,
        "cases": cases,
        "sweep": sweep,
        "sweep_orbits": [list(o) for o in SWEEP_ORBITS],
        "sweep_physics": ["kepler", "j2drag"],
        "sweep_phases_s": list(PHASES),
        "sweep_sample_s": SAMPLE,
        "two_body_domain_bound_table": table,
        "all_certified_bounds_hold": all(r["bound_holds"] for r in certified),
        "all_dips_within_sampled_estimates": all(r["dip_within_sampled_estimate"] for r in sampled),
        "perturbed_motion": "no certified bound; sampled estimates only (M3T0-R2-F1)",
    }


# ------------------------------------------------------------- stiffness and domain
def vrel_circular(h: float) -> float:
    """The DR-0029 P1 proxy (circular speed at spherical radius a + h; no co-rotation)."""
    return math.sqrt(m.MU / (m.A_WGS84 + h))


def vrel_bound(h: float) -> float:
    """Upper bound on |v_rel| for every bound state at geodetic height h."""
    return math.sqrt(2.0 * m.MU / (m.B_WGS84 + h)) + m.OMEGA_E * (m.A_WGS84 + h)


def threshold(kappa: float, b: float, speed) -> dict:
    """The largest h with rho(h) speed(h) dt / b >= kappa (admissible: h above it)."""

    def lam(h: float) -> float:
        return m.density(h) * speed(h) * DT / b

    grid = np.arange(0.0, 400_000.0 + 1e-6, 10.0)
    vals = np.array([lam(float(h)) for h in grid])
    above = np.nonzero(vals >= kappa)[0]
    if not above.size:
        return {"threshold_m": None}
    i = int(above[-1])
    lo, hi = float(grid[i]), float(grid[i + 1])
    base = next((bb.base_km * 1e3 for bb in m.TABLE if lo < bb.base_km * 1e3 <= hi), None)
    if base is not None and lam(base) < kappa:
        if lam(math.nextafter(base, 0.0)) >= kappa:
            return {"threshold_m": base, "at_band_base": True, "sign_changes_on_grid": 0}
        hi = base
    h_star = brentq(lambda h: lam(h) - kappa, lo, hi, xtol=1e-9, rtol=1e-15)
    changes = int(np.count_nonzero(np.diff((vals >= kappa).astype(int))))
    return {
        "threshold_m": h_star,
        "lambda_dt_at_threshold": lam(h_star),
        "sign_changes_on_10m_grid": changes,
    }


def stiffness_thresholds() -> dict:
    out = {}
    for sname, speed in (("circular_speed", vrel_circular), ("bound_speed", vrel_bound)):
        out[sname] = {
            bname: {repr(k): threshold(k, b, speed) for k in KAPPAS}
            for bname, b in (("B25.8", B_V1), ("B100", 100.0))
        }
    out["lambda_dt_circular_at_90km_B25.8"] = m.density(90e3) * vrel_circular(90e3) * DT / B_V1
    out["lambda_dt_circular_at_80km_B100"] = m.density(80e3) * vrel_circular(80e3) * DT / 100.0
    return out


def admissibility_counterexamples() -> dict:
    """Review 01 F2 inputs (stress tests of the unrestricted rule, not proposed vehicles)."""
    hf, b = 21_500.0, 1e9
    r = np.array([m.A_WGS84 + 22_000.0, 0.0, 0.0])
    v = np.array([-10_000.0, 0.0, 0.0])
    y0 = np.concatenate([r, v, [b * 2.2 * 15.0]])
    rec = {
        "h_f_m": hf,
        "initial_h_m": m.geodetic_iterative(r)[1],
        "a_minus_b_m": m.A_WGS84 - m.B_WGS84,
        "lambda_dt_circular": m.density(hf) * vrel_circular(hf) * DT / b,
        "lambda_dt_bound": m.density(hf) * vrel_bound(hf) * DT / b,
        "two_body_energy_J_per_kg": 0.5 * float(v @ v) - m.MU / float(np.linalg.norm(r)),
    }
    try:
        m.rk4_step(m.rhs(J2_DRAG), 0.0, y0, DT)
        rec["fail_closed"] = None
    except m.OutsideDomainError as exc:
        rec["fail_closed"] = f"OutsideDomainError: {exc}"
    diag = m.Config(j2=m.J2_FROM_C20, drag=m.Drag(cd=2.2, area_m2=15.0, below="extrapolate"))
    stages: list = []
    y1 = m.rk4_step(m.rhs(diag), 0.0, y0, DT, stages)
    rec["diagnostic_stage_heights_m"] = [m.geodetic_iterative(s.r)[1] for s in stages]
    rec["diagnostic_committed_h_m"] = m.geodetic_iterative(y1[:3])[1]
    rec["diagnostic_committed_spherical_alt_m"] = m.spherical_altitude(y1[:3])
    rec["reentry_and_impact_same_tick"] = (
        rec["diagnostic_committed_h_m"] <= hf and rec["diagnostic_committed_spherical_alt_m"] <= 0.0
    )
    lip = stage_lipschitz_check(m.rhs(diag), y0)
    rec["lipschitz_lower_bound_holds"] = lip["holds"]

    # Eccentric retrograde perigee at the circular-proxy kappa = 0.01 threshold (B 25.8).
    h_star = threshold(0.01, B_V1, vrel_circular)["threshold_m"]
    rn = m.A_WGS84 + h_star
    v_e09 = math.sqrt(m.MU / rn) * math.sqrt(1.9) + m.OMEGA_E * rn
    ecc = {
        "h_m": h_star,
        "vrel_mps": v_e09,
        "lambda_dt_actual": m.density(h_star) * v_e09 * DT / B_V1,
        "lambda_dt_circular_proxy": m.density(h_star) * vrel_circular(h_star) * DT / B_V1,
        "vrel_bound_mps": vrel_bound(h_star),
        "covered_by_bound_speed": vrel_bound(h_star) >= v_e09,
    }
    return {"stress_input": rec, "eccentric_retrograde": ecc}


def stage_lipschitz_check(f, y0: np.ndarray) -> dict:
    """h(stage) >= h(r0) - |stage displacement| (1-Lipschitz height), for one step."""
    stages: list = []
    m.rk4_step(f, 0.0, y0, DT, stages)
    h0 = m.geodetic_iterative(y0[:3])[1]
    worst = min(
        m.geodetic_iterative(s.r)[1] - (h0 - float(np.linalg.norm(s.r - y0[:3]))) for s in stages
    )
    return {"min_margin_m": worst, "holds": worst >= -1e-6}


G_BOUND = (1.0 + 3.0 * m.J2_FROM_C20 * (m.A_WGS84 / m.B_WGS84) ** 2) * m.MU / m.B_WGS84**2
BASES_M = tuple(bb.base_km * 1e3 for bb in m.TABLE)


# ------------------------------------- floating-point enclosure (Review 03 M3T0-R3-F1)
# The force is a function of the model's *computed* height, and the density is
# discontinuous in height, so a bound proved for exact heights does not bound the
# implemented force (R3-F1). Every quantity below encloses the binary64 evaluation of the
# model (`t0_model`), derived operation by operation. Assumptions (A-FP), corrected after
# Review 04 M3T0-R4-F1, which showed that a purely relative rounding model fails once
# results are subnormal (the earlier A-FP-1 dropped their absolute errors):
#   A-FP-1  IEEE 754 binary64, round to nearest even, gradual underflow (no flush-to-zero
#           or denormals-are-zero mode). With u = 2^-53 and eta0 = 2^-1075 (half the
#           smallest subnormal), for * and /: fl(x op y) = (x op y)(1 + d) + e, |d| <= u,
#           |e| <= eta0, d e = 0; for + and -: fl(x op y) = (x op y)(1 + d) (a sum that
#           underflows is exact); sqrt: fl(sqrt x) = sqrt(x)(1 + d) (never subnormal);
#           multiplying by 0.5 is exact unless the result is subnormal; a result of
#           magnitude <= eta0 rounds to 0.
#   A-FP-2  libm sin, cos, atan2, hypot, exp and pow: |computed - exact| <= UF |exact| + nu
#           with UF = LIBM_ULP 2^-52 and nu = LIBM_ULP 2^-1074. The absolute term covers
#           subnormal results and exp rounding to 0; no relative bound is assumed there.
#           Not proved: an assumption about the platform library, measured on this
#           platform in `t0_height_error.py`. Every bound below is derived under it, and
#           `libm_sensitivity` reports how far LIBM_ULP can grow before a published floor
#           fails.
#   A-FP-3  numpy evaluates the 3-element products elementwise in binary64 and a 3-term
#           dot product x . x within gamma_3 sum x_i^2 + 3 (1 + u)^2 eta0 (any order, with
#           or without fused multiply-add: each underflow error passes at most two later
#           roundings).
# Supported domain: points outside the ellipsoid (true height >= 0), no overflow.
U = Fraction(1, 2**53)
ETA0 = Fraction(1, 2**1075)  # A-FP-1: largest absolute error of an underflowing * or /
TINY = Fraction(1, 2**1074)  # the smallest subnormal
TINY_D = Decimal(math.ulp(0.0))  # 2^-1074 exactly
# 2, not 1: on macOS x86_64 (the M1/M2 reference host) `t0_height_error.py` measured cos
# at 1.41 ulp (0.94 x 2^-52 relative), so the usual "within 1 ulp" is false there and
# 1 x 2^-52 has almost no margin. 2 x 2^-52 remains an assumption, not a proof.
LIBM_ULP = 2
UF = 2 * LIBM_ULP * U
PI_HALF_UP = Fraction(355, 226)  # > pi / 2
LAT_TOL = Fraction(1e-15)  # geodetic_iterative stops when |dlat| <= 1e-15 (binary64)
LAT_ITER = 60
PREC = 60  # decimal digits of the enclosure arithmetic below
PAD = Decimal("1e-45")  # covers the decimal rounding of every bound (relative <= 1e-55)
CD_V1, AREA_V1 = 2.2, 15.0  # the illustrative vehicle's drag coefficient and area [m^2]


def _sqrt_bounds(q: Fraction) -> tuple[Fraction, Fraction]:
    s = math.isqrt(q.numerator * 10**80 // q.denominator)
    return Fraction(s, 10**40), Fraction(s + 1, 10**40)


def _up(q) -> float:
    """The smallest binary64 >= q (q a Fraction or a Decimal); +inf beyond the largest."""
    x = float(q)
    if math.isinf(x):
        return x
    return x if Fraction(x) >= Fraction(q) else math.nextafter(x, math.inf)


def _dn(q) -> float:
    x = float(q)
    return x if Fraction(x) <= Fraction(q) else math.nextafter(x, -math.inf)


def _decimal_table() -> tuple[tuple[Decimal, Decimal, Decimal], ...]:
    """(base [m], rho0, scale [m]) as the exact decimals of the pinned file."""
    m.load_table()  # digest check
    rows = []
    for line in m.TABLE_COPY.read_text().splitlines():
        if line.strip():
            h, rho, s = (Decimal(x.strip()) for x in line.split(","))
            rows.append((h * 1000, rho, s * 1000))
    return tuple(rows)


DEC_TABLE = _decimal_table()


def rounding_allowances(libm_ulp: int = LIBM_ULP) -> dict:
    """The derived constants, in exact rational arithmetic (see the module notes below).

    E1 height. `geodetic_iterative` returns lat ~ phi and
        h^ = fl(fl(fl(p c) + fl(z s)) - fl(a sqrt(fl(1 - fl(fl(e2 s) s)))))
    with s, c = fl(sin, cos)(lat), p = fl(hypot(x, y)). For exact sin and cos of lat this
    is H(lat) = p cos lat + z sin lat - a sqrt(1 - e2 sin^2 lat), the signed distance from r
    to the supporting plane of the ellipsoid with normal n(lat) (a sqrt(1 - e2 sin^2) is
    the ellipsoid's support function). For a point outside the ellipsoid:
      (i)  H(lat) <= h for every lat (the distance to a convex body is the maximum over
           supporting planes), with equality at the geodetic latitude phi, where H' = 0;
      (ii) H'' = -H - M (M the meridian radius of curvature), so |H''| <= |r| + a +
           a / sqrt(1 - e2) and 0 <= h - H(lat) <= C_H (lat - phi)^2 / 2;
      (iii) rounding: |h^ - H(lat)| <= (1 + u) (Theta12 |r| + theta4 a) + u |H|, where the
           first term uses p |c| + |z s| <= |r| (Cauchy-Schwarz), the second the relative
           error of a sqrt(.) and the last the final subtraction;
      (iv) |r| <= a + h.
    Latitude error: the iteration lat <- T(lat) = atan2(z + e2 N(lat) sin lat, p) is the
    direction from the point (0, -e2 N sin lat) on the axis to r. That point moves by at
    most Q' = e2 a / (1 - e2)^1.5 per radian and stays within Q = e2 a / sqrt(1 - e2) of
    the centre, so |T'| <= k = Q' / (b - Q) < 0.0069 for every lat and every |r| >= b: a
    contraction whose fixed point is phi. One computed step differs from T by at most eta
    (rounding of N, of e2 N s, of z + ., of hypot, and of atan2; the angle between two
    vectors v and v + dv is <= (pi/2) |dv| / |v|). With the stopping rule |dlat| <= 1e-15 or
    60 iterations: |lat - phi| <= eta / (1 - k) + max(k 1e-15 / (1 - k), k^60 pi).
    Underflow (R4-F1): p, s and atan2 may be subnormal (points near the axis or the
    equator) and the products p c, z s, e2 s s and e2 N s may underflow. Their absolute
    errors (nu for libm, eta0 for a product) add to eta through Y = z + e2 N s and p
    (e2 N nu + eta0 and nu, divided by |v| >= b - Q) plus nu for atan2, and to the final
    formula (1 + u)^3 nu (|r| + 1 + UF) + 2 (1 + u)^2 eta0 + a (1 + u)^6 (3 e2 (1 + UF) nu
    + 2 eta0) / (2 sqrt(1 - e2) (1 - rho3)) (z nu, p's nu, the two products, and e2 s s
    through the square root, whose argument is >= (1 - e2)(1 - rho3)).
    Result: |h^ - h| <= alpha h + beta.

    E2 kilometre conversion. `density` selects the band and evaluates the formula at
    h_km = fl(h^ / 1000); the selection height h_s = 1000 h_km satisfies |h_s - h^| <= u
    |h^| + 1000 eta0 (the division may underflow; the bases are integers in km), so
    |h_s - h| <= alpha_sel h + beta_sel.

    E3 density. rho^ = fl(rho0 fl(exp(-fl(fl(h_km - base) / scale)))) with the table's
    decimal rho0 and scale read to binary64 (relative <= u each). The exponent's division
    may underflow (-eta0), so exp(-t) <= exp(-(1 - theta_x) X) e^eta0, and A-FP-2 adds nu:
        rho^ <= F_rho e^eta0 rho(h_s) exp(theta_x X) + N_rho,
        N_rho = (1 + u)^2 rho0_max nu + eta0,
    with X = (h_s - base) / H >= 0 the exponent of the exact table formula. In the top
    band, once (1 + u) rho0 ((1 + UF) e^eta0 exp(-(1 - theta_x) X) + nu) < eta0 the
    product rounds to 0: rho^ = 0 for every selection height above h_zero
    (`zero_density_height`), and the force is then exactly 0.

    E4 drag. The model computes k = fl(fl(fl(fl(0.5 rho^) cd) area) / mass), n =
    fl(sqrt(fl(v_rel . v_rel))), d_i = fl(fl(k n) v_rel_i) with v_rel = fl(v - fl(omega Z x
    r)). With S = |v| + omega |r| >= omega b, |v_rel^| <= (1 + u)^2 S + sqrt(2) (1 + u)
    eta0, n |v_rel^| <= (1 + u) sqrt(1 + gamma_3) (|v_rel^|^2 + 2 eta0) <= (1 + u)^5
    sqrt(1 + gamma_3) S^2 (1 + tau), tau = 3 eta0 / S_min + 2 eta0 / S_min^2 + 2 eta0^2 /
    S_min^2, S_min = omega b, and k <= (1 + u)^3 (cd area / mass) 0.5 rho^ + W with
    W = eta0 (1 + (1 + u)^3 cd area / mass + (1 + u)^2 area / mass + (1 + u) / mass).
    The vehicle enters only through cd area / mass <= R (E4a, `inverse_ballistic_bound`,
    corrected after Review 05 M3T0-R5-F1: the conversion between b and mass may underflow).
    Writing R = phi_B / b_R (b_R <= b; b_R = b wherever the conversion is normal):
        |d^| <= F_D' rho(h_s) exp(theta_x X) S^2 / (2 b_R)                 (relative)
              + (F_A N_rho / (2 b_R) + K_W W) S^2 + K_1 eta0 S + 2 eta0     (absolute)
    with F_D' = F_D e^eta0 (1 + tau), F_D = F_rho (1 + u)^10 sqrt(1 + gamma_3) phi_B (the
    coefficient's 3 roundings, the dot and sqrt, the two products with v_rel and |v_rel^|^2),
    F_A = (1 + u)^10 sqrt(1 + gamma_3) phi_B (1 + tau), K_W = (1 + u)^7 sqrt(1 + gamma_3)
    (1 + tau), K_1 = (1 + u)^3, and W <= eta0 (1 + phi_B / b_R ((1 + u)^3 + (1 + u)^2 / cd +
    (1 + u) / (cd area))).

    E4a ballistic coefficient. The model takes mass; the envelope takes b, formed in one of
    two ways (A-FP-1, each rounding may underflow):
      C1  b = fl(mass / P), P = fl(cd area) (B 25.8 here). b finite and mass > 0 give P > 0,
          so P >= 2 eta0 and cd area > eta0. P = cd area (1 + d) or cd area + e gives
          cd area / P <= min(max(1 / (1 - u), cd area / (cd area - eta0)), cd area / (2 eta0));
          b = (mass / P)(1 + d) or mass / P + e gives P / mass <= max((1 + u) / b,
          1 / (b - eta0)) (b >= 2 eta0). R1 is the product of the two.
      C2  mass = fl(fl(b cd) area) (B 100 here). mass > 0 gives Q = fl(b cd) >= 2 eta0 and
          mass >= 2 eta0; Q >= Q_lo = max(2 eta0, min(b cd (1 - u), b cd - eta0)) and mass >=
          M_lo = max(2 eta0, min(Q_lo area (1 - u), Q_lo area - eta0)); R2 = cd area / M_lo.
    R = max(phi_B / b, R1, R2) holds for either construction, with no condition on the
    vehicle. Where every result is normal, R1 = (1 + u) / ((1 - u) b) and R2 = 1 / ((1 -
    u)^2 b) are below phi_B / b, so R = phi_B / b. The eta0 terms take over when b, P, Q or
    mass is subnormal. R is non-increasing in b.

    E4b no area. If cd area <= eta0 (C1 then gives b = +inf), the model's force is exactly
    0. c0 = fl(0.5 rho^) <= 5/8 (rho^ <= F_rho e^eta0 rho0_max + N_rho). If area <= 1/4:
    fl(c0 cd) area <= (5/8)(1 + u) eta0 + eta0 / 4 < eta0, which rounds to 0. Otherwise cd <
    4 eta0, so cd = 2 eta0 and area <= 1/2; c0 cd <= 1.25 eta0 rounds to at most 2 eta0, and
    2 eta0 area <= eta0 rounds to 0. Then k = 0 / mass = 0 and every drag component is 0.

    E5 gravity with J2. |a^_grav + a^_J2| <= (1 + u) max(F_g, F_J) G + 4 eta0 with G = (1 +
    3 J2 (a/b)^2) mu / b^2, from the operation counts of `t0_model.acceleration` and
    `j2_accel` (|r| >= b; the J2 direction vector has norm <= 2 |r|). Underflow: mu / |r|^3
    and the J2 factor are normal without overflow; each of the 3 products with r underflows
    by <= eta0 (sqrt(3) eta0), and in J2 the products 5 z z, x (1 - zz) and k (.) add <=
    (1 + 2.1 |k| |r|) eta0 <= 1.05 eta0 per component (|k| |r| <= 1.5 J2 mu a^2 / b^4 <
    0.017). |a^| <= (1 + u)(that + |a^_drag|) for the final vector difference.

    E6 RK4 stages. A stage w = fl(r0 + fl(c k)) (c = 5 or 10, exact) satisfies |w - r0| <=
    (1 + u)^2 c |k| + u |r0| + 2 eta0, and a stage velocity |fl(v0 + fl(5 a))| <= (1 + u)
    |v0| + 5 (1 + u)^2 |a| + 2 eta0 (each product may underflow: (1 + u) sqrt(3) eta0)."""
    uf = 2 * libm_ulp * U
    nu = libm_ulp * TINY
    e2, a = Fraction(m.E2_WGS84), Fraction(m.A_WGS84)
    s_lo, _ = _sqrt_bounds(1 - e2)
    b_lo = a * s_lo
    g3 = 3 * U / (1 - 3 * U)
    sq1_lo, _ = _sqrt_bounds(1 - g3)
    _, sq1_hi = _sqrt_bounds(1 + g3)

    # E1 height evaluation at the returned latitude
    theta1 = (1 + uf) ** 2 * (1 + U) - 1
    big12 = theta1 + U * (1 + theta1)
    theta3 = (1 + uf) ** 2 * (1 + U) ** 2 - 1
    rho3 = (e2 * theta3 + U * (1 + e2 * theta3)) / (1 - e2)
    sq = rho3 / (2 - rho3)  # |sqrt(1 + t) - 1| <= |t| / (1 + sqrt(1 - |t|)) <= |t| / (2 - |t|)
    theta4 = (1 + sq) * (1 + U) ** 2 - 1
    # latitude: contraction constant and one-step rounding
    q = e2 * a / s_lo
    qp = e2 * a / s_lo**3
    k = qp / (b_lo - q)
    nu1 = (1 + U) / (1 - ((1 + sq) * (1 + U) - 1)) - 1
    theta5 = (1 + nu1) * (1 + uf) * (1 + U) ** 2 - 1
    ratio = (uf * b_lo + (theta5 + U * (1 + theta5)) * q) / (b_lo - q)
    n_hi = a / s_lo * Fraction(1001, 1000)  # >= the computed N
    y_uf = (1 + U) ** 2 * e2 * n_hi * nu + (1 + U) * ETA0  # underflow in z + e2 N s
    eta_uf = PI_HALF_UP * (nu + y_uf) / (b_lo - q) + nu
    eta = PI_HALF_UP * (ratio + uf) + eta_uf
    k60 = Fraction(_up(k)) ** LAT_ITER
    dphi = eta / (1 - k) + max(k * LAT_TOL / (1 - k), k60 * 2 * PI_HALF_UP)
    alpha_lat = dphi**2 / 2
    beta_lat = (2 * a + a / s_lo) * dphi**2 / 2
    h_uf_r = (1 + U) ** 3 * nu  # coefficient of |r| <= a + h
    h_uf_c = (
        (1 + U) ** 3 * (1 + uf) * nu
        + 2 * (1 + U) ** 2 * ETA0
        + a * (1 + U) ** 6 * (3 * e2 * (1 + uf) * nu + 2 * ETA0) / (2 * s_lo * (1 - rho3))
    )
    alpha_rel = (1 + U) * big12 + U + (1 + U) * alpha_lat
    beta_rel = (1 + U) * (big12 + theta4) * a + (1 + U) * beta_lat
    beta_uf = h_uf_r * a + h_uf_c
    alpha = alpha_rel + h_uf_r
    beta = beta_rel + beta_uf
    # E2 km conversion
    alpha_sel = alpha * (1 + U) + U
    beta_sel = beta * (1 + U) + 1000 * ETA0
    # E3, E4 density and drag
    theta_x = (1 + U) ** 2 / (1 - U) - 1
    f_rho = (1 + uf) * (1 + U) ** 2
    phi_b = (1 + U) / (1 - U) ** 2
    s_min = Fraction(m.OMEGA_E) * b_lo
    tau = 3 * ETA0 / s_min + 2 * ETA0 / s_min**2 + 2 * ETA0**2 / s_min**2
    exp_eta = 1 + 2 * ETA0  # >= e^eta0
    f_d = f_rho * (1 + U) ** 10 * sq1_hi * phi_b * exp_eta * (1 + tau)
    rho0_max = max(Fraction(row[1]) for row in DEC_TABLE)
    n_rho = (1 + U) ** 2 * rho0_max * nu + ETA0
    f_a = (1 + U) ** 10 * sq1_hi * phi_b * (1 + tau)
    k_w = (1 + U) ** 7 * sq1_hi * (1 + tau)
    # E4b: fl(0.5 rho^) <= 0.5 rho^ + eta0 <= 5/8
    c0_max = (f_rho * exp_eta * rho0_max + n_rho) / 2 + ETA0
    if not c0_max <= Fraction(5, 8):
        raise ValueError("E4b: fl(0.5 rho^) <= 5/8 does not hold")
    # E5 gravity and J2
    rn_lo = sq1_lo * (1 - U)
    f_g = (1 + U) ** 2 / ((1 - uf) * rn_lo**3)
    f_k = (1 + U) ** 5 / ((1 - g3) ** 2 * (1 - U) ** 3 * sq1_lo)
    zeta = (1 + U) ** 3 / (1 - g3) - 1
    f_j = f_k * (1 + U) ** 3 * (1 + Fraction(5, 2) * zeta)
    j2, mu = Fraction(m.J2_FROM_C20), Fraction(m.MU)
    kr_j2 = Fraction(3, 2) * j2 * mu * a**2 / b_lo**4  # >= |k| |r| in j2_accel
    if not (1 + Fraction(21, 10) * kr_j2) * (1 + U) ** 3 <= Fraction(105, 100):
        raise ValueError("E5: the J2 underflow allowance 1.05 eta0 does not hold")
    g_exact_up = (1 + 3 * j2 * a**2 / b_lo**2) * mu / b_lo**2
    g_rel = (1 + U) * max(f_g, f_j) * g_exact_up
    g_uf = 4 * ETA0
    g_hat = g_rel + g_uf
    return {
        "u": U,
        "libm_ulp": libm_ulp,
        "b_lower_m": b_lo,
        "contraction_k": k,
        "lat_step_rounding_rad": eta,
        "lat_error_rad": dphi,
        "alpha": alpha,
        "beta_m": beta,
        "alpha_sel": alpha_sel,
        "beta_sel_m": beta_sel,
        "theta_x": theta_x,
        "F_D": f_d,
        "F_g": f_g,
        "F_J": f_j,
        "gravity_hat_mps2": g_hat,
        "phi_B": phi_b,
        "F_A": f_a,
        "K_W": k_w,
        "K_1": (1 + U) ** 3,
        "tau": tau,
        "zero_force_c0_max": c0_max,
        "N_rho_in_2^-1074": n_rho / TINY,
        "nu_in_2^-1074": nu / TINY,
        "stage_abs_in_2^-1074": 2 * ETA0 / TINY,
        # the underflow parts of E1 and E5, kept separate so that they can be audited
        "alpha_relative_part": alpha_rel,
        "alpha_underflow_part": h_uf_r,
        "beta_relative_part_m": beta_rel,
        "beta_underflow_part_m": beta_uf,
        "lat_step_underflow_rad": eta_uf,
        "gravity_relative_part_mps2": g_rel,
        "gravity_underflow_part_mps2": g_uf,
    }


def zero_density_height(fpa: dict) -> Fraction:
    """h_zero (E3): above this selection height the model's density is exactly 0. In the top
    band (base_T, rho0_T, H_T), X > X0 makes (1 + u) rho0_T ((1 + UF) e^eta0 exp(-(1 -
    theta_x) X) + nu) < eta0, so fl(rho0 exp^) = 0 (round to nearest). X0 = -ln(E0) / (1 -
    theta_x) with E0 = (eta0 / ((1 + u) rho0_T) - nu) / ((1 + UF)(1 + 2 eta0)), bounded
    outward in 60-digit decimals; h_zero = base_T + H_T X0, rounded up."""
    base, rho0, scale = DEC_TABLE[-1]
    u, uf = fpa["u"], 2 * fpa["libm_ulp"] * fpa["u"]
    nu = fpa["nu_in_2^-1074"] * TINY
    e0 = (ETA0 / ((1 + u) * Fraction(rho0)) - nu) / ((1 + uf) * (1 + 2 * ETA0))
    if not e0 > 0:
        raise ValueError("no zero-density height under these assumptions")
    with localcontext() as ctx:
        ctx.prec = PREC
        e0_lo = Decimal(e0.numerator) / Decimal(e0.denominator) * (1 - PAD)
        th = Decimal(fpa["theta_x"].numerator) / Decimal(fpa["theta_x"].denominator)
        x0 = -e0_lo.ln() * (1 + PAD) / (1 - th) * (1 + PAD)
        return Fraction((base + scale * x0) * (1 + PAD))


def derived_constants(libm_ulp: int = LIBM_ULP) -> tuple[dict, dict]:
    """(exact constants, binary64 upper bounds) for a libm accuracy LIBM_ULP (A-FP-2)."""
    fpa = rounding_allowances(libm_ulp)
    fpa["h_zero_m"] = zero_density_height(fpa)
    fp = {key: _up(val) for key, val in fpa.items() if key not in ("b_lower_m",)}
    fp["b_lower_m"] = _dn(fpa["b_lower_m"])
    return fpa, fp


FPA, FP = derived_constants()


def height_error_bound(h: float) -> float:
    """eps_h(h) = alpha h + beta >= |computed - true| geodetic height at true height h."""
    return _up(FPA["alpha"] * Fraction(h) + FPA["beta_m"])


def drag_envelope_exact_height(low: float, s: float, b: float) -> float:
    """SUPERSEDED (Review 03 M3T0-R3-F1): the Review 02 envelope, sup over exact heights
    h >= low of rho(h) (s + omega_E (a + h))^2 / (2 B). It bounds drag evaluated at the
    exact height, not the model's force, which uses the computed height. Kept only to
    reproduce the finding."""
    if math.isinf(b):
        return 0.0

    def f(h: float) -> float:
        vr = s + m.OMEGA_E * (m.A_WGS84 + h)
        return 0.5 * m.density(h) * vr * vr / b

    return max([f(low)] + [f(base) for base in BASES_M if base > low])


def _envelope_relative(low: float, s: float, b: float | Decimal, fp: dict) -> Decimal:
    """sup over h_s >= ell of F_D' rho(h_s) exp(theta_x X) (s + omega_E (a + (h_s +
    beta_sel) / (1 - alpha_sel)))^2 / (2 b), in 60-digit decimals (see `drag_envelope`)."""
    al, be, tx = Decimal(fp["alpha_sel"]), Decimal(fp["beta_sel_m"]), Decimal(fp["theta_x"])
    a, w = Decimal(m.A_WGS84), Decimal(m.OMEGA_E)
    if not all(2 * row[2] < (1 - al) * (1 - tx) * a for row in DEC_TABLE):
        raise ValueError("a band violates (1 - alpha)(1 - theta_x) a > 2 H")
    ell = max((1 - al) * Decimal(low) - be, Decimal(0))
    best = Decimal(0)
    for h in [ell] + [row[0] for row in DEC_TABLE if row[0] > ell]:
        base, rho0, scale = DEC_TABLE[max(i for i, r in enumerate(DEC_TABLE) if r[0] <= h)]
        rho = rho0 * (-(1 - tx) * (h - base) / scale).exp()
        vr = Decimal(s) + w * (a + (h + be) / (1 - al))
        best = max(best, rho * vr * vr)
    return best * Decimal(fp["F_D"]) / (2 * Decimal(b))


def _envelope_absolute(s: float, b: float | Decimal, cd: float, area: float, fp: dict) -> Decimal:
    """The absolute (underflow) part of E4: (F_A N_rho / (2 b) + K_W W) S_max^2 + K_1 eta0
    S_max + 2 eta0, with S_max = s + omega_E (a + (h_zero + beta_sel) / (1 - alpha_sel)),
    the largest |v| + omega |r| at which the computed density can be nonzero (E3)."""
    al, be = Decimal(fp["alpha_sel"]), Decimal(fp["beta_sel_m"])
    a, w = Decimal(m.A_WGS84), Decimal(m.OMEGA_E)
    one_u, phi = 1 + Decimal(fp["u"]), Decimal(fp["phi_B"])
    eta0 = TINY_D / 2
    cd_d, area_d, b_d = Decimal(cd), Decimal(area), Decimal(b)
    smax = Decimal(s) + w * (a + (Decimal(fp["h_zero_m"]) + be) / (1 - al))
    w_coef = eta0 * (1 + phi / b_d * (one_u**3 + one_u**2 / cd_d + one_u / (cd_d * area_d)))
    n_rho = Decimal(fp["N_rho_in_2^-1074"]) * TINY_D
    return (
        (Decimal(fp["F_A"]) * n_rho / (2 * b_d) + Decimal(fp["K_W"]) * w_coef) * smax * smax
        + Decimal(fp["K_1"]) * eta0 * smax
        + 2 * eta0
    )


def drag_envelope_relative_only(low: float, s: float, b: float) -> float:
    """SUPERSEDED (Review 04 M3T0-R4-F1): the Review 03 correction, `drag_envelope` without
    its absolute (underflow) part. It assumed relative rounding for subnormal results and is
    exceeded where the computed density is subnormal. Kept only to reproduce the finding."""
    if math.isinf(b):
        return 0.0
    with localcontext() as ctx:
        ctx.prec = PREC
        return _up(_envelope_relative(low, s, b, FP) * (1 + PAD))


def drag_envelope_relative_conversion(
    low: float, s: float, b: float, cd: float = CD_V1, area: float = AREA_V1
) -> float:
    """SUPERSEDED (Review 05 M3T0-R5-F1): the Review 04 correction, `drag_envelope` with cd
    area / mass bounded by phi_B / b, a relative-only rounding of the conversion between b
    and the mass. Exceeded where b is subnormal. Kept only to reproduce the finding."""
    if math.isinf(b):
        return 0.0
    with localcontext() as ctx:
        ctx.prec = PREC
        rel = _envelope_relative(low, s, b, FP)
        return _up((rel + _envelope_absolute(s, b, cd, area, FP)) * (1 + PAD))


def inverse_ballistic_bound(b: float, cd: float, area: float, phi: Fraction) -> Fraction:
    """R >= cd area / mass (E4a) for every positive binary64 vehicle whose finite ballistic
    coefficient b was formed by C1, b = fl(mass / fl(cd area)), or C2, mass = fl(fl(b cd)
    area), with the absolute error of every underflowing rounding (Review 05 M3T0-R5-F1).
    phi >= phi_B is the relative factor the envelope uses."""
    bq, prod = Fraction(b), Fraction(cd) * Fraction(area)
    tiny = 2 * ETA0  # the smallest positive binary64
    r1 = Fraction(0)  # C1 gives a finite b only when cd area > eta0 (P > 0)
    if prod > ETA0:
        p_ratio = min(max(1 / (1 - U), prod / (prod - ETA0)), prod / tiny)
        r1 = p_ratio * max((1 + U) / bq, 1 / (bq - ETA0))
    bcd = bq * Fraction(cd)
    q_lo = max(tiny, min(bcd * (1 - U), bcd - ETA0))
    m_lo = max(tiny, min(q_lo * Fraction(area) * (1 - U), q_lo * Fraction(area) - ETA0))
    r2 = prod / m_lo
    return max(phi / bq, r1, r2)


def envelope_ballistic_coefficient(b: float, cd: float, area: float, fp: dict) -> float | Decimal:
    """b_R = phi_B / R <= b (E4a), the ballistic coefficient the envelope uses: b itself
    (the same binary64) when R = phi_B / b, otherwise phi_B / R rounded down in decimals."""
    phi = Fraction(fp["phi_B"])
    r = inverse_ballistic_bound(b, cd, area, phi)
    if r == phi / Fraction(b):
        return b
    q = phi / r
    with localcontext() as ctx:
        ctx.prec, ctx.rounding = PREC, ROUND_FLOOR
        return Decimal(q.numerator) / Decimal(q.denominator)


def drag_envelope(
    low: float,
    s: float,
    b: float,
    cd: float = CD_V1,
    area: float = AREA_V1,
    fp: dict | None = None,
) -> float:
    """Upper bound on the model's computed drag acceleration |a^_drag| at every point whose
    true geodetic height is >= low (>= 0), with inertial speed |v| <= s, for a vehicle of
    ballistic coefficient b with drag coefficient cd and area [m^2] (E4).

    The density is selected and evaluated at h_s, with |h_s - h| <= alpha_sel h + beta_sel
    (E1, E2). For true h >= low, h_s >= low - eps_sel(low) =: ell, and |r| <= a + h <= a +
    (h_s + beta_sel) / (1 - alpha_sel). So
        |a^_drag| <= sup over h_s >= ell of g(h_s) + A(s, b),
        g(h) = F_D' rho(h) exp(theta_x X(h)) (s + omega_E (a + (h + beta_sel) / (1 -
        alpha_sel)))^2 / (2 b),
    with rho the exact table formula (decimal values) and X(h) = (h - base_i) / H_i inside
    band i, and A the absolute (underflow) part of E4 at S_max (Review 04 M3T0-R4-F1: the
    sup of the absolute part is taken over every selection height with nonzero computed
    density, h_s <= h_zero). On band i, d ln g / dh = -(1 - theta_x) / H_i + 2 omega_E / ((1 -
    alpha_sel) s + omega_E ((1 - alpha_sel) a + h + beta_sel)) < 0 whenever (1 - alpha_sel)
    (1 - theta_x) a > 2 H_i (ell >= -beta_sel), so g decreases inside every band, including
    the unbounded top band, and the supremum is attained at ell or at a band base above ell,
    where X = 0 and the band above applies (GMAT's rule). ell is clamped at the lower edge
    0: a computed height below it raises OutsideDomainError and applies no force.
    Both parts use b_R = phi_B / R <= b (E4a), which bounds cd area / mass for a vehicle
    whose b was formed from its mass by either construction, including subnormal b, P, Q or
    mass (Review 05 M3T0-R5-F1). b_R = b where the conversion is normal. b = +inf is the
    drag-free limit (0): a vehicle reaches it only through C1 with fl(cd area) = 0, where
    the force is exactly 0 (E4b), or through an overflow of mass / P, which the supported
    domain (no overflow) excludes.
    Evaluated in 60-digit decimal arithmetic with an outward pad, then rounded up."""
    fp = FP if fp is None else fp
    if math.isinf(b):
        return 0.0
    if not low >= 0.0:
        raise ValueError("the envelope is defined above the lower edge only")
    with localcontext() as ctx:
        ctx.prec = PREC
        b_r = envelope_ballistic_coefficient(b, cd, area, fp)
        rel = _envelope_relative(low, s, b_r, fp)
        return _up((rel + _envelope_absolute(s, b_r, cd, area, fp)) * (1 + PAD))


def drag_only(cfg: m.Config, r: np.ndarray, v: np.ndarray, mass: float) -> float:
    """|drag acceleration| of the model at a state (total minus the drag-free total)."""
    nodrag = m.Config(j2=cfg.j2)
    return float(
        np.linalg.norm(
            m.acceleration(cfg, 0.0, r, v, mass) - m.acceleration(nodrag, 0.0, r, v, mass)
        )
    )


def model_drag(r: np.ndarray, v: np.ndarray, mass: float, drag: m.Drag = J2_DRAG.drag) -> float:
    """The model's own drag vector, computed exactly as inside the force (mu = 0 and J2 off
    make the gravity terms exact zeros), and its binary64 norm rounded up."""
    vec = -m.acceleration(m.Config(mu=0.0, drag=drag), 0.0, r, v, mass)
    with localcontext() as ctx:
        ctx.prec = PREC
        return _up(sum(Decimal(float(x)) ** 2 for x in vec).sqrt() * (1 + PAD))


def envelope_counterexample() -> dict:
    """Review 02 M3T0-R2-F2: lower bound L = 79 999.9 m, actual height 80 000 m, s = 11 000 m/s
    retrograde at the equator, B 25.76 kg/m^2."""
    low, s, h = 79_999.9, 11_000.0, 80_000.0
    r = np.array([m.A_WGS84 + h, 0.0, 0.0])
    v = np.array([0.0, -s, 0.0])
    actual = drag_only(J2_DRAG, r, v, MASS)
    old_rho = max([m.density(low)] + [m.density(x) for x in BASES_M if x > low])
    old = 0.5 * old_rho * (s + m.OMEGA_E * (m.A_WGS84 + low)) ** 2 / B_V1
    new = drag_envelope(low, s, B_V1)
    return {
        "lower_height_m": low,
        "actual_height_m": m.geodetic_iterative(r)[1],
        "speed_mps": s,
        "actual_drag_mps2": actual,
        "superseded_envelope_mps2": old,
        "corrected_envelope_mps2": new,
        "superseded_covers": old >= actual,
        "corrected_covers": new >= actual,
    }


def r3f1_counterexample() -> dict:
    """Review 03 M3T0-R3-F1: true height 120 000.0000000000233 m (reviewer, 80 digits;
    implementer, 60 digits), computed height 119 999.99999999907 m, L = 120 000 m,
    s = 11 000 m/s, B 25.76 kg/m^2."""
    r = np.array([5420209.728043159, 3584286.6758661848, 1.8499824933775928])
    v = np.array([6067.454938935459, -9175.29239664793, 0.0])
    low, s = 120_000.0, 11_000.0
    actual = model_drag(r, v, MASS)
    old = drag_envelope_exact_height(low, s, B_V1)
    new = drag_envelope(low, s, B_V1)
    return {
        "true_height_m": "120000.0000000000233 (high-precision reference, Review 03)",
        "computed_height_m": m.geodetic_iterative(r)[1],
        "height_error_bound_m": height_error_bound(low),
        "lower_height_m": low,
        "speed_mps": s,
        "model_drag_mps2": actual,
        "superseded_envelope_mps2": old,
        "corrected_envelope_mps2": new,
        "superseded_covers": old >= actual,
        "corrected_covers": new >= actual,
    }


def r4f1_counterexample() -> dict:
    """Review 04 M3T0-R4-F1: r = (197 059 137, 0, 0) m, whose true height is exactly
    190 681 000 m (the foot point is (a, 0, 0)), v = 0, B 25.76 kg/m^2, L = 190 681 000 m,
    s = 0. The computed density is subnormal; the coefficient's last division rounds
    0.51 x 2^-1074 up to 2^-1074, doubling the force."""
    r = np.array([197_059_137.0, 0.0, 0.0])
    low = 190_681_000.0
    if Decimal(r[0]) - Decimal(m.A_WGS84) != Decimal(low):
        raise RuntimeError("the R4-F1 point does not have the stated true height")
    actual = model_drag(r, np.zeros(3), MASS)
    old = drag_envelope_relative_only(low, 0.0, B_V1)
    new = drag_envelope(low, 0.0, B_V1)
    return {
        "true_height_m": low,
        "computed_height_m": m.geodetic_iterative(r)[1],
        "computed_density_kg_m3": m.density(m.geodetic_iterative(r)[1]),
        "speed_mps": 0.0,
        "model_drag_mps2": actual,
        "superseded_envelope_mps2": old,
        "corrected_envelope_mps2": new,
        "superseded_covers": old >= actual,
        "corrected_covers": new >= actual,
    }


def r5f1_counterexamples() -> list[dict]:
    """Review 05 M3T0-R5-F1: r = (186 378 137, 0, 0) m, whose true height is exactly
    180 000 000 m, v = 0, cd 2.2, area 15 m^2 and b = 2^-1074, formed from mass 17 x 2^-1074
    kg by C1 (b = fl(mass / fl(cd area))) and giving mass 30 x 2^-1074 kg by C2 (mass =
    fl(fl(b cd) area)). The relative-only conversion bound is exceeded 1.94 and 1.10 times."""
    r = np.array([186_378_137.0, 0.0, 0.0])
    low = 180_000_000.0
    if Decimal(r[0]) - Decimal(m.A_WGS84) != Decimal(low):
        raise RuntimeError("the R5-F1 point does not have the stated true height")
    tiny = math.ulp(0.0)
    out = []
    for construction, mass in (("C1", 17 * tiny), ("C2", (tiny * CD_V1) * AREA_V1)):
        b = mass / (CD_V1 * AREA_V1) if construction == "C1" else tiny
        actual = model_drag(r, np.zeros(3), mass)
        old = drag_envelope_relative_conversion(low, 0.0, b)
        new = drag_envelope(low, 0.0, b)
        out.append(
            {
                "construction": construction,
                "mass_in_2^-1074_kg": mass / tiny,
                "b_in_2^-1074_kg_per_m2": b / tiny,
                "true_height_m": low,
                "computed_height_m": m.geodetic_iterative(r)[1],
                "model_drag_mps2": actual,
                "superseded_envelope_mps2": old,
                "corrected_envelope_mps2": new,
                "superseded_covers": old >= actual,
                "corrected_covers": new >= actual,
            }
        )
    return out


# The floors published at Review 04 (`44260ef`, the Review 03 correction), for comparison.
PUBLISHED_REVIEW04 = {
    "B25.8": 124456.68544510857,
    "B100": 118633.50894662621,
    "drag-free limit": 111511.96182508787,
}


def floor_comparison(rows: list[dict]) -> dict:
    """Review 04 M3T0-R4-F1 (I-5 section 3): the root of need(h0) before the correction (the
    Review 03 envelope, without the absolute part) and after it, each bracketed to 1e-9 m;
    the floors published at Review 04 and now; and the margins at the published floor."""
    out = []
    for (bname, b), row in zip(VEHICLES, rows, strict=True):
        floor = row["h_f_sufficient_at_least_m"]
        brackets = {}
        for name, env in (
            ("review03_correction", lambda low, s, b: drag_envelope_relative_only(low, s, b)),
            ("corrected", None),
        ):
            lo, hi = floor - 2e-6, floor
            if not stage_need(lo, b, envelope=env) > 0.0 > stage_need(hi, b, envelope=env):
                raise RuntimeError("the root is not bracketed below the published floor")
            while hi - lo > 1e-9:
                mid = 0.5 * (lo + hi)
                lo, hi = (lo, mid) if stage_need(mid, b, envelope=env) < 0.0 else (mid, hi)
            brackets[name] = [lo, hi]
        at = stage_lower_heights(floor, b)
        out.append(
            {
                "vehicle": bname,
                "published_review04_m": PUBLISHED_REVIEW04[bname],
                "published_now_m": floor,
                "published_unchanged": floor == PUBLISHED_REVIEW04[bname],
                "root_bracket_review03_correction_m": brackets["review03_correction"],
                "root_bracket_corrected_m": brackets["corrected"],
                "need_at_published_floor_m": stage_need(floor, b),
                "stage_bounds_at_published_floor_m": {k: at[k] for k in ("M2", "M3", "M4")},
                "two_decimals_nearest_m": round(floor, 2),
                "two_decimals_nearest_is_sufficient": stage_need(round(floor, 2), b) < 0.0,
                "two_decimals_rounded_up_m": math.ceil(floor * 100) / 100,
            }
        )
    return {
        "rows": out,
        "note": "root brackets [lo, hi] with need(lo) > 0 > need(hi); 'review03_correction' "
        "is the stage condition with the superseded relative-only envelope",
    }


def libm_sensitivity(rows: list[dict], max_log2: int = 40) -> dict:
    """I-5 section 5: how far A-FP-2 can be weakened. Every derived constant is
    non-decreasing in LIBM_ULP (through UF and nu), so need(h0) is too: if need < 0 at a
    floor F for LIBM_ULP = 2^j, F holds for every libm within 2^j ulps (relative error <=
    2^j 2^-52 and, for subnormal results, absolute error <= 2^j 2^-1074). For each floor:
    the largest such j <= max_log2 (None if j = 0 fails), at the published bracket end and
    at its 2-decimal quotations rounded up and to nearest."""
    cache: dict[int, dict] = {}

    def fp_for(j: int) -> dict:
        if j not in cache:
            cache[j] = derived_constants(2**j)[1]
        return cache[j]

    out = []
    for (bname, b), row in zip(VEHICLES, rows, strict=True):
        floor = row["h_f_sufficient_at_least_m"]
        heights = {
            "published_bracket_end": floor,
            "two_decimals_rounded_up": math.ceil(floor * 100) / 100,
            "two_decimals_nearest": round(floor, 2),
        }
        res = {}
        for key, h in heights.items():
            best = None
            for j in range(max_log2 + 1):
                if stage_need(h, b, fp=fp_for(j)) >= 0.0:
                    break
                best = j
            res[key] = {"height_m": h, "largest_log2_libm_ulp": best}
        out.append({"vehicle": bname, **res})
    return {
        "rows": out,
        "assumed_libm_ulp": LIBM_ULP,
        "max_log2_tested": max_log2,
        "kind": "the derivation evaluated under weaker libm assumptions (not a measurement)",
    }


def stage_stress(vehicle: str, b: float | None, floor: float, n: int = 2000) -> dict:
    """Empirical check of the derived condition (not part of the proof): bound states at
    floor <= h0 <= floor + 20 km (computed committed height) with near-escape, retrograde
    equatorial and straight-down velocities; each RK4 step must stay in the fail-closed
    domain, with every stage's computed height at or above its guaranteed lower bound
    (1 - alpha) L_k - beta and the stage accelerations within A0 and A2."""
    rng = np.random.default_rng(20261018)
    cfg = m.Config(j2=m.J2_FROM_C20) if b is None else J2_DRAG
    mass = MASS if b is None else b * 2.2 * 15.0
    bb = math.inf if b is None else b
    worst = {"stage_margin_m": math.inf, "a0_margin_mps2": math.inf, "a2_margin_mps2": math.inf}
    lowest = math.inf
    kinds = {"random": 0, "retrograde_equator": 0, "straight_down": 0}
    for i in range(n):
        h0 = floor + (1e-6 if i < 50 else rng.uniform(1e-6, 20_000.0))
        kind = ("random", "retrograde_equator", "straight_down")[i % 3]
        kinds[kind] += 1
        lat = 0.0 if kind == "retrograde_equator" else rng.uniform(-math.pi / 2, math.pi / 2)
        lon = rng.uniform(-math.pi, math.pi)
        r0 = m.geodetic_to_cartesian(lat, lon, h0)
        vesc = math.sqrt(2.0 * m.MU / float(np.linalg.norm(r0)))
        speed = vesc * (1.0 - 10.0 ** rng.uniform(-6.0, -1.0))
        if kind == "random":
            d = rng.normal(size=3)
        elif kind == "retrograde_equator":
            d = np.array([math.sin(lon), -math.cos(lon), 0.0])  # against the rotation
        else:
            d = -normal(lat, lon)
        v0 = speed * d / np.linalg.norm(d)
        y0 = np.concatenate([r0, v0, [mass]])
        h0c = m.geodetic_iterative(r0)[1]
        if h0c < floor:  # the guarantee is stated for computed committed heights >= floor
            raise RuntimeError("a stress state starts below the floor")
        stages: list = []
        m.rk4_step(m.rhs(cfg), 0.0, y0, DT, stages)  # raises OutsideDomainError if it fails
        lim = stage_lower_heights(h0c, bb)
        hs = [m.geodetic_iterative(st.r)[1] for st in stages]
        lowest = min(lowest, *hs)
        margin = min(hs[0] - lim["M2"], hs[1] - lim["M3"], hs[2] - lim["M4"])
        worst["stage_margin_m"] = min(worst["stage_margin_m"], margin)
        a0 = float(np.linalg.norm(m.acceleration(cfg, 0.0, r0, v0, mass)))
        y2 = y0 + 0.5 * DT * m.rhs(cfg)(0.0, y0)
        a2 = float(np.linalg.norm(m.acceleration(cfg, 0.0, y2[:3], y2[3:6], mass)))
        worst["a0_margin_mps2"] = min(worst["a0_margin_mps2"], lim["A0"] - a0)
        worst["a2_margin_mps2"] = min(worst["a2_margin_mps2"], lim["A2"] - a2)
    return {
        "vehicle": vehicle,
        "states": n,
        "kinds": kinds,
        "lowest_stage_height_m": lowest,
        "min_margins": worst,
        "all_within_bounds": min(worst.values()) >= 0.0,
    }


def stage_lower_heights(h0: float, b: float, fp: dict | None = None, envelope=None) -> dict:
    """Bounds for an RK4 step from any bound committed state whose *computed* geodetic
    height is h0 (E1-E6; the simulator only knows computed heights):
      true h0 in [H0, (h0 + beta) / (1 - alpha)], H0 = (h0 - beta) / (1 + alpha);
      |r0| <= R0 = a + (h0 + beta) / (1 - alpha);  |v0| <= V = sqrt(2 mu / (b + H0));
      A0 = (1 + u)(G^ + drag_envelope(H0, V, B)) >= |a^(y0)|;
      true h(r^2) >= L2 = H0 - 5 (1 + u)^2 V - u R0 - 2 eta0;
      |v^2| <= s2 = (1 + u) V + 5 (1 + u)^2 A0 + 2 eta0,
      true h(r^3) >= L3 = H0 - 5 (1 + u)^2 s2 - u R0 - 2 eta0;
      A2 = (1 + u)(G^ + drag_envelope(L2, s2, B)) >= |a^(y2)|;
      |v^3| <= s3 = (1 + u) V + 5 (1 + u)^2 A2 + 2 eta0,
      true h(r^4) >= L4 = H0 - 10 (1 + u)^2 s3 - u R0 - 2 eta0;
      computed stage height >= M_k = (1 - alpha) L_k - beta (E1).
    M_k > 0 implies the stage evaluates without OutsideDomainError (computed height >= 0,
    so fl(h / 1000) >= 0). Evaluated in 60-digit decimal arithmetic with outward pads;
    lower bounds are rounded down and upper bounds up when returned. fp (the constants for
    another LIBM_ULP) and envelope (the superseded one) serve `libm_sensitivity` and
    `floor_comparison` only."""
    fp = FP if fp is None else fp
    env = (lambda low, s, b: drag_envelope(low, s, b, fp=fp)) if envelope is None else envelope
    with localcontext() as ctx:
        ctx.prec = PREC
        one_u = 1 + Decimal(fp["u"])
        al, be = Decimal(fp["alpha"]), Decimal(fp["beta_m"])
        a, mu = Decimal(m.A_WGS84), Decimal(m.MU)
        g_hat = Decimal(fp["gravity_hat_mps2"])
        e6 = Decimal(fp["stage_abs_in_2^-1074"]) * TINY_D
        h0d = Decimal(h0)
        big_h0 = (h0d - be) / (1 + al) - Decimal("1e-35")
        r0 = (a + (h0d + be) / (1 - al)) * (1 + PAD)
        v = (2 * mu / (Decimal(fp["b_lower_m"]) + big_h0)).sqrt() * (1 + PAD)
        a0 = one_u * (g_hat + Decimal(env(_dn(big_h0), _up(v), b))) * (1 + PAD)
        uu = Decimal(fp["u"])
        l2 = big_h0 - 5 * one_u**2 * v - uu * r0 - e6 - Decimal("1e-35")
        s2 = (one_u * v + 5 * one_u**2 * a0 + e6) * (1 + PAD)
        l3 = big_h0 - 5 * one_u**2 * s2 - uu * r0 - e6 - Decimal("1e-35")
        out = {
            "H0": _dn(big_h0),
            "V": _up(v),
            "A0": _up(a0),
            "L2": _dn(l2),
            "L3": _dn(l3),
            "s2": _up(s2),
            "M2": _dn((1 - al) * l2 - be),
            "M3": _dn((1 - al) * l3 - be),
        }
        if out["M2"] <= 0.0:  # the k2 input may already be below the edge; a(y2) not bounded
            out.update(A2=None, s3=None, L4=None, M4=None)
            return out
        a2 = one_u * (g_hat + Decimal(env(_dn(l2), _up(s2), b))) * (1 + PAD)
        s3 = (one_u * v + 5 * one_u**2 * a2 + e6) * (1 + PAD)
        l4 = big_h0 - 10 * one_u**2 * s3 - uu * r0 - e6 - Decimal("1e-35")
        out.update(A2=_up(a2), s3=_up(s3), L4=_dn(l4), M4=_dn((1 - al) * l4 - be))
        return out


def stage_need(h0: float, b: float, fp: dict | None = None, envelope=None) -> float:
    """need(h0) = -min(M2, M3, M4) (or -M2 when the k2 input may already be below the edge):
    negative means every stage of a step from computed height h0 stays in the domain."""
    s = stage_lower_heights(h0, b, fp, envelope)
    if s["M4"] is None:
        return -s["M2"]  # >= 0 already: the k2 input may be below the edge
    return -min(s["M2"], s["M3"], s["M4"])  # >= 0: a stage may leave the domain


VEHICLES = (("B25.8", B_V1), ("B100", 100.0), ("drag-free limit", math.inf))


def sufficient_stage_condition() -> dict:
    """Derived sufficient condition for every RK4 stage of a step to stay above the lower
    edge (0 m, the table's lowest base), from the 1-Lipschitz height and the computed stage
    positions (E6)
        r^2 = fl(r0 + fl(dt/2 v0)),  r^3 = fl(r0 + fl(dt/2 v^2)),  r^4 = fl(r0 + fl(dt v^3)).
    Domain: every committed state with computed geodetic height h0 and negative two-body
    energy, any velocity direction, no thrust. Bounds used (`stage_lower_heights`):
    - |v0| <= V = sqrt(2 mu / (b + H0)), H0 the lower bound of the true height;
    - computed gravity plus J2 <= G^ = (1 + u) max(F_g, F_J) (1 + 3 J2 (a/b)^2) mu / b^2
      anywhere outside the ellipsoid (|r| >= b; |a_J2| = 1.5 J2 mu a^2 / r^4 sqrt(1 - 2w +
      5w^2), w = (z/r)^2, <= 2), E5;
    - computed drag <= `drag_envelope` at each stage's lower true-height bound and speed
      bound, E1-E4 (Review 03 M3T0-R3-F1: the envelope includes every band the computed
      height can select; Review 04 M3T0-R4-F1: and the absolute error of subnormal
      results; Review 05 M3T0-R5-F1: and of the conversion between b and the mass, E4a);
    - the stage's computed height is >= M_k = (1 - alpha) L_k - beta, E1.
    Monotonicity: H0 and L_k increase with h0 (the coefficient of h0 is 1 / (1 + alpha) -
    u / (1 - alpha) > 0), V decreases, the envelope is non-increasing in its lower height
    and non-decreasing in its speed, so A0 and then A2 do not increase and every M_k
    increases with h0. need(h0) = -min(M2, M3, M4) is therefore strictly decreasing and
    has one root. The returned floor is the upper end of a bisection bracket at which the
    outward-rounded need is negative, so the exact need is negative there and at every
    larger h0. The floor for a ballistic coefficient B also covers every larger B."""
    rows = []
    for bname, b in VEHICLES:

        def need(h0: float, b: float = b) -> float:
            return stage_need(h0, b)

        lo, hi = 1.0, 2_000_000.0
        if not (need(lo) > 0.0 > need(hi)):
            raise RuntimeError("the floor is not bracketed")
        while hi - lo > 1e-6:
            mid = 0.5 * (lo + hi)
            if need(mid) < 0.0:
                hi = mid
            else:
                lo = mid
        rows.append(
            {
                "vehicle": bname,
                "B_kg_per_m2": None if math.isinf(b) else b,
                "h_f_sufficient_at_least_m": hi,
                "need_at_floor_m": need(hi),
                "need_below_bracket_m": need(lo),
                "at_floor": stage_lower_heights(hi, b),
            }
        )
    return {
        "dt_s": DT,
        "lower_edge_m": BASES_M[0],
        "gravity_bound_mps2": G_BOUND,
        "gravity_bound_computed_mps2": FP["gravity_hat_mps2"],
        "floor_height_kind": "computed committed geodetic height (Review 03 M3T0-R3-F1)",
        "rows": rows,
        "review02_counterexample": envelope_counterexample(),
        "review03_counterexample": r3f1_counterexample(),
        "review04_counterexample": r4f1_counterexample(),
        "review05_counterexamples": r5f1_counterexamples(),
        "stress": [
            stage_stress(r["vehicle"], r["B_kg_per_m2"], r["h_f_sufficient_at_least_m"])
            for r in rows
        ],
        "note": "Sufficient, not necessary. A sharper condition needs a restriction of the "
        "admissible initial states (for example the inward velocity), which is an owner "
        "decision and is not proposed here.",
    }


def floating_point_enclosure() -> dict:
    """The derived constants of E1-E6 (as binary64 upper bounds) and eps_h at sample heights."""
    return {
        "assumptions": {
            "A-FP-1": "IEEE 754 binary64, round to nearest even, gradual underflow (no "
            "flush-to-zero); * and / within relative u = 2^-53 plus, for an underflowing "
            "result, absolute 2^-1075; + - and sqrt within relative u",
            "A-FP-2": f"libm sin, cos, atan2, hypot, exp, pow: |error| <= {LIBM_ULP} x 2^-52 "
            f"|exact| + {LIBM_ULP} x 2^-1074 (assumption; measured in t0_height_error.py, "
            "not proved; see libm_sensitivity)",
            "A-FP-3": "numpy 3-element products elementwise; 3-term dot x.x within gamma_3 "
            "sum x_i^2 + 3 (1 + u)^2 2^-1075",
            "domain": "true geodetic height >= 0 (outside the ellipsoid), no overflow",
        },
        "constants": {key: FP[key] for key in sorted(FP)},
        "eps_h_m": {f"{h:.0f}": height_error_bound(h) for h in (0.0, 120e3, 1.0e6, 2.0e6)},
        "eps_sel_m": {
            f"{h:.0f}": _up(FPA["alpha_sel"] * Fraction(h) + FPA["beta_sel_m"])
            for h in (0.0, 120e3, 1.0e6, 2.0e6)
        },
        "eps_h_definition": "|computed - true| geodetic height <= alpha h + beta (true h)",
        "underflow": {
            "eta0": "2^-1075",
            "zero_density_selection_height_m": FP["h_zero_m"],
            "absolute_part_mps2": {
                f"{name} s={s:.0f}": _up(
                    _envelope_absolute(
                        s, envelope_ballistic_coefficient(b, CD_V1, AREA_V1, FP), CD_V1, AREA_V1, FP
                    )
                )
                for name, b in VEHICLES[:2]
                for s in (0.0, 11_000.0)
            },
        },
    }


# ------------------------------------------------------------------- stage order (F3)
def stage_order() -> dict:
    r, v = m.circular_state(180e3, 51.6)
    stages: list = []
    m.rk4_step(m.rhs(J2_DRAG), 0.0, np.r_[r, v, MASS], DT, stages)
    return {
        "state": "circular 180 km, i 51.6 deg, J2 + drag, dt 10 s",
        "recorded_order": ["k2 input y + dt/2 k1", "k3 input y + dt/2 k2", "k4 input y + dt k3"],
        "height_minus_initial_m": {
            name: m.geodetic_iterative(s.r)[1] - 180e3
            for name, s in zip(("k2_input", "k3_input", "k4_input"), stages, strict=True)
        },
    }


def main() -> None:
    ssc = sufficient_stage_condition()
    out = {
        "missed_crossing": missed_crossing(),
        "stiffness_thresholds": stiffness_thresholds(),
        "admissibility_counterexamples": admissibility_counterexamples(),
        "floating_point_enclosure": floating_point_enclosure(),
        "sufficient_stage_condition": ssc,
        "floor_comparison": floor_comparison(ssc["rows"]),
        "libm_sensitivity": libm_sensitivity(ssc["rows"]),
        "stage_order": stage_order(),
        "vectorised_height_check_max_abs_m": vector_height_check(),
    }
    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    mc = out["missed_crossing"]
    flags = ("all_certified_bounds_hold", "all_dips_within_sampled_estimates")
    print(json.dumps({"cases": mc["cases"], **{k: mc[k] for k in flags}}, indent=1))
    for row in mc["sweep"]:
        ref = (
            f"certified bound {row['bound_m']:.5f} m"
            if "bound_m" in row
            else f"sampled estimate {row['sampled_estimate_m']:.5f} m (not a bound)"
        )
        print(
            f"{row['physics']:7s} {row['perigee_km']:6.0f} x {row['apogee_km']:6.0f} "
            f"i {row['inclination_deg']:5.1f}: dip {row['max_dip_m']:.5f} m "
            f"(phase {row['phase_s']:.2f} s); {ref}"
        )
    print(json.dumps({k: v for k, v in out.items() if k != "missed_crossing"}, indent=1))


def vector_height_check() -> float:
    rng = np.random.default_rng(20261018)
    pts = []
    for _ in range(200):
        lat = rng.uniform(-math.pi / 2, math.pi / 2)
        lon = rng.uniform(-math.pi, math.pi)
        pts.append(m.geodetic_to_cartesian(lat, lon, rng.uniform(0.0, 2.0e6)))
    rr = np.array(pts).T
    return float(np.max(np.abs(geodetic_heights(rr) - [m.geodetic_iterative(p)[1] for p in pts])))


if __name__ == "__main__":
    main()
