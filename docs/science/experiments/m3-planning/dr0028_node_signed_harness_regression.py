"""DR-0028 amendment 7 / review M3P10-F1: the harness controls run against the original
(defective) mutation check and against the corrected one.

Planning research artifact (not production code, not a Proof gate).

Usage:
    python dr0028_node_signed_harness_regression.py <out.json>

The original harness and verification script are read from git at ORIGINAL (the commit
reviewed by review 10, where M3P10-F1 was found) into a temporary directory. Every control of
the corrected harness (dr0028_node_signed_mutation_check.CONTROLS) is applied to each version:
the same edits, and the same claimed expectation, taken by name from that version's own
MUTATIONS. The original harness classifies a run only as detected or not detected; a control is
met there when it is detected exactly if its declared category is "expected rejection". The
corrected harness must give every control its declared category.

The M3P10-F1 regression controls (REGRESSION_CONTROLS) must each fail against the original
harness, which shows that they reproduce the defect, and pass against the corrected one.
Exit status 0 only if both hold and every control passes against the corrected harness.
Requires git (to read ORIGINAL); otherwise standard library only.
"""

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ORIGINAL = "896d52d"
HARNESS = "dr0028_node_signed_mutation_check.py"
SCRIPT = "dr0028_node_signed_verification.py"
REGRESSION_CONTROLS = (
    "import_failure_inside_mutant",
    "runtime_exception_inside_mutant",
    "exception_suppressed_inside_mutant",
    "allowed_exception_wrong_location",
    "allowed_exception_wrong_type",
)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_show(path):
    root = subprocess.run(
        ["git", "-C", str(HERE), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    relative = (HERE / path).relative_to(root).as_posix()
    return subprocess.run(
        ["git", "-C", root, "show", f"{ORIGINAL}:{relative}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def original_result(old, control, source, workdir):
    """(detected, observed) for one control under the original harness."""
    name, _, edits, claimed, _ = control
    by_name = {m[0]: m for m in old.MUTATIONS}
    expected = by_name[claimed][5]
    if isinstance(edits, str):
        edits = [by_name[edits][3:5]]
    if edits is None:
        observed, detected = old.classify(*old.run(None, workdir, f"old_{name}"), expected)
        return detected, observed
    for fragment, replacement in edits:
        if source.count(fragment) != 1:
            return False, f"not run: fragment occurs {source.count(fragment)} times"
        source = source.replace(fragment, replacement)
    observed, detected = old.classify(*old.run(source, workdir, f"old_{name}"), expected)
    return detected, observed


def main(out_path):
    new = load(HERE / HARNESS, "harness_corrected")
    current = (HERE / SCRIPT).read_text(encoding="utf-8")
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        workdir = pathlib.Path(tmp)
        original_dir = workdir / "original"
        original_dir.mkdir()
        (original_dir / HARNESS).write_text(git_show(HARNESS), encoding="utf-8")
        (original_dir / SCRIPT).write_text(git_show(SCRIPT), encoding="utf-8")
        old = load(original_dir / HARNESS, "harness_original")
        old_source = (original_dir / SCRIPT).read_text(encoding="utf-8")
        for control in new.CONTROLS:
            name, shows, _, claimed, category = control
            detected, observed = original_result(old, control, old_source, workdir)
            old_met = detected == (category == new.EXPECTED)
            corrected = new.run_control(control, current, workdir)
            results[name] = {
                "shows": shows,
                "claimed_expectation": claimed,
                "expected_classification": category,
                "original_harness": {
                    "classified_as_detected": detected,
                    "observed_outcome": observed,
                    "result": "PASS" if old_met else "FAIL",
                },
                "corrected_harness": {
                    "actual_classification": corrected["actual_classification"],
                    "observed_outcome": corrected["observed_outcome"],
                    "result": corrected["result"],
                },
                "regression_control": name in REGRESSION_CONTROLS,
            }
    reproduced = all(
        results[n]["original_harness"]["result"] == "FAIL" for n in REGRESSION_CONTROLS
    )
    corrected_ok = all(r["corrected_harness"]["result"] == "PASS" for r in results.values())
    report = {
        "verdict": "PASS" if reproduced and corrected_ok else "FAIL",
        "original": ORIGINAL,
        "regression_controls_fail_against_original": reproduced,
        "all_controls_pass_against_corrected": corrected_ok,
        "results": results,
    }
    with open(out_path, "w", encoding="ascii") as fh:
        json.dump(report, fh, indent=1)
        fh.write("\n")
    print(
        json.dumps(
            {
                n: [r["original_harness"]["result"], r["corrected_harness"]["result"]]
                for n, r in results.items()
            }
        )
    )
    print(json.dumps({k: report[k] for k in list(report)[:4]}))
    return 0 if reproduced and corrected_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
