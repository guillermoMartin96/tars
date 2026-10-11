# ruff: noqa
import inspect, subprocess, sys
from pathlib import Path
import pytest
from tars.validation import thresholds as t

mutations = {
    "finite": ("if not math.isfinite(limits) or limits < 0:", "if limits < 0:"),
    "negative": ("if not math.isfinite(limits) or limits < 0:", "if not math.isfinite(limits):"),
    "numeric": (
        "if isinstance(limits, bool) or not isinstance(limits, (int, float)):",
        "if False:",
    ),
}
if len(sys.argv) == 1:
    for key in mutations:
        p = subprocess.run([sys.executable, __file__, key], capture_output=True, text=True)
        Path("review_scratch/disabled_limit_" + key + ".log").write_text(p.stdout + p.stderr)
        print(key, "expected test failure", p.returncode == 1)
        assert p.returncode == 1
else:
    key = sys.argv[1]

    class Plugin:
        def pytest_collection_modifyitems(self, items):
            source = inspect.getsource(t._require_finite_limits)
            old, new = mutations[key]
            ns = t.__dict__
            exec(source.replace(old, new), ns)

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
