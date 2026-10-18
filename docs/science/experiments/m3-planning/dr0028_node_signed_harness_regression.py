"""DR-0028 amendments 7-9 / reviews M3P10-F1, M3P11-F1 and M3P12-F1: the harness controls run
against the original (defective) mutation checks and against the corrected one.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python dr0028_node_signed_harness_regression.py <out.json>

Each original harness and its verification script are read from git into a temporary directory:
- 896d52d, the commit reviewed by review 10, where M3P10-F1 was found (an unrelated exception
  inside a built-in mutant counted as detection);
- c16b3b5, the commit reviewed by review 11, where M3P11-F1 was found (any difference from the
  reference counted as an exercised defect);
- 5b12eec, the commit reviewed by review 12, where M3P12-F1 was found (an oracle value injected
  inside check_formulas was observed only where the finite validation ran, so steps skipped after
  an invalid value were never observed). This harness has the independent exercise probe, and it
  is run with it (its own execute and classify, and its own probe process).
Every control of the corrected harness (dr0028_node_signed_mutation_check.CONTROLS) is applied to
each version: the same edits, and the same claimed expectation, taken by name from that version's
own MUTATIONS (a control whose fragment or expectation does not exist in a version is not run
there, which counts as not detected). An original harness is judged only on detection: a control
is met there when it is classified as detected exactly if its declared category is "expected
rejection". The corrected harness must give every control its declared category, exercise
result and reason.

The regression controls of each finding (REGRESSION_CONTROLS) must each fail against the harness
in which the finding was made, which shows that they reproduce the defect, and pass against the
corrected one. Exit status 0 only if this holds and every control passes against the corrected
harness. Requires git (to read the originals); otherwise standard library only.
"""

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
HARNESS = "dr0028_node_signed_mutation_check.py"
SCRIPT = "dr0028_node_signed_verification.py"
EXPECTED = "expected rejection"
REGRESSION_CONTROLS = {
    "896d52d": (  # M3P10-F1 (amendment 7)
        "import_failure_inside_mutant",
        "runtime_exception_inside_mutant",
        "exception_suppressed_inside_mutant",
        "allowed_exception_wrong_location",
        "allowed_exception_wrong_type",
    ),
    "c16b3b5": (  # M3P11-F1 (amendment 8)
        "suppressed_import_reassociated_fallback",
        "defect_in_wrong_component",
        "incidental_rounding_only",
        "partially_exercised_defect",
    ),
    "5b12eec": (  # M3P12-F1 (amendment 9)
        "first_step_only_claimed_all_steps_delta_i",
        "first_step_only_claimed_all_steps_delta_node",
        "partial_steps_claimed_all_steps",
        "intermediate_observations_missing",
        "observation_count_incorrect",
    ),
}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_show(commit, path):
    root = subprocess.run(
        ["git", "-C", str(HERE), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    relative = (HERE / path).relative_to(root).as_posix()
    return subprocess.run(
        ["git", "-C", root, "show", f"{commit}:{relative}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def original_result(old, control, source, workdir, label):
    """(detected, observed) for one control under an original harness.

    896d52d's classify returns (observed, detected); c16b3b5's and 5b12eec's return (category,
    observed). 5b12eec's classify also takes the exercise observation of its own probe."""
    _, _, edits, claimed = control[:4]
    by_name = {m[0]: m for m in old.MUTATIONS}
    if claimed not in by_name or (isinstance(edits, str) and edits not in by_name):
        return False, "not run: the claimed mutation does not exist in this version"
    expected = by_name[claimed][5]
    if isinstance(edits, str):
        edits = [by_name[edits][3:5]]
    if edits is not None:
        for fragment, replacement in edits:
            if source.count(fragment) != 1:
                return False, f"not run: fragment occurs {source.count(fragment)} times"
            source = source.replace(fragment, replacement)
    source = None if edits is None else source
    if hasattr(old, "execute"):  # 5b12eec: the probe decides exercise
        spec = old.exercise_spec(expected, by_name[claimed][6])
        code, output, last, exercise = old.execute(source, workdir, label, spec)
        result = old.classify(code, output, last, expected, exercise)
    else:
        result = old.classify(*old.run(source, workdir, label), expected)
    if isinstance(result[1], bool):
        return result[1], result[0]
    return result[0] == EXPECTED, f"{result[0]}: {result[1]}"


def main(out_path):
    new = load(HERE / HARNESS, "harness_corrected")
    current = (HERE / SCRIPT).read_text(encoding="utf-8")
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        workdir = pathlib.Path(tmp)
        originals = {}
        for commit in REGRESSION_CONTROLS:
            directory = workdir / f"original_{commit}"
            directory.mkdir()
            (directory / HARNESS).write_text(git_show(commit, HARNESS), encoding="utf-8")
            (directory / SCRIPT).write_text(git_show(commit, SCRIPT), encoding="utf-8")
            originals[commit] = (
                load(directory / HARNESS, f"harness_{commit}"),
                (directory / SCRIPT).read_text(encoding="utf-8"),
            )
        for control in new.CONTROLS:
            name, shows, _, claimed, category, _ = control
            entry = {
                "shows": shows,
                "claimed_expectation": claimed,
                "expected_classification": category,
                "regression_control_of": [
                    c for c, names in REGRESSION_CONTROLS.items() if name in names
                ],
            }
            for commit, (old, old_source) in originals.items():
                detected, observed = original_result(
                    old, control, old_source, workdir, f"old_{commit}_{name}"
                )
                entry[f"original_harness_{commit}"] = {
                    "classified_as_detected": detected,
                    "observed_outcome": observed,
                    "result": "PASS" if detected == (category == EXPECTED) else "FAIL",
                }
            corrected = new.run_control(control, current, workdir)
            entry["corrected_harness"] = {
                "actual_classification": corrected["actual_classification"],
                "exercise_established": corrected["exercise_established"],
                "reason_shown": corrected["reason_shown"],
                "observed_outcome": corrected["observed_outcome"],
                "result": corrected["result"],
            }
            results[name] = entry
    reproduced = {
        commit: all(results[n][f"original_harness_{commit}"]["result"] == "FAIL" for n in names)
        for commit, names in REGRESSION_CONTROLS.items()
    }
    corrected_ok = all(r["corrected_harness"]["result"] == "PASS" for r in results.values())
    ok = all(reproduced.values()) and corrected_ok
    report = {
        "verdict": "PASS" if ok else "FAIL",
        "originals": list(REGRESSION_CONTROLS),
        "regression_controls": REGRESSION_CONTROLS,
        "regression_controls_fail_against_original": reproduced,
        "all_controls_pass_against_corrected": corrected_ok,
        "results": results,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")
    columns = [f"original_harness_{c}" for c in REGRESSION_CONTROLS] + ["corrected_harness"]
    for n, r in results.items():
        print(n, *(r[c]["result"] for c in columns))
    print(
        json.dumps({k: report[k] for k in ("verdict", "regression_controls_fail_against_original")})
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
