"""DR-0028 / reviews M3P5-F1, M3P6-F1..F3, M3P7-F1, M3P8-F1: signed verification of the pole-tilt
node and inclination formulas, the exact line-of-nodes identity, the node discontinuity and angle
wrapping.

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
Revised for review 08 (DR-0028 amendment 5, M3P8-F1): every oracle value, first-order prediction
and error is checked with math.isfinite before any tolerance, order or sign comparison, and a
non-finite value is a failure; each formula must reach a minimum number of valid order samples
and of valid sign checks; the exact properties E1-E4 and E6 reject non-finite values instead of
letting max() and comparisons drop them. All finite-input results are unchanged.
Revised for review 09 (DR-0028 amendment 6, M3P9-F1..F3): new built-in mutants make each
assertion load-bearing for its own reason: oracle +/-inf (whole grid and a single sample) must
be rejected as non-finite; a doubled first-order coefficient must be rejected by the order check
and a reversed sign by the sign check, each per formula; a 1 % inclination error in the oracle
must be rejected by E3 and by E4. No check, formula, tolerance or finite result is changed.
Revised for review 10 (DR-0028 amendment 7, M3P10-F1 and F2): each built-in mutant's injected
function is recorded against its reference implementation, so the output shows whether the
defect was exercised; a mutant whose defect is never exercised is invalid and fails the run. An
exception raised by a mutant is recorded with its type, message and call stack within this
script. Six new built-in mutants make six further assertions load-bearing (E2 x3, E5d, finite
and non-finite wrapping); E5d's call to elements() becomes the elements_fn parameter (default
elements, results identical). No check, formula, tolerance or finite result is changed.
Revised for review 11 (DR-0028 amendment 8, M3P11-F1 and F2): a mutant's defect counts as
exercised only if every call of its injected function shows exactly its declared intended defect
(DEFECTS: shown at least once, never missing where it applies, and no other difference), not
merely any difference from the reference; "differing" is still reported but decides nothing.
observe() lets the mutation check make the same observation independently, on this unmutated
script with a mutant taken from a mutated copy. Five new built-in mutants make five further
assertions load-bearing (W5, E1, E2e, and the two E5b sweep assertions). No check, formula,
tolerance or finite result is changed.

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
import traceback
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
GRID_INCLINATIONS = INCLINED + NEAR_POLAR + NEAR_EQUATORIAL
COMPONENTS = ("delta_i", "delta_node")
SERIES_PER_COMPONENT = len(GRID_INCLINATIONS) * len(NODES) * len(TILT_AZIMUTHS) * 2  # 600


def sign_check_minimum(name):
    """Number of grid series in which a sign check of `name` is applicable (M3P8-F1).

    A sign check compares the sign of the finite result with the sign of the first-order term,
    so it is meaningful only where that term is nonzero. On this grid it vanishes exactly
    (in exact arithmetic; node and azimuth are integer degrees) only where
      delta_i:    cos(Omega - phi) = 0, i.e. Omega - phi = 90 or 270 deg;
      delta_node: sin(Omega - phi) = 0 or cot i = 0, i.e. Omega - phi = 0 or 180 deg, or i = 90.
    Every other series must contribute one valid sign check. (At the committed formulas the
    applicable series have min(|finite|, |first order|) >= 4.6e3 x the gate and the vanishing
    ones <= 3e-9 x the gate, so the gate separates them with a wide margin.)
    """
    n = 0
    for inc_deg in GRID_INCLINATIONS:
        for node_deg in NODES:
            for phi_deg in TILT_AZIMUTHS:
                psi = (node_deg - phi_deg) % 360.0
                if name == "delta_i":
                    applicable = psi % 180.0 != 90.0
                else:
                    applicable = psi % 180.0 != 0.0 and inc_deg != 90.0
                n += 2 if applicable else 0  # both tilt signs
    return n


# Minimum valid samples per formula and check (M3P8-F1). Only samples whose oracle value,
# first-order value and error are all finite, and which pass the significance gate, count.
# Sign checks: derived from the grid (sign_check_minimum: 560 and 504).
# Order checks: the counts the unchanged order check has produced on this fixed grid since
# bcb7f9b (506 and 532), so that no existing coverage can be lost. Which series pass the gate
# (errors at the two smallest steps >= SIGNIFICANT x noise) depends on the size of the O(delta^2)
# error, so it is not a closed-form count; it is nevertheless fixed, because rounding moves an
# error by at most noise = gate / SIGNIFICANT, i.e. a gate ratio by at most 1e-3, while the
# nearest samples on either side of the gate sit at ratios 1.0123 and 0.9940 (delta_i) and 1.55
# and 0.495 (delta_node); the run reports these nearest ratios (stats "gate_ratio_nearest").
MIN_VALID_SAMPLES = {
    "delta_i": {"order": 506, "sign": sign_check_minimum("delta_i")},
    "delta_node": {"order": 532, "sign": sign_check_minimum("delta_node")},
}


def step_scale(inc):
    """s = 1e-2 sin i (rad). The node expansion parameter is delta/sin i (the node is singular
    when |delta| ~ sin i); this keeps |delta|/sin i <= 1e-2, well inside the first-order regime.
    """
    return 1.0e-2 * math.sin(inc)


def nonfinite_reason(num, lin):
    """Why a (finite result, first-order value) pair is not a valid sample, or None (M3P8-F1).

    NaN compares false with everything and +/-inf passes every ">= tol" gate, so either would
    otherwise skip or corrupt the order and sign checks silently. Nothing is filtered: the
    caller records the reason as a failure and the sample counts towards no coverage minimum.
    """
    if num is None or not math.isfinite(num):
        return f"oracle={num!r}"
    if not math.isfinite(lin):
        return f"formula={lin!r}"
    return None  # both finite: |num| <= pi and |lin| finite, so num - lin cannot overflow


def check_formulas(formula, oracle=finite):
    """Run the signed order and sign checks for one formula pair. Returns (failures, stats).

    Failure messages start with the check that raised them: "nonfinite <component>",
    "order <component>", "sign <component>" or "coverage <component>".
    """
    failures = []
    orders = {name: [] for name in COMPONENTS}
    signs = dict.fromkeys(COMPONENTS, 0)
    nearest = {(name, check): [math.inf, 0.0] for name in COMPONENTS for check in ("order", "sign")}
    for inc_deg in GRID_INCLINATIONS:
        inc = math.radians(inc_deg)
        tol = SIGNIFICANT * noise(inc)
        for node_deg in NODES:
            for phi_deg in TILT_AZIMUTHS:
                node, phi = math.radians(node_deg), math.radians(phi_deg)
                for sign in (1.0, -1.0):
                    deltas = [sign * step_scale(inc) * 2.0**-k for k in range(HALVINGS)]
                    tag = f"i={inc_deg} node={node_deg} phi={phi_deg} sign={sign:+.0f}"
                    errs = {name: [] for name in COMPONENTS}  # None once a value is invalid
                    for d in deltas:
                        num = dict(zip(COMPONENTS, oracle(inc, node, phi, d), strict=True))
                        lin = dict(zip(COMPONENTS, formula(inc, node, phi, d), strict=True))
                        for name in COMPONENTS:
                            if errs[name] is None:
                                continue
                            reason = nonfinite_reason(num[name], lin[name])
                            if reason is not None:
                                failures.append(f"nonfinite {name} {reason} delta={d!r} {tag}")
                                errs[name] = None
                                continue
                            errs[name].append(abs(num[name] - lin[name]))
                    for name in COMPONENTS:
                        e = errs[name]
                        if e is None:
                            continue
                        ratio = min(e[-2], e[-1]) / tol
                        if e[-2] >= tol and e[-1] >= tol:
                            p = math.log2(e[-2] / e[-1])
                            orders[name].append(p)
                            nearest[name, "order"][0] = min(nearest[name, "order"][0], ratio)
                            if p < P_MIN:
                                failures.append(f"order {name} p={p:.3f} {tag}")
                        else:
                            nearest[name, "order"][1] = max(nearest[name, "order"][1], ratio)
                    # Sign check at the smallest step, with the finite result as the reference
                    # (num and lin still hold the values at deltas[-1]).
                    for name in COMPONENTS:
                        if errs[name] is None:
                            continue
                        n, lin_v = num[name], lin[name]
                        ratio = min(abs(n), abs(lin_v)) / tol
                        if abs(n) >= tol and abs(lin_v) >= tol:
                            signs[name] += 1
                            nearest[name, "sign"][0] = min(nearest[name, "sign"][0], ratio)
                            if (n > 0.0) != (lin_v > 0.0):
                                failures.append(f"sign {name} num={n:.3e} lin={lin_v:.3e} {tag}")
                        else:
                            nearest[name, "sign"][1] = max(nearest[name, "sign"][1], ratio)
    # Coverage (M3P8-F1): each formula, each check, enforced separately.
    for name in COMPONENTS:
        for check, count in (("order", len(orders[name])), ("sign", signs[name])):
            minimum = MIN_VALID_SAMPLES[name][check]
            if not count >= minimum:
                failures.append(f"coverage {name} {check}: {count} valid samples < {minimum}")
    orders_i, orders_node = orders["delta_i"], orders["delta_node"]
    stats = {
        "order_samples_delta_i": len(orders_i),
        "order_samples_delta_node": len(orders_node),
        "observed_order_delta_i_min_max": [min(orders_i), max(orders_i)] if orders_i else None,
        "observed_order_delta_node_min_max": (
            [min(orders_node), max(orders_node)] if orders_node else None
        ),
        "sign_checks": signs["delta_i"] + signs["delta_node"],
        "sign_checks_delta_i": signs["delta_i"],
        "sign_checks_delta_node": signs["delta_node"],
        "minimum_valid_samples": MIN_VALID_SAMPLES,
        "gate_ratio_nearest": {
            f"{name}_{check}": {"lowest_counted": v[0], "highest_not_counted": v[1]}
            for (name, check), v in nearest.items()
        },
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
    oracle=finite,
    wrap_fn=wrap,
    line_of_nodes=line_of_nodes_exact,
    assert_jump=True,
    tilt_fn=tilt_matrix,
    elements_fn=elements,
):
    """Exact (finite-delta) properties, independent of any first-order formula.

    Every value compared against a tolerance is first checked with math.isfinite (M3P8-F1
    audit): max() silently drops a NaN that is not its first argument, and every comparison
    with NaN is false, so a non-finite deviation would otherwise pass.
    """
    failures, report = [], {}

    # E1. R is a proper rotation; R = Rx(-delta) for phi = 0; B's pole is A's pole rotated by
    # +delta about e (so "positive tilt" is the active right-hand sense).
    worst = 0.0
    for phi_deg in TILT_AZIMUTHS:
        for delta_deg in (-20.0, -0.15, 0.15, 20.0):
            phi, delta = math.radians(phi_deg), math.radians(delta_deg)
            r = tilt_fn(phi, delta)
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
            if not math.isfinite(dev) or any(not math.isfinite(x) for row in r for x in row):
                failures.append(f"E1 non-finite rotation matrix phi={phi_deg} d={delta_deg}")
                continue
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
            if not all(math.isfinite(x) for x in (d_i, d_node, exp_i, exp_node)):
                failures.append(f"E2 {kind} non-finite i={inc_deg} d={delta_deg} node={node_deg}")
                continue
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
                h_b = apply(tilt_fn(node, delta), h_from_elements(inc, node))
                rho = math.hypot(h_b[0], h_b[1])
                if not math.isfinite(rho):
                    failures.append(f"E2 endpoint non-finite: i={inc_deg} rho={rho!r}")
                    continue
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
                d_i, d_node = oracle(inc, node, node - math.pi / 2.0, delta, wrap_fn)
                exp_node = math.atan(math.sin(delta) / math.tan(inc))
                exp_i = math.acos(math.cos(delta) * math.cos(inc)) - inc
                if d_node is None or not all(math.isfinite(x) for x in (d_i, d_node)):
                    failures.append(f"E3 non-finite i={inc_deg} node={node_deg} d={delta_deg}")
                    continue
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
                    d_i, _ = oracle(inc, node, phi, delta, wrap_fn)
                    if not math.isfinite(d_i):
                        failures.append(f"E4 non-finite i={inc_deg} node={node_deg} d={delta_deg}")
                        continue
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
    _, node_eq = elements_fn(h_from_elements(0.0, 0.0))
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
            if not math.isfinite(d_node):
                failures.append(f"E5b sweep: non-finite node difference at phi = {k} deg")
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
    if d_node is None or not all(math.isfinite(x) for x in (d_i, d_node, lin_i, lin_node)):
        failures.append("E6 review-04 example non-finite")
        return failures, report
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


def oracle_with_nonfinite(component, value):
    """Mutant oracle (M3P8-F1 audit): one finite-rotation output replaced by a non-finite value."""

    def mutant(inc, node, phi, delta, wrap_fn=wrap):
        out = list(finite(inc, node, phi, delta, wrap_fn))
        out[component] = value
        return tuple(out)

    return mutant


def oracle_with_nonfinite_at(component, value, series):
    """Mutant oracle (M3P9-F1): one output non-finite at a single sample only.

    `series` = (i, Omega, phi in degrees, tilt sign); the sample is the smallest step of that
    series (step_scale(i) * 2^-(HALVINGS-1), computed exactly as check_formulas does).
    """
    inc_deg, node_deg, phi_deg, sign = series
    target_inc = math.radians(inc_deg)
    target = (
        target_inc,
        math.radians(node_deg),
        math.radians(phi_deg),
        sign * step_scale(target_inc) * 2.0 ** -(HALVINGS - 1),
    )

    def mutant(inc, node, phi, delta, wrap_fn=wrap):
        out = list(finite(inc, node, phi, delta, wrap_fn))
        if (inc, node, phi, delta) == target:
            out[component] = value
        return tuple(out)

    return mutant


def oracle_delta_i_scaled(inc, node, phi, delta, wrap_fn=wrap):
    """Mutant oracle (M3P9-F3): Delta i 1 % too large, Delta Omega exact."""
    d_i, d_node = finite(inc, node, phi, delta, wrap_fn)
    return 1.01 * d_i, d_node


def wrap_inexact_reduction(a):
    """Mutant wrap (M3P10-F2): inexact reduction a - TAU round(a / TAU), right interval."""
    if not math.isfinite(a):
        raise ValueError(f"{NONFINITE_MESSAGE}: {a!r}")
    r = a - TAU * round(a / TAU)
    if r <= -PI:
        r += TAU
    return r


def wrap_nonfinite_typeerror(a):
    """Mutant wrap (M3P10-F2): the non-finite guard raises TypeError instead of ValueError."""
    if not math.isfinite(a):
        raise TypeError(f"{NONFINITE_MESSAGE}: {a!r}")
    return wrap(a)


def line_of_nodes_interior_undefined(inc, delta):
    """Mutant line-of-nodes claim (M3P10-F2): the interior regime 0 < j < pi made undefined."""
    if 0.0 < inc - delta < PI:
        return None
    return line_of_nodes_exact(inc, delta)


def line_of_nodes_crossing_node_unchanged(inc, delta):
    """Mutant line-of-nodes claim (M3P10-F2): Delta Omega = 0 in the equator-crossing regimes."""
    expected = line_of_nodes_exact(inc, delta)
    return None if expected is None else (expected[0], 0.0)


def line_of_nodes_endpoints_defined(inc, delta):
    """Mutant line-of-nodes claim (M3P10-F2): the closed interval 0 <= j <= pi, so the two
    endpoints (B equatorial, node undefined) are claimed to have a defined node."""
    if 0.0 <= inc - delta <= PI:
        return -delta, 0.0
    return line_of_nodes_exact(inc, delta)


def elements_equatorial_node_defined(h):
    """Mutant elements() (M3P10-F2): reports a node even for an equatorial orbit."""
    return math.atan2(math.hypot(h[0], h[1]), h[2]), math.atan2(h[0], -h[1])


def wrap_not_periodic(a):
    """Mutant wrap (M3P11-F2, W5): not periodic. An input one or more turns away from 1.0 rad
    (whose exact reduction is 1.0) is reduced to 1.01; 1.0 itself and every other input are exact.
    """
    r = wrap(a)
    return r + 0.01 if r == 1.0 and a != 1.0 else r


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]


def matmul(a, b):
    return [[sum(a[r][k] * b[k][c] for k in range(3)) for c in range(3)] for r in range(3)]


NODE_ORIGIN_OFFSET = 0.01  # rad


def tilt_node_origin_offset(phi, delta):
    """Mutant rotation matrix (M3P11-F2, E1): an extra rotation of 0.01 rad about the pole (an
    offset of the node-longitude origin). It is still a proper rotation, it keeps B's pole, and
    it keeps the E2 endpoints equatorial, but it is not the passive Rot(e, -delta)."""
    return matmul(rot_z(NODE_ORIGIN_OFFSET), tilt_matrix(phi, delta))


AXIS_TABLE_STEP_DEG = 15.0


def tilt_axis_quantized(phi, delta):
    """Mutant rotation matrix (M3P11-F2, E2e): the tilt-axis azimuth taken from a 15 deg table
    (rounded to the nearest multiple of 15 deg). Exact at E1's azimuths, which are all multiples
    of 15 deg; a wrong tilt axis at the E2 endpoint nodes 37, 145 and 200 deg."""
    step = AXIS_TABLE_STEP_DEG
    return tilt_matrix(math.radians(step * round(math.degrees(phi) / step)), delta)


SWEEP_INC = math.radians(0.1)  # the E5b sweep (exact_properties, E5 part 3)


def oracle_node_nan_at_sweep_azimuth(inc, node, phi, delta, wrap_fn=wrap):
    """Mutant oracle (M3P11-F2, E5b-nonfinite): a NaN node difference at one non-crossing azimuth
    of the E5b sweep (i = 0.1 deg, Omega = 0, phi = 1 deg), for both tilt signs. Each sweep keeps
    359 defined samples (the allowed minimum), and both crossing azimuths still assert the jump.
    """
    d_i, d_node = finite(inc, node, phi, delta, wrap_fn)
    if (inc, node, phi) == (SWEEP_INC, 0.0, math.radians(1.0)):
        d_node = math.nan
    return d_i, d_node


def oracle_node_undefined_at_sweep_azimuths(inc, node, phi, delta, wrap_fn=wrap):
    """Mutant oracle (M3P11-F2, E5b-defined): no node at two non-crossing azimuths of the E5b
    sweep (phi = 1 and 2 deg), for both tilt signs: 358 defined samples per sweep, while both
    crossing azimuths still assert the jump."""
    d_i, d_node = finite(inc, node, phi, delta, wrap_fn)
    if (inc, node) == (SWEEP_INC, 0.0) and phi in (math.radians(1.0), math.radians(2.0)):
        d_node = None
    return d_i, d_node


def tilt_with_nan(phi, delta):
    """Mutant rotation matrix (M3P8-F1 audit) with one NaN entry."""
    r = tilt_matrix(phi, delta)
    r[1][1] = math.nan
    return r


def by_test(failures):
    """Count failures by the regression test that raised them."""
    keys = {"E2": 0, "E5a": 0, "E5b": 0, "E5c": 0, "E5d": 0, "wrap": 0, "other": 0}
    keys["wrap_nonfinite"] = 0
    keys.update({"E1": 0, "E3": 0, "E4": 0, "E6": 0})  # M3P8-F1 audit
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
    # M3P8-F1 audit: before amendment 5, a NaN here was dropped by max() or failed every ">"
    # comparison, and E1-E4 and E6 passed.
    "M3P8-F1_audit_rotation_matrix_nan": ({"tilt_fn": tilt_with_nan}, ("E1", "E2")),
    "M3P8-F1_audit_oracle_delta_i_nan": (
        {"oracle": oracle_with_nonfinite(0, math.nan)},
        ("E2", "E3", "E4", "E6"),
    ),
    "M3P8-F1_audit_oracle_delta_node_nan": (
        {"oracle": oracle_with_nonfinite(1, math.nan)},
        ("E2", "E3", "E5b", "E6"),
    ),
    # M3P9-F3: a finite oracle error that only the E3 deviation and E4 bound assertions see
    # among those two tests (E3 and E4 record no non-finite failure for a finite oracle), so
    # removing either assertion leaves this mutant unrejected by its designated test.
    "M3P9-F3_oracle_delta_i_scaled_1pct": ({"oracle": oracle_delta_i_scaled}, ("E3", "E4")),
    # M3P10-F2 (assertions of category A): each mutant fails exactly one assertion of its test,
    # so removing that assertion leaves the mutant unrejected by its designated test.
    "M3P10-F2_wrap_inexact_reduction": ({"wrap_fn": wrap_inexact_reduction}, ("wrap",)),
    "M3P10-F2_wrap_nonfinite_raises_typeerror": (
        {"wrap_fn": wrap_nonfinite_typeerror},
        ("wrap_nonfinite",),
    ),
    "M3P10-F2_line_of_nodes_interior_undefined": (
        {"line_of_nodes": line_of_nodes_interior_undefined},
        ("E2",),
    ),
    "M3P10-F2_line_of_nodes_crossing_node_unchanged": (
        {"line_of_nodes": line_of_nodes_crossing_node_unchanged},
        ("E2",),
    ),
    "M3P10-F2_line_of_nodes_endpoints_defined": (
        {"line_of_nodes": line_of_nodes_endpoints_defined},
        ("E2",),
    ),
    "M3P10-F2_equatorial_node_defined": (
        {"elements_fn": elements_equatorial_node_defined},
        ("E5d",),
    ),
    # M3P11-F2 (five assertions reclassified as category A): the same construction.
    "M3P11-F2_wrap_not_periodic": ({"wrap_fn": wrap_not_periodic}, ("wrap",)),
    "M3P11-F2_node_origin_offset": ({"tilt_fn": tilt_node_origin_offset}, ("E1",)),
    "M3P11-F2_tilt_axis_quantized": ({"tilt_fn": tilt_axis_quantized}, ("E2",)),
    "M3P11-F2_oracle_node_nan_at_sweep_azimuth": (
        {"oracle": oracle_node_nan_at_sweep_azimuth},
        ("E5b",),
    ),
    "M3P11-F2_oracle_node_undefined_at_sweep_azimuths": (
        {"oracle": oracle_node_undefined_at_sweep_azimuths},
        ("E5b",),
    ),
}

# Minimum failure counts beyond "at least one". The guard-removed mutant must fail in every
# non-finite category (NaN, -NaN, +inf, -inf), so that the message check that distinguishes
# the guard from math.fmod's own ValueError for +/-inf is load-bearing too.
MIN_DESIGNATED_FAILURES = {
    "M3P7-F1_nonfinite_guard_removed": {"wrap_nonfinite": 4},
    "M3P10-F2_wrap_nonfinite_raises_typeerror": {"wrap_nonfinite": 4},
}


def formula_with(component, value):
    """Mutant formula (M3P8-F1): the committed pair with one component replaced by `value`."""

    def mutant(inc, node, phi, delta):
        out = list(formulas_amendment2(inc, node, phi, delta))
        out[component] = value
        return tuple(out)

    return mutant


def by_formula_test(failures):
    """Count first-order failures by check and by formula ("order" and "sign" also in total)."""
    keys = {"order": 0, "sign": 0}
    keys.update({f"{c}_{n}": 0 for c in ("nonfinite", "coverage") for n in COMPONENTS})
    keys.update({f"{c}_{n}": 0 for c in ("order", "sign") for n in COMPONENTS})  # M3P9-F2
    for f in failures:
        head, name = f.split()[:2]
        keys[f"{head}_{name}"] += 1
        if head in ("order", "sign"):
            keys[head] += 1
    return keys


# First-order defect mutants (M3P8-F1): keyword arguments for check_formulas, and the checks
# that must each reject the mutant with at least the given number of failures. A non-finite
# value must be reported in every one of the SERIES_PER_COMPONENT series (so no weakened check
# can let some through) and must fail both coverage minima of its formula (order and sign). A
# zero prediction is finite but skips every sign check of its formula, so the coverage minimum
# must reject it. The oracle mutants make the oracle half of nonfinite_reason load-bearing.
FORMULA_DEFECT_MUTANTS = {}
for _index, _name in enumerate(COMPONENTS):
    _minima = {f"nonfinite_{_name}": SERIES_PER_COMPONENT, f"coverage_{_name}": 2}
    for _label, _value in (("nan", math.nan), ("plus_inf", math.inf), ("minus_inf", -math.inf)):
        FORMULA_DEFECT_MUTANTS[f"M3P8-F1_{_name}_{_label}"] = (
            {"formula": formula_with(_index, _value)},
            _minima,
        )
    FORMULA_DEFECT_MUTANTS[f"M3P8-F1_{_name}_zero"] = (
        {"formula": formula_with(_index, 0.0)},
        {f"coverage_{_name}": 1},
    )
    FORMULA_DEFECT_MUTANTS[f"M3P8-F1_audit_oracle_{_name}_nan"] = (
        {"formula": formulas_amendment2, "oracle": oracle_with_nonfinite(_index, math.nan)},
        _minima,
    )

# M3P9-F1: the oracle half of nonfinite_reason must reject +/-inf as well as NaN, everywhere
# (600 failures) and at a single sample. The single sample is the smallest step of a series
# that is a valid order and sign sample of both formulas at the committed formulas; the minima
# equal the observed counts, so losing it must fail both coverage minima of that formula.
SINGLE_SAMPLE_SERIES = (30.0, 37.0, 0.0, 1.0)
for _index, _name in enumerate(COMPONENTS):
    for _label, _value in (("plus_inf", math.inf), ("minus_inf", -math.inf)):
        FORMULA_DEFECT_MUTANTS[f"M3P9-F1_oracle_{_name}_{_label}"] = (
            {"formula": formulas_amendment2, "oracle": oracle_with_nonfinite(_index, _value)},
            {f"nonfinite_{_name}": SERIES_PER_COMPONENT, f"coverage_{_name}": 2},
        )
        FORMULA_DEFECT_MUTANTS[f"M3P9-F1_oracle_{_name}_{_label}_single_sample"] = (
            {
                "formula": formulas_amendment2,
                "oracle": oracle_with_nonfinite_at(_index, _value, SINGLE_SAMPLE_SERIES),
            },
            {f"nonfinite_{_name}": 1, f"coverage_{_name}": 2},
        )


# M3P9-F2: each assertion must reject a defect that only it can see, for each formula. A
# doubled first-order coefficient keeps every sign but leaves an O(delta) error, so it must fail
# the order check in every series where the first-order term is nonzero (sign_check_minimum:
# there the doubled term differs from the correct one by the whole first-order term). A
# reversed sign must fail the sign check in each of those series. The other formula is exact.
def formula_scaled(component, factor):
    """Mutant formula (M3P9-F2): one first-order coefficient multiplied by `factor`."""

    def mutant(inc, node, phi, delta):
        out = list(formulas_amendment2(inc, node, phi, delta))
        out[component] *= factor
        return tuple(out)

    return mutant


for _index, _name in enumerate(COMPONENTS):
    FORMULA_DEFECT_MUTANTS[f"M3P9-F2_{_name}_coefficient_doubled"] = (
        {"formula": formula_scaled(_index, 2.0)},
        {f"order_{_name}": sign_check_minimum(_name)},
    )
    FORMULA_DEFECT_MUTANTS[f"M3P9-F2_{_name}_sign_reversed"] = (
        {"formula": formula_scaled(_index, -1.0)},
        {f"sign_{_name}": sign_check_minimum(_name)},
    )


# Reference implementation of each injectable function (M3P10-F1). Each built-in mutant's
# injected function is compared with it on every call, so the output shows whether the defect
# was exercised. Settings that are not functions are compared with their default.
REFERENCE_IMPLEMENTATIONS = {
    "formula": formulas_amendment2,
    "oracle": finite,
    "wrap_fn": wrap,
    "line_of_nodes": line_of_nodes_exact,
    "tilt_fn": tilt_matrix,
    "elements_fn": elements,
}
SETTING_DEFAULTS = {"assert_jump": True}


def same_value(a, b):
    """Equality of results, with NaN equal to NaN (so an unchanged NaN is not a difference)."""
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(same_value(x, y) for x, y in zip(a, b, strict=True))
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return type(a) is type(b) and a == b


def outcome(fn, args, kw):
    """("value", result) or ("raised", (exception type, message)) for one call."""
    try:
        return "value", fn(*args, **kw)
    except Exception as exc:
        return "raised", (type(exc), str(exc))


def same_outcome(a, b):
    """Equality of two outcomes: the same result (same_value), or the same exception."""
    if a[0] != b[0]:
        return False
    return same_value(a[1], b[1]) if a[0] == "value" else a[1] == b[1]


# --------------------------------------- intended defects (M3P11-F1, DR-0028 amendment 8)
# Each built-in mutant declares, for each injected function, its intended defect: a description
# and expected(args, kw, reference outcome). expected returns None where the defect does not
# apply (the mutant must then behave exactly as the reference), or else a predicate that the
# mutant's outcome must satisfy there. Every call is classified (call_kind):
#   intended    the defect applies and the mutant shows it;
#   unchanged   the defect does not apply and the mutant equals the reference;
#   missing     the defect applies but the mutant equals the reference;
#   unintended  any other outcome: another difference, or a difference where none is intended.
# A defect is exercised only if it is shown at least once, is never missing and nothing else
# differs (exercised). A difference alone (rounding, a reassociated fallback, a change in another
# component) is not evidence (review 11, M3P11-F1). The observation uses only the injected
# function's arguments and outcomes, never the result of a check.
CALL_KINDS = ("intended", "unchanged", "missing", "unintended")


def exactly(expected):
    return lambda got: same_outcome(got, expected)


def values(ref):
    """The reference result, or None if the reference raised."""
    return ref[1] if ref[0] == "value" else None


def defect_outcome(compute, description, where=lambda args, ref: True):
    """The defect: the outcome compute(args, ref) wherever where(args, ref) holds."""

    def expected(args, kw, ref):
        return exactly(compute(args, ref)) if where(args, ref) else None

    return (description, expected, True)


def defect_none():
    """No defect: an injected function that is the reference implementation itself."""
    return ("none (the reference implementation)", lambda args, kw, ref: None, False)


def defect_scaled(factors, description):
    """Each component of a result pair multiplied by its factor (exact for 2 and -1)."""

    def compute(args, ref):
        pair = zip(factors, values(ref), strict=True)
        return "value", tuple(x if f == 1.0 else f * x for f, x in pair)

    return defect_outcome(compute, description, lambda args, ref: values(ref) is not None)


def defect_component(index, value, description, where=None):
    """One component of a result pair replaced by `value`, where where(args) holds."""

    def compute(args, ref):
        pair = list(values(ref))
        pair[index] = value
        return "value", tuple(pair)

    def applies(args, ref):
        return values(ref) is not None and (where is None or where(args))

    return defect_outcome(compute, description, applies)


def at_sample(series):
    """where(args): the smallest step of one first-order grid series (as check_formulas)."""
    inc_deg, node_deg, phi_deg, sign = series
    inc = math.radians(inc_deg)
    step = sign * step_scale(inc) * 2.0 ** -(HALVINGS - 1)
    target = (inc, math.radians(node_deg), math.radians(phi_deg), step)
    return lambda args: tuple(args[:4]) == target


def swapped_trig(args, ref):
    inc, node, phi, delta = args
    return "value", (-delta * math.sin(node - phi), delta / math.tan(inc) * math.cos(node - phi))


def defect_jump_suppressed(only_inc=None):
    def applies(args, ref):
        pair = values(ref)
        return (
            pair is not None
            and pair[1] is not None
            and abs(pair[1]) > PI / 2.0
            and only_inc in (None, args[0])
        )

    where = "" if only_inc is None else f" at i = {math.degrees(only_inc):.1f} deg only"
    return defect_outcome(
        lambda args, ref: ("value", (ref[1][0], 0.0)),
        f"node difference of more than pi/2 replaced by 0 (jump suppressed){where}",
        applies,
    )


def wrap_reduce(compute):
    """A finite-input wrap defect: the outcome of compute(a) for every finite a."""
    return lambda args, ref: outcome(compute, args, {})


def nonfinite_input(args, ref):
    return not math.isfinite(args[0])


def finite_input(args, ref):
    return math.isfinite(args[0])


def previous_reduction(a):
    return a - 2.0 * math.pi * math.floor((a + math.pi) / (2.0 * math.pi))


def inexact_reduction(a):
    r = a - TAU * round(a / TAU)
    return r + TAU if r <= -PI else r


def guard_not_raised(args, kw, ref):
    if math.isfinite(args[0]):
        return None
    return lambda got: (
        not (
            got[0] == "raised"
            and got[1][0] is ValueError
            and got[1][1].startswith(NONFINITE_MESSAGE)
        )
    )


def origin_offset(args, ref):
    c, s = math.cos(NODE_ORIGIN_OFFSET), math.sin(NODE_ORIGIN_OFFSET)
    rz, m = [[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]], ref[1]
    return "value", [
        [sum(rz[r][k] * m[k][q] for k in range(3)) for q in range(3)] for r in range(3)
    ]


def nan_entry(args, ref):
    m = [row[:] for row in ref[1]]
    m[1][1] = math.nan
    return "value", m


def quantized_axis(args, ref):
    phi, delta = args
    return "value", tilt_matrix(math.radians(15.0 * round(math.degrees(phi) / 15.0)), delta)


def has_value(args, ref):
    return ref[0] == "value"


LINE_OF_NODES_DEFECTS = {
    "unrestricted": defect_outcome(
        lambda args, ref: ("value", (-args[1], 0.0)),
        "Delta i = -delta, Delta Omega = 0 in every regime (no domain 0 < i - delta < pi)",
    ),
    "interior_undefined": defect_outcome(
        lambda args, ref: ("value", None),
        "node reported undefined in the interior regime 0 < i - delta < pi",
        lambda args, ref: 0.0 < args[0] - args[1] < PI,
    ),
    "crossing_node_unchanged": defect_outcome(
        lambda args, ref: ("value", (ref[1][0], 0.0)),
        "Delta Omega = 0 instead of +pi in the equator-crossing regimes",
        lambda args, ref: values(ref) is not None and ref[1][1] == PI,
    ),
    "endpoints_defined": defect_outcome(
        lambda args, ref: ("value", (-args[1], 0.0)),
        "a defined node (Delta i = -delta, Delta Omega = 0) at the endpoints j = 0 and j = pi",
        lambda args, ref: args[0] - args[1] in (0.0, PI),
    ),
}
WRAP_DEFECTS = {
    "previous": defect_outcome(
        wrap_reduce(previous_reduction),
        "the bcb7f9b reduction a - 2 pi floor((a + pi) / 2 pi): [-pi, pi), no non-finite guard",
    ),
    "previous_guarded": defect_outcome(
        wrap_reduce(previous_reduction),
        "the bcb7f9b reduction a - 2 pi floor((a + pi) / 2 pi) for finite input: [-pi, pi)",
        finite_input,
    ),
    "guard_removed": (
        "the non-finite guard removed: a non-finite input does not raise the guard's ValueError",
        guard_not_raised,
        True,
    ),
    "inexact_reduction": defect_outcome(
        wrap_reduce(inexact_reduction),
        "the inexact reduction a - 2 pi round(a / 2 pi) for finite input",
        finite_input,
    ),
    "typeerror": defect_outcome(
        lambda args, ref: ("raised", (TypeError, f"{NONFINITE_MESSAGE}: {args[0]!r}")),
        "a non-finite input raises TypeError instead of ValueError (same message)",
        nonfinite_input,
    ),
    "not_periodic": defect_outcome(
        lambda args, ref: ("value", ref[1] + 0.01),
        "an input one or more turns from 1.0 rad reduced to 1.01 instead of 1.0",
        lambda args, ref: values(ref) == 1.0 and args[0] != 1.0,
    ),
}
TILT_DEFECTS = {
    "nan_entry": defect_outcome(nan_entry, "rotation matrix entry [1][1] = NaN", has_value),
    "node_origin_offset": defect_outcome(
        origin_offset,
        "an extra rotation of 0.01 rad about the pole (node-longitude origin offset)",
        has_value,
    ),
    "axis_quantized": defect_outcome(
        quantized_axis,
        "tilt-axis azimuth rounded to the nearest multiple of 15 deg",
        has_value,
    ),
}


def equatorial_node(args, ref):
    h = args[0]
    return "value", (ref[1][0], math.atan2(h[0], -h[1]))


def sweep_azimuths(*phi_deg):
    """where(args): the E5b sweep's oracle calls at these azimuths (both tilt signs)."""
    targets = {(SWEEP_INC, 0.0, math.radians(p)) for p in phi_deg}
    return lambda args: tuple(args[:3]) in targets


