"""M3 T0: decay to the lower atmosphere, RK4 intermediate stages, termination crossings.

Evidence for the DR-0027 T0 proposals (A-4 permitted ranges, A-5 crossing behaviour, A-6
interaction with the domain edges and `impact`, A-s density for RK4 stages, B-4 domain
behaviour). Every termination altitude below is a SPIKE TEST VALUE used to exercise the
mechanism; none is proposed as a scenario value (DR-0027 A-3).

Configuration: J2 + drag, geodetic height, WGS 84, omega_E (DR-0024), Cd 2.2, A 15 m^2,
m 850 kg (B = 25.8 kg/m^2, the VAL-0007/VAL-0018 illustrative case), circular start at
180 km, i = 51.6 deg. The density is evaluated in 'extrapolate' mode only so that the
experiment can observe what an RK4 stage below the lower edge would request; that mode is
a diagnostic, not a proposal.

Usage: uv run --no-sync python t0_decay.py <out.json>
"""

from __future__ import annotations

import json
import math
import sys

import numpy as np
import t0_model as m
from scipy.optimize import brentq

FLOORS_KM = (150.0, 120.0, 100.0, 90.0, 80.0, 70.0, 60.0, 50.0, 40.0, 25.0)
DT = 10.0
DRAG = m.Drag(cd=2.2, area_m2=15.0, below="extrapolate")
CFG = m.Config(j2=m.J2_FROM_C20, drag=DRAG)
MASS = 850.0


def h_geod(r: np.ndarray) -> float:
    return m.geodetic_iterative(r)[1]


def up(r: np.ndarray) -> np.ndarray:
    lat, _ = m.geodetic_iterative(r)
    lon = math.atan2(r[1], r[0])
    return np.array([math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat)])


def hermite_vec(r0, v0, r1, v1, dt, s):
    s2, s3 = s * s, s * s * s
    return (
        (2 * s3 - 3 * s2 + 1) * r0
        + (s3 - 2 * s2 + s) * dt * v0
        + (-2 * s3 + 3 * s2) * r1
        + (s3 - s2) * dt * v1
    )


def hermite_scalar(p0, m0, p1, m1, s):
    s2, s3 = s * s, s * s * s
    return (
        (2 * s3 - 3 * s2 + 1) * p0
        + (s3 - 2 * s2 + s) * m0
        + (-2 * s3 + 3 * s2) * p1
        + (s3 - s2) * m1
    )


def rk4_run(y0: np.ndarray, t_max: float):
    """RK4 at DT until the committed geodetic height is <= 0 (diagnostic: runs to the ground)."""
    f = m.rhs(CFG)
    t, y = 0.0, y0.copy()
    steps = [(t, y.copy(), [])]
    i = 0
    while t < t_max:
        stages: list = []
        y = m.rk4_step(f, t, y, DT, stages)
        i += 1
        t = i * DT
        steps.append((t, y.copy(), stages))
        if not np.all(np.isfinite(y)) or h_geod(y[:3]) <= 0.0:
            break
        # Numerical divergence (stiff drag, |lambda dt| beyond RK4's stability): the height
        # rises above the start or the speed grows; stop and record it.
        if h_geod(y[:3]) > 200_000.0 or float(np.linalg.norm(y[3:6])) > 9_000.0:
            break
    return steps


def divergence(steps, truth) -> dict:
    """Where does RK4 at DT stop following the DOP853 solution near the ground?"""
    f = m.rhs(CFG)
    t_end_true = truth["ground"][0]
    times = np.array([s[0] for s in steps if s[0] <= t_end_true])
    sol = m.dop853(f, steps[0][1], float(times[-1]), t_eval=times)
    rows = []
    for j, t in enumerate(sol.t):
        y = steps[j][1]
        h_true = h_geod(sol.y[:3, j])
        if h_true > 150_000.0:
            continue
        rows.append(
            {
                "t_s": float(t),
                "h_dop853_m": h_true,
                "h_rk4_m": h_geod(y[:3]),
                "speed_dop853_mps": float(np.linalg.norm(sol.y[3:6, j])),
                "speed_rk4_mps": float(np.linalg.norm(y[3:6])),
            }
        )
    first_bad = {}
    for tol in (1.0, 100.0, 10_000.0):
        bad = [r for r in rows if abs(r["h_rk4_m"] - r["h_dop853_m"]) > tol]
        first_bad[repr(tol)] = bad[0] if bad else None
    last = steps[-1]
    return {
        "rk4_stop_t_s": last[0],
        "rk4_stop_h_m": h_geod(last[1][:3]) if np.all(np.isfinite(last[1])) else None,
        "rk4_stop_speed_mps": float(np.linalg.norm(last[1][3:6])),
        "first_step_with_height_error_above_m": first_bad,
        "samples_below_150km": rows,
    }


