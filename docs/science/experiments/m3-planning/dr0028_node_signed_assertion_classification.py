"""DR-0028 amendment 7 / review M3P10-F2 (I-10 section 4): classification of the 18 assertions
that review 10's assertion-removal sweep found not individually load-bearing.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python dr0028_node_signed_assertion_classification.py <out.json>

Categories (I-10 section 4):
  A  independently important: removing it could let an otherwise undetected correctness defect
     pass. A built-in mutant now fails exactly this assertion of its test (amendment 7). The
     evidence: with the assertion present, the mutant's designated test rejects it; with only
     this assertion removed, the designated test reports nothing.
  B  redundant: another, named check rejects the same relevant defect. The evidence: with only
     this assertion removed, a defect of the kind it guards is still rejected by that check.
  C  diagnostic: it guards test configuration or reporting, not a computed correctness
     property. The rationale is recorded; nothing is executed for it.
  D  uncertain: none.

Each executed demonstration loads a copy of the verification script with exactly one
`failures.append(...)` statement replaced by `pass` (located with ast), imports it, and calls its
exact-property tests with the defect. Exit status 0 only if every demonstration holds. Nothing
in the verification script is changed. Standard library only.
"""

import ast
import importlib.util
import json
import math
import pathlib
import sys
import tempfile

SCRIPT = pathlib.Path(__file__).with_name("dr0028_node_signed_verification.py")


# ------------------------------------------------------------- demonstration defects (B)
def wrap_no_correction(m):
    """fmod without the (-pi, pi] correction step: results in (-2 pi, 2 pi)."""

    def wrap_fn(a):
        if not math.isfinite(a):
            raise ValueError(f"{m.NONFINITE_MESSAGE}: {a!r}")
        return math.fmod(a, m.TAU)

    return {"wrap_fn": wrap_fn}


def tilt_sign_flipped(m):
    """The active instead of the passive transform: Rot(e, +delta)."""
    return {"tilt_fn": lambda phi, delta: m.rot((math.cos(phi), math.sin(phi), 0.0), delta)}


def oracle_node_nan(m):
    return {"oracle": m.oracle_with_nonfinite(1, math.nan)}


def oracle_node_undefined_at_sweep_crossing(m):
    """The oracle reports no node at the two crossing azimuths of the E5b sweep (i = 0.1 deg)."""

    def oracle(inc, node, phi, delta, wrap_fn=m.wrap):
        d_i, d_node = m.finite(inc, node, phi, delta, wrap_fn)
        if inc == math.radians(0.1) and node == 0.0 and phi in (0.0, math.radians(180.0)):
            return d_i, None
        return d_i, d_node

    return {"oracle": oracle}


def oracle_node_scaled(m):
    """Delta Omega 0.01 % too large."""

    def oracle(inc, node, phi, delta, wrap_fn=m.wrap):
        d_i, d_node = m.finite(inc, node, phi, delta, wrap_fn)
        return d_i, None if d_node is None else 1.0001 * d_node

    return {"oracle": oracle}


def oracle_node_negated(m):
    """Delta Omega with the wrong sign."""

    def oracle(inc, node, phi, delta, wrap_fn=m.wrap):
        d_i, d_node = m.finite(inc, node, phi, delta, wrap_fn)
        return d_i, None if d_node is None else -d_node

    return {"oracle": oracle}


def builtin(name):
    """The kwargs of a built-in exact mutant of the (mutated) module."""
    return lambda m: m.EXACT_MUTANTS[name][0]