JUMP_ASSERTIONS_OFF = ("the jump assertions switched off (assert_jump = False)", False)

# The intended defect of every built-in mutant, for each injected function or setting. The two
# M3P8-F1_audit_oracle_*_nan names occur in two sections with the same oracle defect; the
# first-order section also injects the reference formula (defect_none).
DEFECTS = {
    "amendment1_original_both_signs_reversed": {
        "formula": defect_scaled((-1.0, -1.0), "both first-order signs reversed")
    },
    "delta_i_sign_reversed": {"formula": defect_scaled((-1.0, 1.0), "Delta i sign reversed")},
    "delta_node_sign_reversed": {
        "formula": defect_scaled((1.0, -1.0), "Delta Omega sign reversed")
    },
    "cos_sin_swapped": {"formula": defect_outcome(swapped_trig, "cos and sin swapped")},
}
for _index, _name in enumerate(COMPONENTS):
    _factors = {f: tuple(f if k == _index else 1.0 for k in range(2)) for f in (2.0, -1.0)}
    _oracle_nan = defect_component(_index, math.nan, f"{_name} oracle value NaN everywhere")
    DEFECTS[f"M3P8-F1_audit_oracle_{_name}_nan"] = {"formula": defect_none(), "oracle": _oracle_nan}
    for _label, _value in (("nan", math.nan), ("plus_inf", math.inf), ("minus_inf", -math.inf)):
        DEFECTS[f"M3P8-F1_{_name}_{_label}"] = {
            "formula": defect_component(_index, _value, f"{_name} formula returns {_value!r}")
        }
    for _label, _value in (("plus_inf", math.inf), ("minus_inf", -math.inf)):
        DEFECTS[f"M3P9-F1_oracle_{_name}_{_label}"] = {
            "formula": defect_none(),
            "oracle": defect_component(_index, _value, f"{_name} oracle value {_value!r}"),
        }
        DEFECTS[f"M3P9-F1_oracle_{_name}_{_label}_single_sample"] = {
            "formula": defect_none(),
            "oracle": defect_component(
                _index,
                _value,
                f"{_name} oracle value {_value!r} at one sample only",
                at_sample(SINGLE_SAMPLE_SERIES),
            ),
        }
    DEFECTS[f"M3P8-F1_{_name}_zero"] = {
        "formula": defect_component(_index, 0.0, f"{_name} formula returns 0")
    }
    DEFECTS[f"M3P9-F2_{_name}_coefficient_doubled"] = {
        "formula": defect_scaled(_factors[2.0], f"{_name} first-order coefficient doubled")
    }
    DEFECTS[f"M3P9-F2_{_name}_sign_reversed"] = {
        "formula": defect_scaled(_factors[-1.0], f"{_name} first-order sign reversed")
    }
