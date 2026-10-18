"""DR-0028 amendments 5-9 / reviews M3P8-F1, M3P9-F1..F3, M3P10-F1, M3P11-F1, M3P12-F1:
file-level mutation check of dr0028_node_signed_verification.py through its real entrypoint.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python dr0028_node_signed_mutation_check.py <out.json>

Each mutation replaces one exact text fragment of the verification script (the fragment must
occur exactly once), writes the mutated copy to a temporary directory and runs it as a separate
process (`python -I <copy> <out.json>`), exactly as the script is normally run.

Each mutation declares its expected rejection as predicates on the script's output, and every
run is classified into exactly one category (M3P10-F1; I-10 section 2):
- "invalid mutation setup": the fragment does not occur exactly once (the copy is not run), or
  the mutation's intended defect is not established as exercised (see below);
- "process failure": the process wrote no output (a syntax error, import failure, missing file
  or any other crash), or its exit status and verdict are inconsistent;
- "normal execution": exit 0 with verdict PASS (the mutation survived);
- "unexpected exception": a built-in mutant raised an exception that the mutation's expectation
  does not allow, by mutant, exception type, message and call stack;
- "rejected for another reason": exit 1 with verdict FAIL, but the expected rejection is not
  shown;
- "expected rejection": exit 1 with verdict FAIL, no unexpected exception, and every predicate
  holds. Only this category is a detection.

Defect exercise (M3P11-F1, DR-0028 amendment 8; I-11 section 2). Every mutation declares an
exercise predicate for its intended defect, and a detection requires that the defect is
established as exercised AND that the expected rejection is shown. Exercise is decided by an
independent probe: a separate process (this file with --probe) that loads the unmutated script
and the mutated copy, and observes the copy's injected defect against the unmutated script's
reference implementations and declared defects. The probe reads only the injected function's
arguments and outcomes (or, for an oracle value injected inside check_formulas, the value handed
to the finite validation), never a check's result. Each observed call is intended, unchanged,
missing or unintended (the script's call_kind); the defect is exercised only if it is shown at
least once, never missing and nothing else differs, so a difference alone (rounding, a
reassociated fallback, another component) is never evidence. Predicate families:
- built-in: the mutation weakens a check, and its evidence is a built-in mutant of the script
  (not_rejected, raised, unexercised predicates). Each such mutant is observed in its designated
  test of the unmutated script, with the mutant taken from the copy; the copy's own record must
  agree (exercised, or not exercised for an "unexercised" predicate);
- formula: the formula under test is edited; it is observed against formulas_amendment2;
- oracle values: an oracle value is replaced inside check_formulas. Amendment 9 (M3P12-F1): the
  samples that check_formulas evaluates are fixed first from the unmutated script's grid
  (oracle_schedule); the copy's check_formulas then runs with an observing formula, which it
  calls at every step after the oracle value and before any validation, so steps that the
  validation skips after an invalid value are observed too. Every scheduled sample must be
  observed exactly once (none unobserved, duplicate or unscheduled), and the defect must be shown
  at every sample where it is claimed. (Amendment 8 observed the value reaching the finite
  validation, which misses the steps skipped after the first invalid value.) The unmutated
  script must observe the whole schedule;
- injected: wrap() or line_of_nodes_exact() is edited; it is observed in the exact properties.
A direct (non built-in) predicate must not be met by the unmutated script.

A built-in mutant counts as "not rejected" (the evidence that an assertion was removed) only if
it completed without an exception, its designated checks stayed silent, and its intended defect
was exercised. An exception is accepted only where a "raised" predicate allows exactly that
mutant, type, message prefix and stack. These allowances are limited to the E2 and E5b
wrap-guard cases and to the order-estimate math domain error of the four mutations that let an
oracle +/-inf through the finite validation.

The unmutated script must exit 0 with verdict PASS, and no expectation may already be met by its
output. Controls (I-10 section 3, I-11 section 2) each declare the category they must receive and
whether the claimed defect is exercised: process-level failures, a neutral edit, invalid setup,
wrong reasons, exceptions raised or suppressed inside built-in mutants, an allowed exception at
the wrong location or of the wrong type, defects that are absent, partial, in another component or
rounding only, a tampered in-script record, expected exceptions, and valid mutations; and (I-12
section 3) oracle values injected at the first, the last or some steps only but claimed at every
step, missing intermediate observations, an incorrect observation count, and a correct injection
at every step. Each control also declares the reason it must show (CONTROL_REASONS). Exit status
0 only if the baseline passes, every mutation is detected and every control receives its
declared category, exercise result and reason. Standard library only.
"""

import importlib.util
import json
import math
import pathlib
import subprocess
import sys
import tempfile