# ------------------------------------------------------------------ the 18 assertions
# (id, test, text identifying the assertion, category, protects, evidence)
# A: evidence = (built-in mutant, designated test)
# B: evidence = (defect, defect description, text of the independent check's failure)
# C: evidence = rationale
ASSERTIONS = [
    (
        "W1",
        "finite wrap",
        "outside (-pi, pi]",
        "B",
        "results lie in (-pi, pi]",
        (
            builtin("M3P6-F3_previous_wrap_minus_pi_to_pi"),
            "the previous [-pi, pi) wrap",
            "exact reduction",
        ),
    ),
    (
        "W2",
        "finite wrap",
        "exact reduction",
        "A",
        "each result equals the exact rational reduction (amendments 3 and 4)",
        ("M3P10-F2_wrap_inexact_reduction", "wrap"),
    ),
    (
        "W3",
        "finite wrap",
        "not deterministic",
        "C",
        "two calls with the same input agree",
        "wrap() is a stateless function of one float in IEEE arithmetic, so it cannot return "
        "different results for the same input unless mutable state is added to it. W2 checks "
        "every result against the exact reduction. W3 is a diagnostic for such a change; a "
        "mutant that it alone rejects would have to be correct on the first call and wrong on "
        "the second, which is not a plausible defect of this implementation.",
    ),
    (
        "W4",
        "finite wrap",
        "wrap endpoint (",
        "B",
        "wrap(+pi) = wrap(-pi) = +pi",
        (
            builtin("M3P6-F3_previous_wrap_minus_pi_to_pi"),
            "the previous [-pi, pi) wrap (wrap(-pi) = -pi)",
            "exact reduction",
        ),
    ),
    (
        "W5",
        "finite wrap",
        "for exact equivalents",
        "B",
        "angles differing by an exact multiple of 2 pi wrap to the same result",
        (
            wrap_no_correction,
            "fmod without the correction step (not periodic on (-pi, pi])",
            "exact reduction",
        ),
    ),
    (
        "W6",
        "finite wrap",
        "exactly representable equivalent pairs",
        "C",
        "W5 has at least 5 exactly representable pairs to test",
        "A coverage guard on the fixed input list of W5 (30 pairs are found). It can fail only "
        "if that list in the code is edited, and it protects W5 from becoming vacuous, not a "
        "computed property.",
    ),
    (
        "N1",
        "non-finite wrap",
        "raised {type(exc).__name__}",
        "A",
        "a non-finite input raises ValueError, not another exception type (amendment 4)",
        ("M3P10-F2_wrap_nonfinite_raises_typeerror", "wrap_nonfinite"),
    ),
    (
        "E1",
        "E1",
        "E1 rotation convention deviation",
        "B",
        "the tilt transform is the passive Rot(e, -delta), a proper rotation",
        (tilt_sign_flipped, "the active transform Rot(e, +delta)", "E2 endpoint not equatorial"),
    ),
    (
        "E2a",
        "E2",
        "E2 counterexample i = 2 deg",
        "C",
        "the review-06 counterexample (i = 2 deg, delta = 5 deg) is among the E2 cases",
        "A guard on the fixed E2 case list in the code. The case it requires is constructed "
        "from LOW_INC and CROSS_BY and is checked by the E2 identity like every other case; "
        "the guard fails only if those constants are edited.",
    ),
    (
        "E2b",
        "E2",
        "unexpected undefined node",
        "A",
        "no E2 case is skipped because a node is reported undefined (E2 cannot become vacuous)",
        ("M3P10-F2_line_of_nodes_interior_undefined", "E2"),
    ),
    (
        "E2c",
        "E2",
        ": {dev:.3e}",
        "A",
        "the exact line-of-nodes identity in every regime (amendment 3)",
        ("M3P10-F2_line_of_nodes_crossing_node_unchanged", "E2"),
    ),
    (
        "E2d",
        "E2",
        "E2 endpoint claims a defined node",
        "A",
        "the node is undefined at the endpoints j = 0 and j = pi (amendment 3)",
        ("M3P10-F2_line_of_nodes_endpoints_defined", "E2"),
    ),
    (
        "E2e",
        "E2",
        "E2 endpoint not equatorial",
        "B",
        "B is equatorial at the endpoints",
        (tilt_sign_flipped, "the active transform Rot(e, +delta)", "E1 rotation convention"),
    ),
    (
        "E5b-nonfinite",
        "E5b",
        "E5b sweep: non-finite node difference",
        "B",
        "a non-finite node difference in the azimuth sweep is a failure",
        (oracle_node_nan, "a NaN node difference", "E5b sweep: only"),
    ),
    (
        "E5b-defined",
        "E5b",
        "E5b sweep: only {defined}",
        "B",
        "the sweep has at least 359 defined samples per tilt sign",
        (
            oracle_node_undefined_at_sweep_crossing,
            "no node at the sweep's crossing azimuths, so the jump is never asserted",
            "E5c coverage",
        ),
    ),
    (
        "E5d",
        "E5d",
        "E5d equatorial node",
        "A",
        "an equatorial orbit has no node",
        ("M3P10-F2_equatorial_node_defined", "E5d"),
    ),
    (
        "E6-value",
        "E6",
        "E6 review-04 example not reproduced",
        "B",
        "the review-04 node example 90.2598055437 deg",
        (oracle_node_scaled, "Delta Omega 0.01 % too large", "E3 closed form"),
    ),
    (
        "E6-sign",
        "E6",
        "E6 review-04 example sign disagreement",
        "B",
        "the review-04 example's node change and first-order term agree in sign",
        (oracle_node_negated, "Delta Omega with the wrong sign", "E3 closed form"),
    ),
]