DEFECTS.update(
    {
        "M3P6-F1_unrestricted_line_of_nodes_claim": {
            "line_of_nodes": LINE_OF_NODES_DEFECTS["unrestricted"]
        },
        "M3P6-F2_oracle_jump_suppressed": {"oracle": defect_jump_suppressed()},
        "M3P6-F2_oracle_jump_suppressed_at_i_0p1_deg_only": {
            "oracle": defect_jump_suppressed(math.radians(0.1))
        },
        "M3P6-F2_jump_assertion_disabled": {"assert_jump": JUMP_ASSERTIONS_OFF},
        "M3P6-F3_previous_wrap_minus_pi_to_pi": {"wrap_fn": WRAP_DEFECTS["previous"]},
        "M3P7-F1_nonfinite_guard_removed": {"wrap_fn": WRAP_DEFECTS["guard_removed"]},
        "M3P8-F1_audit_rotation_matrix_nan": {"tilt_fn": TILT_DEFECTS["nan_entry"]},
        "M3P9-F3_oracle_delta_i_scaled_1pct": {
            "oracle": defect_scaled((1.01, 1.0), "delta_i oracle value 1 % too large")
        },
        "M3P10-F2_wrap_inexact_reduction": {"wrap_fn": WRAP_DEFECTS["inexact_reduction"]},
        "M3P10-F2_wrap_nonfinite_raises_typeerror": {"wrap_fn": WRAP_DEFECTS["typeerror"]},
        "M3P10-F2_line_of_nodes_interior_undefined": {
            "line_of_nodes": LINE_OF_NODES_DEFECTS["interior_undefined"]
        },
        "M3P10-F2_line_of_nodes_crossing_node_unchanged": {
            "line_of_nodes": LINE_OF_NODES_DEFECTS["crossing_node_unchanged"]
        },
        "M3P10-F2_line_of_nodes_endpoints_defined": {
            "line_of_nodes": LINE_OF_NODES_DEFECTS["endpoints_defined"]
        },
        "M3P10-F2_equatorial_node_defined": {
            "elements_fn": defect_outcome(
                equatorial_node,
                "a node reported for an equatorial orbit",
                lambda args, ref: values(ref) is not None and ref[1][1] is None,
            )
        },
        "M3P11-F2_wrap_not_periodic": {"wrap_fn": WRAP_DEFECTS["not_periodic"]},
        "M3P11-F2_node_origin_offset": {"tilt_fn": TILT_DEFECTS["node_origin_offset"]},
        "M3P11-F2_tilt_axis_quantized": {"tilt_fn": TILT_DEFECTS["axis_quantized"]},
        "M3P11-F2_oracle_node_nan_at_sweep_azimuth": {
            "oracle": defect_component(
                1, math.nan, "NaN node difference at sweep azimuth 1 deg", sweep_azimuths(1.0)
            )
        },
        "M3P11-F2_oracle_node_undefined_at_sweep_azimuths": {
            "oracle": defect_component(
                1, None, "no node at sweep azimuths 1 and 2 deg", sweep_azimuths(1.0, 2.0)
            )
        },
    }
)