SCRIPT = pathlib.Path(__file__).with_name("dr0028_node_signed_verification.py")
HARNESS = pathlib.Path(__file__).resolve()
BUILT_IN = ("built-in",)  # exercise predicate derived from the expectation's built-in mutants
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
                        ("formula", "component", index, repr(value), condition),
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
                        ("oracle values", COMPONENT_NAMES.index(name), repr(value), condition),
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
            ("formula", "component", COMPONENT_NAMES.index(name), repr(value), "True"),
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
        BUILT_IN,
    ),
    (
        "delta_node_coverage_disabled",
        "M3P8-F1 coverage",
        "delta_node coverage minima",
        COVERAGE_LOOP,
        COVERAGE_LOOP.replace("in COMPONENTS", 'in ("delta_i",)'),
        not_designated("M3P8-F1_delta_node_zero"),
        BUILT_IN,
    ),
    (
        "sign_coverage_removed",
        "M3P8-F1 coverage",
        "sign coverage minima",
        COVERAGE_PAIRS,
        '(("order", len(orders[name])),)',
        not_designated("M3P8-F1_delta_i_zero") + not_designated("M3P8-F1_delta_node_zero"),
        BUILT_IN,
    ),
    (
        "order_coverage_removed",
        "M3P8-F1 coverage",
        "order coverage minima",
        COVERAGE_PAIRS,
        '(("sign", signs[name]),)',
        not_designated("M3P8-F1_delta_i_nan") + not_designated("M3P8-F1_delta_node_nan"),
        BUILT_IN,
    ),
    (
        "coverage_comparison_disabled",
        "M3P8-F1 coverage",
        "coverage comparison",
        "if not count >= minimum:",
        "if False:",
        not_designated("M3P8-F1_delta_i_zero") + not_designated("M3P8-F1_delta_node_zero"),
        BUILT_IN,
    ),
    (
        "sign_counter_moved_outside_gate",
        "M3P8-F1 coverage",
        "sign coverage counter",
        SIGN_GATE,
        "                        signs[name] += 1\n"
        "                        if abs(n) >= tol and abs(lin_v) >= tol:\n",
        not_designated("M3P8-F1_delta_i_zero") + not_designated("M3P8-F1_delta_node_zero"),
        BUILT_IN,
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
        BUILT_IN,
    ),
    (
        "formula_check_weakened_to_isnan",
        "M3P8-F1 validation",
        "finite validation of formula values (+/-inf)",
        '    if not math.isfinite(lin):\n        return f"formula',
        '    if math.isnan(lin):\n        return f"formula',
        not_designated("M3P8-F1_delta_i_plus_inf") + not_designated("M3P8-F1_delta_i_minus_inf"),
        BUILT_IN,
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
        BUILT_IN,
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
        BUILT_IN,
    ),
    # M3P8-F1 audit: finite checks of the exact properties removed.
    (
        "E1_finite_check_removed",
        "M3P8-F1 audit",
        "E1 finite check",
        "if not math.isfinite(dev) or any(not math.isfinite(x) for row in r for x in row):",
        "if False:",
        not_designated_exact("M3P8-F1_audit_rotation_matrix_nan"),
        BUILT_IN,
    ),
    (
        "E2_finite_check_removed",
        "M3P8-F1 audit",
        "E2 finite check",
        "if not all(math.isfinite(x) for x in (d_i, d_node, exp_i, exp_node)):",
        "if False:",
        [wrap_guard_at("exact_properties: " + E2_IDENTITY_LINE)],
        BUILT_IN,
    ),
    (
        "E2_endpoint_finite_check_removed",
        "M3P8-F1 audit",
        "E2 endpoint finite check",
        "if not math.isfinite(rho):",
        "if False:",
        not_designated_exact("M3P8-F1_audit_rotation_matrix_nan"),
        BUILT_IN,
    ),
    (
        "E3_finite_check_removed",
        "M3P8-F1 audit",
        "E3 finite check",
        "if d_node is None or not all(math.isfinite(x) for x in (d_i, d_node)):",
        "if False:",
        not_designated_exact("M3P8-F1_audit_oracle_delta_i_nan"),
        BUILT_IN,
    ),
    (
        "E4_finite_check_removed",
        "M3P8-F1 audit",
        "E4 finite check",
        "if not math.isfinite(d_i):",
        "if False:",
        not_designated_exact("M3P8-F1_audit_oracle_delta_i_nan"),
        BUILT_IN,
    ),
    (
        "E5b_finite_check_removed",
        "M3P8-F1 audit",
        "E5b finite check",
        "if not math.isfinite(d_node):",
        "if False:",
        [wrap_guard_at("exact_properties: " + E5B_JUMP_LINE)],
        BUILT_IN,
    ),
    (
        "E6_finite_check_removed",
        "M3P8-F1 audit",
        "E6 finite check",
        "if d_node is None or not all(math.isfinite(x) for x in (d_i, d_node, lin_i, lin_node)):",
        "if False:",
        not_designated_exact("M3P8-F1_audit_oracle_delta_i_nan"),
        BUILT_IN,
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
            ("oracle values", COMPONENT_NAMES.index(name), repr(value), ONE_SAMPLE),
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
        BUILT_IN,
    ),
    (
        "oracle_check_weakened_to_isinf",
        "M3P9-F1 oracle",
        "finite validation of oracle values (NaN)",
        ORACLE_CHECK,
        "if num is None or math.isinf(num):",
        not_designated("M3P8-F1_audit_oracle_delta_i_nan")
        + not_designated("M3P8-F1_audit_oracle_delta_node_nan"),
        BUILT_IN,
    ),
    # M3P9-F2: order and sign assertions, each formula separately.
    (
        "delta_i_coefficient_doubled",
        "M3P9-F2 order and sign",
        "delta_i order check",
        FORMULA,
        f"return -2.0 * delta * math.cos(node - phi), {NODE_TERM}",
        [under_test("order delta_i ", 560), under_test("sign delta_i ", 0)],
        ("formula", "scaled", 2.0, 1.0),
    ),
    (
        "delta_node_coefficient_doubled",
        "M3P9-F2 order and sign",
        "delta_node order check",
        FORMULA,
        "return -delta * math.cos(node - phi), 2.0 * delta / math.tan(inc) * math.sin(node - phi)",
        [under_test("order delta_node ", 504), under_test("sign delta_node ", 0)],
        ("formula", "scaled", 1.0, 2.0),
    ),
    (
        "order_assertion_disabled",
        "M3P9-F2 order and sign",
        "order check (both formulas)",
        ORDER_ASSERT,
        "if False:",
        not_designated("M3P9-F2_delta_i_coefficient_doubled")
        + not_designated("M3P9-F2_delta_node_coefficient_doubled"),
        BUILT_IN,
    ),
    (
        "delta_i_order_assertion_disabled",
        "M3P9-F2 order and sign",
        "delta_i order check",
        ORDER_ASSERT,
        'if p < P_MIN and name != "delta_i":',
        not_designated("M3P9-F2_delta_i_coefficient_doubled"),
        BUILT_IN,
    ),
    (
        "delta_node_order_assertion_disabled",
        "M3P9-F2 order and sign",
        "delta_node order check",
        ORDER_ASSERT,
        'if p < P_MIN and name != "delta_node":',
        not_designated("M3P9-F2_delta_node_coefficient_doubled"),
        BUILT_IN,
    ),
    (
        "sign_assertion_disabled",
        "M3P9-F2 order and sign",
        "sign check (both formulas)",
        SIGN_ASSERT,
        "if False:",
        not_designated("M3P9-F2_delta_i_sign_reversed")
        + not_designated("M3P9-F2_delta_node_sign_reversed"),
        BUILT_IN,
    ),
    (
        "delta_i_sign_assertion_disabled",
        "M3P9-F2 order and sign",
        "delta_i sign check",
        SIGN_ASSERT,
        'if (n > 0.0) != (lin_v > 0.0) and name != "delta_i":',
        not_designated("M3P9-F2_delta_i_sign_reversed"),
        BUILT_IN,
    ),
    (
        "delta_node_sign_assertion_disabled",
        "M3P9-F2 order and sign",
        "delta_node sign check",
        SIGN_ASSERT,
        'if (n > 0.0) != (lin_v > 0.0) and name != "delta_node":',
        not_designated("M3P9-F2_delta_node_sign_reversed"),
        BUILT_IN,
    ),
    # M3P9-F3: exact-property assertions.
    (
        "E3_assertion_removed",
        "M3P9-F3 exact properties",
        "E3 closed-form deviation assertion",
        E3_ASSERT,
        "",
        not_designated_exact("M3P9-F3_oracle_delta_i_scaled_1pct"),
        BUILT_IN,
    ),
    (
        "E4_assertion_removed",
        "M3P9-F3 exact properties",
        "E4 inclination-bound assertion",
        E4_ASSERT,
        "",
        not_designated_exact("M3P9-F3_oracle_delta_i_scaled_1pct"),
        BUILT_IN,
    ),
    # Earlier findings (reviews 05-07), preserved.
    (
        "M3P5_delta_i_sign_reversed",
        "earlier",
        "delta_i sign check",
        FORMULA,
        FORMULA.replace("-delta", "delta", 1),
        [under_test("sign delta_i ", 560)],
        ("formula", "scaled", -1.0, 1.0),
    ),
    (
        "M3P5_delta_node_sign_reversed",
        "earlier",
        "delta_node sign check",
        FORMULA,
        FORMULA.replace(", delta /", ", -delta /"),
        [under_test("sign delta_node ", 504)],
        ("formula", "scaled", 1.0, -1.0),
    ),
    (
        "M3P6-F1_unrestricted_claim_restored",
        "earlier",
        "E2 line-of-nodes identity",
        "    j = inc - delta\n    if 0.0 < j < PI:",
        "    j = inc - delta\n    return -delta, 0.0\n    if 0.0 < j < PI:",
        [exact("E2 ")],
        (
            "injected",
            "line_of_nodes",
            "line_of_nodes_exact",
            "LINE_OF_NODES_DEFECTS",
            "unrestricted",
        ),
    ),
    (
        "M3P6-F2_E5a_removed",
        "earlier",
        "E5a node-jump assertion",
        "if circ(d_node, PI, wrap) > tol:",
        "if False:",
        not_designated_exact("M3P6-F2_oracle_jump_suppressed"),
        BUILT_IN,
    ),
    (
        "M3P6-F2_E5b_removed",
        "earlier",
        "E5b node-jump assertion",
        "if circ(d_node, PI, wrap) > pair_noise(inc, inc + d_i):",
        "if False:",
        not_designated_exact("M3P6-F2_oracle_jump_suppressed"),
        BUILT_IN,
    ),
    (
        "M3P6-F2_E5c_removed",
        "earlier",
        "E5c jump-assertion coverage guard",
        "if jump_asserts[sign] < MIN_CROSSINGS_PER_SIGN + 1:",
        "if False:",
        not_designated_exact("M3P6-F2_jump_assertion_disabled"),
        BUILT_IN,
    ),
    (
        "M3P6-F3_previous_wrap_implementation",
        "earlier",
        "wrap interval (-pi, pi]",
        WRAP_BODY,
        '        raise ValueError(f"{NONFINITE_MESSAGE}: {a!r}")\n'
        "    return a - 2.0 * math.pi * math.floor((a + math.pi) / (2.0 * math.pi))\n",
        [exact("wrap("), exact("wrap endpoint (")],
        ("injected", "wrap_fn", "wrap", "WRAP_DEFECTS", "previous_guarded"),
    ),
    (
        "M3P7-F1_guard_removed",
        "earlier",
        "wrap non-finite guard",
        WRAP_GUARD,
        "    r = math.fmod(a, TAU)\n",
        [exact("wrap-nonfinite: ")],
        ("injected", "wrap_fn", "wrap", "WRAP_DEFECTS", "guard_removed"),
    ),
    (
        "M3P7-F1_message_check_weakened_to_type_only",
        "earlier",
        "wrap non-finite test (message check)",
        "ok = str(exc).startswith(NONFINITE_MESSAGE)",
        "ok = True",
        not_designated_exact("M3P7-F1_nonfinite_guard_removed"),
        BUILT_IN,
    ),
    (
        "M3P7-F1_nonfinite_tests_disabled",
        "earlier",
        "wrap non-finite tests",
        "for name, a in cases.items():",
        "for name, a in {}.items():",
        [unexercised("exact_and_wrap_mutants", "M3P7-F1_nonfinite_guard_removed")]
        + [report_missing("wrap_nonfinite", k) for k in ("nan", "plus_inf", "minus_inf")],
        BUILT_IN,
    ),
    *injection_matrix(),
]


