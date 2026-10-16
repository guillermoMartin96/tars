"""DR-0028 / reviews M3P5-F1, M3P6-F1..F3: signed verification of the pole-tilt node and
inclination formulas, the exact line-of-nodes identity, the node discontinuity and angle wrapping.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python dr0028_node_signed_verification.py <out.json>

Exit status 0 only if (a) every exact property, wrapping test and check of the signed
first-order formulas passes, and (b) every deliberate mutant (of a formula, of the wrapping
function, of the exact line-of-nodes claim, of the oracle's node discontinuity, or of the
discontinuity assertion itself) is rejected by at least one check. Standard library only.

Revision history: first version at commit bcb7f9b (DR-0028 amendment 2). Revised for
review 06 (DR-0028 amendment 3): wrap() now returns (-pi, pi] as documented (M3P6-F3); E2 tests
the full line-of-nodes identity including equator crossings and endpoints (M3P6-F1); E5 asserts
the node discontinuity with a coverage guard (M3P6-F2). The first-order checks are unchanged.
Revised for review 07 (DR-0028 amendment 4, M3P7-F1): wrap() accepts finite angles only and
raises ValueError for NaN and +/-inf; all finite-input behaviour is unchanged.

Conventions (DR-0028 Resolution amendments 1 and 2; DR-0024 "Q4 coordinate conventions,
revision 2", r_B = R r_A):
- Rot(u, a) is the active right-hand rotation by angle a about unit axis u (Rodrigues).
- Frame B's axes are frame A's axes rotated by +delta about e = (cos phi, sin phi, 0); B's
  pole is therefore A's pole tilted by +delta. Components transform passively:
  v_B = R v_A with R = Rot(e, -delta). For phi = 0 this is Rx(-delta), as in review 04.
- In each frame, from the unit angular-momentum vector h:
      i     = atan2(hypot(h_x, h_y), h_z)     (well conditioned for all i)
      Omega = atan2(h_x, -h_y)                (undefined when hypot(h_x, h_y) = 0)
- Differences are B minus A; Delta Omega is wrapped to (-pi, pi]: wrap(+pi) = wrap(-pi) = +pi.

Formulas under test (first order in delta; DR-0028 amendment 2):
      Delta i     ~ -delta cos(Omega - phi)
      Delta Omega ~ +delta cot(i) sin(Omega - phi)

The numerical oracle (`finite`) uses only the rotation matrix and the two element definitions
above. It never evaluates the formulas under test.
"""

import json
import math
import sys
from fractions import Fraction

EPS = sys.float_info.epsilon
PI = math.pi
TAU = 2.0 * math.pi  # exact doubling of the float pi


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


NONFINITE_MESSAGE = "wrap: non-finite angle"


def wrap(a):
    """Reduce a finite float angle to (-PI, PI], exactly (PI and TAU = 2 PI the float constants).

    Domain: finite floats only. NaN, +inf and -inf raise ValueError(NONFINITE_MESSAGE)
    (DR-0028 amendment 4, M3P7-F1); no guarantee below applies to them.

    For finite a: math.fmod is exact in IEEE arithmetic, giving r with |r| < TAU and
    r = a - m TAU exactly. The single correction r -/+ TAU is applied only when |r| >= TAU/2,
    so it is exact by Sterbenz's lemma. The result is therefore the unique float in (-PI, PI]
    that differs from a by an exact integer multiple of TAU; in particular
    wrap(PI) = wrap(-PI) = +PI.
    """
    if not math.isfinite(a):
        raise ValueError(f"{NONFINITE_MESSAGE}: {a!r}")
    r = math.fmod(a, TAU)
    if r > PI:
        r -= TAU
    elif r <= -PI:
        r += TAU
    return r


def wrap_without_nonfinite_guard(a):
    """The f999626 implementation (no domain guard), kept only as a mutant (M3P7-F1)."""
    r = math.fmod(a, TAU)
    if r > PI:
        r -= TAU
    elif r <= -PI:
        r += TAU
    return r


def wrap_previous(a):
    """The bcb7f9b implementation, kept only as a mutant (M3P6-F3): it returns [-pi, pi)."""
    return a - 2.0 * math.pi * math.floor((a + math.pi) / (2.0 * math.pi))


def finite(inc, node, phi, delta, wrap_fn=wrap):
    """Exact (finite-rotation) Delta i and Delta Omega, B minus A. Delta Omega None if undefined."""
    h_b = apply(tilt_matrix(phi, delta), h_from_elements(inc, node))
    i_b, node_b = elements(h_b)
    i_a, node_a = elements(h_from_elements(inc, node))
    d_node = None if node_a is None or node_b is None else wrap_fn(node_b - node_a)
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