def dop_crossings(y0: np.ndarray, t_max: float) -> dict:
    f = m.rhs(CFG)
    events = []
    for floor in FLOORS_KM:

        def ev(t, y, floor=floor):
            return h_geod(y[:3]) - floor * 1000.0

        ev.direction = -1
        events.append(ev)

    def ground(t, y):
        return h_geod(y[:3])

    ground.terminal = True
    ground.direction = -1
    sol = m.dop853(f, y0, t_max, events=[*events, ground])
    out = {}
    # sol.t_events has one more entry (the terminal ground event) than FLOORS_KM.
    for floor, te, ye in zip(FLOORS_KM, sol.t_events, sol.y_events, strict=False):
        if te.size:
            out[floor] = (float(te[0]), ye[0])
    out["ground"] = (
        (float(sol.t_events[-1][0]), sol.y_events[-1][0]) if sol.t_events[-1].size else None
    )
    return out


def crossing_methods(steps, floor_m: float):
    """Locate the first committed step that ends at or below floor_m, and refine it."""
    for k in range(1, len(steps)):
        t0, y0, _ = steps[k - 1]
        t1, y1, stages = steps[k]
        h0, h1 = h_geod(y0[:3]), h_geod(y1[:3])
        if h0 > floor_m >= h1:
            r0, v0, r1, v1 = y0[:3], y0[3:6], y1[:3], y1[3:6]
            # (b1) scalar cubic Hermite on h with dh/dt = n_up . v (exact gradient of h).
            m0 = float(up(r0) @ v0) * DT
            m1 = float(up(r1) @ v1) * DT
            seg = (h0, m0, h1, m1)
            sb1 = brentq(lambda s, c=seg: hermite_scalar(*c, s) - floor_m, 0.0, 1.0, xtol=1e-15)
            # (b2) cubic Hermite of the position vector, geodetic height of the interpolant.
            ends = (r0, v0, r1, v1)
            sb2 = brentq(
                lambda s, c=ends: h_geod(hermite_vec(*c, DT, s)) - floor_m, 0.0, 1.0, xtol=1e-15
            )
            stage_h = [h_geod(st.r) for st in stages]
            return {
                "step_index": k,
                "committed_t_before_s": t0,
                "committed_t_after_s": t1,
                "committed_h_before_m": h0,
                "committed_h_after_m": h1,
                "undershoot_at_committed_state_m": floor_m - h1,
                "t_scalar_hermite_s": t0 + sb1 * DT,
                "t_vector_hermite_s": t0 + sb2 * DT,
                "stage_heights_m": stage_h,
                "min_stage_minus_floor_m": min(stage_h) - floor_m,
                "spherical_alt_at_committed_after_m": m.spherical_altitude(r1),
                "latitude_deg_after": math.degrees(m.geodetic_iterative(r1)[0]),
            }
    return None