MUTATION_INDEX = {m[0]: m for m in MUTATIONS}

SCALED = "        out[component] *= factor\n"
E2_FINITE = "if not all(math.isfinite(x) for x in (d_i, d_node, exp_i, exp_node)):"
E5B_FINITE = "if not math.isfinite(d_node):"
EXERCISED_RETURN = "    return all(key_exercised(r) for r in record.values()) and any(\n"
DELTA_NODE_DOUBLED = MUTATION_INDEX["delta_node_coefficient_doubled"][4]
# Review 11's counterexample (M3P11-F1): the import failure is suppressed and the fallback returns
# the correct formulas, with the Delta Omega product reassociated (a rounding-level difference).
REVIEW11_FALLBACK = (
    "        if factor == 2.0:\n"
    "            try:\n"
    "                import nonexistent_review11_dependency  # noqa: F401\n"
    "            except ImportError:\n"
    "                return (\n"
    "                    -delta * math.cos(node - phi),\n"
    "                    delta * (math.sin(node - phi) / math.tan(inc)),\n"
    "                )\n"
)
SUPPRESSED_FALLBACK = (
    "        if factor == 2.0:\n"
    "            try:\n"
    "                import m3p10_control_missing_module  # noqa: F401\n"
    "            except ImportError:\n"
    "                return formulas_amendment2(inc, node, phi, delta)\n"
)

EXPECTED = "expected rejection"
CATEGORIES = (
    "invalid mutation setup",
    "process failure",
    "normal execution",
    "unexpected exception",
    "rejected for another reason",
    EXPECTED,
)
INVALID = CATEGORIES[0]

