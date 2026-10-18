"""DR-0028 / review M3P4-F1: sensitivity of inclination and ascending node to a pole tilt.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python dr0028_node_sensitivity.py <out.json>

Pure geometry, standard library only. Frame A has pole z_A. Frame B is A rotated by a
small angle delta about an equatorial axis e = (cos phi, sin phi, 0); components transform
passively, v_B = R v_A, with R the rotation by -delta about e (review 04 used R = Rx(-delta)).
For an orbit with unit angular-momentum vector h, each frame gives
    inclination i = acos(h_z),
    node longitude Omega = atan2(h_x, -h_y), measured from that frame's own x axis,
    node point N = z x h / |z x h|, a unit vector on the orbit circle.
Three quantities are compared between A and B:
    |Delta i|                      (inclination change),
    |Delta Omega|                  (node-longitude change, frame-carried x axes),
    angle(N_A, N_B)                (node-point displacement along the orbit).
The first-order estimates checked are delta*|cos(Omega - phi)|, delta*|cot i|*|sin(Omega - phi)|
and delta*|sin(Omega - phi)|/sin i. Only |Delta i| <= delta is a geometric bound; the other two
are approximations for delta << i (and delta << 180 deg - i).
"""

import json
import math
import sys


def rot(axis, angle):
    """Rotation matrix about a unit axis (right-hand rule)."""
    x, y, z = axis
    c, s, t = math.cos(angle), math.sin(angle), 1.0 - math.cos(angle)
    return [
        [t * x * x + c, t * x * y - s * z, t * x * z + s * y],
        [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
        [t * x * z - s * y, t * y * z + s * x, t * z * z + c],
    ]


def apply(m, v):
    return [sum(m[r][k] * v[k] for k in range(3)) for r in range(3)]


def unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v]


def angle(a, b):
    """Angle between unit vectors, robust near 0 and pi."""
    cross = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    return math.atan2(
        math.sqrt(sum(c * c for c in cross)), sum(x * y for x, y in zip(a, b, strict=True))
    )


def elements(h):
    """Inclination, node longitude and node point (all in the frame of h's components).

    The node is undefined for an equatorial orbit (|z x h| = 0); None is returned then.
    """
    inc = math.acos(max(-1.0, min(1.0, h[2])))
    if math.hypot(h[0], h[1]) < 1e-15:
        return inc, None, None
    node = math.atan2(h[0], -h[1])
    return inc, node, unit([-h[1], h[0], 0.0])


def compare(inc, node, phi, delta):
    h_a = [math.sin(inc) * math.sin(node), -math.sin(inc) * math.cos(node), math.cos(inc)]
    r = rot((math.cos(phi), math.sin(phi), 0.0), -delta)
    h_b = apply(r, h_a)
    i_a, o_a, n_a = elements(h_a)
    i_b, o_b, n_b = elements(h_b)
    if o_a is None or o_b is None:
        return {"d_inc": abs(i_b - i_a), "node_undefined": True}
    # Node points compared in one frame: map B's node point back to A components.
    n_b_in_a = apply([list(col) for col in zip(*r, strict=True)], n_b)
    d_node = (o_b - o_a + math.pi) % (2.0 * math.pi) - math.pi
    return {
        "d_inc": abs(i_b - i_a),
        "d_node_longitude": abs(d_node),
        "node_point_shift": angle(n_a, n_b_in_a),
        "node_longitude_b_deg": math.degrees(o_b) % 360.0,
    }


def sig(x):
    return float(f"{x:.12g}")


def main(out_path):
    delta = math.radians(0.15)

    # Review 04 counterexample: h = (sin 30, 0, cos 30), R = Rx(-0.15 deg), node at 90 deg.
    ex = compare(math.radians(30.0), math.radians(90.0), 0.0, delta)
    example = {
        "assumptions": "h_A = (sin 30 deg, 0, cos 30 deg); R = Rx(-0.15 deg) (phi = 0); "
        "node longitudes from each frame's own x axis (x_B = x_A here)",
        "node_longitude_a_deg": 90.0,
        "node_longitude_b_deg": sig(ex["node_longitude_b_deg"]),
        "d_node_longitude_deg": sig(math.degrees(ex["d_node_longitude"])),
        "first_order_delta_cot_i_deg": sig(0.15 / math.tan(math.radians(30.0))),
        "delta_over_sin_i_deg": sig(0.15 / math.sin(math.radians(30.0))),
        "node_point_shift_deg": sig(math.degrees(ex["node_point_shift"])),
        "d_inc_deg": sig(math.degrees(ex["d_inc"])),
    }

    # Sweep: tilt-axis azimuth relative to the node, for several inclinations.
    sweep = []
    max_inc_ratio = 0.0
    for inc_deg in (1.0, 5.0, 10.0, 30.0, 51.6, 90.0, 120.0, 170.0):
        inc = math.radians(inc_deg)
        worst = {"d_inc": 0.0, "d_node_longitude": 0.0, "node_point_shift": 0.0}
        for k in range(360):
            res = compare(inc, math.radians(40.0), math.radians(40.0 + k), delta)
            for key in worst:
                worst[key] = max(worst[key], res[key])
        max_inc_ratio = max(max_inc_ratio, worst["d_inc"] / delta)
        sweep.append(
            {
                "inclination_deg": inc_deg,
                "max_d_inc_over_delta": sig(worst["d_inc"] / delta),
                "max_d_node_longitude_over_delta": sig(worst["d_node_longitude"] / delta),
                "abs_cot_i": sig(abs(1.0 / math.tan(inc))),
                "max_node_point_shift_over_delta": sig(worst["node_point_shift"] / delta),
                "one_over_sin_i": sig(1.0 / math.sin(inc)),
            }
        )

    # Near-equatorial: the node is ill-conditioned when i is comparable to delta.
    near_eq = []
    for inc_deg in (0.3, 0.15, 0.1):
        worst, undefined = 0.0, 0
        for k in range(360):
            res = compare(math.radians(inc_deg), 0.0, math.radians(k), delta)
            if res.get("node_undefined"):
                undefined += 1
            else:
                worst = max(worst, res["d_node_longitude"])
        near_eq.append(
            {
                "inclination_deg": inc_deg,
                "max_d_node_longitude_deg": sig(math.degrees(worst)),
                "tilt_azimuths_with_undefined_node": undefined,
            }
        )

    # Inclination bound on random-free grid of orientations (geometric, not first order).
    big = math.radians(5.0)
    max_ratio_big = 0.0
    for inc_deg in range(0, 181, 5):
        for k in range(0, 360, 10):
            res = compare(math.radians(inc_deg), 0.3, math.radians(k), big)
            max_ratio_big = max(max_ratio_big, res["d_inc"] / big)

    result = {
        "pole_tilt_deg": 0.15,
        "review04_example": example,
        "sweep_delta_0p15_deg": sweep,
        "max_d_inc_over_delta_all_sweeps": sig(max_inc_ratio),
        "max_d_inc_over_delta_tilt_5_deg_grid": sig(max_ratio_big),
        "near_equatorial_delta_0p15_deg": near_eq,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(result, fh, indent=1)
        fh.write("\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
