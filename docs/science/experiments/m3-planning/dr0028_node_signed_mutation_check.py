"""DR-0028 amendment 5 / review M3P8-F1: file-level mutation check of
dr0028_node_signed_verification.py through its real entrypoint.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python dr0028_node_signed_mutation_check.py <out.json>

Each mutation replaces one exact text fragment of the verification script (the fragment must
occur exactly once), writes the mutated copy to a temporary directory and runs it as a separate
process (`python -I <copy> <out.json>`), exactly as the script is normally run. A mutation is
detected when that process exits nonzero. The unmutated script must exit 0 with verdict PASS.
Exit status 0 only if the baseline passes and every mutation is detected. Standard library only.

The outcome of each run is recorded as "PASS verdict", "FAIL verdict" or the exception type that
ended the process, so a detection by a crash is never reported as a FAIL verdict.
"""

import json
import pathlib
import subprocess
import sys
import tempfile

SCRIPT = pathlib.Path(__file__).with_name("dr0028_node_signed_verification.py")

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

# (name, group, old fragment, new fragment)
MUTATIONS = [
    # M3P8-F1: non-finite first-order output injected at the source, run through main().
    ("delta_i_formula_returns_nan", "M3P8-F1 injection", FORMULA, f"return math.nan, {NODE_TERM}"),
    (
        "delta_i_formula_returns_plus_inf",
        "M3P8-F1 injection",
        FORMULA,
        f"return math.inf, {NODE_TERM}",
    ),
    (
        "delta_i_formula_returns_minus_inf",
        "M3P8-F1 injection",
        FORMULA,
        f"return -math.inf, {NODE_TERM}",
    ),
    (
        "delta_node_formula_returns_nan",
        "M3P8-F1 injection",
        FORMULA,
        "return -delta * math.cos(node - phi), math.nan",
    ),
    (
        "delta_node_formula_returns_plus_inf",
        "M3P8-F1 injection",
        FORMULA,
        "return -delta * math.cos(node - phi), math.inf",
    ),
    (
        "delta_node_formula_returns_minus_inf",
        "M3P8-F1 injection",
        FORMULA,
        "return -delta * math.cos(node - phi), -math.inf",
    ),
    # M3P8-F1: coverage minima disabled or weakened.
    (
        "delta_i_coverage_disabled",
        "M3P8-F1 coverage",
        COVERAGE_LOOP,
        COVERAGE_LOOP.replace("in COMPONENTS", 'in ("delta_node",)'),
    ),
    (
        "delta_node_coverage_disabled",
        "M3P8-F1 coverage",
        COVERAGE_LOOP,
        COVERAGE_LOOP.replace("in COMPONENTS", 'in ("delta_i",)'),
    ),
    (
        "sign_coverage_removed",
        "M3P8-F1 coverage",
        COVERAGE_PAIRS,
        '(("order", len(orders[name])),)',
    ),
    ("order_coverage_removed", "M3P8-F1 coverage", COVERAGE_PAIRS, '(("sign", signs[name]),)'),
    ("coverage_comparison_disabled", "M3P8-F1 coverage", "if not count >= minimum:", "if False:"),
    (
        "sign_counter_moved_outside_gate",
        "M3P8-F1 coverage",
        SIGN_GATE,
        "                        signs[name] += 1\n"
        "                        if abs(n) >= tol and abs(lin_v) >= tol:\n",
    ),
    # M3P8-F1: finite-value validation removed or weakened.
    (
        "finite_validation_removed",
        "M3P8-F1 validation",
        "reason = nonfinite_reason(num[name], lin[name])",
        "reason = None",
    ),
    (
        "formula_check_weakened_to_isnan",
        "M3P8-F1 validation",
        '    if not math.isfinite(lin):\n        return f"formula',
        '    if math.isnan(lin):\n        return f"formula',
    ),
    (
        "oracle_check_removed",
        "M3P8-F1 validation",
        "if num is None or not math.isfinite(num):",
        "if num is None:",
    ),
    (
        "invalid_sample_not_discarded",
        "M3P8-F1 validation",
        "                                errs[name] = None\n"
        "                                continue\n"
        "                            errs[name].append",
        "                            errs[name].append",
    ),
    # M3P8-F1 audit: finite checks of the exact properties removed.
    (
        "E1_finite_check_removed",
        "M3P8-F1 audit",
        "if not math.isfinite(dev) or any(not math.isfinite(x) for row in r for x in row):",
        "if False:",
    ),
    (
        "E2_finite_check_removed",
        "M3P8-F1 audit",
        "if not all(math.isfinite(x) for x in (d_i, d_node, exp_i, exp_node)):",
        "if False:",
    ),
    (
        "E2_endpoint_finite_check_removed",
        "M3P8-F1 audit",
        "if not math.isfinite(rho):",
        "if False:",
    ),
    (
        "E3_finite_check_removed",
        "M3P8-F1 audit",
        "if d_node is None or not all(math.isfinite(x) for x in (d_i, d_node)):",
        "if False:",
    ),
    (
        "E4_finite_check_removed",
        "M3P8-F1 audit",
        "if not math.isfinite(d_i):",
        "if False:",
    ),
    (
        "E5b_finite_check_removed",
        "M3P8-F1 audit",
        "if not math.isfinite(d_node):",
        "if False:",
    ),
    (
        "E6_finite_check_removed",
        "M3P8-F1 audit",
        "if d_node is None or not all(math.isfinite(x) for x in (d_i, d_node, lin_i, lin_node)):",
        "if False:",
    ),
    # Earlier findings (reviews 05-07), preserved.
    ("M3P5_delta_i_sign_reversed", "earlier", FORMULA, FORMULA.replace("-delta", "delta", 1)),
    (
        "M3P5_delta_node_sign_reversed",
        "earlier",
        FORMULA,
        FORMULA.replace(", delta /", ", -delta /"),
    ),
    (
        "M3P6-F1_unrestricted_claim_restored",
        "earlier",
        "    j = inc - delta\n    if 0.0 < j < PI:",
        "    j = inc - delta\n    return -delta, 0.0\n    if 0.0 < j < PI:",
    ),
    ("M3P6-F2_E5a_removed", "earlier", "if circ(d_node, PI, wrap) > tol:", "if False:"),
    (
        "M3P6-F2_E5b_removed",
        "earlier",
        "if circ(d_node, PI, wrap) > pair_noise(inc, inc + d_i):",
        "if False:",
    ),
    (
        "M3P6-F2_E5c_removed",
        "earlier",
        "if jump_asserts[sign] < MIN_CROSSINGS_PER_SIGN + 1:",
        "if False:",
    ),
    (
        "M3P6-F3_previous_wrap_implementation",
        "earlier",
        WRAP_BODY,
        '        raise ValueError(f"{NONFINITE_MESSAGE}: {a!r}")\n'
        "    return a - 2.0 * math.pi * math.floor((a + math.pi) / (2.0 * math.pi))\n",
    ),
    (
        "M3P7-F1_guard_removed",
        "earlier",
        '    if not math.isfinite(a):\n        raise ValueError(f"{NONFINITE_MESSAGE}: {a!r}")\n',
        "",
    ),
    (
        "M3P7-F1_message_check_weakened_to_type_only",
        "earlier",
        "ok = str(exc).startswith(NONFINITE_MESSAGE)",
        "ok = True",
    ),
    (
        "M3P7-F1_nonfinite_tests_disabled",
        "earlier",
        "for name, a in cases.items():",
        "for name, a in {}.items():",
    ),
]