def stage_statistics(steps) -> dict:
    """How far below the lower of its two committed heights can an RK4 stage go?"""
    worst = {"undershoot_m": -math.inf}
    by_band = {}
    for k in range(1, len(steps)):
        _, y0, _ = steps[k - 1]
        t1, y1, stages = steps[k]
        if not stages or not np.all(np.isfinite(y1)):
            continue
        lo = min(h_geod(y0[:3]), h_geod(y1[:3]))
        mins = min(h_geod(st.r) for st in stages)
        under = lo - mins
        band = int(lo // 10_000) * 10
        by_band[band] = max(by_band.get(band, -math.inf), under)
        if under > worst["undershoot_m"]:
            worst = {"undershoot_m": under, "t_s": t1, "committed_low_m": lo, "min_stage_m": mins}
    return {
        "worst": worst,
        "max_undershoot_by_10km_height_band_m": {str(k): v for k, v in sorted(by_band.items())},
    }


def missed_crossing_fixed_phase() -> dict:
    """How far does the trajectory dip below the lower committed height inside a step?

    Eccentric 250 x 800 km orbit, J2 + drag, over two orbits, with the committed states at
    one fixed sampling phase (t = 0, 10, 20 ... s from perigee) and the inside of each step
    sampled every 0.5 s. This is a single-phase MEASUREMENT, not a bound (Review 01
    M3T0-F1): the derived bound and the sampling-phase, eccentricity and inclination sweeps
    are in t0_termination.py (`missed_crossing`).
    """
    r0, v0 = m.perigee_state(250_000.0, 800_000.0, 51.6)
    y0 = np.concatenate([r0, v0, [MASS]])
    f = m.rhs(CFG)
    t_end = 2 * 5850.0
    grid = np.arange(0.0, t_end + 1e-9, 0.5)
    sol = m.dop853(f, y0, t_end, t_eval=grid)
    h = np.array([h_geod(sol.y[:3, j]) for j in range(sol.y.shape[1])])
    per = int(DT / 0.5)
    dips = []
    for k in range(0, len(h) - per, per):
        seg = h[k : k + per + 1]
        dips.append(min(seg[0], seg[-1]) - seg.min())
    return {
        "configuration": "perigee 250 km, apogee 800 km (spherical), i 51.6, J2 + drag, 2 orbits",
        "sampling": "one fixed phase (committed states at t = 0, 10, 20 ... s from perigee); "
        "0.5 s inside each step. A measurement at that phase, not a bound: see "
        "t0_termination_results.json -> missed_crossing",
        "max_dip_below_committed_states_m": float(max(dips)),
    }


def main() -> None:
    r0, v0 = m.circular_state(180_000.0, 51.6)
    y0 = np.concatenate([r0, v0, [MASS]])
    t_max = 5 * 86400.0
    truth = dop_crossings(y0, t_max)
    steps = rk4_run(y0, t_max)
    t_ground = truth["ground"][0]
    out = {
        "configuration": {
            "start": "circular 180 km (spherical), i 51.6 deg, RAAN 0",
            "physics": "point mass + J2 (EGM2008 tide-free, from C20) + drag (pinned table, "
            "geodetic WGS 84, omega_E 7.292115e-5, extrapolate mode)",
            "cd": 2.2,
            "area_m2": 15.0,
            "mass_kg": MASS,
            "dt_s": DT,
            "floors_km_spike_test_values": list(FLOORS_KM),
        },
        "dop853_time_to_geodetic_zero_s": t_ground,
        "rk4_steps": len(steps) - 1,
        "rk4_last_committed_h_m": h_geod(steps[-1][1][:3])
        if np.all(np.isfinite(steps[-1][1]))
        else None,
        "floors": {},
        "stages": stage_statistics(steps),
        "missed_crossing": missed_crossing_fixed_phase(),
        "rk4_divergence": divergence(steps, truth),
        "sphere_minus_ellipsoid_max_m": m.A_WGS84 - m.B_WGS84,
    }
    for floor in FLOORS_KM:
        rec = crossing_methods(steps, floor * 1000.0)
        t_true, y_true = truth[floor]
        if rec is not None:
            rec["dop853_crossing_t_s"] = t_true
            rec["dop853_spherical_alt_at_crossing_m"] = m.spherical_altitude(y_true[:3])
            rec["committed_state_time_error_s"] = rec["committed_t_after_s"] - t_true
            rec["scalar_hermite_minus_dop853_s"] = rec["t_scalar_hermite_s"] - t_true
            rec["vector_hermite_minus_dop853_s"] = rec["t_vector_hermite_s"] - t_true
            rec["scalar_minus_vector_hermite_s"] = (
                rec["t_scalar_hermite_s"] - rec["t_vector_hermite_s"]
            )
            # lambda dt at the floor with the circular-speed proxy of DR-0029 P1 (as in
            # t0_atmosphere.stiffness); not a bound on lambda (Review 01 M3T0-F2)
            v = math.sqrt(m.MU / (m.A_WGS84 + floor * 1000.0))
            rec["lambda_dt_at_floor"] = m.density(floor * 1000.0) * v / (MASS / (2.2 * 15.0)) * DT
        out["floors"][str(floor)] = rec
    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True, default=float)
        fh.write("\n")
    brief = {
        k: None
        if v is None
        else {
            x: v[x]
            for x in (
                "committed_state_time_error_s",
                "scalar_hermite_minus_dop853_s",
                "vector_hermite_minus_dop853_s",
                "undershoot_at_committed_state_m",
                "min_stage_minus_floor_m",
                "spherical_alt_at_committed_after_m",
                "lambda_dt_at_floor",
            )
        }
        for k, v in out["floors"].items()
    }
    div = {k: v for k, v in out["rk4_divergence"].items() if k != "samples_below_150km"}
    print(
        json.dumps(
            {
                "t_ground": t_ground,
                "floors": brief,
                "stages": out["stages"],
                "missed": out["missed_crossing"],
                "divergence": div,
            },
            indent=1,
        )
    )


if __name__ == "__main__":
    main()