# ------------------------------------------- exact line-of-nodes identity (M3P6-F1)
def line_of_nodes_exact(inc, delta):
    """Exact (Delta i, Delta Omega) for a tilt about the line of nodes (phi = Omega).

    With j = i - delta, h_B = (sin j sin Omega, -sin j cos Omega, cos j) (DR-0028 amendment 3),
    and with i in [0, pi] from atan2(hypot, h_z):
      0 < j < pi        : i_B = j,          Delta i = -delta,          Delta Omega = 0
      -pi < j < 0       : i_B = -j,         Delta i = delta - 2 i,     Delta Omega = +pi
      pi < j < 2 pi     : i_B = 2 pi - j,   Delta i = 2 pi - 2 i + delta, Delta Omega = +pi
      j = 0 or j = pi   : equatorial in B; node undefined (returned as None)
    Valid for 0 < i < pi (A's node defined) and -pi < j < 2 pi.
    """
    j = inc - delta
    if 0.0 < j < PI:
        return -delta, 0.0
    if -PI < j < 0.0:
        return delta - 2.0 * inc, PI
    if PI < j < TAU:
        return TAU - 2.0 * inc + delta, PI
    return None


def line_of_nodes_unrestricted(inc, delta):
    """The amendment-2 claim without its domain (M3P6-F1 original defect), kept as a mutant."""
    return -delta, 0.0


def circ(a, b, wrap_fn=wrap):
    """Circular distance |a - b| modulo 2 pi."""
    return abs(wrap_fn(a - b))


def pair_noise(inc_a, inc_b):
    """noise() with the larger 1/sin amplification of the two frames (same derivation)."""
    return 64.0 * EPS / max(min(math.sin(inc_a), math.sin(inc_b)), EPS)


LOW_INC = (0.1, 2.0, 10.0, 30.0)  # degrees; bottom crossings use delta > i (positive tilt)
HIGH_INC = (179.9, 178.0, 170.0, 150.0)  # top crossings use delta < i - 180 (negative tilt)
CROSS_BY = (0.05, 3.0, 25.0)  # degrees beyond the equator
MIN_CROSSINGS_PER_SIGN = len(LOW_INC) * len(CROSS_BY) * len(NODES)  # every constructed case