# Controls (I-9 section 6, I-10 section 3, I-11 section 2): (name, what it shows, edits,
# expectation, category, exercise). edits: a list of (old fragment, new fragment), the name of a
# mutation, or None to run a script path that does not exist. expectation: the name of the
# mutation whose declared expected rejection and exercise predicate are claimed. exercise: whether
# the claimed intended defect must be established as exercised (None: no copy produced output).
CONTROLS = [
    (
        "syntax_error",
        "a syntax error is a process failure, not a detection",
        [(FORMULA, "return (")],
        "delta_i_formula_returns_nan",
        "process failure",
        None,
    ),
    (
        "import_failure",
        "an import failure that ends the process is not a detection",
        [("import json\n", "import json\nimport m3p9_control_missing_module\n")],
        "delta_i_formula_returns_nan",
        "process failure",
        None,
    ),
    (
        "missing_script",
        "a missing script is not a detection",
        None,
        "delta_i_formula_returns_nan",
        "process failure",
        None,
    ),
    (
        "neutral_edit",
        "a run that completes with verdict PASS is normal execution; the probe sees no defect",
        [("import json\n", "import json  # neutral edit\n")],
        "delta_i_formula_returns_nan",
        "normal execution",
        False,
    ),
    (
        "fragment_absent",
        "a mutation whose fragment does not occur is invalid setup and is not run",
        [("m3p10 control: this fragment does not occur", "x")],
        "delta_i_formula_returns_nan",
        INVALID,
        None,
    ),
    (
        "wrong_reason",
        "a Delta i sign reversal claimed as the Delta Omega sign reversal is not detected: the "
        "claimed defect is not exercised (amendment 8; amendment 7 classified it 'rejected for "
        "another reason')",
        [(FORMULA, FORMULA.replace("-delta", "delta", 1))],
        "M3P5_delta_node_sign_reversed",
        INVALID,
        False,
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
        False,
    ),
    (
        "runtime_exception_inside_mutant",
        "an unrelated runtime exception inside a built-in mutant is not detection",
        [(SCALED, "        if factor == -1.0:\n            _ = factor / 0.0\n" + SCALED)],
        "sign_assertion_disabled",
        "unexpected exception",
        False,
    ),
    (
        "exception_suppressed_inside_mutant",
        "an exception caught and suppressed by a mutant (which then returns the reference "
        "result) is not detection: its defect is no longer exercised",
        [(SCALED, SUPPRESSED_FALLBACK + SCALED)],
        "order_assertion_disabled",
        INVALID,
        False,
    ),
    (
        "allowed_exception_wrong_location",
        "the allowed wrap-guard exception raised at E5b, claimed for the E2 removal, is not "
        "accepted",
        [(E5B_FINITE, "if False:")],
        "E2_finite_check_removed",
        "unexpected exception",
        True,
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
        True,
    ),
    (
        "valid_mutant_rejected_by_targeted_check",
        "an injected defect rejected by its targeted check is detected",
        "delta_i_coefficient_doubled",
        "delta_i_coefficient_doubled",
        EXPECTED,
        True,
    ),
    (
        "valid_mutant_completes_without_rejection",
        "with the Delta i order assertion removed, the designated built-in mutant completes, "
        "exercises its defect and is not rejected; that is detected as the removal",
        "delta_i_order_assertion_disabled",
        "delta_i_order_assertion_disabled",
        EXPECTED,
        True,
    ),
    # M3P11-F1 regression controls: each was classified as detection by the harness reviewed in
    # review 11 (c16b3b5), because any difference counted as an exercised defect.
    (
        "suppressed_import_reassociated_fallback",
        "review 11's counterexample: a suppressed import failure followed by the correct "
        "formulas with a reassociated product is not an exercised defect (M3P11-F1)",
        [(SCALED, REVIEW11_FALLBACK + SCALED)],
        "order_assertion_disabled",
        INVALID,
        False,
    ),
    (
        "defect_in_wrong_component",
        "a mutant that changes only the other formula (doubles the wrong component) does not "
        "exercise its intended defect",
        [(SCALED, "        out[1 - component] *= factor\n")],
        "order_assertion_disabled",
        INVALID,
        False,
    ),
    (
        "incidental_rounding_only",
        "a mutant whose only change is a rounding-level difference (one ulp) in its own component "
        "does not exercise its intended defect",
        [(SCALED, "        out[component] *= 1.0 + 2.0**-52\n")],
        "order_assertion_disabled",
        INVALID,
        False,
    ),
    (
        "partially_exercised_defect",
        "a mutant that shows its defect in one series only (and is correct everywhere else) is "
        "not exercised: the defect is missing where it applies",
        [
            (
                SCALED,
                "        if (inc, node, phi) == (math.radians(30.0), math.radians(37.0), 0.0):\n"
                "            out[component] *= factor\n",
            )
        ],
        "order_assertion_disabled",
        INVALID,
        False,
    ),
    # Further I-11 controls (not regressions of the review-11 harness).
    (
        "exercised_rejected_for_another_reason",
        "a correctly exercised defect (Delta Omega coefficient doubled) whose run fails only "
        "because the Delta Omega order assertion is gone is not detected: the intended check "
        "did not reject it",
        [(FORMULA, DELTA_NODE_DOUBLED), (ORDER_ASSERT, 'if p < P_MIN and name != "delta_node":')],
        "delta_node_coefficient_doubled",
        "rejected for another reason",
        True,
    ),
    (
        "script_record_claims_exercise",
        "a copy whose own record is edited to claim an exercised defect, with a mutant that "
        "returns the reference result, is not detection: the independent probe decides",
        [(SCALED, SUPPRESSED_FALLBACK + SCALED), (EXERCISED_RETURN, "    return True or (\n")],
        "order_assertion_disabled",
        INVALID,
        False,
    ),
    (
        "expected_exception_wrap_guard",
        "the allowed wrap-guard exception at E2 remains an expected rejection",
        "E2_finite_check_removed",
        "E2_finite_check_removed",
        EXPECTED,
        True,
    ),
    (
        "expected_exception_order_estimate",
        "the allowed order-estimate math domain error remains an expected rejection",
        "oracle_check_weakened_to_isnan",
        "oracle_check_weakened_to_isnan",
        EXPECTED,
        True,
    ),
    (
        "direct_injection_exercised",
        "a genuine injection into the formula under test is exercised and detected",
        "review09_formula_delta_i_nan_one_series",
        "review09_formula_delta_i_nan_one_series",
        EXPECTED,
        True,
    ),
    (
        "direct_injection_wrong_component",
        "a NaN injected into the Delta Omega formula, claimed as the Delta i injection, is not "
        "exercised",
        [(FORMULA, formula_injection(1, math.nan, "True"))],
        "delta_i_formula_returns_nan",
        INVALID,
        False,
    ),
]
REGRESSION_CONTROLS_M3P11 = (
    "suppressed_import_reassociated_fallback",
    "defect_in_wrong_component",
    "incidental_rounding_only",
    "partially_exercised_defect",
)

