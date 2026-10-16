"""DR-0028 / review M3P5-F1: signed verification of the pole-tilt node and inclination formulas.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python dr0028_node_signed_verification.py <out.json>

Exit status 0 only if (a) every exact property and every check of the signed first-order
formulas passes, and (b) every deliberately mutated formula is rejected by at least one check.
Standard library only.

Conventions (DR-0028 Resolution amendments 1 and 2; DR-0024 "Q4 coordinate conventions,
revision 2", r_B = R r_A):
- Rot(u, a) is the active right-hand rotation by angle a about unit axis u (Rodrigues).
- Frame B's axes are frame A's axes rotated by +delta about e = (cos phi, sin phi, 0); B's
  pole is therefore A's pole tilted by +delta. Components transform passively:
  v_B = R v_A with R = Rot(e, -delta). For phi = 0 this is Rx(-delta), as in review 04.
- In each frame, from the unit angular-momentum vector h:
      i     = atan2(hypot(h_x, h_y), h_z)     (well conditioned for all i)
      Omega = atan2(h_x, -h_y)                (undefined when hypot(h_x, h_y) = 0)
- Differences are B minus A; Delta Omega is wrapped to (-pi, pi].

Formulas under test (first order in delta; DR-0028 amendment 2):
      Delta i     ~ -delta cos(Omega - phi)
      Delta Omega ~ +delta cot(i) sin(Omega - phi)

The numerical oracle (`finite`) uses only the rotation matrix and the two element definitions
above. It never evaluates the formulas under test.
"""

import json
import math
import sys

EPS = sys.float_info.epsilon


