# ruff: noqa
import sys, inspect, pytest, math
from unittest.mock import patch
from tars.validation import m2, gmat_m2, thresholds

mode = sys.argv[1]


class Plugin:
    def pytest_sessionstart(self, session):
        if mode == "worst":
            m2.worst = max
            gmat_m2.worst = max
        elif mode == "o9finite":
            src = inspect.getsource(gmat_m2.o9_metrics).replace(
                "invalid = [t for t in times if not np.all(np.isfinite(reference[t]))]",
                "invalid = []",
            )
            exec(src, gmat_m2.__dict__)
        elif mode == "o4finite":
            src = inspect.getsource(m2.reference_metrics).replace(
                "if any(not np.all(np.isfinite(ref[t])) for t in marks):", "if False:"
            )
            exec(src, m2.__dict__)
        elif mode == "integration":
            src = inspect.getsource(m2.dop853_reference).replace(
                "if not np.all(np.isfinite(sol.y)):", "if False:"
            )
            exec(src, m2.__dict__)
        elif mode in ("m1loader", "m2loader"):
            orig = thresholds._require_finite_limits
            target = 2 if mode == "m1loader" else 3

            def disabled(limits, depth, where="limits"):
                if where == "limits" and depth == target:
                    return
                return orig(limits, depth, where)

            thresholds._require_finite_limits = disabled
        elif mode == "structure":
            src = inspect.getsource(thresholds._require_finite_limits).replace(
                'raise ValueError(f"threshold {where} must be an object")', "return"
            )
            exec(src, thresholds.__dict__)
        elif mode == "objectleaf":
            src = inspect.getsource(thresholds._require_finite_limits).replace(
                "if limits is None:", "if limits is None or isinstance(limits, dict):"
            )
            exec(src, thresholds.__dict__)


selectors = {
    "worst": "test_worst_never_discards_nan",
    "o9finite": "test_nan_in_an_unreduced_reference_component_fails_o9",
    "o4finite": "test_nan_reference_state_fails_o4",
    "integration": "test_dop853_reference_rejects_non_finite_integration",
    "m1loader": "test_threshold_loaders_reject_object_limits",
    "m2loader": "test_threshold_loaders_reject_object_limits",
    "structure": "test_threshold_loaders_reject_a_wrong_structure",
    "objectleaf": "test_threshold_loaders_reject_object_limits",
}
sys.exit(
    pytest.main(
        ["-q", "-p", "no:cacheprovider", "tests/test_gmat_m2.py::" + selectors[mode]],
        plugins=[Plugin()],
    )
)
