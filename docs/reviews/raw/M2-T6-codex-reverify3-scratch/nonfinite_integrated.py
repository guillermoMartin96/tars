# ruff: noqa
import importlib.util, json
from unittest.mock import patch
from tars.validation import m2
from tars.validation.thresholds import load_scoped_thresholds
from tars.validation.m2_missions import MISSIONS

spec = importlib.util.spec_from_file_location("proof", "toolbox/validators/m2_proof.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
original = m2.dop853_reference
calls = 0


def corrupt(*args, **kw):
    global calls
    ref = original(*args, **kw)
    if 650.0 in ref:
        ref[650.0] = ref[650.0].copy()
        ref[650.0][:6] = float("nan")
        calls += 1
    return ref


mission = next(m for m in MISSIONS if m.name == "m2_prograde_burn")
gates = p.Gates(load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS)))
with patch.object(m2, "dop853_reference", corrupt):
    checks, info = p.mission_checks(mission, gates, quick=True)
    print(
        json.dumps(
            {
                "corrupted_reference_calls": calls,
                "checks": len(checks),
                "failed": [c.validator for c in checks if not c.passed],
                "missing_gates": gates.missing,
                "o9": [
                    {"passed": c.passed, "metrics": c.metrics}
                    for c in checks
                    if c.validator == "o9_gmat[m2_prograde_burn]"
                ],
            }
        ),
        flush=True,
    )
