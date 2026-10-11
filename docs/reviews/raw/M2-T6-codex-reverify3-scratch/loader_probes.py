# ruff: noqa
import json, inspect, sys, subprocess
from pathlib import Path
import pytest
from tars.validation import thresholds as t
from tars.validation.m2_missions import MISSIONS

if len(sys.argv) > 1:
    which = sys.argv[1]

    class Plugin:
        def pytest_collection_modifyitems(self, items):
            original = getattr(t, which)
            source = inspect.getsource(original)
            ns = dict(t.__dict__)
            exec(source.replace('    _require_finite_limits(data["limits"])\n', ""), ns)
            setattr(t, which, ns[which])

    sys.exit(
        pytest.main(
            [
                "-q",
                "-p",
                "no:cacheprovider",
                "tests/test_gmat_m2.py::test_threshold_loaders_reject_non_finite_or_negative_limits",
            ],
            plugins=[Plugin()],
        )
    )
for which in ["load_thresholds", "load_scoped_thresholds"]:
    for bad in [float("inf"), float("-inf"), float("nan"), -1, "0.6", True, [], {}]:
        source = t.M1_THRESHOLDS if which == "load_thresholds" else t.M2_THRESHOLDS
        data = json.loads(source.read_text())
        values = (
            data["limits"]["kepler_reference"]
            if which == "load_thresholds"
            else data["limits"]["o9_gmat"]["all"]
        )
        key = next(k for k, v in values.items() if v is not None)
        values[key] = bad
        path = Path("review_scratch") / "bad_limits.json"
        path.write_text(json.dumps(data))
        try:
            result = getattr(t, which)(
                path,
                **(
                    {"missions": frozenset(m.name for m in MISSIONS)}
                    if which == "load_scoped_thresholds"
                    else {}
                ),
            )
            print(which, repr(bad), "ACCEPTED", flush=True)
        except ValueError as e:
            print(which, repr(bad), "rejected", str(e), flush=True)
    for_disable = subprocess.run([sys.executable, __file__, which], capture_output=True, text=True)
    Path("review_scratch/disabled_" + which + ".log").write_text(
        for_disable.stdout + for_disable.stderr
    )
    print(which, "disabled tests fail", for_disable.returncode == 1, flush=True)
    assert for_disable.returncode == 1
