# ruff: noqa
import sys, importlib.util, subprocess, json, os
from pathlib import Path

root = Path.cwd()
if len(sys.argv) == 1:
    cases = ["F1", "F2", "F3", "F4", "F5", "F6"]
    spec = importlib.util.spec_from_file_location("t", root / "tests/test_gmat_m2.py")
    t = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t)
    cases += sorted(t.ROW_CASES | t.EVENT_CASES)
    results = {}
    for case in cases:
        p = subprocess.run(
            [sys.executable, __file__, case],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        (root / "review_scratch" / ("revert-" + case + ".log")).write_text(p.stdout)
        results[case] = p.returncode
    print(json.dumps(results, indent=2))
    sys.exit(0)
from tars.validation import gmat_m2 as g
import pytest

case = sys.argv[1]


class Plugin:
    def pytest_collection_modifyitems(self, session, config, items):
        modules = {item.module for item in items}
        if case == "F1":
            for module in modules:
                old = module._cli

                def cli(old=old):
                    c = old()
                    c._evaluate = lambda *a, **k: (
                        [],
                        c.Check("disabled", {"gmat_rows": 1}, {}, "provisional"),
                    )
                    return c

                module._cli = cli
        elif case == "F2":

            def split(script):
                values = {}
                lines = []
                for line in script.splitlines():
                    m = g._STATE_LINE.match(line)
                    if m:
                        values[m[1]] = float(m[2])
                    else:
                        lines.append(line)
                import numpy as np

                return (
                    lines,
                    np.array([values[k] for k in g._STATE_KEYS[:3]]) * 1000,
                    np.array([values[k] for k in g._STATE_KEYS[3:]]) * 1000,
                )

            g.split_script = split
        elif case == "F3":
            g.provenance_problems = lambda *a, **k: []
        elif case == "F4":
            for module in modules:
                old = module._cli

                def cli(old=old):
                    c = old()

                    def generate(args):
                        for name in args.missions:
                            g.reference_files(name)["script"].write_text(
                                c._script(name, f"{name}_report.txt")
                            )
                        return 0

                    # Redirect all references to scratch before invoking the unsafe old workflow.
                    import shutil

                    dst = root / "review_scratch" / "revert-F4-refs"
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(g.reference_dir(), dst)
                    g.reference_dir = lambda: dst
                    c.cmd_generate = generate
                    return c

                module._cli = cli
        elif case == "F5":
            g.coverage_problems = lambda *a, **k: []
        elif case == "F6":
            g.missing_gates = lambda *a, **k: []
        else:
            for fn in ["alignment_metrics", "o9_metrics"]:
                old = getattr(g, fn)

                def disabled(*a, old=old, **k):
                    result = old(*a, **k)
                    if case in result:
                        result[case] = 0.0
                    return result

                setattr(g, fn, disabled)


tests = {
    "F1": "test_run_validates_a_staged_reference_and_replaces_nothing_on_failure",
    "F2": "test_state_assignments_must_stay_in_place_once",
    "F3": "test_provenance_is_required",
    "F4": "test_generate_never_writes_into_the_references",
    "F5": "test_missing_observations_are_not_vacuous_passes",
    "F6": "test_standalone_compare_fails_closed_without_thresholds",
}
if case not in tests:
    spec = importlib.util.spec_from_file_location("t", root / "tests/test_gmat_m2.py")
    t = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t)
    test = (
        "test_each_reference_metric_fails_on_its_corruption"
        if case in t.ROW_CASES
        else "test_each_simulator_metric_fails_on_its_corruption"
    ) + f"[{case}]"
else:
    test = tests[case]
sys.exit(
    pytest.main(
        ["-q", "-p", "no:cacheprovider", str(root / "tests/test_gmat_m2.py") + "::" + test],
        plugins=[Plugin()],
    )
)
