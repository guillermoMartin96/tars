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


def drag_envelope(low: float, s: float, b: float) -> float:
    """sup of the drag acceleration rho(h) |v_rel|^2 / (2 B) over every point at geodetic
    height h >= low (>= 0) with inertial speed |v| <= s.

    |v_rel| = |v - omega_E Z x r| <= s + omega_E |r| <= s + omega_E (a + h), since the point
    is r_s + h n with |r_s| <= a. Both factors are evaluated at the same h, so the bound is
    sup_{h >= low} f(h) with f(h) = rho(h) (s + omega_E (a + h))^2 / (2 B) (Review 02
    M3T0-R2-F2: the rotation term grows with h and is not bounded at the lower end).
    On each band rho = rho_i exp(-(h - base_i) / H_i), so
        f'(h) / f(h) = 2 omega_E / (s + omega_E (a + h)) - 1 / H_i < 0   whenever a > 2 H_i,
    and f decreases inside every band, including the unbounded top band. The supremum over
    [low, inf) is therefore attained at low or at a band base above it (the bases where the
    table jumps upward)."""
    if math.isinf(b):
        return 0.0
    if not low >= 0.0:
        raise ValueError("the envelope is defined above the lower edge only")
    if not all(2.0 * bb.scale_km * 1e3 < m.A_WGS84 for bb in m.TABLE):
        raise ValueError("a band violates a > 2 H; f need not decrease inside it")

    def f(h: float) -> float:
        vr = s + m.OMEGA_E * (m.A_WGS84 + h)
        return 0.5 * m.density(h) * vr * vr / b

    return max([f(low)] + [f(base) for base in BASES_M if base > low])


def drag_only(cfg: m.Config, r: np.ndarray, v: np.ndarray, mass: float) -> float:
    """|drag acceleration| of the model at a state (total minus the drag-free total)."""
    nodrag = m.Config(j2=cfg.j2)
    return float(
        np.linalg.norm(
            m.acceleration(cfg, 0.0, r, v, mass) - m.acceleration(nodrag, 0.0, r, v, mass)
        )
    )


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


def stage_stress(vehicle: str, b: float | None, floor: float, n: int = 2000) -> dict:
    """Empirical check of the derived condition (not part of the proof): bound states at
    floor <= h0 <= floor + 20 km with near-escape, retrograde equatorial and straight-down
    velocities; each RK4 step must stay in the fail-closed domain, with every stage at or
    above its lower bound and the stage accelerations within A0 and A2."""
    rng = np.random.default_rng(20261018)
    cfg = m.Config(j2=m.J2_FROM_C20) if b is None else J2_DRAG
    mass = MASS if b is None else b * 2.2 * 15.0
    bb = math.inf if b is None else b
    worst = {"stage_margin_m": math.inf, "a0_margin_mps2": math.inf, "a2_margin_mps2": math.inf}
    lowest = math.inf
    kinds = {"random": 0, "retrograde_equator": 0, "straight_down": 0}
    for i in range(n):
        h0 = floor + (0.0 if i < 50 else rng.uniform(0.0, 20_000.0))
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
        stages: list = []
        m.rk4_step(m.rhs(cfg), 0.0, y0, DT, stages)  # raises OutsideDomainError if it fails
        lim = stage_lower_heights(m.geodetic_iterative(r0)[1], bb)
        hs = [m.geodetic_iterative(st.r)[1] for st in stages]
        lowest = min(lowest, *hs)
        margin = min(hs[0] - lim["L2"], hs[1] - lim["L3"], hs[2] - lim["L4"])
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
    """Lower bounds L2, L3, L4 on the heights of the k2, k3 and k4 inputs of an RK4 step from
    any bound committed state at geodetic height h0, with the speed and acceleration bounds
    they use. L_k > 0 implies the stage is outside the ellipsoid (the segment from r0 would
    otherwise cross the surface, at distance >= h0 from r0)."""
    v = math.sqrt(2.0 * m.MU / (m.B_WGS84 + h0))  # |v0|^2 < 2 mu / |r0|, |r0| >= b + h0
    a0 = G_BOUND + drag_envelope(h0, v, b)
    l2 = h0 - 0.5 * DT * v
    l3 = h0 - 0.5 * DT * (v + 0.5 * DT * a0)
    out = {"V": v, "A0": a0, "L2": l2, "L3": l3, "s2": v + 0.5 * DT * a0}
    if l2 <= 0.0:  # the k2 input may already be below the edge; a(y2) is not bounded
        out.update(A2=None, L4=None)
        return out
    a2 = G_BOUND + drag_envelope(l2, out["s2"], b)
    out.update(A2=a2, L4=h0 - DT * (v + 0.5 * DT * a2))
    return out