def call_kind(intended, args, kw, ref, got):
    """Classify one call of an injected function against its intended defect (CALL_KINDS)."""
    if intended is None:  # no declared defect: nothing can be evidence
        return "unintended"
    present = intended[1](args, kw, ref)
    if present is None or present(ref):
        return "unchanged" if same_outcome(got, ref) else "unintended"
    if present(got):
        return "intended"
    return "missing" if same_outcome(got, ref) else "unintended"


def instrumented(kwargs, defects):
    """Wrap each injected function in a recorder; return (kwargs, record).

    The recorder calls the mutant, then the reference implementation with the same arguments,
    and classifies the call against the mutant's intended defect (call_kind). "differing"
    (amendment 7) still counts every call whose outcome differs in any way; it is reported for
    comparison and decides nothing. A setting is compared with its declared defective value. The
    mutant's own result, or exception, is passed on unchanged.
    """
    wrapped, record = {}, {}
    for key, value in kwargs.items():
        intended = defects.get(key)
        description = None if intended is None else intended[0]
        if key in SETTING_DEFAULTS:
            wrapped[key] = value
            default = SETTING_DEFAULTS[key]
            record[key] = {
                "defect": description,
                "setting": value,
                "default": default,
                "intended": intended is not None and value == intended[1] != default,
            }
            continue
        counts = record[key] = {"calls": 0, "differing": 0, "defect": description}
        counts.update(changes=intended is None or intended[2], **dict.fromkeys(CALL_KINDS, 0))

        def note(args, kw, got, _ref=REFERENCE_IMPLEMENTATIONS[key], _d=intended, _c=counts):
            ref = outcome(_ref, args, kw)
            _c["calls"] += 1
            _c["differing"] += not same_outcome(got, ref)
            _c[call_kind(_d, args, kw, ref, got)] += 1

        def recorder(*args, _impl=value, _note=note, **kw):
            try:
                result = _impl(*args, **kw)
            except Exception as exc:
                _note(args, kw, ("raised", (type(exc), str(exc))))
                raise
            _note(args, kw, ("value", result))
            return result

        wrapped[key] = recorder
    return wrapped, record


