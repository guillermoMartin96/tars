"""DR-0028 amendments 7 and 8 / reviews M3P10-F2 and M3P11-F2 (I-10 section 4, I-11 section 3):
classification of the 18 assertions that review 10's assertion-removal sweep found not
individually load-bearing.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python dr0028_node_signed_assertion_classification.py <out.json>

Categories (I-10 section 4):
  A  independently important: removing it could let an otherwise undetected correctness defect
     pass. A built-in mutant violates exactly the property it protects. The evidence, executed
     here for each: the mutant's intended defect is exercised (its declared defect, observed
     against the reference implementations: shown, never missing, nothing else different) and it
     raises no exception; with the assertion present, the designated test rejects it; with only
     this assertion removed, the designated test reports nothing and no exact-property or
     wrapping check reports anything (the defect escapes every one of them).
  B  redundant: another, named check rejects every defect this assertion can see. The evidence:
     a property-wide argument, with its premises executed here (the other check covers the same
     inputs with an equal or tighter criterion), and a demonstration that, with only this
     assertion removed, a defect of its kind is still rejected by that check.
  C  diagnostic: it guards test configuration or reporting, not a computed correctness
     property. The rationale is recorded; nothing is executed for it.
  D  uncertain: none.
Amendment 7 classified W5, E1, E2e, E5b-nonfinite and E5b-defined as B on the evidence of one
overlapping defect each; review 11 (M3P11-F2) gave a counterexample for each, and amendment 8
classifies them as A, each with a built-in mutant (M3P11-F2_*).

The 18 assertions are identified in the script's actual inventory: each identifying text must
select exactly one `failures.append(...)` statement, the 18 must be distinct, and they must be
exactly the 18 statements that the assertion-removal sweep committed at 896d52d (review 10)
found surviving.

Each executed demonstration loads a copy of the verification script with exactly one
`failures.append(...)` statement replaced by `pass` (located with ast), imports it, and calls its
exact-property tests with the defect. Exit status 0 only if every demonstration holds. Nothing in
the verification script is changed. Requires git (to read the 896d52d sweep); otherwise standard
library only.
"""

import ast
import importlib.util
import json
import math
import pathlib
import subprocess
import sys
import tempfile
from fractions import Fraction

SCRIPT = pathlib.Path(__file__).with_name("dr0028_node_signed_verification.py")
SWEEP = pathlib.Path(__file__).with_name("dr0028_node_signed_assertion_sweep_results.json")
SWEEP_AT_REVIEW_10 = "896d52d"
E6_COMMITTED_NODE_DEG = 90.2598055437  # exact_properties, E6
E6_TOLERANCE_DEG = 5.0e-11


# ------------------------------------------------------------- demonstration defects (B)
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


# --------------------------------------------- property-wide redundancy premises (B)
def wrap_inputs(m):
    """Every input that the finite wrapping test passes to wrap_fn, in order."""
    seen = []

    def recording(a):
        seen.append(a)
        return m.wrap(a)

    m.wrap_tests(recording)
    return seen


def premises_w1(m):
    """W1 (result in (-pi, pi]) fails at input a only if got is outside (-pi, pi]. W2 compares the
    same got, at the same input in the same loop iteration, with the exact reduction; if that
    reduction lies in (-pi, pi] for every input, W1 failing implies W2 failing there."""
    inputs = wrap_inputs(m)
    pi = Fraction(m.PI)
    inside = all(-pi < m.wrap_reference(a) <= pi for a in inputs)
    return inside, {"inputs": len(inputs), "every_exact_reduction_in_interval": inside}


def premises_w4(m):
    """W4 (wrap(+pi) = wrap(-pi) = +pi) fails only if wrap_fn(pi) or wrap_fn(-pi) is not +pi. W2
    checks both inputs against their exact reduction, which is +pi for both; so W4 failing implies
    W2 failing, provided wrap_fn returns the same result for the same input (W3, category C)."""
    inputs = wrap_inputs(m)
    both = m.PI in inputs and -m.PI in inputs
    reduce_to_pi = all(m.wrap_reference(a) == Fraction(m.PI) for a in (m.PI, -m.PI))
    ok = both and reduce_to_pi
    return ok, {"pi_and_minus_pi_in_W2_inputs": both, "exact_reduction_is_plus_pi": reduce_to_pi}


def e6_call(m):
    return (math.radians(30.0), math.radians(90.0), 0.0, math.radians(0.15))


def oracle_calls(m):
    calls = []

    def recording(inc, node, phi, delta, wrap_fn=m.wrap):
        calls.append((inc, node, phi, delta))
        return m.finite(inc, node, phi, delta, wrap_fn)

    m.exact_properties(oracle=recording)
    return calls


