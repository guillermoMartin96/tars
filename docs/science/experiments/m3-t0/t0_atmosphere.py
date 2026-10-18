"""M3 T0: atmosphere table boundaries, discontinuities and numerical sensitivity.

Exercises every band boundary of the pinned table (DR-0027 B-1; DR-0024 Q5a; DR-0025
principle 5), the lower edge and the region above the top base, and measures how a single
boundary crossing affects fixed-step RK4 (dt = 20 ... 1.25 s) against a reference that
restarts the integration exactly at the crossing.

Research only; no threshold is proposed here. Usage:
  uv run --no-sync python t0_atmosphere.py <out.json>
"""

from __future__ import annotations

import itertools
import json
import math
import sys

import numpy as np
import t0_model as m

RK4_REAL_STABILITY = 2.785293563405282  # |lambda dt| limit of classical RK4 on the real axis


def boundary_records() -> list[dict]:
    out = []
    for k in range(1, len(m.TABLE)):
        lo, hi = m.TABLE[k - 1], m.TABLE[k]
        base_m = hi.base_km * 1000.0
        left = lo.rho0 * math.exp(-(hi.base_km - lo.base_km) / lo.scale_km)
        below_m = math.nextafter(base_m, -math.inf)
        above_m = math.nextafter(base_m, math.inf)
        # Which band does each evaluation route select at and one ulp around the base?
        km_route = {
            "at_base": m.band_index(base_m / 1000.0),
            "one_ulp_below": m.band_index(below_m / 1000.0),
            "one_ulp_above": m.band_index(above_m / 1000.0),
        }
        # Largest height below the base that the km route still assigns to the upper band.
        h = base_m
        steps = 0
        while m.band_index(math.nextafter(h, -math.inf) / 1000.0) == k and steps < 10_000:
            h = math.nextafter(h, -math.inf)
            steps += 1
        rec = {
            "boundary_km": hi.base_km,
            "lower_band_left_limit_kg_m3": left,
            "upper_band_base_kg_m3": hi.rho0,
            "relative_value_jump": hi.rho0 / left - 1.0,
            "scale_height_below_km": lo.scale_km,
            "scale_height_above_km": hi.scale_km,
            "relative_log_slope_change": lo.scale_km / hi.scale_km - 1.0,
            "relative_drho_dh_jump": (hi.rho0 / hi.scale_km) / (left / lo.scale_km) - 1.0,
            "density_at_base_km_route": m.density(base_m),
            "density_one_ulp_below_km_route": m.density(below_m),
            "density_one_ulp_above_km_route": m.density(above_m),
            "density_at_base_m_route": m.density(base_m, units="m"),
            "density_one_ulp_below_m_route": m.density(below_m, units="m"),
            "band_selected_km_route": km_route,
            "band_selected_m_route": {
                "at_base": k,
                "one_ulp_below": k - 1
                if m.density(below_m, units="m") != m.density(base_m, units="m")
                else k,
            },
            "km_route_upper_band_below_base_ulps": steps,
            "km_route_upper_band_below_base_m": base_m - h,
            "base_m_exact": float(hi.base_km) * 1000.0 == round(hi.base_km * 1000.0),
        }
        out.append(rec)
    return out


def edges() -> dict:
    low = {}
    for h in (0.0, -1e-9, -1.0, -100.0, -1000.0):
        try:
            low[repr(h)] = {"raise_mode": m.density(h)}
        except m.OutsideDomainError as exc:
            low[repr(h)] = {"raise_mode": f"OutsideDomainError: {exc}"}
        low[repr(h)]["extrapolate_mode"] = m.density(h, below="extrapolate")
    top = m.TABLE[-1]
    above = {}
    for h_km in (999.999, 1000.0, 1100.0, 1500.0, 2000.0, 5000.0):
        above[repr(h_km)] = {
            "band_base_km": m.TABLE[m.band_index(h_km)].base_km,
            "density": m.density(h_km * 1000.0),
        }
    return {
        "lower_edge_km": m.TABLE[0].base_km,
        "below_lower_edge": low,
        "top_base_km": top.base_km,
        "above_top_base": above,
        "note": "values above 1000 km are the top band's formula extrapolated; DR-0027 B-2 "
        "records +19.6 % / +145 % / +500 % vs the author's file at 1100/1500/2000 km",
    }


def stiffness() -> dict:
    """Linearised drag decay rate |d(dv/dt)/dv| = rho v / B for a circular orbit, B = m/(Cd A).

    RK4 is stable on the real axis only for |lambda| dt <= 2.785; its local relative error is
    ~ (lambda dt)^5 / 120. The heights at which dt = 10 s reaches given |lambda dt| bound the
    numerically meaningful termination altitudes (DR-0027 A-4).
    """
    out = {}
    for b_name, b in (("B25.8", 850.0 / (2.2 * 15.0)), ("B100", 100.0)):
        rows = []
        for h_km in [x * 5.0 for x in range(0, 61)]:
            rho = m.density(h_km * 1000.0)
            v = math.sqrt(m.MU / (m.A_WGS84 + h_km * 1000.0))
            lam = rho * v / b
            rows.append({"h_km": h_km, "lambda_per_s": lam, "lambda_dt10": lam * 10.0})
        crossings = {}
        for target in (RK4_REAL_STABILITY, 1.0, 0.1, 0.01):
            hit = [r["h_km"] for r in rows if r["lambda_dt10"] >= target]
            crossings[repr(target)] = max(hit) if hit else None
        out[b_name] = {
            "ballistic_kg_m2": b,
            "highest_grid_height_km_with_lambda_dt10_at_least": crossings,
            "grid": rows,
        }
    return out