def key_exercised(r):
    """One injected function or setting shows exactly its intended defect (M3P11-F1)."""
    if "setting" in r:
        return r["intended"]
    clean = r["defect"] is not None and r["missing"] == 0 and r["unintended"] == 0
    return clean and (r["intended"] > 0) == r["changes"]


def exercised(record):
    """A mutant's defect was exercised only if every injected function and setting shows
    exactly its intended defect (key_exercised) and at least one of them is a real defect."""
    return all(key_exercised(r) for r in record.values()) and any(
        r.get("changes", True) for r in record.values()
    )


def exception_record(exc):
    """Type, message and call stack (function: source line, frames of this script only)."""
    here = exception_record.__code__.co_filename
    frames = traceback.extract_tb(exc.__traceback__)[1:]  # without mutant_failures itself
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "stack": [f"{f.name}: {f.line}" for f in frames if f.filename == here],
    }


def mutant_failures(run, defects, **kwargs):
    """(failures, exception, defect record) for one built-in defect mutant.

    A mutant that raises was not rejected by any check: the exception is recorded with its
    location (M3P10-F1) and the mutant counts as not rejected, so the verdict is FAIL. This
    applies to mutants only; the formulas under test and the exact properties are never
    wrapped, and raise as before.
    """
    wrapped, record = instrumented(kwargs, defects)
    try:
        return run(**wrapped)[0], None, record
    except Exception as exc:  # recorded and failed closed, never treated as a rejection
        return [], exception_record(exc), record