# M3P12-F1 controls (I-12 section 3): an oracle value injected inside check_formulas, claimed as
# the injection at every step. Each must be invalid setup for its own reason (CONTROL_REASONS).
STEP_LOOP = "                    for d in deltas:\n"
SKIP_INTERMEDIATE = (
    "                        if d in deltas[1:-1]:\n                            continue\n"
)
ALL_STEPS_DELTA_I = "review09_oracle_delta_i_nan_all"


def oracle_nan_delta_i(condition):
    return [(ORACLE_CALL, oracle_injection("delta_i", math.nan, condition))]


CONTROLS += [
    (
        "first_step_only_claimed_all_steps_delta_i",
        "review 12's counterexample: a Delta i oracle NaN at the first step only, claimed as the "
        "NaN at every step, is not exercised: the defect is missing at the later steps, which "
        "the validation skips but the probe observes (M3P12-F1)",
        "review09_oracle_delta_i_nan_first_step",
        ALL_STEPS_DELTA_I,
        INVALID,
        False,
    ),
    (
        "first_step_only_claimed_all_steps_delta_node",
        "the same for Delta Omega (M3P12-F1)",
        "review09_oracle_delta_node_nan_first_step",
        "review09_oracle_delta_node_nan_all",
        INVALID,
        False,
    ),
    (
        "partial_steps_claimed_all_steps",
        "a NaN at steps 0, 2 and 4 only, claimed at every step, is not exercised: missing at "
        "steps 1 and 3",
        oracle_nan_delta_i("d in deltas[::2]"),
        ALL_STEPS_DELTA_I,
        INVALID,
        False,
    ),
    (
        "intermediate_observations_missing",
        "a copy that skips the intermediate steps 1-3 of every series (no formula call there) "
        "and injects the NaN at every step it reaches is not exercised: 1800 scheduled samples "
        "are never observed",
        [
            (
                ORACLE_CALL,
                ORACLE_CALL
                + SKIP_INTERMEDIATE
                + oracle_nan_delta_i("True")[0][1][len(ORACLE_CALL) :],
            )
        ],
        ALL_STEPS_DELTA_I,
        INVALID,
        False,
    ),
    (
        "observation_count_incorrect",
        "a copy that evaluates the last step of every series twice and injects the NaN at every "
        "step is not exercised: 600 samples are observed twice",
        [
            (STEP_LOOP, "                    for d in deltas + deltas[-1:]:\n"),
            *oracle_nan_delta_i("True"),
        ],
        ALL_STEPS_DELTA_I,
        INVALID,
        False,
    ),
    (
        "last_step_only_claimed_all_steps",
        "a NaN at the last step only, claimed at every step, is not exercised: missing at steps "
        "0-3 (not a regression: the validation reaches those steps first)",
        oracle_nan_delta_i("d == deltas[-1]"),
        ALL_STEPS_DELTA_I,
        INVALID,
        False,
    ),
    (
        "all_steps_correctly_injected",
        "the NaN genuinely injected at every step is exercised at all 3000 samples and detected",
        ALL_STEPS_DELTA_I,
        ALL_STEPS_DELTA_I,
        EXPECTED,
        True,
    ),
]
REGRESSION_CONTROLS_M3P12 = (
    "first_step_only_claimed_all_steps_delta_i",
    "first_step_only_claimed_all_steps_delta_node",
    "partial_steps_claimed_all_steps",
    "intermediate_observations_missing",
    "observation_count_incorrect",
)
ORACLE_COUNTS = (
    "oracle values oracle values: intended {}, missing {}, unintended 0, unobserved {}, "
)
# The reason each control must show (I-12 section 3): a fragment of its observed outcome.
CONTROL_REASONS = {
    "syntax_error": "SyntaxError",
    "import_failure": "No module named 'm3p9_control_missing_module'",
    "missing_script": "No such file or directory",
    "neutral_edit": "exit 0, PASS verdict",
    "fragment_absent": "fragment occurs 0 times",
    "wrong_reason": "intended defect not exercised: formula formula: intended 0, missing 0, "
    "unintended 3000",
    "import_failure_inside_mutant": "raised ModuleNotFoundError: No module named "
    "'m3p10_control_missing_module'",
    "runtime_exception_inside_mutant": "raised ZeroDivisionError",
    "exception_suppressed_inside_mutant": "intended defect not exercised: "
    "M3P9-F2_delta_i_coefficient_doubled formula: intended 0, missing 3000, unintended 0",
    "allowed_exception_wrong_location": "exact_properties: if circ(d_node, PI, wrap) > "
    "pair_noise(inc, inc + d_i):",
    "allowed_exception_wrong_type": "raised TypeError: wrap: non-finite angle",
    "valid_mutant_rejected_by_targeted_check": "expected rejection shown; intended defect "
    "exercised: formula formula: intended 3000, missing 0, unintended 0",
    "valid_mutant_completes_without_rejection": "expected rejection shown; intended defect "
    "exercised: M3P9-F2_delta_i_coefficient_doubled formula: intended 3000, missing 0",
    "suppressed_import_reassociated_fallback": "intended 0, missing 2060, unintended 940",
    "defect_in_wrong_component": "M3P9-F2_delta_node_coefficient_doubled formula: intended 0, "
    "missing 0, unintended 3000",
    "incidental_rounding_only": "M3P9-F2_delta_i_coefficient_doubled formula: intended 0, "
    "missing 0, unintended 3000",
    "partially_exercised_defect": "intended 10, missing 2990, unintended 0",
    "exercised_rejected_for_another_reason": "not shown: formulas under test: exactly 504 "
    "failure(s) starting 'order delta_node '",
    "script_record_claims_exercise": "intended defect not exercised: "
    "M3P9-F2_delta_i_coefficient_doubled formula: intended 0, missing 3000",
    "expected_exception_wrap_guard": "M3P8-F1_audit_oracle_delta_node_nan raised ValueError as "
    "allowed",
    "expected_exception_order_estimate": "raised ValueError as allowed",
    "direct_injection_exercised": "intended defect exercised: formula formula: intended 5, "
    "missing 0, unintended 0",
    "direct_injection_wrong_component": "intended defect not exercised: formula formula: "
    "intended 0, missing 0, unintended 3000",
    "first_step_only_claimed_all_steps_delta_i": ORACLE_COUNTS.format(600, 2400, 0),
    "first_step_only_claimed_all_steps_delta_node": ORACLE_COUNTS.format(600, 2400, 0),
    "partial_steps_claimed_all_steps": ORACLE_COUNTS.format(1800, 1200, 0),
    "intermediate_observations_missing": ORACLE_COUNTS.format(1200, 0, 1800),
    "observation_count_incorrect": ORACLE_COUNTS.format(3000, 0, 0) + "duplicate 600, ",
    "last_step_only_claimed_all_steps": ORACLE_COUNTS.format(600, 2400, 0),
    "all_steps_correctly_injected": "expected rejection shown; intended defect exercised: "
    + ORACLE_COUNTS.format(3000, 0, 0)
    + "duplicate 0, unscheduled 0 of 3000 samples",
}


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