# ---------------------------------------------------------------- wrapping (M3P6-F3)
def wrap_reference(a):
    """Exact rational reduction of the float a into (-PI, PI] modulo TAU (float constants)."""
    big_a, big_pi, big_tau = Fraction(a), Fraction(PI), Fraction(TAU)
    m = -((-(big_a - big_pi)) // big_tau)  # ceil((a - PI) / TAU)
    return big_a - m * big_tau


def wrap_tests(wrap_fn):
    """Return (failures, report) for the wrapping convention (-PI, PI]."""
    failures, report = [], {}
    up, down = math.nextafter(PI, math.inf), math.nextafter(PI, -math.inf)
    inputs = [PI, -PI, 0.0, -0.0, up, down, -up, -down, TAU, -TAU, 1.0e6, -1.0e6]
    inputs += [PI + k * TAU for k in range(1, 6)] + [-PI - k * TAU for k in range(1, 6)]
    for a in inputs:
        got = wrap_fn(a)
        ref = wrap_reference(a)
        if not -PI < got <= PI:
            failures.append(f"wrap({a!r}) = {got!r} outside (-pi, pi]")
        if Fraction(got) != ref:
            failures.append(f"wrap({a!r}) = {got!r}, exact reduction {float(ref)!r}")
        if wrap_fn(a) != got:
            failures.append(f"wrap({a!r}) not deterministic")
    # The two endpoints, explicitly.
    for a in (PI, -PI):
        if wrap_fn(a) != PI:
            failures.append(f"wrap endpoint ({a!r}) = {wrap_fn(a)!r}, expected +pi")
    # Equivalent angles: b = a + k TAU, used only when the float sum is exact.
    equivalent = 0
    for a in (PI, -PI, 1.0, -2.5, 3.0):
        for k in (-3, -2, -1, 1, 2, 3):
            b = a + k * TAU
            if Fraction(b) - Fraction(a) == k * Fraction(TAU):
                equivalent += 1
                if wrap_fn(a) != wrap_fn(b):
                    failures.append(f"wrap({a!r}) != wrap({b!r}) for exact equivalents")
    report["inputs_checked"] = len(inputs)
    report["exact_equivalent_pairs"] = equivalent
    report["wrap_pi"] = wrap_fn(PI)
    report["wrap_minus_pi"] = wrap_fn(-PI)
    if equivalent < 5:
        failures.append(f"wrap: only {equivalent} exactly representable equivalent pairs")
    return failures, report


def wrap_nonfinite_tests(wrap_fn):
    """Return (failures, report): each non-finite input must raise the guard's ValueError.

    The message is checked as well as the type, because math.fmod itself raises a ValueError
    ("math domain error") for +/-inf: a type-only check would not detect a removed guard.
    """
    failures, report = [], {}
    cases = {
        "nan": math.nan,
        "negative_nan": math.copysign(math.nan, -1.0),
        "plus_inf": math.inf,
        "minus_inf": -math.inf,
    }
    for name, a in cases.items():
        try:
            got = wrap_fn(a)
        except ValueError as exc:
            ok = str(exc).startswith(NONFINITE_MESSAGE)
            report[name] = "ValueError (guard)" if ok else "ValueError (not the guard)"
            if not ok:
                failures.append(f"wrap-nonfinite: {name} raised another ValueError: {exc}")
        except Exception as exc:  # any other outcome is a contract violation, not a crash
            report[name] = f"{type(exc).__name__} (not ValueError)"
            failures.append(f"wrap-nonfinite: {name} raised {type(exc).__name__}: {exc}")
        else:
            report[name] = f"returned {got!r}"
            failures.append(f"wrap-nonfinite: {name} returned {got!r} instead of raising")
    report["cases_checked"] = len(cases)
    return failures, report


def exact_properties(
    oracle=finite, wrap_fn=wrap, line_of_nodes=line_of_nodes_exact, assert_jump=True
):
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

    # E2. Tilt about the line of nodes (phi = Omega): the full exact identity
    # (line_of_nodes_exact), on interior, crossing and endpoint cases (M3P6-F1).
    counts = {"interior": 0, "crossing_positive_tilt": 0, "crossing_negative_tilt": 0}
    worst = 0.0
    jump_asserts = {"positive": 0, "negative": 0}
    cases = []
    for inc_deg in (30.0, 51.6, 90.0, 120.0):
        for delta_deg in (-20.0, -5.0, -0.15, 0.15, 5.0, 20.0):
            cases.append(("interior", inc_deg, delta_deg))
    for inc_deg, delta_deg in ((2.0, -5.0), (2.0, 1.5), (178.0, 5.0), (178.0, -1.5)):
        cases.append(("interior", inc_deg, delta_deg))
    for inc_deg in LOW_INC:
        for by in CROSS_BY:
            cases.append(("crossing_positive_tilt", inc_deg, inc_deg + by))
    for inc_deg in HIGH_INC:
        for by in CROSS_BY:
            cases.append(("crossing_negative_tilt", inc_deg, inc_deg - 180.0 - by))
    if ("crossing_positive_tilt", 2.0, 5.0) not in [(c, i, round(d, 9)) for c, i, d in cases]:
        failures.append("E2 counterexample i = 2 deg, delta = 5 deg missing")
    for kind, inc_deg, delta_deg in cases:
        for node_deg in NODES:
            inc, node, delta = (math.radians(x) for x in (inc_deg, node_deg, delta_deg))
            d_i, d_node = oracle(inc, node, node, delta, wrap_fn)
            expected = line_of_nodes(inc, delta)
            i_b = inc + d_i
            tol = pair_noise(inc, i_b)
            if expected is None or d_node is None:
                failures.append(f"E2 {kind} unexpected undefined node i={inc_deg} d={delta_deg}")
                continue
            exp_i, exp_node = expected
            dev = max(abs(d_i - exp_i), circ(d_node, exp_node, wrap)) / tol
            worst = max(worst, dev)
            if dev > 1.0:
                failures.append(f"E2 {kind} i={inc_deg} d={delta_deg} node={node_deg}: {dev:.3e}")
            counts[kind] += 1
            # E5 part 1 (M3P6-F2): every crossing must show the +pi node discontinuity.
            if kind != "interior" and assert_jump:
                sign = "positive" if delta > 0.0 else "negative"
                jump_asserts[sign] += 1
                if circ(d_node, PI, wrap) > tol:
                    failures.append(f"E5a no node jump i={inc_deg} d={delta_deg} node={node_deg}")
    report["E2_case_counts"] = counts
    # Review-06 counterexample, recorded explicitly: i = 2 deg, Omega = phi = 0, delta = +5 deg.
    d_i, d_node = oracle(math.radians(2.0), 0.0, 0.0, math.radians(5.0), wrap_fn)
    report["E2_counterexample_i2_delta5_delta_i_deg"] = math.degrees(d_i)
    report["E2_counterexample_i2_delta5_delta_node_deg"] = (
        None if d_node is None else math.degrees(d_node)
    )
    report["E2_counterexample_i2_delta5_expected_deg"] = [1.0, 180.0]
    report["E2_max_dev_noise_units"] = worst
    # Endpoints j = 0 and j = pi: B is equatorial. Each computed component of h_B carries at
    # most 16 eps error (see noise()), plus <= 2 eps from rounding delta = i - pi, so the
    # computed hypot(h_x, h_y) must be <= 16 sqrt(2) eps + 2 eps < 32 eps.
    endpoints, worst_rho = 0, 0.0
    for inc_deg in (2.0, 30.0, 90.0, 178.0):
        inc = math.radians(inc_deg)
        top = inc - PI  # pick the float delta with inc - delta == PI exactly
        for cand in (top, math.nextafter(top, math.inf), math.nextafter(top, -math.inf)):
            if inc - cand == PI:
                top = cand
                break
        for node_deg in NODES:
            node = math.radians(node_deg)
            for delta in (inc, top):
                endpoints += 1
                if line_of_nodes(inc, delta) is not None:
                    failures.append(f"E2 endpoint claims a defined node: i={inc_deg}")
                h_b = apply(tilt_matrix(node, delta), h_from_elements(inc, node))
                rho = math.hypot(h_b[0], h_b[1])
                worst_rho = max(worst_rho, rho / EPS)
                if rho > 32.0 * EPS:
                    failures.append(f"E2 endpoint not equatorial: i={inc_deg} rho={rho:.3e}")
    report["E2_endpoint_cases"] = endpoints
    report["E2_endpoint_max_hypot_in_eps"] = worst_rho

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

    # E5. Singularities and the node discontinuity (M3P6-F2). Part 1 is asserted in E2 for
    # every crossing case. Part 2: an equatorial orbit has no node. Part 3: at i = 0.1 deg with
    # |delta| = 0.15 deg, sweep the tilt azimuth; the line-of-nodes azimuth (phi = Omega for
    # delta > 0, phi = Omega + 180 deg for delta < 0, the same rotation) crosses the equator and
    # the node must jump by pi there. Tolerance: pair_noise(i_A, i_B), as in E2.
    _, node_eq = elements(h_from_elements(0.0, 0.0))
    report["E5_equatorial_node_undefined"] = node_eq is None
    if node_eq is not None:
        failures.append("E5d equatorial node not reported as undefined")
    inc = math.radians(0.1)
    for sign, cross_k in (("positive", 0), ("negative", 180)):
        delta = math.radians(0.15) * (1.0 if sign == "positive" else -1.0)
        defined, largest = 0, 0.0
        for k in range(360):
            d_i, d_node = oracle(inc, 0.0, math.radians(k), delta, wrap_fn)
            if d_node is None:
                continue
            defined += 1
            largest = max(largest, abs(d_node))
            if k == cross_k and assert_jump:
                jump_asserts[sign] += 1
                if circ(d_node, PI, wrap) > pair_noise(inc, inc + d_i):
                    failures.append(f"E5b sweep: no node jump at phi = {k} deg, tilt {sign}")
        report[f"E5_sweep_{sign}_tilt_defined_samples"] = defined
        report[f"E5_sweep_{sign}_tilt_max_abs_delta_node_deg"] = math.degrees(largest)
        if defined < 359:  # at most one azimuth may hit an exact endpoint
            failures.append(f"E5b sweep: only {defined} defined samples, tilt {sign}")
    # Coverage guard: the jump assertions must actually have run, for both tilt signs.
    report["E5_jump_assertions"] = jump_asserts
    for sign in ("positive", "negative"):
        if jump_asserts[sign] < MIN_CROSSINGS_PER_SIGN + 1:
            failures.append(f"E5c coverage: {jump_asserts[sign]} jump assertions, tilt {sign}")

    # E6. Review-04 example (preserved): h_A = (sin 30, 0, cos 30), R = Rx(-0.15 deg).
    d_i, d_node = oracle(math.radians(30.0), math.radians(90.0), 0.0, math.radians(0.15), wrap_fn)
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


def suppress_jump(oracle, only_inc=None):
    """Mutant oracle: hides the node discontinuity (Delta Omega forced to 0 when |.| > pi/2)."""

    def mutant(inc, node, phi, delta, wrap_fn=wrap):
        d_i, d_node = oracle(inc, node, phi, delta, wrap_fn)
        if d_node is not None and abs(d_node) > PI / 2.0 and (only_inc in (None, inc)):
            d_node = 0.0
        return d_i, d_node

    return mutant


def by_test(failures):
    """Count failures by the regression test that raised them."""
    keys = {"E2": 0, "E5a": 0, "E5b": 0, "E5c": 0, "E5d": 0, "wrap": 0, "other": 0}
    keys["wrap_nonfinite"] = 0
    for f in failures:
        head = f.split()[0]
        if head.startswith("wrap-nonfinite"):
            keys["wrap_nonfinite"] += 1
        else:
            keys[head if head in keys else ("wrap" if head.startswith("wrap") else "other")] += 1
    return keys


def run_exact(**kwargs):
    wrap_fn = kwargs.get("wrap_fn", wrap)
    failures, report = exact_properties(**kwargs)
    w_failures, w_report = wrap_tests(wrap_fn)
    nf_failures, nf_report = wrap_nonfinite_tests(wrap_fn)
    return failures + w_failures + nf_failures, report, w_report, nf_report


# Each defect mutant names the regression tests (failure prefixes) that must each reject it, so
# that removing any one of those checks makes the script fail. E5a: crossing-case jumps; E5b:
# azimuth-sweep jumps; E5c: the coverage guard on the number of executed jump assertions.
EXACT_MUTANTS = {
    "M3P6-F1_unrestricted_line_of_nodes_claim": (
        {"line_of_nodes": line_of_nodes_unrestricted},
        ("E2",),
    ),
    "M3P6-F2_oracle_jump_suppressed": ({"oracle": suppress_jump(finite)}, ("E5a", "E5b")),
    "M3P6-F2_oracle_jump_suppressed_at_i_0p1_deg_only": (
        {"oracle": suppress_jump(finite, math.radians(0.1))},
        ("E5a", "E5b"),
    ),
    "M3P6-F2_jump_assertion_disabled": ({"assert_jump": False}, ("E5c",)),
    "M3P6-F3_previous_wrap_minus_pi_to_pi": ({"wrap_fn": wrap_previous}, ("wrap",)),
    "M3P7-F1_nonfinite_guard_removed": (
        {"wrap_fn": wrap_without_nonfinite_guard},
        ("wrap_nonfinite",),
    ),
}

# Minimum failure counts beyond "at least one". The guard-removed mutant must fail in every
# non-finite category (NaN, -NaN, +inf, -inf), so that the message check that distinguishes
# the guard from math.fmod's own ValueError for +/-inf is load-bearing too.
MIN_DESIGNATED_FAILURES = {"M3P7-F1_nonfinite_guard_removed": {"wrap_nonfinite": 4}}


def main(out_path):
    exact_failures, exact_report, wrap_report, nonfinite_report = run_exact()
    exact_mutants = {}
    for name, (kwargs, tests) in EXACT_MUTANTS.items():
        failures, _, _, _ = run_exact(**kwargs)
        counts = by_test(failures)
        exact_mutants[name] = {
            "designated_tests": list(tests),
            "failures_by_test": counts,
            "rejected_by_designated_test": all(
                counts[t] >= MIN_DESIGNATED_FAILURES.get(name, {}).get(t, 1) for t in tests
            ),
        }
    under_test_failures, under_test_stats = check_formulas(formulas_amendment2)
    mutants = {}
    for name, formula in MUTANTS.items():
        failures, _ = check_formulas(formula)
        mutants[name] = {"failing_checks": len(failures), "rejected": bool(failures)}
    ok = (
        not exact_failures
        and not under_test_failures
        and all(m["rejected"] for m in mutants.values())
        and all(m["rejected_by_designated_test"] for m in exact_mutants.values())
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
        "wrap_convention": wrap_report,
        "wrap_nonfinite": nonfinite_report,
        "exact_property_failures": exact_failures,
        "formulas_under_test": {
            "delta_i": "-delta cos(Omega - phi)",
            "delta_node": "+delta cot(i) sin(Omega - phi)",
            "stats": under_test_stats,
            "failures": under_test_failures,
        },
        "mutants": mutants,
        "exact_and_wrap_mutants": exact_mutants,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(rounded(result), fh, indent=1)
        fh.write("\n")
    print(json.dumps(rounded(result), indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