# The test that each section of built-in mutants is run through (main).
SECTION_RUNS = {
    "mutants": check_formulas,
    "formula_defect_mutants": check_formulas,
    "exact_and_wrap_mutants": run_exact,
}


def observe(run, defects, **kwargs):
    """Independent observation of an injected defect (M3P11-F1): the defect record of `kwargs`
    under `run`, whose failures are discarded. The mutation check calls it in a separate process
    on the unmutated script, with injected functions taken from a mutated copy, so that neither
    the copy's own recorder nor any check decides whether the defect occurred."""
    _, exception, record = mutant_failures(run, defects, **kwargs)
    return {"defect_calls": record, "defect_exercised": exercised(record), "exception": exception}


def mutant_entry(entry, exception, record):
    """Add the defect record, and the exception if any, to a mutant's output entry."""
    entry["defect_calls"] = record
    entry["defect_exercised"] = exercised(record)
    if exception is not None:
        entry["exception"] = exception
    return entry


def main(out_path):
    exact_failures, exact_report, wrap_report, nonfinite_report = run_exact()
    exact_mutants = {}
    for name, (kwargs, tests) in EXACT_MUTANTS.items():
        failures, exception, record = mutant_failures(run_exact, DEFECTS.get(name, {}), **kwargs)
        counts = by_test(failures)
        exact_mutants[name] = mutant_entry(
            {
                "designated_tests": list(tests),
                "failures_by_test": counts,
                "rejected_by_designated_test": exception is None
                and all(
                    counts[t] >= MIN_DESIGNATED_FAILURES.get(name, {}).get(t, 1) for t in tests
                ),
            },
            exception,
            record,
        )
    under_test_failures, under_test_stats = check_formulas(formulas_amendment2)
    mutants = {}
    for name, formula in MUTANTS.items():
        failures, exception, record = mutant_failures(
            check_formulas, DEFECTS.get(name, {}), formula=formula
        )
        mutants[name] = mutant_entry(
            {"failing_checks": len(failures), "rejected": exception is None and bool(failures)},
            exception,
            record,
        )
    formula_defect_mutants = {}
    for name, (kwargs, minima) in FORMULA_DEFECT_MUTANTS.items():
        failures, exception, record = mutant_failures(
            check_formulas, DEFECTS.get(name, {}), **kwargs
        )
        counts = by_formula_test(failures)
        formula_defect_mutants[name] = mutant_entry(
            {
                "designated_minimum_failures": minima,
                "failures_by_check": counts,
                "rejected_by_designated_checks": exception is None
                and all(counts[t] >= m for t, m in minima.items()),
            },
            exception,
            record,
        )
    # Invalid mutant setup (M3P10-F1): a built-in mutant whose defect is never exercised tests
    # nothing, so the run fails. Since amendment 8 (M3P11-F1) "exercised" means that exactly the
    # declared intended defect occurred (exercised), and every injected function and setting of
    # every built-in mutant must declare one.
    sections = (mutants, formula_defect_mutants, exact_mutants)
    unexercised = sorted(n for s in sections for n, m in s.items() if not m["defect_exercised"])
    injected = [(n, {"formula"}) for n in MUTANTS]
    injected += [
        (n, set(k)) for n, (k, _) in (*FORMULA_DEFECT_MUTANTS.items(), *EXACT_MUTANTS.items())
    ]
    undeclared = sorted({n for n, keys in injected if not keys <= set(DEFECTS.get(n, {}))})
    ok = (
        not unexercised
        and not undeclared
        and not exact_failures
        and not under_test_failures
        and all(m["rejected"] for m in mutants.values())
        and all(m["rejected_by_designated_test"] for m in exact_mutants.values())
        and all(m["rejected_by_designated_checks"] for m in formula_defect_mutants.values())
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
        "formula_defect_mutants": formula_defect_mutants,
        "exact_and_wrap_mutants": exact_mutants,
        "mutants_with_defect_not_exercised": unexercised,
        "exercise_criterion": (
            "amendment 8 (M3P11-F1): each injected function shows exactly its declared intended "
            "defect (intended >= 1, missing = 0, unintended = 0); 'differing' is reported only"
        ),
        "mutants_without_declared_defect": undeclared,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(rounded(result), fh, indent=1)
        fh.write("\n")
    print(json.dumps(rounded(result), indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