# -------------------------------------------------------- exercise probe (M3P11-F1)
TABLES = {
    "mutants": "MUTANTS",
    "formula_defect_mutants": "FORMULA_DEFECT_MUTANTS",
    "exact_and_wrap_mutants": "EXACT_MUTANTS",
}
FORMULA_ARGS = ("inc", "node", "phi", "delta")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def injected_kwargs(module, section, mutant):
    """A built-in mutant's injected functions and settings, from the module's own table."""
    entry = getattr(module, TABLES[section])[mutant]
    return {"formula": entry} if section == "mutants" else entry[0]


def formula_defect(orig, spec):
    """The intended defect of a mutation of the formula under test, from the unmutated script."""
    _, kind, *params = spec
    if kind == "scaled":
        return orig.defect_scaled(
            tuple(params), f"first-order factors {params[0]!r}, {params[1]!r}"
        )
    index, value_repr, condition = params

    def where(args):
        return bool(eval(condition, {"math": math}, dict(zip(FORMULA_ARGS, args, strict=True))))

    description = f"{orig.COMPONENTS[index]} formula value {value_repr} where {condition}"
    return orig.defect_component(index, float(value_repr), description, where)


def oracle_schedule(orig):
    """Every sample at which check_formulas evaluates the oracle (M3P12-F1): {(inc, node, phi,
    delta): names}, built from the unmutated script's grid constants before any copy runs. The
    names are those a condition may use. There must be SERIES_PER_COMPONENT x HALVINGS samples."""
    schedule = {}
    for inc_deg in orig.GRID_INCLINATIONS:
        inc = math.radians(inc_deg)
        for node_deg in orig.NODES:
            for phi_deg in orig.TILT_AZIMUTHS:
                node, phi = math.radians(node_deg), math.radians(phi_deg)
                for sign in (1.0, -1.0):
                    deltas = [sign * orig.step_scale(inc) * 2.0**-k for k in range(orig.HALVINGS)]
                    for k, d in enumerate(deltas):
                        schedule[inc, node, phi, d] = {
                            "inc_deg": inc_deg,
                            "node_deg": node_deg,
                            "phi_deg": phi_deg,
                            "sign": sign,
                            "inc": inc,
                            "node": node,
                            "phi": phi,
                            "deltas": deltas,
                            "d": d,
                            "k": k,
                        }
    expected = orig.SERIES_PER_COMPONENT * orig.HALVINGS
    if len(schedule) != expected or orig.SERIES_PER_COMPONENT != SERIES:
        raise ValueError(f"oracle schedule has {len(schedule)} samples, expected {expected}")
    return schedule


def observe_oracle_values(orig, mut, index, value_repr, condition):
    """Observe an oracle value injected inside check_formulas (M3P11-F1; M3P12-F1).

    The expected samples are fixed first (oracle_schedule, from the unmutated script). The copy's
    check_formulas is then run with an observing formula: check_formulas calls the formula at
    every step, right after the oracle value (and any injection) and before any validation, so a
    step that the validation would skip after an earlier invalid value is still observed. Each
    call is identified by the formula's own arguments, which must be a scheduled sample seen once;
    the oracle values then held by check_formulas (its `num`) are compared, per component, with
    the unmutated oracle at that sample. The condition is evaluated on the scheduled sample, with
    the unmutated script's names, not on the copy's state. Counts: intended, unchanged, missing,
    unintended (per component, call_kind), and per sample unobserved (scheduled, never seen),
    duplicate (seen again) and unscheduled (not a scheduled sample). The defect is exercised only
    if it is shown, never missing, nothing else differs, every scheduled sample is observed
    exactly once, nothing unscheduled is observed and check_formulas raises nothing."""
    target, value = orig.COMPONENTS[index], float(value_repr)
    schedule = oracle_schedule(orig)
    names = dict(vars(orig))
    counts = {"calls": 0, "defect": f"{target} oracle value {value_repr} where {condition}"}
    counts.update(changes=True, **dict.fromkeys(orig.CALL_KINDS, 0))
    counts.update(
        expected_samples=len(schedule), observed_samples=0, unobserved=0, duplicate=0, unscheduled=0
    )
    seen = dict.fromkeys(schedule, 0)
    code = mut.check_formulas.__code__

    def formula(inc, node, phi, delta):
        frame = sys._getframe(1)
        sample = (inc, node, phi, delta)
        if frame.f_code is not code or sample not in schedule:
            counts["unscheduled"] += 1
        elif seen[sample]:
            seen[sample] += 1
            counts["duplicate"] += 1
        else:
            seen[sample] += 1
            num = frame.f_locals["num"]
            ref = orig.finite(inc, node, phi, delta)
            applies = bool(eval(condition, names, dict(schedule[sample])))
            for k, name in enumerate(orig.COMPONENTS):
                counts["calls"] += 1
                got = num[name]
                if k == index and applies and not orig.same_value(ref[k], value):
                    kind = (
                        "intended"
                        if orig.same_value(got, value)
                        else "missing"
                        if orig.same_value(got, ref[k])
                        else "unintended"
                    )
                else:
                    kind = "unchanged" if orig.same_value(got, ref[k]) else "unintended"
                counts[kind] += 1
        return orig.formulas_amendment2(inc, node, phi, delta)

    exception = None
    try:
        mut.check_formulas(formula)
    except Exception as exc:
        exception = {"type": type(exc).__name__, "message": str(exc)}
    counts["observed_samples"] = sum(1 for n in seen.values() if n)
    counts["unobserved"] = sum(1 for n in seen.values() if not n)
    complete = (
        counts["observed_samples"] == counts["expected_samples"]
        and counts["unobserved"] == counts["duplicate"] == counts["unscheduled"] == 0
        and counts["calls"] == len(schedule) * len(orig.COMPONENTS)
    )
    counts["observation_complete"] = complete
    record = {"oracle values": counts}
    return {
        "defect_calls": record,
        "defect_exercised": orig.exercised(record) and complete and exception is None,
        "exception": exception,
    }