def premises_e6_value(m):
    """E6 calls the oracle once, at (i, Omega, phi, delta) = (30, 90, 0, 0.15) deg. E3 calls it at
    the same arguments (phi = Omega - 90 deg is exactly 0.0) and compares Delta Omega with the
    closed form within noise(30 deg). If the closed form is within `margin` of E6's committed value
    inside E6's tolerance, and noise(30 deg) is smaller than that margin, any Delta Omega that E6
    rejects deviates from the closed form by more than E3's tolerance, so E3 rejects it too."""
    args = e6_call(m)
    same_call = oracle_calls(m).count(args) >= 2  # E3 and E6
    inc, _, _, delta = args
    closed = math.atan(math.sin(delta) / math.tan(inc))
    margin_deg = E6_TOLERANCE_DEG - abs(90.0 + math.degrees(closed) - E6_COMMITTED_NODE_DEG)
    e3_tol_deg = math.degrees(m.noise(inc))
    ok = same_call and e3_tol_deg < margin_deg
    return ok, {
        "E3_makes_the_same_oracle_call": same_call,
        "E6_margin_deg": margin_deg,
        "E3_tolerance_deg": e3_tol_deg,
    }


def premises_e6_sign(m):
    """E6-sign requires Delta Omega > 0 (and the committed formula's value > 0) at E6's call. The
    closed form there is positive and larger than E3's tolerance, so a Delta Omega <= 0 deviates
    from it by more than the tolerance and E3 rejects it at the same call. The formula's sign at
    this (i, Omega - phi) is covered on the first-order grid by the sign check (amendment 6)."""
    args = e6_call(m)
    same_call = oracle_calls(m).count(args) >= 2
    inc, _, _, delta = args
    closed = math.atan(math.sin(delta) / math.tan(inc))
    ok = same_call and closed > m.noise(inc)
    return ok, {
        "E3_makes_the_same_oracle_call": same_call,
        "closed_form_rad": closed,
        "E3_tolerance_rad": m.noise(inc),
    }


# ------------------------------------------------------------------ the 18 assertions
# (id, test, text identifying the assertion, category, protects, evidence)
# A: evidence = (built-in mutant, designated test)
# B: evidence = (premises, defect, defect description, text of the independent check's failure)
# C: evidence = rationale
ASSERTIONS = [
    (
        "W1",
        "finite wrap",
        "outside (-pi, pi]",
        "B",
        "results lie in (-pi, pi]",
        (
            premises_w1,
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
            premises_w4,
            builtin("M3P6-F3_previous_wrap_minus_pi_to_pi"),
            "the previous [-pi, pi) wrap (wrap(-pi) = -pi)",
            "exact reduction",
        ),
    ),
    (
        "W5",
        "finite wrap",
        "for exact equivalents",
        "A",
        "angles differing by an exact multiple of 2 pi wrap to the same result (periodicity), "
        "including inputs that W2's fixed list does not contain",
        ("M3P11-F2_wrap_not_periodic", "wrap"),
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
        "A",
        "the tilt transform is exactly the passive Rot(e, -delta) (R = Rx(-delta) at phi = 0), "
        "not merely a proper rotation that keeps B's pole and the equatorial endpoints",
        ("M3P11-F2_node_origin_offset", "E1"),
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
        "A",
        "B is equatorial at the endpoints j = 0 and j = pi for every tested node, including tilt "
        "azimuths that E1 does not sample",
        ("M3P11-F2_tilt_axis_quantized", "E2"),
    ),
    (
        "E5b-nonfinite",
        "E5b",
        "E5b sweep: non-finite node difference",
        "A",
        "every node difference in the azimuth sweep is finite (a non-finite value is a failure, "
        "not merely a sample not counted)",
        ("M3P11-F2_oracle_node_nan_at_sweep_azimuth", "E5b"),
    ),
    (
        "E5b-defined",
        "E5b",
        "E5b sweep: only {defined}",
        "A",
        "the node is defined at every sweep azimuth except at most one exact endpoint (at least "
        "359 defined samples per tilt sign), not only at the crossing azimuths",
        ("M3P11-F2_oracle_node_undefined_at_sweep_azimuths", "E5b"),
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
        (premises_e6_value, oracle_node_scaled, "Delta Omega 0.01 % too large", "E3 closed form"),
    ),
    (
        "E6-sign",
        "E6",
        "E6 review-04 example sign disagreement",
        "B",
        "the review-04 example's node change and first-order term agree in sign",
        (
            premises_e6_sign,
            oracle_node_negated,
            "Delta Omega with the wrong sign",
            "E3 closed form",
        ),
    ),
]


def assertion_nodes(text):
    """Every `failures.append(...)` statement of the script."""
    return [
        node
        for node in ast.walk(ast.parse(text))
        if isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Attribute)
        and node.value.func.attr == "append"
        and isinstance(node.value.func.value, ast.Name)
        and node.value.func.value.id == "failures"
    ]


