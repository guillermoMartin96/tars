"""M3 T0: frame-convention checks under DR-0028 J-ax-1 (DR-0024 "Q4 coordinate conventions,
revision 2", FC-2, FC-3, FC-5, FC-6, FC-8), at spike level.

The checks are on the spike model only; they establish the conventions T1/T2 must test in
production code and give their expected values. FC-1 (the identity I <-> EA) has no code to
test in J-ax-1; FC-4 is in t0_geodetic.py; FC-7 (one pinned axis) is a configuration-identity
test that needs the production physics configuration (T1/T2).

Usage: uv run --no-sync python t0_frames.py <out.json>
"""

from __future__ import annotations

import json
import math
import sys

import numpy as np
import t0_model as m


def rot_z(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def main() -> None:
    a = m.A_WGS84
    out = {}
    # FC-2 (a) omega = 0 -> v_rel = v exactly; (b) a point at rest off the axis sees -omega x r.
    r, v = m.circular_state(250_000.0, 51.6)
    out["fc2a_vrel_equals_v_when_omega_zero"] = bool(np.array_equal(v - m.air_velocity(r, 0.0), v))
    rest = np.array([a, 0.0, 0.0])
    vr = np.zeros(3) - m.air_velocity(rest, m.OMEGA_E)
    out["fc2b_vrel_at_rest_mps"] = vr.tolist()
    out["fc2b_nonzero"] = bool(np.linalg.norm(vr) > 0.0)
    # FC-5 signs: air at r = a X is +omega a Y (eastward); prograde/retrograde equatorial |v_rel|.
    out["fc5_air_velocity_at_aX_mps"] = m.air_velocity(rest, m.OMEGA_E).tolist()
    out["fc5_expected_mps"] = [0.0, m.OMEGA_E * a, 0.0]
    for name, inc in (("prograde", 0.0), ("retrograde", 180.0)):
        r_e, v_e = m.circular_state(250_000.0, inc)
        rel = float(np.linalg.norm(v_e - m.air_velocity(r_e, m.OMEGA_E)))
        expect = float(np.linalg.norm(v_e)) + (
            -1.0 if name == "prograde" else 1.0
        ) * m.OMEGA_E * float(np.linalg.norm(r_e))
        out[f"fc5_{name}_vrel_minus_expected_mps"] = rel - expect
    # FC-3 axisymmetry of J2: a(Qz r) = Qz a(r).
    worst = 0.0
    for lat in (-89.0, -45.0, 0.0, 30.0, 51.6, 89.0):
        r_t = m.geodetic_to_cartesian(math.radians(lat), 0.4, 250_000.0)
        base = m.j2_accel(r_t, m.J2_FROM_C20, m.MU, a)
        for ang in np.linspace(0.0, 2 * math.pi, 9):
            q = rot_z(ang)
            diff = m.j2_accel(q @ r_t, m.J2_FROM_C20, m.MU, a) - q @ base
            worst = max(worst, float(np.linalg.norm(diff) / np.linalg.norm(base)))
    out["fc3_j2_axisymmetry_max_rel_diff"] = worst
    # FC-6 direction: equator inward along -r, pole outward along +Z.
    eq = m.j2_accel(np.array([a + 250e3, 0.0, 0.0]), m.J2_FROM_C20, m.MU, a)
    po = m.j2_accel(np.array([0.0, 0.0, a + 250e3]), m.J2_FROM_C20, m.MU, a)
    out["fc6_equator_accel"] = eq.tolist()
    out["fc6_pole_accel"] = po.tolist()
    out["fc6_equator_inward"] = bool(eq[0] < 0.0 and eq[1] == 0.0 and eq[2] == 0.0)
    out["fc6_pole_outward"] = bool(po[2] > 0.0 and po[0] == 0.0 and po[1] == 0.0)
    # FC-8 inclined orbit: v_rel not parallel to v; the angle and cross-track part along the orbit.
    rows = []
    for u_deg in (0.0, 45.0, 90.0):
        u = math.radians(u_deg)
        i = math.radians(51.6)
        rn = a + 250e3
        vc = math.sqrt(m.MU / rn)
        rr = rn * np.array([math.cos(u), math.sin(u) * math.cos(i), math.sin(u) * math.sin(i)])
        vv = vc * np.array([-math.sin(u), math.cos(u) * math.cos(i), math.cos(u) * math.sin(i)])
        rel = vv - m.air_velocity(rr, m.OMEGA_E)
        hhat = np.cross(rr, vv) / np.linalg.norm(np.cross(rr, vv))
        rows.append(
            {
                "arg_latitude_deg": u_deg,
                "angle_v_vrel_deg": math.degrees(
                    math.acos(float(rel @ vv) / (np.linalg.norm(rel) * np.linalg.norm(vv)))
                ),
                "cross_track_component_mps": float(rel @ hhat),
            }
        )
    out["fc8_inclined_51.6"] = rows
    # omega x r lies along v only at the highest-latitude point (u = 90 deg): FC-8 must test
    # away from it, and a test at u = 90 deg cannot detect a v-for-v_rel substitution.
    out["fc8_not_parallel_away_from_vertex"] = all(r_["angle_v_vrel_deg"] > 1.0 for r_ in rows[:2])
    out["fc8_parallel_at_vertex"] = rows[2]["angle_v_vrel_deg"] < 1e-6
    # Size of the co-rotation term relative to v (DR-0024 §10: |omega x r| < |v| precondition).
    out["omega_r_over_v_at_250km"] = m.OMEGA_E * (a + 250e3) / math.sqrt(m.MU / (a + 250e3))
    with open(sys.argv[1], "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
