"""DR-0028 amendments 5 and 6 / reviews M3P8-F1, M3P9-F1..F3: file-level mutation check of
dr0028_node_signed_verification.py through its real entrypoint.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python dr0028_node_signed_mutation_check.py <out.json>

Each mutation replaces one exact text fragment of the verification script (the fragment must
occur exactly once), writes the mutated copy to a temporary directory and runs it as a separate
process (`python -I <copy> <out.json>`), exactly as the script is normally run.

A mutation is detected only for its intended reason (M3P9 / I-9 section 6). Each mutation
declares its expected rejection as predicates on the script's output, and the run must show
it: the process exits 1 with nothing on stderr, writes a FAIL verdict, and every predicate
holds. Examples: "the built-in mutant M3P9-F2_delta_i_coefficient_doubled is no longer rejected
by its designated check" (an assertion was removed), or "the formulas under test report exactly
600 'nonfinite delta_i formula=nan' failures" (a defect was injected). Any other outcome is NOT
detected and fails this check: exit 0; a FAIL verdict for another reason; any exception that
ends the process (a syntax error, import failure, missing file or any other crash); or a
fragment that does not occur exactly once. (A built-in mutant that raises inside the script is
recorded there as not rejected, with its exception; amendment 6.) The unmutated script must
exit 0 with verdict PASS, and no expectation may already be met by its output (all of its
predicates holding), so no expectation is vacuous.

Negative controls (I-9 section 6) show that the classification fails closed: a syntax error,
an import failure, a missing script, a neutral edit, and a real defect paired with the wrong
expected reason must each be classified as NOT detected, or this check fails.
Exit status 0 only if the baseline passes and every mutation is detected. Standard library only.
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


# ------------------------------------------------------------------- expected rejections
def not_rejected(section, mutant):
    """Predicate: a built-in mutant is no longer rejected (the assertion guarding it is gone)."""
    return ("not_rejected", section, mutant)


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


def holds(predicate, out):
    kind, a, b = predicate
    if kind == "not_rejected":
        return out[a][b][FLAGS[a]] is False
    if kind == "under_test":
        failures = out["formulas_under_test"]["failures"]
    else:
        failures = out["exact_property_failures"]
    n = sum(1 for f in failures if f.startswith(a))
    return n >= 1 if b is None else n == b


def describe(predicate):
    kind, a, b = predicate
    if kind == "not_rejected":
        return f"built-in mutant {b} not rejected ({a})"
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
        not_designated("M3P8-F1_delta_i_nan") + not_designated("M3P8-F1_audit_oracle_delta_i_nan"),
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
        + not_designated("M3P9-F1_oracle_delta_i_plus_inf"),
    ),
    (
        "invalid_sample_not_discarded",
        "M3P8-F1 validation",
        "invalid samples excluded from coverage",
        "                                errs[name] = None\n"
        "                                continue\n"
        "                            errs[name].append",
        "                            errs[name].append",
        not_designated("M3P8-F1_delta_i_plus_inf"),
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
        not_designated_exact("M3P8-F1_audit_oracle_delta_node_nan"),
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
        not_designated_exact("M3P8-F1_audit_oracle_delta_node_nan"),
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
            not_rejected("formula_defect_mutants", f"M3P9-F1_oracle_{name}_{label}{scope}")
            for name in COMPONENT_NAMES
            for label in ("plus_inf", "minus_inf")
            for scope in ("", "_single_sample")
        ],
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
        '    if not math.isfinite(a):\n        raise ValueError(f"{NONFINITE_MESSAGE}: {a!r}")\n',
        "",
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
        not_designated_exact("M3P7-F1_nonfinite_guard_removed"),
    ),
    *injection_matrix(),
]


# Negative controls: (name, failure kind, old fragment, new fragment or None, expected rejection).
# new = None runs a script path that does not exist.
CONTROLS = [
    ("syntax_error", "syntax error", FORMULA, "return (", [under_test("nonfinite delta_i ")]),
    (
        "import_failure",
        "import failure",
        "import json\n",
        "import json\nimport m3p9_control_missing_module\n",
        [under_test("nonfinite delta_i ")],
    ),
    ("missing_script", "missing file", FORMULA, None, [under_test("nonfinite delta_i ")]),
    (
        "neutral_edit",
        "no defect (exit 0)",
        "import json\n",
        "import json  # neutral edit\n",
        [under_test("nonfinite delta_i ")],
    ),
    (
        "wrong_reason",
        "FAIL verdict for another reason",
        FORMULA,
        FORMULA.replace("-delta", "delta", 1),
        [under_test("sign delta_node ")],
    ),
]


def run(source, workdir, label):
    """Run one copy of the script; return (exit code, output or None, last stderr line).

    source = None runs a path that does not exist (negative control)."""
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


def classify(code, output, last, expected):
    """Return (observed outcome, detected for the intended reason)."""
    if output is None:
        return f"exit {code}, no output; process failure: {last or 'no stderr'}", False
    observed = f"exit {code}, {output['verdict']} verdict"
    if code != 1 or output["verdict"] != "FAIL":
        return observed, False
    failed = [describe(p) for p in expected if not holds(p, output)]
    if failed:
        return observed + "; expected rejection not shown: " + "; ".join(failed), False
    raised = [
        f"{b} raised {out}"
        for kind, a, b in expected
        if kind == "not_rejected" and (out := output[a][b].get("exception"))
    ]
    return observed + "; expected rejection shown" + "".join(f"; {r}" for r in raised), True


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
            occurrences = original.count(old)
            if name in results or occurrences != 1:
                entry["observed_outcome"] = f"not run: fragment occurs {occurrences} times"
                entry["result"] = "FAIL"
                results[name + ("#duplicate" if name in results else "")] = entry
                continue
            code, output, last = run(original.replace(old, new), workdir, name)
            entry["observed_outcome"], detected = classify(code, output, last, expected)
            entry["result"] = "PASS" if detected else "FAIL"
            results[name] = entry
        controls = {}
        for name, kind, old, new, expected in CONTROLS:
            source = None if new is None else original.replace(old, new)
            if new is not None and original.count(old) != 1:
                observed, detected = "not run: fragment not unique", True  # fails closed
            else:
                code, output, last = run(source, workdir, f"control_{name}")
                observed, detected = classify(code, output, last, expected)
            controls[name] = {
                "failure_kind": kind,
                "observed_outcome": observed,
                "classified_as_detected": detected,
                "result": "FAIL" if detected else "PASS",
            }
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
        "negative_controls": controls,
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
