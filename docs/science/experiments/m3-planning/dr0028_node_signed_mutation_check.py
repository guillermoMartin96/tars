"""DR-0028 amendments 5-7 / reviews M3P8-F1, M3P9-F1..F3, M3P10-F1: file-level mutation check
of dr0028_node_signed_verification.py through its real entrypoint.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python dr0028_node_signed_mutation_check.py <out.json>

Each mutation replaces one exact text fragment of the verification script (the fragment must
occur exactly once), writes the mutated copy to a temporary directory and runs it as a separate
process (`python -I <copy> <out.json>`), exactly as the script is normally run.

Each mutation declares its expected rejection as predicates on the script's output, and every
run is classified into exactly one category (M3P10-F1; I-10 section 2):
- "invalid mutation setup": the fragment does not occur exactly once (the copy is not run), or a
  built-in mutant named by the expectation never exercised its defect;
- "process failure": the process wrote no output (a syntax error, import failure, missing file
  or any other crash), or its exit status and verdict are inconsistent;
- "normal execution": exit 0 with verdict PASS (the mutation survived);
- "unexpected exception": a built-in mutant raised an exception that the mutation's expectation
  does not allow, by mutant, exception type, message and call stack;
- "rejected for another reason": exit 1 with verdict FAIL, but the expected rejection is not
  shown;
- "expected rejection": exit 1 with verdict FAIL, no unexpected exception, and every predicate
  holds. Only this category is a detection.

A built-in mutant counts as "not rejected" (the evidence that an assertion was removed) only if
it completed without an exception, its designated checks stayed silent, and its injected defect
was exercised (some call differed from the reference implementation). An exception is accepted
only where a "raised" predicate allows exactly that mutant, type, message prefix and stack.
These allowances are limited to the E2 and E5b wrap-guard cases and to the order-estimate
math domain error of the four mutations that let an oracle +/-inf through the finite validation.

The unmutated script must exit 0 with verdict PASS, and no expectation may already be met by its
output. Controls (I-10 section 3) each declare the category they must receive: process-level
failures, a neutral edit, invalid setup, a wrong reason, exceptions raised or suppressed inside
built-in mutants, an allowed exception at the wrong location or of the wrong type, and valid
mutations. Exit status 0 only if the baseline passes, every mutation is detected and every
control receives its declared category. Standard library only.
"""

import json
import math
import pathlib
import subprocess
import sys
import tempfile

SCRIPT = pathlib.Path(__file__).with_name("dr0028_node_signed_verification.py")
SERIES = 600  # series per formula (SERIES_PER_COMPONENT in the script)

FORMULA = "return -delta * math.cos(node - phi), delta / math.tan(inc) * math.sin(node - phi)"
NODE_TERM = "delta / math.tan(inc) * math.sin(node - phi)"
COVERAGE_LOOP = (
    "    for name in COMPONENTS:\n"
    '        for check, count in (("order", len(orders[name])), ("sign", signs[name])):'
)
COVERAGE_PAIRS = '(("order", len(orders[name])), ("sign", signs[name]))'
SIGN_GATE = (
    "                        if abs(n) >= tol and abs(lin_v) >= tol:\n"
    "                            signs[name] += 1\n"
)
WRAP_BODY = (
    '        raise ValueError(f"{NONFINITE_MESSAGE}: {a!r}")\n'
    "    r = math.fmod(a, TAU)\n"
    "    if r > PI:\n"
    "        r -= TAU\n"
    "    elif r <= -PI:\n"
    "        r += TAU\n"
    "    return r\n"
)
ORDER_ASSERT = "if p < P_MIN:"
SIGN_ASSERT = "if (n > 0.0) != (lin_v > 0.0):"
ORACLE_CHECK = "if num is None or not math.isfinite(num):"
ORACLE_CALL = (
    "                        num = dict(zip(COMPONENTS, oracle(inc, node, phi, d), strict=True))\n"
)
E3_ASSERT = (
    "    if worst > 1.0:\n"
    '        failures.append(f"E3 closed form deviation {worst:.3e} noise units")\n'
)
E4_ASSERT = (
    "    if ratio > 1.0:\n"
    '        failures.append(f"E4 inclination bound exceeded: {ratio:.3e} x 64 eps")\n'
)


# The wrap guard (amendment 4), with the line that follows it, so the fragment is unique.
WRAP_GUARD = (
    "    if not math.isfinite(a):\n"
    '        raise ValueError(f"{NONFINITE_MESSAGE}: {a!r}")\n'
    "    r = math.fmod(a, TAU)\n"
)
WRAP_GUARD_RAISE = 'wrap: raise ValueError(f"{NONFINITE_MESSAGE}: {a!r}")'
E2_IDENTITY_LINE = "dev = max(abs(d_i - exp_i), circ(d_node, exp_node, wrap)) / tol"
E5B_JUMP_LINE = "if circ(d_node, PI, wrap) > pair_noise(inc, inc + d_i):"
ORDER_ESTIMATE_LINE = "check_formulas: p = math.log2(e[-2] / e[-1])"