def probe(original, mutated, spec):
    """The independent exercise observation of one mutated copy (run in its own process)."""
    orig = load(original, "m3p11_probe_original")
    try:
        mut = load(mutated, "m3p11_probe_mutated")
    except BaseException as exc:  # a copy that cannot be loaded shows no defect
        return {"exercised": False, "reason": f"copy not loadable: {type(exc).__name__}: {exc}"}
    kind, observations = spec[0], {}
    try:
        if kind == "built-in":
            for section, mutant, _ in spec[1]:
                kwargs = injected_kwargs(mut, section, mutant)
                run_fn, defects = orig.SECTION_RUNS[section], orig.DEFECTS[mutant]
                observations[mutant] = orig.observe(run_fn, defects, **kwargs)
        elif kind == "formula":
            defects = {"formula": formula_defect(orig, spec)}
            observations["formula"] = orig.observe(
                orig.check_formulas, defects, formula=mut.formulas_amendment2
            )
        elif kind == "injected":
            _, key, attribute, table, name = spec
            defects = {key: getattr(orig, table)[name]}
            observations[key] = orig.observe(
                orig.run_exact, defects, **{key: getattr(mut, attribute)}
            )
        elif kind == "oracle values":
            observations["oracle values"] = observe_oracle_values(orig, mut, *spec[1:])
        else:
            return {"exercised": False, "reason": f"unknown exercise predicate {kind!r}"}
    except BaseException as exc:
        reason = f"defect not observable: {type(exc).__name__}: {exc}"
        return {"exercised": False, "reason": reason, "observations": observations}
    exercised = bool(observations) and all(o["defect_exercised"] for o in observations.values())
    return {"exercised": exercised, "observations": observations}


