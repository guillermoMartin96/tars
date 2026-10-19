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
from decimal import Decimal, localcontext
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
# model (`t0_model`), derived operation by operation. Assumptions (A-FP):
#   A-FP-1  IEEE 754 binary64, round to nearest even; +, -, *, / and sqrt are correctly
#           rounded: fl(x op y) = (x op y)(1 + d), |d| <= u = 2^-53. Absolute errors of
#           subnormal results (< 1e-300 in every quantity here) are negligible against
#           the relative terms and are not carried.
#   A-FP-2  libm sin, cos, atan2, hypot, exp and pow return their exact value with a
#           relative error <= UF = LIBM_ULP 2^-52 (= 2 LIBM_ULP u). Not proved here: an
#           assumption about the platform library, measured on this platform in
#           `t0_height_error.py`; every bound below is derived only under it.
#   A-FP-3  numpy evaluates the 3-element products elementwise in binary64 and a 3-term
#           dot product within gamma_3 = 3u / (1 - 3u) of the sum of |terms| (any order
#           or fused multiply-add).
# Supported domain: points outside the ellipsoid (true height >= 0), no overflow.
U = Fraction(1, 2**53)
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


def _sqrt_bounds(q: Fraction) -> tuple[Fraction, Fraction]:
    s = math.isqrt(q.numerator * 10**80 // q.denominator)
    return Fraction(s, 10**40), Fraction(s + 1, 10**40)


def _up(q) -> float:
    """The smallest binary64 >= q (q a Fraction or a Decimal)."""
    x = float(q)
    return x if Fraction(x) >= Fraction(q) else math.nextafter(x, math.inf)


def _dn(q) -> float:
    x = float(q)
    return x if Fraction(x) <= Fraction(q) else math.nextafter(x, -math.inf)


def rounding_allowances() -> dict:
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
    Result: |h^ - h| <= alpha h + beta.

    E2 kilometre conversion. `density` selects the band and evaluates the formula at
    h_km = fl(h^ / 1000); the selection height h_s = 1000 h_km satisfies |h_s - h^| <= u
    |h^| exactly (the bases are integers in km), so |h_s - h| <= alpha_sel h + beta_sel.

    E3 density. rho^ = fl(rho0 fl(exp(-fl(fl(h_km - base) / scale)))) with the table's
    decimal rho0 and scale read to binary64 (relative <= u each): rho^ <= rho(h_s) exp(
    theta_x X) F_rho with X = (h_s - base) / H >= 0 the exponent of the exact table formula.

    E4 drag. |a^_drag| <= F_D rho(h_s) exp(theta_x X) (|v| + omega |r|)^2 / (2 b) for a
    vehicle with mass / (cd area) >= b / phi_B (the constructions b = fl(mass / fl(cd area))
    and mass = fl(fl(b cd) area) used here both satisfy it): coefficient (3 operations),
    the 3-term dot and sqrt, the two products with v_rel, and |fl(v - omega Z x r)| <=
    (1 + u)^2 (|v| + omega |r|).

    E5 gravity with J2. |a^_grav + a^_J2| <= (1 + u) max(F_g, F_J) G with G = (1 + 3 J2
    (a/b)^2) mu / b^2, from the operation counts of `t0_model.acceleration` and `j2_accel`
    (|r| >= b; the J2 direction vector has norm <= 2 |r|), and |a^| <= (1 + u)(that +
    |a^_drag|) for the final vector difference.

    E6 RK4 stages. A stage w = fl(r0 + fl(c k)) (c = 5 or 10, exact) satisfies |w - r0| <=
    (1 + u)^2 c |k| + u |r0|, and a stage velocity |fl(v0 + fl(5 a))| <= (1 + u) |v0| +
    5 (1 + u)^2 |a|."""
    e2, a = Fraction(m.E2_WGS84), Fraction(m.A_WGS84)
    s_lo, _ = _sqrt_bounds(1 - e2)
    b_lo = a * s_lo
    g3 = 3 * U / (1 - 3 * U)
    sq1_lo, _ = _sqrt_bounds(1 - g3)
    _, sq1_hi = _sqrt_bounds(1 + g3)

    # E1 height evaluation at the returned latitude
    theta1 = (1 + UF) ** 2 * (1 + U) - 1
    big12 = theta1 + U * (1 + theta1)
    theta3 = (1 + UF) ** 2 * (1 + U) ** 2 - 1
    rho3 = (e2 * theta3 + U * (1 + e2 * theta3)) / (1 - e2)
    sq = rho3 / (2 - rho3)  # |sqrt(1 + t) - 1| <= |t| / (1 + sqrt(1 - |t|)) <= |t| / (2 - |t|)
    theta4 = (1 + sq) * (1 + U) ** 2 - 1
    # latitude: contraction constant and one-step rounding
    q = e2 * a / s_lo
    qp = e2 * a / s_lo**3
    k = qp / (b_lo - q)
    nu = (1 + U) / (1 - ((1 + sq) * (1 + U) - 1)) - 1
    theta5 = (1 + nu) * (1 + UF) * (1 + U) ** 2 - 1
    ratio = (UF * b_lo + (theta5 + U * (1 + theta5)) * q) / (b_lo - q)
    eta = PI_HALF_UP * (ratio + UF)
    k60 = Fraction(_up(k)) ** LAT_ITER
    dphi = eta / (1 - k) + max(k * LAT_TOL / (1 - k), k60 * 2 * PI_HALF_UP)
    alpha_lat = dphi**2 / 2
    beta_lat = (2 * a + a / s_lo) * dphi**2 / 2
    alpha = (1 + U) * big12 + U + (1 + U) * alpha_lat
    beta = (1 + U) * (big12 + theta4) * a + (1 + U) * beta_lat
    # E2 km conversion
    alpha_sel = alpha * (1 + U) + U
    beta_sel = beta * (1 + U)
    # E3, E4 density and drag
    theta_x = (1 + U) ** 2 / (1 - U) - 1
    f_rho = (1 + UF) * (1 + U) ** 2
    phi_b = (1 + U) / (1 - U) ** 2
    f_d = f_rho * (1 + U) ** 10 * sq1_hi * phi_b
    # E5 gravity and J2
    rn_lo = sq1_lo * (1 - U)
    f_g = (1 + U) ** 2 / ((1 - UF) * rn_lo**3)
    f_k = (1 + U) ** 5 / ((1 - g3) ** 2 * (1 - U) ** 3 * sq1_lo)
    zeta = (1 + U) ** 3 / (1 - g3) - 1
    f_j = f_k * (1 + U) ** 3 * (1 + Fraction(5, 2) * zeta)
    j2, mu = Fraction(m.J2_FROM_C20), Fraction(m.MU)
    g_exact_up = (1 + 3 * j2 * a**2 / b_lo**2) * mu / b_lo**2
    g_hat = (1 + U) * max(f_g, f_j) * g_exact_up
    return {
        "u": U,
        "libm_ulp": LIBM_ULP,
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
    }


FPA = rounding_allowances()
FP = {key: _up(val) for key, val in FPA.items() if key not in ("b_lower_m",)}
FP["b_lower_m"] = _dn(FPA["b_lower_m"])


def height_error_bound(h: float) -> float:
    """eps_h(h) = alpha h + beta >= |computed - true| geodetic height at true height h."""
    return _up(FPA["alpha"] * Fraction(h) + FPA["beta_m"])


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


def drag_envelope(low: float, s: float, b: float) -> float:
    """Upper bound on the model's computed drag acceleration |a^_drag| at every point whose
    true geodetic height is >= low (>= 0), with inertial speed |v| <= s, for a vehicle of
    ballistic coefficient b (E4).

    The density is selected and evaluated at h_s, with |h_s - h| <= alpha_sel h + beta_sel
    (E1, E2). For true h >= low, h_s >= low - eps_sel(low) =: ell, and |r| <= a + h <= a +
    (h_s + beta_sel) / (1 - alpha_sel). So
        |a^_drag| <= sup over h_s >= ell of g(h_s),
        g(h) = F_D rho(h) exp(theta_x X(h)) (s + omega_E (a + (h + beta_sel) / (1 -
        alpha_sel)))^2 / (2 b),
    with rho the exact table formula (decimal values) and X(h) = (h - base_i) / H_i inside
    band i. On band i, d ln g / dh = -(1 - theta_x) / H_i + 2 omega_E / ((1 - alpha_sel) s
    + omega_E ((1 - alpha_sel) a + h + beta_sel)) < 0 whenever (1 - alpha_sel)(1 - theta_x)
    a > 2 H_i (ell >= -beta_sel), so g decreases inside every band, including the unbounded
    top band, and the supremum is attained at ell or at a band base above ell, where X = 0
    and the band above applies (GMAT's rule). ell is clamped at the lower edge 0: a
    computed height below it raises OutsideDomainError and applies no force.
    Evaluated in 60-digit decimal arithmetic with an outward pad, then rounded up."""
    if math.isinf(b):
        return 0.0
    if not low >= 0.0:
        raise ValueError("the envelope is defined above the lower edge only")
    with localcontext() as ctx:
        ctx.prec = PREC
        al, be, tx = Decimal(FP["alpha_sel"]), Decimal(FP["beta_sel_m"]), Decimal(FP["theta_x"])
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
        return _up(best * Decimal(FP["F_D"]) / (2 * Decimal(b)) * (1 + PAD))


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


def stage_lower_heights(h0: float, b: float) -> dict:
    """Bounds for an RK4 step from any bound committed state whose *computed* geodetic
    height is h0 (E1-E6; the simulator only knows computed heights):
      true h0 in [H0, (h0 + beta) / (1 - alpha)], H0 = (h0 - beta) / (1 + alpha);
      |r0| <= R0 = a + (h0 + beta) / (1 - alpha);  |v0| <= V = sqrt(2 mu / (b + H0));
      A0 = (1 + u)(G^ + drag_envelope(H0, V, B)) >= |a^(y0)|;
      true h(r^2) >= L2 = H0 - 5 (1 + u)^2 V - u R0;
      |v^2| <= s2 = (1 + u) V + 5 (1 + u)^2 A0,  true h(r^3) >= L3 = H0 - 5 (1 + u)^2 s2 - u R0;
      A2 = (1 + u)(G^ + drag_envelope(L2, s2, B)) >= |a^(y2)|;
      |v^3| <= s3 = (1 + u) V + 5 (1 + u)^2 A2, true h(r^4) >= L4 = H0 - 10 (1 + u)^2 s3 - u R0;
      computed stage height >= M_k = (1 - alpha) L_k - beta (E1).
    M_k > 0 implies the stage evaluates without OutsideDomainError (computed height >= 0,
    so fl(h / 1000) >= 0). Evaluated in 60-digit decimal arithmetic with outward pads;
    lower bounds are rounded down and upper bounds up when returned."""
    with localcontext() as ctx:
        ctx.prec = PREC
        one_u = 1 + Decimal(FP["u"])
        al, be = Decimal(FP["alpha"]), Decimal(FP["beta_m"])
        a, mu = Decimal(m.A_WGS84), Decimal(m.MU)
        g_hat = Decimal(FP["gravity_hat_mps2"])
        h0d = Decimal(h0)
        big_h0 = (h0d - be) / (1 + al) - Decimal("1e-35")
        r0 = (a + (h0d + be) / (1 - al)) * (1 + PAD)
        v = (2 * mu / (Decimal(FP["b_lower_m"]) + big_h0)).sqrt() * (1 + PAD)
        a0 = one_u * (g_hat + Decimal(drag_envelope(_dn(big_h0), _up(v), b))) * (1 + PAD)
        uu = Decimal(FP["u"])
        l2 = big_h0 - 5 * one_u**2 * v - uu * r0 - Decimal("1e-35")
        s2 = (one_u * v + 5 * one_u**2 * a0) * (1 + PAD)
        l3 = big_h0 - 5 * one_u**2 * s2 - uu * r0 - Decimal("1e-35")
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
        a2 = one_u * (g_hat + Decimal(drag_envelope(_dn(l2), _up(s2), b))) * (1 + PAD)
        s3 = (one_u * v + 5 * one_u**2 * a2) * (1 + PAD)
        l4 = big_h0 - 10 * one_u**2 * s3 - uu * r0 - Decimal("1e-35")
        out.update(A2=_up(a2), s3=_up(s3), L4=_dn(l4), M4=_dn((1 - al) * l4 - be))
        return out


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
      height can select);
    - the stage's computed height is >= M_k = (1 - alpha) L_k - beta, E1.
    Monotonicity: H0 and L_k increase with h0 (the coefficient of h0 is 1 / (1 + alpha) -
    u / (1 - alpha) > 0), V decreases, the envelope is non-increasing in its lower height
    and non-decreasing in its speed, so A0 and then A2 do not increase and every M_k
    increases with h0. need(h0) = -min(M2, M3, M4) is therefore strictly decreasing and
    has one root. The returned floor is the upper end of a bisection bracket at which the
    outward-rounded need is negative, so the exact need is negative there and at every
    larger h0. The floor for a ballistic coefficient B also covers every larger B."""
    rows = []
    for bname, b in (("B25.8", B_V1), ("B100", 100.0), ("drag-free limit", math.inf)):

        def need(h0: float, b: float = b) -> float:
            s = stage_lower_heights(h0, b)
            if s["M4"] is None:
                return -s["M2"]  # >= 0 already: the k2 input may be below the edge
            return -min(s["M2"], s["M3"], s["M4"])  # >= 0: a stage may leave the domain

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
            "A-FP-1": "IEEE 754 binary64, round to nearest even; + - * / sqrt correctly rounded",
            "A-FP-2": f"libm sin, cos, atan2, hypot, exp, pow relative error <= {LIBM_ULP} "
            "x 2^-52 (assumption; measured in t0_height_error.py, not proved)",
            "A-FP-3": "numpy 3-element products elementwise; 3-term dot within gamma_3",
            "domain": "true geodetic height >= 0 (outside the ellipsoid), no overflow",
        },
        "constants": {key: FP[key] for key in sorted(FP)},
        "eps_h_m": {f"{h:.0f}": height_error_bound(h) for h in (0.0, 120e3, 1.0e6, 2.0e6)},
        "eps_sel_m": {
            f"{h:.0f}": _up(FPA["alpha_sel"] * Fraction(h) + FPA["beta_sel_m"])
            for h in (0.0, 120e3, 1.0e6, 2.0e6)
        },
        "eps_h_definition": "|computed - true| geodetic height <= alpha h + beta (true h)",
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
    out = {
        "missed_crossing": missed_crossing(),
        "stiffness_thresholds": stiffness_thresholds(),
        "admissibility_counterexamples": admissibility_counterexamples(),
        "floating_point_enclosure": floating_point_enclosure(),
        "sufficient_stage_condition": sufficient_stage_condition(),
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
