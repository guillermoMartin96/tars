"""M3 T0: geodetic-height test points and algorithm cross-checks (DR-0025 Q-G2-7; FC-4).

Candidate sources of test points, each with its own independence:
  1. Exact known answers: on the equator h = sqrt(x^2 + y^2) - a; on the axis h = |z| - b.
  2. Points constructed by the closed-form forward transformation (geodetic -> Cartesian),
     inverted by the algorithms under test (the forward formula is exact up to round-off and
     shares no code with the inverse).
  3. Published examples: GeographicLib CartConvert(1) manual page, WGS 84, cm resolution
     (https://geographiclib.sourceforge.io/C++/doc/CartConvert.1.html, read 2026-10-18).
  4. GMAT R2026a's own geodetic conversion (measured by t0_gmat.py, case `geodetic_points`).
The algorithms: iterative-to-convergence (the spike's reference), Vermeille (2002) closed
form, and a replica of GMAT's 1e-7 rad stopping rule (diagnostic).

Usage: uv run --no-sync python t0_geodetic.py <out.json>
"""

from __future__ import annotations

import json
import math
import sys

import numpy as np
import t0_model as m

LATS_DEG = [
    -90.0,
    -89.999999,
    -75.0,
    -51.6,
    -30.0,
    -1e-7,
    0.0,
    1e-7,
    15.0,
    33.3,
    45.0,
    51.6,
    60.0,
    80.0,
    89.999999,
    90.0,
]
LONS_DEG = [0.0, 44.4, 135.0, -100.0]
HEIGHTS_M = [
    -10_000.0,
    -100.0,
    0.0,
    1.0,
    25_000.0,
    100_000.0,
    250_000.0,
    900_000.0,
    1_000_000.0,
    2_000_000.0,
]
ALGORITHMS = {
    "iterative": m.geodetic_iterative,
    "vermeille": m.geodetic_vermeille,
    "gmat_replica": m.geodetic_gmat_replica,
}

PUBLISHED = {
    "source": "GeographicLib CartConvert(1) manual, EXAMPLES (WGS 84 default)",
    "forward": {
        "lat_deg": 33.3,
        "lon_deg": 44.4,
        "h_m": 6000.0,
        "xyz_m": [3816209.60, 3737108.55, 3485109.57],
    },
    "reverse": {
        "xyz_m": [30000.0, 30000.0, 0.0],
        "lat_deg": 6.483,
        "lon_deg": 45.0,
        "h_m": -6335709.73,
    },
    "resolution": "xyz and h printed to 0.01 m; the reverse latitude to 0.001 deg",
}


def grid_errors() -> dict:
    stats = {
        name: {"max_abs_h_err_m": 0.0, "max_abs_lat_err_rad": 0.0, "worst": None}
        for name in ALGORITHMS
    }
    count = 0
    for lat_d in LATS_DEG:
        for lon_d in LONS_DEG:
            for h in HEIGHTS_M:
                lat, lon = math.radians(lat_d), math.radians(lon_d)
                r = m.geodetic_to_cartesian(lat, lon, h)
                count += 1
                for name, fn in ALGORITHMS.items():
                    lat_c, h_c = fn(r)
                    eh, el = abs(h_c - h), abs(lat_c - lat)
                    st = stats[name]
                    if eh > st["max_abs_h_err_m"]:
                        st["max_abs_h_err_m"] = eh
                        st["worst"] = {
                            "lat_deg": lat_d,
                            "lon_deg": lon_d,
                            "h_m": h,
                            "h_err_m": h_c - h,
                        }
                    st["max_abs_lat_err_rad"] = max(st["max_abs_lat_err_rad"], el)
    return {"points": count, "by_algorithm": stats}


def exact_answers() -> dict:
    rows = []
    for rho in (m.A_WGS84 - 10_000.0, m.A_WGS84, m.A_WGS84 + 250_000.0, m.A_WGS84 + 2_000_000.0):
        for lon in (0.0, 0.7, 2.0):
            r = np.array([rho * math.cos(lon), rho * math.sin(lon), 0.0])
            expect = rho - m.A_WGS84
            rows.append(
                {
                    "kind": "equator",
                    "point": r.tolist(),
                    "expected_h_m": expect,
                    **{name: fn(r)[1] - expect for name, fn in ALGORITHMS.items()},
                }
            )
    for z in (m.B_WGS84 - 10_000.0, m.B_WGS84, m.B_WGS84 + 250_000.0, -(m.B_WGS84 + 250_000.0)):
        r = np.array([0.0, 0.0, z])
        expect = abs(z) - m.B_WGS84
        res = {}
        for name, fn in ALGORITHMS.items():
            try:
                res[name] = fn(r)[1] - expect
            except (ZeroDivisionError, ValueError) as exc:
                res[name] = f"{type(exc).__name__}: {exc}"
        rows.append({"kind": "axis", "point": r.tolist(), "expected_h_m": expect, **res})
    return {"rows": rows, "b_m": m.B_WGS84}


def published() -> dict:
    fw = PUBLISHED["forward"]
    xyz = m.geodetic_to_cartesian(
        math.radians(fw["lat_deg"]), math.radians(fw["lon_deg"]), fw["h_m"]
    )
    inv = {}
    for name, fn in ALGORITHMS.items():
        lat, h = fn(np.array(fw["xyz_m"]))
        inv[name] = {
            "lat_deg_minus_published": math.degrees(lat) - fw["lat_deg"],
            "h_minus_published_m": h - fw["h_m"],
        }
    rv = PUBLISHED["reverse"]
    rev = {}
    for name, fn in ALGORITHMS.items():
        try:
            lat, h = fn(np.array(rv["xyz_m"]))
            rev[name] = {
                "lat_deg": math.degrees(lat),
                "h_m": h,
                "h_minus_published_m": h - rv["h_m"],
            }
        except (ValueError, ZeroDivisionError) as exc:
            rev[name] = f"{type(exc).__name__}: {exc}"
    return {
        **PUBLISHED,
        "forward_xyz_minus_published_m": (xyz - np.array(fw["xyz_m"])).tolist(),
        "inverse_of_published_xyz": inv,
        "reverse_case": rev,
        "note": "the reverse case lies deep inside the ellipsoid (outside any M3 domain); it "
        "probes algorithm robustness only",
    }


def axisymmetry() -> dict:
    """FC-4: h(Q_z r) = h(r) for rotations about +Z, measured in metres."""
    worst = 0.0
    for lat_d in LATS_DEG:
        for h in HEIGHTS_M:
            r = m.geodetic_to_cartesian(math.radians(lat_d), 0.3, h)
            h0 = m.geodetic_iterative(r)[1]
            for ang in np.linspace(0.0, 2 * math.pi, 13):
                c, s = math.cos(ang), math.sin(ang)
                rq = np.array([c * r[0] - s * r[1], s * r[0] + c * r[1], r[2]])
                worst = max(worst, abs(m.geodetic_iterative(rq)[1] - h0))
    return {"max_abs_h_difference_m": worst}


def main() -> None:
    out = {
        "ellipsoid": {"a_m": m.A_WGS84, "inv_f": m.INV_F_WGS84, "b_m": m.B_WGS84, "e2": m.E2_WGS84},
        "grid": grid_errors(),
        "exact_answers": exact_answers(),
        "published": published(),
        "axisymmetry_fc4": axisymmetry(),
    }
    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({k: out[k] for k in ("grid", "published", "axisymmetry_fc4")}, indent=1))
    for row in out["exact_answers"]["rows"]:
        print(row["kind"], row["expected_h_m"], {k: row[k] for k in ALGORITHMS})


if __name__ == "__main__":
    main()