# ------------------------------------------------------------------- expected rejections
def not_rejected(section, mutant):
    """Predicate: a built-in mutant completed without an exception, exercised its defect, and
    was not rejected by its designated checks (the assertion guarding it is gone)."""
    return ("not_rejected", section, mutant)


def raised(section, mutant, exc_type, message, stack):
    """Predicate and allowance: a built-in mutant raised exactly this exception type, with a
    message starting with `message`, through exactly this call stack (function: source line,
    frames of the verification script), and was therefore not rejected."""
    return ("raised", section, mutant, exc_type, message, tuple(stack))


def under_test(prefix, count=None):
    """Predicate: the formulas under test report failures starting with `prefix`.

    With `count`, exactly that many; otherwise at least one.
    """
    return ("under_test", prefix, count)


def exact(prefix):
    """Predicate: at least one exact-property or wrapping failure starts with `prefix`."""
    return ("exact", prefix, None)


FLAGS = {
    "formula_defect_mutants": "rejected_by_designated_checks",
    "exact_and_wrap_mutants": "rejected_by_designated_test",
    "mutants": "rejected",
}


def unexercised(section, mutant):
    """Predicate: a built-in mutant completed without an exception and was not rejected because
    nothing exercised its defect (it is listed in mutants_with_defect_not_exercised); used only
    together with report_missing, which shows that the exercising test itself was disabled."""
    return ("unexercised", section, mutant)


def report_missing(section, key):
    """Predicate: the script's report `section` has no entry `key` (a test was not run)."""
    return ("report_missing", section, key)


def matches(predicate, exception):
    _, _, _, exc_type, message, stack = predicate
    return (
        exception["type"] == exc_type
        and exception["message"].startswith(message)
        and tuple(exception["stack"]) == stack
    )


def holds(predicate, out):
    kind, a, b = predicate[:3]
    if kind == "not_rejected":
        entry = out[a][b]
        return entry[FLAGS[a]] is False and "exception" not in entry and entry["defect_exercised"]
    if kind == "raised":
        entry = out[a][b]
        return entry[FLAGS[a]] is False and matches(predicate, entry.get("exception", {}))
    if kind == "unexercised":
        entry = out[a][b]
        return (
            entry[FLAGS[a]] is False
            and "exception" not in entry
            and b in out["mutants_with_defect_not_exercised"]
        )
    if kind == "report_missing":
        return b not in out[a]
    if kind == "under_test":
        failures = out["formulas_under_test"]["failures"]
    else:
        failures = out["exact_property_failures"]
    n = sum(1 for f in failures if f.startswith(a))
    return n >= 1 if b is None else n == b


def describe(predicate):
    kind, a, b = predicate[:3]
    if kind == "not_rejected":
        return f"built-in mutant {b} completed, defect exercised, not rejected ({a})"
    if kind == "unexercised":
        return f"built-in mutant {b} completed, not rejected, defect not exercised ({a})"
    if kind == "report_missing":
        return f"report {a} has no entry {b!r} (test not run)"
    if kind == "raised":
        _, _, _, exc_type, message, stack = predicate
        return f"built-in mutant {b} raised {exc_type}({message!r}...) at {' > '.join(stack)} ({a})"
    where = "formulas under test" if kind == "under_test" else "exact properties"
    many = "at least 1" if b is None else f"exactly {b}"
    return f"{where}: {many} failure(s) starting {a!r}"


# ----------------------------------------------------------------- mutation definitions
def nonfinite_name(value):
    return {"nan": "nan", "inf": "plus_inf", "-inf": "minus_inf"}[repr(value)]


def value_source(value):
    return {"nan": "math.nan", "inf": "math.inf", "-inf": "-math.inf"}[repr(value)]