# ------------------------------------------------- one boundary crossing under RK4
def crossing_experiment() -> dict:
    """Equatorial circular orbit 2 km above the 250 km base, decaying through it.

    At the equator geodetic height = |r| - a, so the crossing is clean. The reference
    integrates with DOP853 in two pieces split exactly at the crossing (terminal event), which
    is the exact solution of the discontinuous right-hand side to DOP853 accuracy.
    """
    drag = m.Drag(cd=2.2, area_m2=15.0 * 40.0)  # B = 0.645 kg/m^2: crosses in ~4 h
    cfg = m.Config(drag=drag)
    r0, v0 = m.circular_state(252_000.0, 0.0)
    y0 = np.concatenate([r0, v0, [850.0]])
    f = m.rhs(cfg)
    horizon = 4.0 * 3600.0

    def ev(t, y):
        return float(np.linalg.norm(y[:3])) - m.A_WGS84 - 250_000.0

    ev.terminal = True
    ev.direction = -1
    first = m.dop853(f, y0, horizon, events=ev)
    if not first.t_events[0].size:
        raise RuntimeError("no crossing")
    tc = float(first.t_events[0][0])
    yc = first.y_events[0][0]
    # End 1200 s after the crossing, on a multiple of every dt used below.
    t_end = math.ceil((tc + 1200.0) / 20.0) * 20.0
    # Restart just below the base so the upper band is never evaluated again.
    second = m.dop853(lambda t, y: f(t + tc, y), yc, t_end - tc)
    ref = second.y[:, -1]
    # Smooth control: the same orbit with a one-band table (no boundary at all).
    smooth_cfg = m.Config(
        drag=m.Drag(cd=2.2, area_m2=600.0, table=m.ONE_BAND_250, below="extrapolate")
    )
    fs = m.rhs(smooth_cfg)
    ref_s = m.dop853(fs, y0, t_end).y[:, -1]
    rows = []
    for dt in (20.0, 10.0, 5.0, 2.5, 1.25):
        n = round(t_end / dt)
        y, ys = y0.copy(), y0.copy()
        for i in range(n):
            y = m.rk4_step(f, i * dt, y, dt)
            ys = m.rk4_step(fs, i * dt, ys, dt)
        rows.append(
            {
                "dt": dt,
                "pos_err_m": float(np.linalg.norm(y[:3] - ref[:3])),
                "pos_err_smooth_control_m": float(np.linalg.norm(ys[:3] - ref_s[:3])),
            }
        )
    for a, b in itertools.pairwise(rows):
        for key in ("pos_err_m", "pos_err_smooth_control_m"):
            ratio = a[key] / b[key]
            b[key.replace("err", "ratio")] = ratio
            b[key.replace("pos_err", "apparent_order")] = math.log2(ratio)
    return {
        "configuration": "equatorial circular, start 252 km, Cd 2.2, A 600 m^2, m 850 kg "
        "(B 0.644 kg/m^2, chosen only to reach the boundary quickly), full table vs one-band",
        "crossing_time_s": tc,
        "t_end_s": t_end,
        "relative_value_jump_at_250km": m.TABLE[17].rho0
        / (m.TABLE[16].rho0 * math.exp(-50.0 / m.TABLE[16].scale_km))
        - 1.0,
        "rk4": rows,
    }


def main() -> None:
    out = {
        "table_sha256": m.TABLE_SHA256,
        "boundaries": boundary_records(),
        "edges": edges(),
        "stiffness_dt10": stiffness(),
        "single_crossing_rk4": crossing_experiment(),
    }
    jumps = [abs(b["relative_value_jump"]) for b in out["boundaries"]]
    out["summary"] = {
        "boundaries": len(out["boundaries"]),
        "max_abs_value_jump": max(jumps),
        "max_abs_value_jump_at_km": out["boundaries"][jumps.index(max(jumps))]["boundary_km"],
        "km_route_boundaries_with_upper_band_below_base": [
            b["boundary_km"]
            for b in out["boundaries"]
            if b["km_route_upper_band_below_base_ulps"] > 0
        ],
        "max_km_route_upper_band_below_base_m": max(
            b["km_route_upper_band_below_base_m"] for b in out["boundaries"]
        ),
    }
    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out["summary"], indent=2))
    print(json.dumps(out["single_crossing_rk4"], indent=2))


if __name__ == "__main__":
    main()