def remove_assertion(text, identifying):
    """The script with the one failures.append(...) whose source contains `identifying`
    replaced by `pass`."""
    lines = text.splitlines(keepends=True)
    found = []
    for node in ast.walk(ast.parse(text)):
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "append"
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "failures"
            and identifying in ast.get_source_segment(text, node)
        ):
            found.append(node)
    if len(found) != 1:
        raise ValueError(f"{identifying!r} identifies {len(found)} assertions")
    node = found[0]
    removed = " " * node.col_offset + "pass  # assertion removed\n"
    return "".join([*lines[: node.lineno - 1], removed, *lines[node.end_lineno :]]), node.lineno


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def failures_of(m, kwargs):
    failures, _, _, _ = m.run_exact(**kwargs)
    return failures


def main(out_path):
    text = SCRIPT.read_text(encoding="utf-8")
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        workdir = pathlib.Path(tmp)
        intact = load(SCRIPT, "verification_intact")
        for ident, test, identifying, category, protects, evidence in ASSERTIONS:
            mutated, line = remove_assertion(text, identifying)
            entry = {
                "id": ident,
                "test": test,
                "line": line,
                "category": category,
                "protects": protects,
            }
            if category == "C":
                entry["rationale"] = evidence
                entry["result"] = "PASS"
                results.append(entry)
                continue
            path = workdir / f"removed_{ident}.py"
            path.write_text(mutated, encoding="utf-8")
            removed = load(path, f"removed_{ident.replace('-', '_')}")
            if category == "A":
                mutant, designated = evidence
                minimum = intact.MIN_DESIGNATED_FAILURES.get(mutant, {}).get(designated, 1)
                before = intact.by_test(failures_of(intact, intact.EXACT_MUTANTS[mutant][0]))
                after = removed.by_test(failures_of(removed, removed.EXACT_MUTANTS[mutant][0]))
                entry["built_in_mutant"] = mutant
                entry["designated_test"] = designated
                entry["designated_failures_with_assertion"] = before[designated]
                entry["designated_failures_without_assertion"] = after[designated]
                ok = before[designated] >= minimum and after[designated] < minimum
            else:
                defect, description, independent = evidence
                with_assertion = failures_of(intact, defect(intact))
                without = failures_of(removed, defect(removed))
                entry["defect"] = description
                entry["independent_check"] = independent
                entry["independent_failures_without_assertion"] = sum(
                    independent in f for f in without
                )
                entry["independent_failures_with_assertion"] = sum(
                    independent in f for f in with_assertion
                )
                ok = (
                    entry["independent_failures_without_assertion"] > 0
                    and entry["independent_failures_with_assertion"] > 0
                )
            entry["result"] = "PASS" if ok else "FAIL"
            results.append(entry)
    counts = {c: sum(1 for r in results if r["category"] == c) for c in "ABCD"}
    ok = len(results) == 18 and all(r["result"] == "PASS" for r in results)
    report = {
        "verdict": "PASS" if ok else "FAIL",
        "script": SCRIPT.name,
        "assertions": len(results),
        "categories": counts,
        "results": results,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: report[k] for k in ("verdict", "assertions", "categories")}))
    for r in results:
        print(r["id"], r["category"], r["result"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