# Review-09 injection matrix (preserved from Codex review 09's 60 independent cases):
# formula path, 2 formulas x 3 values x 7 subsets = 42; oracle path, 2 x 3 x 3 = 18.
# Formula subsets act inside formulas_amendment2 (the formula under test); the expected count is
# the number of grid series that contain at least one corrupted step, since a series is
# discarded at its first invalid value.
FORMULA_SUBSETS = {
    "all": ("True", SERIES),
    "first_step": ("abs(delta) == 1.0e-2 * math.sin(inc)", SERIES),
    "last_step": ("abs(delta) == 1.0e-2 * math.sin(inc) * 2.0**-4", SERIES),
    "one_series": (
        "(inc, node, phi, delta > 0.0) == (math.radians(30.0), math.radians(37.0), 0.0, True)",
        1,
    ),
    "positive_tilt": ("delta > 0.0", SERIES // 2),
    "near_equatorial": ("round(math.degrees(inc), 9) in (2.0, 5.0, 175.0, 178.0)", 240),
    "near_polar": ("round(math.degrees(inc), 9) in (89.0, 90.0, 91.0)", 180),
}
# Oracle subsets act on the oracle values inside check_formulas.
ORACLE_SUBSETS = {
    "all": ("True", SERIES),
    "first_step": ("d == deltas[0]", SERIES),
    "negative_tilt_near_polar": ("sign < 0.0 and inc_deg in NEAR_POLAR", 90),
}
COMPONENT_NAMES = ("delta_i", "delta_node")


def formula_injection(index, value, condition):
    """Replace the formula under test by one that returns `value` for one formula where
    `condition` holds (a Python expression in inc, node, phi, delta)."""
    return (
        "out = [-delta * math.cos(node - phi), delta / math.tan(inc) * math.sin(node - phi)]\n"
        f"    if {condition}:\n"
        f"        out[{index}] = {value_source(value)}\n"
        "    return tuple(out)"
    )


def oracle_injection(name, value, condition):
    """Inject `value` into one oracle output inside check_formulas where `condition` holds."""
    return (
        ORACLE_CALL + f"                        if {condition}:\n"
        f'                            num["{name}"] = {value_source(value)}\n'
    )


def injection_matrix():
    rows = []
    for index, name in enumerate(COMPONENT_NAMES):
        for value in (math.nan, math.inf, -math.inf):
            for subset, (condition, count) in FORMULA_SUBSETS.items():
                rows.append(
                    (
                        f"review09_formula_{name}_{nonfinite_name(value)}_{subset}",
                        "review-09 injection matrix",
                        f"finite validation of the {name} formula ({subset})",
                        FORMULA,
                        formula_injection(index, value, condition),
                        [under_test(f"nonfinite {name} formula={value!r} ", count)],
                    )
                )
    for name in COMPONENT_NAMES:
        for value in (math.nan, math.inf, -math.inf):
            for subset, (condition, count) in ORACLE_SUBSETS.items():
                rows.append(
                    (
                        f"review09_oracle_{name}_{nonfinite_name(value)}_{subset}",
                        "review-09 injection matrix",
                        f"finite validation of the {name} oracle ({subset})",
                        ORACLE_CALL,
                        oracle_injection(name, value, condition),
                        [under_test(f"nonfinite {name} oracle={value!r} ", count)],
                    )
                )
    return rows


def wrap_guard_at(site):
    """Allowance (M3P10-F1): with an E2 or E5b finite check removed, the oracle-NaN mutant
    reaches circ() at that site, and the amendment-4 wrap guard raises ValueError there."""
    return raised(
        "exact_and_wrap_mutants",
        "M3P8-F1_audit_oracle_delta_node_nan",
        "ValueError",
        "wrap: non-finite angle: ",
        [
            "run_exact: failures, report = exact_properties(**kwargs)",
            site,
            "circ: return abs(wrap_fn(a - b))",
            WRAP_GUARD_RAISE,
        ],
    )


# Allowance (M3P10-F1): when the finite validation is weakened (isnan), bypassed or does not
# discard an invalid sample, a single-sample oracle +/-inf reaches the order estimate as
# e[-1] = inf, and log2(finite / inf) = log2(0) raises "math domain error" there, for exactly the
# four single-sample mutants.
ORDER_ESTIMATE_RAISES = [
    raised(
        "formula_defect_mutants",
        f"M3P9-F1_oracle_{name}_{label}_single_sample",
        "ValueError",
        "math domain error",
        [ORDER_ESTIMATE_LINE],
    )
    for name in ("delta_i", "delta_node")
    for label in ("plus_inf", "minus_inf")
]


def not_designated(mutant):
    return [not_rejected("formula_defect_mutants", mutant)]


def not_designated_exact(mutant):
    return [not_rejected("exact_and_wrap_mutants", mutant)]


ONE_SAMPLE = "(inc_deg, node_deg, phi_deg, sign) == (30.0, 37.0, 0.0, 1.0) and d == deltas[-1]"

# (name, group, target property, old fragment, new fragment, expected rejection)
MUTATIONS = [
    # M3P8-F1: non-finite first-order output injected at the source.
    *[
        (
            f"{name}_formula_returns_{nonfinite_name(value)}",
            "M3P8-F1 injection",
            f"finite validation of the {name} formula",
            FORMULA,
            (
                f"return {value_source(value)}, {NODE_TERM}"
                if name == "delta_i"
                else f"return -delta * math.cos(node - phi), {value_source(value)}"
            ),
            [under_test(f"nonfinite {name} formula={value!r} ", SERIES)],
        )
        for name in COMPONENT_NAMES
        for value in (math.nan, math.inf, -math.inf)
    ],
    # M3P8-F1: coverage minima disabled or weakened.
    (
        "delta_i_coverage_disabled",
        "M3P8-F1 coverage",
        "delta_i coverage minima",
        COVERAGE_LOOP,
        COVERAGE_LOOP.replace("in COMPONENTS", 'in ("delta_node",)'),
        not_designated("M3P8-F1_delta_i_zero"),
    ),
    (
        "delta_node_coverage_disabled",
        "M3P8-F1 coverage",
        "delta_node coverage minima",
        COVERAGE_LOOP,
        COVERAGE_LOOP.replace("in COMPONENTS", 'in ("delta_i",)'),
        not_designated("M3P8-F1_delta_node_zero"),
    ),
    (
        "sign_coverage_removed",
        "M3P8-F1 coverage",
        "sign coverage minima",
        COVERAGE_PAIRS,
        '(("order", len(orders[name])),)',
        not_designated("M3P8-F1_delta_i_zero") + not_designated("M3P8-F1_delta_node_zero"),
    ),
    (
        "order_coverage_removed",
        "M3P8-F1 coverage",
        "order coverage minima",
        COVERAGE_PAIRS,
        '(("sign", signs[name]),)',
        not_designated("M3P8-F1_delta_i_nan") + not_designated("M3P8-F1_delta_node_nan"),
    ),
    (
        "coverage_comparison_disabled",
        "M3P8-F1 coverage",
        "coverage comparison",
        "if not count >= minimum:",
        "if False:",
        not_designated("M3P8-F1_delta_i_zero") + not_designated("M3P8-F1_delta_node_zero"),
    ),
    (
        "sign_counter_moved_outside_gate",
        "M3P8-F1 coverage",
        "sign coverage counter",
        SIGN_GATE,
        "                        signs[name] += 1\n"
        "                        if abs(n) >= tol and abs(lin_v) >= tol:\n",
        not_designated("M3P8-F1_delta_i_zero") + not_designated("M3P8-F1_delta_node_zero"),
    ),
    # M3P8-F1: finite-value validation removed or weakened.
    (
        "finite_validation_removed",
        "M3P8-F1 validation",
        "finite validation of oracle and formula values",
        "reason = nonfinite_reason(num[name], lin[name])",
        "reason = None",
        not_designated("M3P8-F1_delta_i_nan")
        + not_designated("M3P8-F1_audit_oracle_delta_i_nan")
        + ORDER_ESTIMATE_RAISES,
    ),
    (
        "formula_check_weakened_to_isnan",
        "M3P8-F1 validation",
        "finite validation of formula values (+/-inf)",
        '    if not math.isfinite(lin):\n        return f"formula',
        '    if math.isnan(lin):\n        return f"formula',
        not_designated("M3P8-F1_delta_i_plus_inf") + not_designated("M3P8-F1_delta_i_minus_inf"),
    ),
    (
        "oracle_check_removed",
        "M3P8-F1 validation",
        "finite validation of oracle values",
        ORACLE_CHECK,
        "if num is None:",
        not_designated("M3P8-F1_audit_oracle_delta_i_nan")
        + not_designated("M3P9-F1_oracle_delta_i_plus_inf")
        + ORDER_ESTIMATE_RAISES,
    ),
    (
        "invalid_sample_not_discarded",
        "M3P8-F1 validation",
        "invalid samples excluded from coverage",
        "                                errs[name] = None\n"
        "                                continue\n"
        "                            errs[name].append",
        "                            errs[name].append",
        not_designated("M3P8-F1_delta_i_plus_inf") + ORDER_ESTIMATE_RAISES,
    ),
    # M3P8-F1 audit: finite checks of the exact properties removed.
    (
        "E1_finite_check_removed",
        "M3P8-F1 audit",
        "E1 finite check",
        "if not math.isfinite(dev) or any(not math.isfinite(x) for row in r for x in row):",
        "if False:",
        not_designated_exact("M3P8-F1_audit_rotation_matrix_nan"),
    ),
    (
        "E2_finite_check_removed",
        "M3P8-F1 audit",
        "E2 finite check",
        "if not all(math.isfinite(x) for x in (d_i, d_node, exp_i, exp_node)):",
        "if False:",
        [wrap_guard_at("exact_properties: " + E2_IDENTITY_LINE)],
    ),
    (
        "E2_endpoint_finite_check_removed",
        "M3P8-F1 audit",
        "E2 endpoint finite check",
        "if not math.isfinite(rho):",
        "if False:",
        not_designated_exact("M3P8-F1_audit_rotation_matrix_nan"),
    ),
    (
        "E3_finite_check_removed",
        "M3P8-F1 audit",
        "E3 finite check",
        "if d_node is None or not all(math.isfinite(x) for x in (d_i, d_node)):",
        "if False:",
        not_designated_exact("M3P8-F1_audit_oracle_delta_i_nan"),
    ),
    (
        "E4_finite_check_removed",
        "M3P8-F1 audit",
        "E4 finite check",
        "if not math.isfinite(d_i):",
        "if False:",
        not_designated_exact("M3P8-F1_audit_oracle_delta_i_nan"),
    ),
    (
        "E5b_finite_check_removed",
        "M3P8-F1 audit",
        "E5b finite check",
        "if not math.isfinite(d_node):",
        "if False:",
        [wrap_guard_at("exact_properties: " + E5B_JUMP_LINE)],
    ),
    (
        "E6_finite_check_removed",
        "M3P8-F1 audit",
        "E6 finite check",
        "if d_node is None or not all(math.isfinite(x) for x in (d_i, d_node, lin_i, lin_node)):",
        "if False:",
        not_designated_exact("M3P8-F1_audit_oracle_delta_i_nan"),
    ),
    # M3P9-F1: oracle +/-inf rejection, through the entrypoint and with a weakened check.
    *[
        (
            f"oracle_{name}_{nonfinite_name(value)}_single_sample",
            "M3P9-F1 oracle",
            f"finite validation of the {name} oracle (one value)",
            ORACLE_CALL,
            oracle_injection(name, value, ONE_SAMPLE),
            [
                under_test(f"nonfinite {name} oracle={value!r} ", 1),
                under_test(f"coverage {name} ", 2),
            ],
        )
        for name in COMPONENT_NAMES
        for value in (math.inf, -math.inf)
    ],
    (
        "oracle_check_weakened_to_isnan",
        "M3P9-F1 oracle",
        "finite validation of oracle values (+/-inf)",
        ORACLE_CHECK,
        "if num is None or math.isnan(num):",
        [
            not_rejected("formula_defect_mutants", f"M3P9-F1_oracle_{name}_{label}")
            for name in COMPONENT_NAMES
            for label in ("plus_inf", "minus_inf")
        ]
        + ORDER_ESTIMATE_RAISES,
    ),
    (
        "oracle_check_weakened_to_isinf",
        "M3P9-F1 oracle",
        "finite validation of oracle values (NaN)",
        ORACLE_CHECK,
        "if num is None or math.isinf(num):",
        not_designated("M3P8-F1_audit_oracle_delta_i_nan")
        + not_designated("M3P8-F1_audit_oracle_delta_node_nan"),
    ),
    # M3P9-F2: order and sign assertions, each formula separately.
    (
        "delta_i_coefficient_doubled",
        "M3P9-F2 order and sign",
        "delta_i order check",
        FORMULA,
        f"return -2.0 * delta * math.cos(node - phi), {NODE_TERM}",
        [under_test("order delta_i ", 560), under_test("sign delta_i ", 0)],
    ),
    (
        "delta_node_coefficient_doubled",
        "M3P9-F2 order and sign",
        "delta_node order check",
        FORMULA,
        "return -delta * math.cos(node - phi), 2.0 * delta / math.tan(inc) * math.sin(node - phi)",
        [under_test("order delta_node ", 504), under_test("sign delta_node ", 0)],
    ),
    (
        "order_assertion_disabled",
        "M3P9-F2 order and sign",
        "order check (both formulas)",
        ORDER_ASSERT,
        "if False:",
        not_designated("M3P9-F2_delta_i_coefficient_doubled")
        + not_designated("M3P9-F2_delta_node_coefficient_doubled"),
    ),
    (
        "delta_i_order_assertion_disabled",
        "M3P9-F2 order and sign",
        "delta_i order check",
        ORDER_ASSERT,
        'if p < P_MIN and name != "delta_i":',
        not_designated("M3P9-F2_delta_i_coefficient_doubled"),
    ),
    (
        "delta_node_order_assertion_disabled",
        "M3P9-F2 order and sign",
        "delta_node order check",
        ORDER_ASSERT,
        'if p < P_MIN and name != "delta_node":',
        not_designated("M3P9-F2_delta_node_coefficient_doubled"),
    ),
    (
        "sign_assertion_disabled",
        "M3P9-F2 order and sign",
        "sign check (both formulas)",
        SIGN_ASSERT,
        "if False:",
        not_designated("M3P9-F2_delta_i_sign_reversed")
        + not_designated("M3P9-F2_delta_node_sign_reversed"),
    ),
    (
        "delta_i_sign_assertion_disabled",
        "M3P9-F2 order and sign",
        "delta_i sign check",
        SIGN_ASSERT,
        'if (n > 0.0) != (lin_v > 0.0) and name != "delta_i":',
        not_designated("M3P9-F2_delta_i_sign_reversed"),
    ),
    (
        "delta_node_sign_assertion_disabled",
        "M3P9-F2 order and sign",
        "delta_node sign check",
        SIGN_ASSERT,
        'if (n > 0.0) != (lin_v > 0.0) and name != "delta_node":',
        not_designated("M3P9-F2_delta_node_sign_reversed"),
    ),
    # M3P9-F3: exact-property assertions.
    (
        "E3_assertion_removed",
        "M3P9-F3 exact properties",
        "E3 closed-form deviation assertion",
        E3_ASSERT,
        "",
        not_designated_exact("M3P9-F3_oracle_delta_i_scaled_1pct"),
    ),
    (
        "E4_assertion_removed",
        "M3P9-F3 exact properties",
        "E4 inclination-bound assertion",
        E4_ASSERT,
        "",
        not_designated_exact("M3P9-F3_oracle_delta_i_scaled_1pct"),
    ),
    # Earlier findings (reviews 05-07), preserved.
    (
        "M3P5_delta_i_sign_reversed",
        "earlier",
        "delta_i sign check",
        FORMULA,
        FORMULA.replace("-delta", "delta", 1),
        [under_test("sign delta_i ", 560)],
    ),
    (
        "M3P5_delta_node_sign_reversed",
        "earlier",
        "delta_node sign check",
        FORMULA,
        FORMULA.replace(", delta /", ", -delta /"),
        [under_test("sign delta_node ", 504)],
    ),
    (
        "M3P6-F1_unrestricted_claim_restored",
        "earlier",
        "E2 line-of-nodes identity",
        "    j = inc - delta\n    if 0.0 < j < PI:",
        "    j = inc - delta\n    return -delta, 0.0\n    if 0.0 < j < PI:",
        [exact("E2 ")],
    ),
    (
        "M3P6-F2_E5a_removed",
        "earlier",
        "E5a node-jump assertion",
        "if circ(d_node, PI, wrap) > tol:",
        "if False:",
        not_designated_exact("M3P6-F2_oracle_jump_suppressed"),
    ),
    (
        "M3P6-F2_E5b_removed",
        "earlier",
        "E5b node-jump assertion",
        "if circ(d_node, PI, wrap) > pair_noise(inc, inc + d_i):",
        "if False:",
        not_designated_exact("M3P6-F2_oracle_jump_suppressed"),
    ),
    (
        "M3P6-F2_E5c_removed",
        "earlier",
        "E5c jump-assertion coverage guard",
        "if jump_asserts[sign] < MIN_CROSSINGS_PER_SIGN + 1:",
        "if False:",
        not_designated_exact("M3P6-F2_jump_assertion_disabled"),
    ),
    (
        "M3P6-F3_previous_wrap_implementation",
        "earlier",
        "wrap interval (-pi, pi]",
        WRAP_BODY,
        '        raise ValueError(f"{NONFINITE_MESSAGE}: {a!r}")\n'
        "    return a - 2.0 * math.pi * math.floor((a + math.pi) / (2.0 * math.pi))\n",
        [exact("wrap(")],
    ),
    (
        "M3P7-F1_guard_removed",
        "earlier",
        "wrap non-finite guard",
        WRAP_GUARD,
        "    r = math.fmod(a, TAU)\n",
        [exact("wrap-nonfinite: ")],
    ),
    (
        "M3P7-F1_message_check_weakened_to_type_only",
        "earlier",
        "wrap non-finite test (message check)",
        "ok = str(exc).startswith(NONFINITE_MESSAGE)",
        "ok = True",
        not_designated_exact("M3P7-F1_nonfinite_guard_removed"),
    ),
    (
        "M3P7-F1_nonfinite_tests_disabled",
        "earlier",
        "wrap non-finite tests",
        "for name, a in cases.items():",
        "for name, a in {}.items():",
        [unexercised("exact_and_wrap_mutants", "M3P7-F1_nonfinite_guard_removed")]
        + [report_missing("wrap_nonfinite", k) for k in ("nan", "plus_inf", "minus_inf")],
    ),
    *injection_matrix(),
]


SCALED = "        out[component] *= factor\n"
E2_FINITE = "if not all(math.isfinite(x) for x in (d_i, d_node, exp_i, exp_node)):"
E5B_FINITE = "if not math.isfinite(d_node):"

EXPECTED = "expected rejection"
CATEGORIES = (
    "invalid mutation setup",
    "process failure",
    "normal execution",
    "unexpected exception",
    "rejected for another reason",
    EXPECTED,
)

# Controls (I-9 section 6, I-10 section 3): (name, what it shows, edits, expectation, category).
# edits: a list of (old fragment, new fragment), or None to run a script path that does not
# exist. expectation: the name of the mutation whose declared expected rejection is claimed.
CONTROLS = [
    (
        "syntax_error",
        "a syntax error is a process failure, not a detection",
        [(FORMULA, "return (")],
        "delta_i_formula_returns_nan",
        "process failure",
    ),
    (
        "import_failure",
        "an import failure that ends the process is not a detection",
        [("import json\n", "import json\nimport m3p9_control_missing_module\n")],
        "delta_i_formula_returns_nan",
        "process failure",
    ),
    (
        "missing_script",
        "a missing script is not a detection",
        None,
        "delta_i_formula_returns_nan",
        "process failure",
    ),
    (
        "neutral_edit",
        "a run that completes with verdict PASS is normal execution",
        [("import json\n", "import json  # neutral edit\n")],
        "delta_i_formula_returns_nan",
        "normal execution",
    ),
    (
        "fragment_absent",
        "a mutation whose fragment does not occur is invalid setup and is not run",
        [("m3p10 control: this fragment does not occur", "x")],
        "delta_i_formula_returns_nan",
        "invalid mutation setup",
    ),
    (
        "wrong_reason",
        "a mutant rejected for an unrelated reason is not detected",
        [(FORMULA, FORMULA.replace("-delta", "delta", 1))],
        "M3P5_delta_node_sign_reversed",
        "rejected for another reason",
    ),
    (
        "import_failure_inside_mutant",
        "an import failure inside a built-in mutant is not detection (M3P10-F1)",
        [
            (
                SCALED,
                "        if factor == 2.0:\n"
                "            import m3p10_control_missing_module  # noqa: F401\n" + SCALED,
            )
        ],
        "order_assertion_disabled",
        "unexpected exception",
    ),
    (
        "runtime_exception_inside_mutant",
        "an unrelated runtime exception inside a built-in mutant is not detection",
        [(SCALED, "        if factor == -1.0:\n            _ = factor / 0.0\n" + SCALED)],
        "sign_assertion_disabled",
        "unexpected exception",
    ),
    (
        "exception_suppressed_inside_mutant",
        "an exception caught and suppressed by a mutant (which then returns the reference "
        "result) is not detection: its defect is no longer exercised",
        [
            (
                SCALED,
                "        if factor == 2.0:\n"
                "            try:\n"
                "                import m3p10_control_missing_module  # noqa: F401\n"
                "            except ImportError:\n"
                "                return formulas_amendment2(inc, node, phi, delta)\n" + SCALED,
            )
        ],
        "order_assertion_disabled",
        "invalid mutation setup",
    ),
    (
        "allowed_exception_wrong_location",
        "the allowed wrap-guard exception raised at E5b, claimed for the E2 removal, is not "
        "accepted",
        [(E5B_FINITE, "if False:")],
        "E2_finite_check_removed",
        "unexpected exception",
    ),
    (
        "allowed_exception_wrong_type",
        "the allowed exception at the right location but of another type (TypeError) is not "
        "accepted",
        [
            (E2_FINITE, "if False:"),
            (WRAP_GUARD, WRAP_GUARD.replace("raise ValueError", "raise TypeError")),
        ],
        "E2_finite_check_removed",
        "unexpected exception",
    ),
    (
        "valid_mutant_rejected_by_targeted_check",
        "an injected defect rejected by its targeted check is detected",
        "delta_i_coefficient_doubled",
        "delta_i_coefficient_doubled",
        EXPECTED,
    ),
    (
        "valid_mutant_completes_without_rejection",
        "with the Delta i order assertion removed, the designated built-in mutant completes, "
        "exercises its defect and is not rejected; that is detected as the removal",
        "delta_i_order_assertion_disabled",
        "delta_i_order_assertion_disabled",
        EXPECTED,
    ),
]
MUTATION_INDEX = {m[0]: m for m in MUTATIONS}


def run(source, workdir, label):
    """Run one copy of the script; return (exit code, output or None, last stderr line).

    source = None runs a path that does not exist (control)."""
    copy = workdir / f"{label}.py"
    out = workdir / f"{label}.json"
    if source is not None:
        copy.write_text(source, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-I", str(copy), str(out)],
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    stderr = proc.stderr.strip()
    last = stderr.splitlines()[-1] if stderr else ""
    # Machine-specific paths are replaced so that two runs give byte-identical output.
    last = last.replace(str(workdir), "<tmp>").replace(sys.executable, "<python>")
    output = json.loads(out.read_text(encoding="ascii")) if out.exists() and not stderr else None
    return proc.returncode, output, last


def recorded_exceptions(output):
    """(section, mutant, exception) for every built-in mutant that raised."""
    return [
        (section, name, entry["exception"])
        for section in FLAGS
        for name, entry in output[section].items()
        if "exception" in entry
    ]


def classify(code, output, last, expected):
    """Return (category, observed outcome). Only EXPECTED is a detection."""
    if output is None:
        return "process failure", f"exit {code}, no output: {last or 'no stderr'}"
    observed = f"exit {code}, {output['verdict']} verdict"
    if code == 0 and output["verdict"] == "PASS":
        return "normal execution", observed
    if code != 1 or output["verdict"] != "FAIL":
        return "process failure", observed + " (inconsistent exit status and verdict)"
    allowed = {(p[1], p[2]): p for p in expected if p[0] == "raised"}
    unexpected = [
        f"{name} raised {exc['type']}: {exc['message']} at {' > '.join(exc['stack'])}"
        for section, name, exc in recorded_exceptions(output)
        if not ((section, name) in allowed and matches(allowed[section, name], exc))
    ]
    if unexpected:
        return "unexpected exception", observed + "; " + "; ".join(unexpected)
    unexercised = [
        p[2]
        for p in expected
        if p[0] == "not_rejected" and not output[p[1]][p[2]]["defect_exercised"]
    ]
    if unexercised:
        return "invalid mutation setup", observed + "; defect not exercised: " + ", ".join(
            unexercised
        )
    failed = [describe(p) for p in expected if not holds(p, output)]
    if failed:
        return "rejected for another reason", observed + "; not shown: " + "; ".join(failed)
    allowed_seen = [f"{p[2]} raised {p[3]} as allowed" for p in allowed.values()]
    return EXPECTED, observed + "; expected rejection shown" + "".join(
        f"; {a}" for a in allowed_seen
    )


def apply_edits(original, edits):
    """The mutated source, or None with the reason if some fragment is not unique."""
    source = original
    for old, new in edits:
        count = source.count(old)
        if count != 1:
            return None, f"not run: fragment occurs {count} times"
        source = source.replace(old, new)
    return source, None


def run_control(control, original, workdir):
    """Run one control; return its report entry."""
    name, shows, edits, claimed, category = control
    expected = MUTATION_INDEX[claimed][5]
    if isinstance(edits, str):  # a mutation of MUTATIONS, by name
        edits = [MUTATION_INDEX[edits][3:5]]
    if edits is None:
        actual, observed = classify(*run(None, workdir, f"control_{name}"), expected)
    else:
        source, problem = apply_edits(original, edits)
        if source is None:
            actual, observed = "invalid mutation setup", problem
        else:
            actual, observed = classify(*run(source, workdir, f"control_{name}"), expected)
    return {
        "shows": shows,
        "claimed_expectation": claimed,
        "expected_classification": category,
        "actual_classification": actual,
        "observed_outcome": observed,
        "result": "PASS" if actual == category else "FAIL",
    }


def main(out_path):
    original = SCRIPT.read_text(encoding="utf-8")
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        workdir = pathlib.Path(tmp)
        code, output, last = run(original, workdir, "baseline")
        baseline_ok = code == 0 and output is not None and output["verdict"] == "PASS"
        baseline = {
            "exit_code": code,
            "outcome": f"{output['verdict']} verdict" if output else f"no output: {last}",
        }
        vacuous = []
        if output is not None:
            baseline_ok = baseline_ok and not recorded_exceptions(output)
            for name, _, _, _, _, expected in MUTATIONS:
                if all(holds(p, output) for p in expected):
                    vacuous.append(name)
        baseline["expectations_already_true_at_baseline"] = vacuous
        baseline_ok = baseline_ok and not vacuous
        for name, group, target, old, new, expected in MUTATIONS:
            entry = {
                "group": group,
                "target_property": target,
                "expected_rejection": [describe(p) for p in expected],
            }
            source, problem = apply_edits(original, [(old, new)])
            if name in results or source is None:
                category, observed = "invalid mutation setup", problem or "duplicate name"
            else:
                category, observed = classify(*run(source, workdir, name), expected)
            entry["classification"] = category
            entry["observed_outcome"] = observed
            entry["result"] = "PASS" if category == EXPECTED else "FAIL"
            results[name + ("#duplicate" if name in results else "")] = entry
        controls = {c[0]: run_control(c, original, workdir) for c in CONTROLS}
    groups = {}
    for entry in results.values():
        g = groups.setdefault(entry["group"], {"mutations": 0, "detected": 0})
        g["mutations"] += 1
        g["detected"] += entry["result"] == "PASS"
    detected = sum(1 for r in results.values() if r["result"] == "PASS")
    controls_ok = all(c["result"] == "PASS" for c in controls.values())
    ok = baseline_ok and controls_ok and detected == len(MUTATIONS) == len(results)
    report = {
        "verdict": "PASS" if ok else "FAIL",
        "script": SCRIPT.name,
        "baseline": baseline,
        "mutations": len(MUTATIONS),
        "detected": detected,
        "groups": groups,
        "controls": controls,
        "results": results,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")
    summary = ("verdict", "mutations", "detected", "groups")
    print(json.dumps({k: report[k] for k in summary}))
    print(json.dumps({k: c["result"] for k, c in controls.items()}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