def probe_run(mutated, spec, workdir, label):
    """Run the probe for one copy in a separate process; return its result."""
    out = workdir / f"{label}.probe.json"
    command = [sys.executable, "-I", str(HARNESS), "--probe", str(SCRIPT), str(mutated)]
    proc = subprocess.run(
        [*command, json.dumps(spec), str(out)],
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    if proc.returncode != 0 or not out.exists():
        stderr = proc.stderr.strip()
        last = stderr.splitlines()[-1] if stderr else "no stderr"
        last = last.replace(str(workdir), "<tmp>").replace(sys.executable, "<python>")
        return {"exercised": False, "reason": f"probe failed: {last}"}
    return json.loads(out.read_text(encoding="ascii"))


def exercise_spec(expected, declared):
    """A mutation's exercise predicate; for BUILT_IN, the built-in mutants of its expectation."""
    if declared != BUILT_IN:
        return list(declared)
    kinds = ("not_rejected", "raised", "unexercised")
    return ["built-in", [[p[1], p[2], p[0]] for p in expected if p[0] in kinds]]


def exercise_summary(result):
    if "reason" in result:
        return result["reason"]
    parts = []
    for label, o in result["observations"].items():
        for key, r in o["defect_calls"].items():
            if "setting" in r:
                parts.append(f"{label} {key} = {r['setting']!r}")
            else:
                kinds = ("intended", "missing", "unintended")
                if "expected_samples" in r:  # oracle values (M3P12-F1)
                    kinds += ("unobserved", "duplicate", "unscheduled")
                counts = ", ".join(f"{k} {r[k]}" for k in kinds)
                if "expected_samples" in r:
                    counts += f" of {r['expected_samples']} samples"
                parts.append(f"{label} {key}: {counts}")
        if o.get("exception"):
            parts.append(f"{label} raised {o['exception']['type']}")
    return "; ".join(parts)


def exercise_established(exercise, output):
    """(established, evidence) for a run's (exercise predicate, probe result)."""
    spec, result = exercise
    if not result["exercised"]:
        return False, "intended defect not exercised: " + exercise_summary(result)
    if spec[0] == "built-in":
        for section, mutant, kind in spec[1]:
            reported = output.get(section, {}).get(mutant, {}).get("defect_exercised")
            if reported is not (kind != "unexercised"):
                return False, f"{mutant}: the copy's own record reports defect_exercised={reported}"
    return True, "intended defect exercised: " + exercise_summary(result)


def classify(code, output, last, expected, exercise=None):
    """Return (category, observed outcome). Only EXPECTED is a detection.

    `exercise` is (exercise predicate, probe result), or None if no copy produced output."""
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
    if exercise is None:
        return INVALID, observed + "; no exercise observation"
    established, evidence = exercise_established(exercise, output)
    if not established:
        return INVALID, observed + "; " + evidence
    failed = [describe(p) for p in expected if not holds(p, output)]
    if failed:
        return "rejected for another reason", f"{observed}; {evidence}; not shown: " + "; ".join(
            failed
        )
    allowed_seen = "".join(f"; {p[2]} raised {p[3]} as allowed" for p in allowed.values())
    return EXPECTED, f"{observed}; expected rejection shown; {evidence}{allowed_seen}"


def apply_edits(original, edits):
    """The mutated source, or None with the reason if some fragment is not unique."""
    source = original
    for old, new in edits:
        count = source.count(old)
        if count != 1:
            return None, f"not run: fragment occurs {count} times"
        source = source.replace(old, new)
    return source, None


def execute(source, workdir, label, spec):
    """Run one copy; if it produced output, observe its intended defect with the probe."""
    code, output, last = run(source, workdir, label)
    exercise = None
    if source is not None and output is not None:
        exercise = (spec, probe_run(workdir / f"{label}.py", spec, workdir, label))
    return code, output, last, exercise


def run_control(control, original, workdir):
    """Run one control; return its report entry."""
    name, shows, edits, claimed, category, exercised = control
    expected = MUTATION_INDEX[claimed][5]
    spec = exercise_spec(expected, MUTATION_INDEX[claimed][6])
    if isinstance(edits, str):  # a mutation of MUTATIONS, by name
        edits = [MUTATION_INDEX[edits][3:5]]
    established = None
    if edits is None:
        actual, observed = classify(*run(None, workdir, f"control_{name}"), expected)
    else:
        source, problem = apply_edits(original, edits)
        if source is None:
            actual, observed = INVALID, problem
        else:
            code, output, last, exercise = execute(source, workdir, f"control_{name}", spec)
            actual, observed = classify(code, output, last, expected, exercise)
            if exercise is not None:
                established = exercise_established(exercise, output)[0]
    reason = CONTROL_REASONS[name]
    shown = reason in observed
    return {
        "shows": shows,
        "claimed_expectation": claimed,
        "expected_classification": category,
        "actual_classification": actual,
        "expected_exercise": exercised,
        "exercise_established": established,
        "required_reason": reason,
        "reason_shown": shown,
        "observed_outcome": observed,
        "result": "PASS" if actual == category and established == exercised and shown else "FAIL",
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
            for m in MUTATIONS:
                if all(holds(p, output) for p in m[5]):
                    vacuous.append(m[0])
        baseline["expectations_already_true_at_baseline"] = vacuous
        # A direct exercise predicate must not be met by the unmutated script (M3P11-F1).
        # The oracle-value schedule must be observed completely on the unmutated script, so that
        # the schedule is the one check_formulas actually runs (M3P12-F1).
        observed_unmutated, incomplete = [], []
        for m in MUTATIONS:
            if m[6] == BUILT_IN:
                continue
            result = probe_run(workdir / "baseline.py", list(m[6]), workdir, f"baseline_{m[0]}")
            if result["exercised"]:
                observed_unmutated.append(m[0])
            if m[6][0] == "oracle values":
                o = result.get("observations", {}).get("oracle values", {})
                counts = o.get("defect_calls", {}).get("oracle values", {})
                if not counts.get("observation_complete") or o.get("exception") is not None:
                    incomplete.append(m[0])
        baseline["direct_exercise_predicates_checked_at_baseline"] = sum(
            1 for m in MUTATIONS if m[6] != BUILT_IN
        )
        baseline["direct_exercise_already_met_at_baseline"] = observed_unmutated
        baseline["oracle_schedules_checked_at_baseline"] = sum(
            1 for m in MUTATIONS if m[6] != BUILT_IN and m[6][0] == "oracle values"
        )
        baseline["oracle_schedule_not_fully_observed_at_baseline"] = incomplete
        baseline_ok = baseline_ok and not vacuous and not observed_unmutated and not incomplete
        for name, group, target, old, new, expected, declared in MUTATIONS:
            spec = exercise_spec(expected, declared)
            entry = {
                "group": group,
                "target_property": target,
                "exercise_predicate": spec,
                "expected_rejection": [describe(p) for p in expected],
            }
            source, problem = apply_edits(original, [(old, new)])
            exercise = None
            if name in results or source is None:
                category, observed = INVALID, problem or "duplicate name"
            else:
                code, output, last, exercise = execute(source, workdir, name, spec)
                category, observed = classify(code, output, last, expected, exercise)
            entry["classification"] = category
            entry["observed_outcome"] = observed
            entry["exercise_established"] = (
                None if exercise is None else exercise_established(exercise, output)[0]
            )
            entry["exercise_observation"] = None if exercise is None else exercise[1]
            entry["result"] = "PASS" if category == EXPECTED else "FAIL"
            results[name + ("#duplicate" if name in results else "")] = entry
        controls = {c[0]: run_control(c, original, workdir) for c in CONTROLS}
    groups = {}
    for entry in results.values():
        g = groups.setdefault(entry["group"], {"mutations": 0, "detected": 0})
        g["mutations"] += 1
        g["detected"] += entry["result"] == "PASS"
    detected = sum(1 for r in results.values() if r["result"] == "PASS")
    exercise = [r["exercise_established"] for r in results.values()]
    summary = {
        "mutations_attempted": len(MUTATIONS),
        "validly_exercised": exercise.count(True),
        "not_exercised": exercise.count(False),
        "exercise_not_observed_no_output": exercise.count(None),
        "detected_for_intended_reason": detected,
        "by_classification": {
            c: sum(1 for r in results.values() if r["classification"] == c) for c in CATEGORIES
        },
        "controls": len(CONTROLS),
        "controls_with_declared_outcome": sum(
            1 for c in controls.values() if c["result"] == "PASS"
        ),
    }
    controls_ok = all(c["result"] == "PASS" for c in controls.values())
    ok = baseline_ok and controls_ok and detected == len(MUTATIONS) == len(results)
    report = {
        "verdict": "PASS" if ok else "FAIL",
        "script": SCRIPT.name,
        "exercise_criterion": (
            "amendments 8 and 9 (M3P11-F1, M3P12-F1): a detection requires the intended defect "
            "established as exercised by the independent probe (intended >= 1, missing = 0, "
            "unintended = 0; for oracle values also every scheduled sample observed exactly once, "
            "none unobserved, duplicate or unscheduled, and no exception) and the expected "
            "rejection shown"
        ),
        "baseline": baseline,
        "mutations": len(MUTATIONS),
        "detected": detected,
        "summary": summary,
        "groups": groups,
        "controls": controls,
        "results": results,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: report[k] for k in ("verdict", "mutations", "detected", "groups")}))
    print(json.dumps(summary))
    print(json.dumps({k: c["result"] for k, c in controls.items()}))
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1] == "--probe":  # internal: one exercise observation (probe_run)
        original_path, mutated_path, spec_json, probe_out = sys.argv[2:6]
        result = probe(
            pathlib.Path(original_path), pathlib.Path(mutated_path), json.loads(spec_json)
        )
        with open(probe_out, "w", encoding="ascii") as fh:
            json.dump(result, fh, indent=1)
        sys.exit(0)
    sys.exit(main(sys.argv[1]))