# ---------------------------------------------------------------- oracle (finite rotation)
def rot(axis, a):
    """Active right-hand rotation matrix by angle a about a unit axis (Rodrigues)."""
    x, y, z = axis
    c, s = math.cos(a), math.sin(a)
    t = 1.0 - c
    return [
        [t * x * x + c, t * x * y - s * z, t * x * z + s * y],
        [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
        [t * x * z - s * y, t * y * z + s * x, t * z * z + c],
    ]


def apply(m, v):
    return [m[r][0] * v[0] + m[r][1] * v[1] + m[r][2] * v[2] for r in range(3)]


def transpose(m):
    return [[m[c][r] for c in range(3)] for r in range(3)]


def tilt_matrix(phi, delta):
    """Passive component transform A -> B for B's axes = A's axes rotated by +delta about e."""
    return rot((math.cos(phi), math.sin(phi), 0.0), -delta)


def h_from_elements(inc, node):
    return [math.sin(inc) * math.sin(node), -math.sin(inc) * math.cos(node), math.cos(inc)]


def elements(h):
    """(i, Omega) from a unit angular-momentum vector; Omega is None for an equatorial orbit."""
    rho = math.hypot(h[0], h[1])
    inc = math.atan2(rho, h[2])
    return inc, (math.atan2(h[0], -h[1]) if rho > 0.0 else None)


def wrap(a):
    return a - 2.0 * math.pi * math.floor((a + math.pi) / (2.0 * math.pi))


def finite(inc, node, phi, delta):
    """Exact (finite-rotation) Delta i and Delta Omega, B minus A. Delta Omega None if undefined."""
    h_b = apply(tilt_matrix(phi, delta), h_from_elements(inc, node))
    i_b, node_b = elements(h_b)
    i_a, node_a = elements(h_from_elements(inc, node))
    d_node = None if node_a is None or node_b is None else wrap(node_b - node_a)
    return i_b - i_a, d_node


# ------------------------------------------------------- formulas under test and mutants
def formulas_amendment2(inc, node, phi, delta):
    return -delta * math.cos(node - phi), delta / math.tan(inc) * math.sin(node - phi)


MUTANTS = {
    "amendment1_original_both_signs_reversed": lambda i, n, p, d: (
        d * math.cos(n - p),
        -d / math.tan(i) * math.sin(n - p),
    ),
    "delta_i_sign_reversed": lambda i, n, p, d: (
        d * math.cos(n - p),
        d / math.tan(i) * math.sin(n - p),
    ),
    "delta_node_sign_reversed": lambda i, n, p, d: (
        -d * math.cos(n - p),
        -d / math.tan(i) * math.sin(n - p),
    ),
    "cos_sin_swapped": lambda i, n, p, d: (
        -d * math.sin(n - p),
        d / math.tan(i) * math.cos(n - p),
    ),
}


# ----------------------------------------------------------------------- tolerances
def noise(inc):
    """Rounding-noise bound (rad) for a finite-rotation difference at inclination inc.

    Each component of h_A and of R h_A carries at most ~16 eps absolute error (unit-magnitude
    entries; a handful of roundings in the trigonometric construction, Rodrigues entries and a
    3-term dot product). atan2 of the components amplifies that by at most 1/hypot(h_x, h_y)
    = 1/sin i for Omega and by ~1 for i. A difference of two angles doubles it, giving
    32 eps / sin i; a further factor 2 margin gives 64 eps / sin i.
    """
    return 64.0 * EPS / max(math.sin(inc), EPS)


SIGNIFICANT = 1.0e3  # a quantity is used for order/sign checks only if >= 1e3 x noise:
#                      noise then shifts an observed order by at most log2(1 + 2e-3) < 0.003.
P_MIN = 1.5  # midpoint between order 1 (a wrong first-order term leaves an O(delta) error)
#              and order 2 (the smallest order of the error when the first-order term is right).


# ------------------------------------------------------------------------ the grid
INCLINED = (30.0, 51.6, 120.0)
NEAR_POLAR = (89.0, 90.0, 91.0)
NEAR_EQUATORIAL = (2.0, 5.0, 175.0, 178.0)
NODES = (0.0, 37.0, 90.0, 145.0, 200.0, 300.0)
TILT_AZIMUTHS = (0.0, 60.0, 135.0, 210.0, 300.0)
HALVINGS = 5  # delta_k = sign * s * 2^-k, k = 0..4


def step_scale(inc):
    """s = 1e-2 sin i (rad). The node expansion parameter is delta/sin i (the node is singular
    when |delta| ~ sin i); this keeps |delta|/sin i <= 1e-2, well inside the first-order regime.
    """
    return 1.0e-2 * math.sin(inc)


def check_formulas(formula):
    """Run the signed order and sign checks for one formula pair. Returns (failures, stats)."""
    failures, orders_i, orders_node, sign_checks = [], [], [], 0
    for inc_deg in INCLINED + NEAR_POLAR + NEAR_EQUATORIAL:
        inc = math.radians(inc_deg)
        tol = SIGNIFICANT * noise(inc)
        for node_deg in NODES:
            for phi_deg in TILT_AZIMUTHS:
                node, phi = math.radians(node_deg), math.radians(phi_deg)
                for sign in (1.0, -1.0):
                    deltas = [sign * step_scale(inc) * 2.0**-k for k in range(HALVINGS)]
                    err_i, err_node = [], []
                    for d in deltas:
                        num_i, num_node = finite(inc, node, phi, d)
                        lin_i, lin_node = formula(inc, node, phi, d)
                        err_i.append(abs(num_i - lin_i))
                        err_node.append(abs(num_node - lin_node))
                    tag = f"i={inc_deg} node={node_deg} phi={phi_deg} sign={sign:+.0f}"
                    for name, errs, store in (
                        ("delta_i", err_i, orders_i),
                        ("delta_node", err_node, orders_node),
                    ):
                        if errs[-2] >= tol and errs[-1] >= tol:
                            p = math.log2(errs[-2] / errs[-1])
                            store.append(p)
                            if p < P_MIN:
                                failures.append(f"order {name} p={p:.3f} {tag}")
                    # Sign check at the smallest step, with the finite result as the reference.
                    d = deltas[-1]
                    num_i, num_node = finite(inc, node, phi, d)
                    lin_i, lin_node = formula(inc, node, phi, d)
                    for name, num, lin in (
                        ("delta_i", num_i, lin_i),
                        ("delta_node", num_node, lin_node),
                    ):
                        if abs(num) >= tol and abs(lin) >= tol:
                            sign_checks += 1
                            if (num > 0.0) != (lin > 0.0):
                                failures.append(f"sign {name} num={num:.3e} lin={lin:.3e} {tag}")
    stats = {
        "order_samples_delta_i": len(orders_i),
        "order_samples_delta_node": len(orders_node),
        "observed_order_delta_i_min_max": [min(orders_i), max(orders_i)] if orders_i else None,
        "observed_order_delta_node_min_max": (
            [min(orders_node), max(orders_node)] if orders_node else None
        ),
        "sign_checks": sign_checks,
    }
    return failures, stats


def exact_properties():
    """Exact (finite-delta) properties, independent of any first-order formula."""
    failures, report = [], {}

    # E1. R is a proper rotation; R = Rx(-delta) for phi = 0; B's pole is A's pole rotated by
    # +delta about e (so "positive tilt" is the active right-hand sense).
    worst = 0.0
    for phi_deg in TILT_AZIMUTHS:
        for delta_deg in (-20.0, -0.15, 0.15, 20.0):
            phi, delta = math.radians(phi_deg), math.radians(delta_deg)
            r = tilt_matrix(phi, delta)
            rrt = [[sum(r[a][k] * r[b][k] for k in range(3)) for b in range(3)] for a in range(3)]
            det = (
                r[0][0] * (r[1][1] * r[2][2] - r[1][2] * r[2][1])
                - r[0][1] * (r[1][0] * r[2][2] - r[1][2] * r[2][0])
                + r[0][2] * (r[1][0] * r[2][1] - r[1][1] * r[2][0])
            )
            pole_b = apply(transpose(r), [0.0, 0.0, 1.0])
            pole_expected = apply(rot((math.cos(phi), math.sin(phi), 0.0), delta), [0, 0, 1.0])
            dev = max(
                max(abs(rrt[a][b] - (a == b)) for a in range(3) for b in range(3)),
                abs(det - 1.0),
                max(abs(x - y) for x, y in zip(pole_b, pole_expected, strict=True)),
            )
            if phi_deg == 0.0:
                c, s = math.cos(-delta), math.sin(-delta)
                rx = [[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]]
                dev = max(dev, max(abs(r[a][b] - rx[a][b]) for a in range(3) for b in range(3)))
            worst = max(worst, dev)
    report["E1_rotation_convention_max_deviation"] = worst
    if worst > 16.0 * EPS:  # entries are O(1); a few roundings each
        failures.append(f"E1 rotation convention deviation {worst:.3e}")

    # E2. Tilt about the line of nodes (phi = Omega): the node is fixed and Delta i = -delta
    # exactly (the rotation axis lies in both equators and in the orbit plane).
    worst_i = worst_node = 0.0
    for inc_deg in (30.0, 51.6, 90.0, 120.0):
        for node_deg in NODES:
            for delta_deg in (-20.0, -5.0, -0.15, 0.15, 5.0, 20.0):
                inc, node, delta = (math.radians(x) for x in (inc_deg, node_deg, delta_deg))
                d_i, d_node = finite(inc, node, node, delta)
                worst_i = max(worst_i, abs(d_i - (-delta)) / noise(inc))
                worst_node = max(worst_node, abs(d_node) / noise(inc))
    report["E2_line_of_nodes_max_dev_delta_i_noise_units"] = worst_i
    report["E2_line_of_nodes_max_abs_delta_node_noise_units"] = worst_node
    if worst_i > 1.0 or worst_node > 1.0:
        failures.append(f"E2 line-of-nodes tilt: {worst_i:.3e}, {worst_node:.3e} noise units")

    # E3. Tilt axis 90 deg behind the node (phi = Omega - 90 deg). Exact closed form, derived
    # by hand for Omega = 90 deg, phi = 0 and extended by symmetry about z:
    #     h_B = (sin i, sin(delta) cos i, cos(delta) cos i)
    #     Delta Omega = atan(sin(delta) cot i),   cos i_B = cos(delta) cos i.
    worst = 0.0
    for inc_deg in (2.0, 30.0, 51.6, 89.0, 120.0, 178.0):
        for node_deg in NODES:
            for delta_deg in (-1.0, -0.15, 0.15, 1.0):
                inc, node, delta = (math.radians(x) for x in (inc_deg, node_deg, delta_deg))
                d_i, d_node = finite(inc, node, node - math.pi / 2.0, delta)
                exp_node = math.atan(math.sin(delta) / math.tan(inc))
                exp_i = math.acos(math.cos(delta) * math.cos(inc)) - inc
                worst = max(
                    worst, abs(d_node - exp_node) / noise(inc), abs(d_i - exp_i) / noise(inc)
                )
    report["E3_closed_form_max_dev_in_noise_units"] = worst
    if worst > 1.0:
        failures.append(f"E3 closed form deviation {worst:.3e} noise units")

    # E4. |Delta i| <= |delta| for any finite tilt (triangle inequality on the sphere).
    ratio = 0.0
    for inc_deg in range(0, 181, 5):
        for node_deg in NODES:
            for phi_deg in TILT_AZIMUTHS:
                for delta_deg in (-30.0, -5.0, -0.15, 0.15, 5.0, 30.0):
                    inc, node, phi, delta = (
                        math.radians(x) for x in (inc_deg, node_deg, phi_deg, delta_deg)
                    )
                    d_i, _ = finite(inc, node, phi, delta)
                    ratio = max(ratio, (abs(d_i) - abs(delta)) / (64.0 * EPS))
    # Inclinations come from atan2(hypot, h_z), whose error is ~1x the component error, so the
    # noise of Delta i is <= 64 eps (see noise()); the excess is reported in those units.
    report["E4_max_excess_of_abs_delta_i_over_abs_delta_in_64eps_units"] = ratio
    if ratio > 1.0:
        failures.append(f"E4 inclination bound exceeded: {ratio:.3e} x 64 eps")

    # E5. Singularities: an equatorial orbit has no node; for i < |delta| the node can jump.
    _, node_eq = elements(h_from_elements(0.0, 0.0))
    report["E5_equatorial_node_undefined"] = node_eq is None
    if node_eq is not None:
        failures.append("E5 equatorial node not reported as undefined")
    jump = 0.0
    for k in range(360):
        _, d_node = finite(math.radians(0.1), 0.0, math.radians(k), math.radians(0.15))
        if d_node is not None:
            jump = max(jump, abs(d_node))
    report["E5_max_node_jump_deg_i_0p1_delta_0p15"] = math.degrees(jump)

    # E6. Review-04 example (preserved): h_A = (sin 30, 0, cos 30), R = Rx(-0.15 deg).
    d_i, d_node = finite(math.radians(30.0), math.radians(90.0), 0.0, math.radians(0.15))
    lin_i, lin_node = formulas_amendment2(
        math.radians(30.0), math.radians(90.0), 0.0, math.radians(0.15)
    )
    report["E6_review04_node_b_deg"] = 90.0 + math.degrees(d_node)
    report["E6_review04_delta_node_deg"] = math.degrees(d_node)
    report["E6_review04_first_order_delta_node_deg"] = math.degrees(lin_node)
    report["E6_review04_delta_i_deg"] = math.degrees(d_i)
    report["E6_review04_first_order_delta_i_deg"] = math.degrees(lin_i)
    # The committed value 90.2598055437 has 10 decimals: rounding <= 5e-11 deg.
    if abs(report["E6_review04_node_b_deg"] - 90.2598055437) > 5.0e-11:
        failures.append("E6 review-04 example not reproduced")
    if not (d_node > 0.0 and lin_node > 0.0):
        failures.append("E6 review-04 example sign disagreement")
    return failures, report


def rounded(x):
    if isinstance(x, float):
        return float(f"{x:.12g}")
    if isinstance(x, list):
        return [rounded(v) for v in x]
    if isinstance(x, dict):
        return {k: rounded(v) for k, v in x.items()}
    return x


def main(out_path):
    exact_failures, exact_report = exact_properties()
    under_test_failures, under_test_stats = check_formulas(formulas_amendment2)
    mutants = {}
    for name, formula in MUTANTS.items():
        failures, _ = check_formulas(formula)
        mutants[name] = {"failing_checks": len(failures), "rejected": bool(failures)}
    ok = (
        not exact_failures
        and not under_test_failures
        and all(m["rejected"] for m in mutants.values())
    )
    result = {
        "verdict": "PASS" if ok else "FAIL",
        "grid": {
            "inclinations_deg": {
                "inclined": INCLINED,
                "near_polar": NEAR_POLAR,
                "near_equatorial": NEAR_EQUATORIAL,
            },
            "node_longitudes_deg": NODES,
            "tilt_azimuths_deg": TILT_AZIMUTHS,
            "tilt_signs": [1, -1],
            "steps": "delta_k = sign * 1e-2 sin(i) * 2^-k rad, k = 0..4",
        },
        "tolerances": {
            "noise_rad": "64 eps / sin i",
            "significance_factor": SIGNIFICANT,
            "order_threshold": P_MIN,
        },
        "exact_properties": exact_report,
        "exact_property_failures": exact_failures,
        "formulas_under_test": {
            "delta_i": "-delta cos(Omega - phi)",
            "delta_node": "+delta cot(i) sin(Omega - phi)",
            "stats": under_test_stats,
            "failures": under_test_failures,
        },
        "mutants": mutants,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(rounded(result), fh, indent=1)
        fh.write("\n")
    print(json.dumps(rounded(result), indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