def sufficient_stage_condition() -> dict:
    """Derived sufficient condition for every RK4 stage of a step to stay above the lower
    edge (0 m, the table's lowest base), from the 1-Lipschitz height and the stage positions
        r2 = r0 + dt/2 v0,  r3 = r0 + dt/2 (v0 + dt/2 a(y0)),  r4 = r0 + dt (v0 + dt/2 a(y2)):
    h2 >= h0 - dt/2 V,  h3 >= h0 - dt/2 (V + dt/2 A0),  h4 >= h0 - dt (V + dt/2 A2).
    Domain: every committed state at geodetic height h0 with negative two-body energy, any
    velocity direction, no thrust. Bounds used:
    - V = sqrt(2 mu / (b + h0)) >= |v0|;
    - gravity plus J2 <= (1 + 3 J2 (a/b)^2) mu / b^2 at any point outside the ellipsoid
      (|r| >= b; |a_J2| = 1.5 J2 mu a^2 / r^4 sqrt(1 - 2u + 5u^2), u = (z/r)^2, <= 2);
    - drag <= `drag_envelope` at each stage's lower height bound and speed bound
      (|v(y0)| <= V, |v(y2)| <= V + dt/2 A0).
    Monotonicity: V decreases in h0, and the envelope decreases in its lower height and
    increases in its speed, so A0 decreases, L2, L3 and then A2 and L4 increase with h0.
    need(h0) = -min(L2, L3, L4) is therefore strictly decreasing and has one root, the floor:
    every h0 above it satisfies the condition. The floor for a ballistic coefficient B also
    covers every larger B (less drag)."""
    rows = []
    for bname, b in (("B25.8", B_V1), ("B100", 100.0), ("drag-free limit", math.inf)):

        def need(h0: float, b: float = b) -> float:
            s = stage_lower_heights(h0, b)
            if s["L4"] is None:
                return -s["L2"]  # > 0 already: the k2 input may be below the edge
            return -min(s["L2"], s["L3"], s["L4"])  # > 0: a stage may leave the domain

        lo, hi = 1.0, 2_000_000.0
        if not (need(lo) > 0.0 > need(hi)):
            raise RuntimeError("the floor is not bracketed")
        h_req = brentq(need, lo, hi, xtol=1e-6)
        rows.append(
            {
                "vehicle": bname,
                "B_kg_per_m2": None if math.isinf(b) else b,
                "h_f_sufficient_at_least_m": h_req,
                "at_floor": stage_lower_heights(h_req, b),
            }
        )
    return {
        "dt_s": DT,
        "lower_edge_m": BASES_M[0],
        "gravity_bound_mps2": G_BOUND,
        "rows": rows,
        "review02_counterexample": envelope_counterexample(),
        "stress": [
            stage_stress(r["vehicle"], r["B_kg_per_m2"], r["h_f_sufficient_at_least_m"])
            for r in rows
        ],
        "note": "Sufficient, not necessary. A sharper condition needs a restriction of the "
        "admissible initial states (for example the inward velocity), which is an owner "
        "decision and is not proposed here.",
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