def run(source, workdir, label):
    """Run one copy of the script; return (exit code, outcome)."""
    copy = workdir / f"{label}.py"
    out = workdir / f"{label}.json"
    copy.write_text(source, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-I", str(copy), str(out)],
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    if out.exists() and proc.stderr.strip() == "":
        verdict = json.loads(out.read_text(encoding="ascii"))["verdict"]
        outcome = f"{verdict} verdict"
    else:
        last = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "no output"
        outcome = f"exception: {last.split(':')[0]}"
    return proc.returncode, outcome


def main(out_path):
    original = SCRIPT.read_text(encoding="utf-8")
    results, ok = {}, True
    with tempfile.TemporaryDirectory() as tmp:
        workdir = pathlib.Path(tmp)
        code, outcome = run(original, workdir, "baseline")
        baseline = {"exit_code": code, "outcome": outcome}
        ok = code == 0 and outcome == "PASS verdict"
        for name, group, old, new in MUTATIONS:
            occurrences = original.count(old)
            if occurrences != 1:
                results[name] = {"group": group, "error": f"fragment occurs {occurrences} times"}
                ok = False
                continue
            code, outcome = run(original.replace(old, new), workdir, name)
            detected = code != 0
            results[name] = {
                "group": group,
                "exit_code": code,
                "outcome": outcome,
                "detected": detected,
            }
            ok = ok and detected
    report = {
        "verdict": "PASS" if ok else "FAIL",
        "script": SCRIPT.name,
        "baseline": baseline,
        "mutations": len(MUTATIONS),
        "detected": sum(1 for r in results.values() if r.get("detected")),
        "results": results,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")
    print(json.dumps(report, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