def find_assertion(text, identifying):
    found = [n for n in assertion_nodes(text) if identifying in ast.get_source_segment(text, n)]
    if len(found) != 1:
        raise ValueError(f"{identifying!r} identifies {len(found)} assertions")
    return found[0]


def remove_assertion(text, identifying):
    """The script with the one failures.append(...) whose source contains `identifying`
    replaced by `pass`."""
    lines = text.splitlines(keepends=True)
    node = find_assertion(text, identifying)
    removed = " " * node.col_offset + "pass  # assertion removed\n"
    return "".join([*lines[: node.lineno - 1], removed, *lines[node.end_lineno :]]), node.lineno


def inventory(text):
    """The 18 identities checked against the script's assertion statements and against the
    statements that the 896d52d sweep (review 10) found surviving, by their first source line."""
    lines = text.splitlines()
    first = [lines[find_assertion(text, a[2]).lineno - 1].strip() for a in ASSERTIONS]
    root = subprocess.run(
        ["git", "-C", str(SWEEP.parent), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    relative = SWEEP.resolve().relative_to(root).as_posix()
    sweep = json.loads(
        subprocess.run(
            ["git", "-C", root, "show", f"{SWEEP_AT_REVIEW_10}:{relative}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    survivors = sorted(r["assertion"] for r in sweep["results"] if r["outcome"] == "survives")
    report = {
        "assertion_statements_in_script": len(assertion_nodes(text)),
        "identified": len(first),
        "distinct": len(set(first)),
        "sweep_at_896d52d_survivors": len(survivors),
        "identical_to_sweep_at_896d52d_survivors": sorted(first) == survivors,
    }
    ok = len(set(first)) == len(first) == 18 and report["identical_to_sweep_at_896d52d_survivors"]
    return ok, report


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def failures_of(m, kwargs):
    failures, _, _, _ = m.run_exact(**kwargs)
    return failures


def category_a(entry, intact, removed, mutant, designated):
    kwargs = intact.EXACT_MUTANTS[mutant][0]
    observed = intact.observe(intact.run_exact, intact.DEFECTS[mutant], **kwargs)
    minimum = intact.MIN_DESIGNATED_FAILURES.get(mutant, {}).get(designated, 1)
    before = failures_of(intact, kwargs)
    after = failures_of(removed, removed.EXACT_MUTANTS[mutant][0])
    entry["built_in_mutant"] = mutant
    entry["intended_defect"] = [r["defect"] for r in observed["defect_calls"].values()]
    entry["defect_exercised"] = observed["defect_exercised"]
    entry["defect_calls"] = observed["defect_calls"]
    entry["exception"] = observed["exception"]
    entry["designated_test"] = designated
    entry["designated_failures_with_assertion"] = intact.by_test(before)[designated]
    entry["designated_failures_without_assertion"] = removed.by_test(after)[designated]
    entry["all_failures_with_assertion"] = len(before)
    entry["all_failures_without_assertion"] = len(after)
    return (
        observed["defect_exercised"]
        and observed["exception"] is None
        and entry["designated_failures_with_assertion"] >= minimum
        and entry["designated_failures_without_assertion"] < minimum
        and not after
    )


def category_b(entry, intact, removed, evidence):
    premises, defect, description, independent = evidence
    premises_ok, premises_report = premises(intact)
    entry["redundancy_argument"] = " ".join(premises.__doc__.split())
    entry["premises"] = premises_report
    entry["premises_hold"] = premises_ok
    with_assertion = failures_of(intact, defect(intact))
    without = failures_of(removed, defect(removed))
    entry["defect"] = description
    entry["independent_check"] = independent
    entry["independent_failures_without_assertion"] = sum(independent in f for f in without)
    entry["independent_failures_with_assertion"] = sum(independent in f for f in with_assertion)
    return (
        premises_ok
        and entry["independent_failures_without_assertion"] > 0
        and entry["independent_failures_with_assertion"] > 0
    )


def main(out_path):
    text = SCRIPT.read_text(encoding="utf-8")
    inventory_ok, inventory_report = inventory(text)
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
                ok = category_a(entry, intact, removed, *evidence)
            else:
                ok = category_b(entry, intact, removed, evidence)
            entry["result"] = "PASS" if ok else "FAIL"
            results.append(entry)
    counts = {c: sum(1 for r in results if r["category"] == c) for c in "ABCD"}
    ok = inventory_ok and len(results) == 18 and all(r["result"] == "PASS" for r in results)
    report = {
        "verdict": "PASS" if ok else "FAIL",
        "script": SCRIPT.name,
        "inventory": inventory_report,
        "assertions": len(results),
        "categories": counts,
        "reclassified_by_amendment_8": ["W5", "E1", "E2e", "E5b-nonfinite", "E5b-defined"],
        "results": results,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: report[k] for k in ("verdict", "inventory", "assertions", "categories")}))
    for r in results:
        print(r["id"], r["category"], r["result"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
