# ruff: noqa
import importlib.util
import inspect
import json
from unittest.mock import patch
import numpy as np
from tars.astro import kepler

spec = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
original = kepler.propagate
calls = 0


def corrupted(*args, **kwargs):
    global calls
    r, v = original(*args, **kwargs)
    caller = inspect.currentframe().f_back
    if (
        caller.f_code.co_name == "kepler_state"
        and caller.f_back.f_code.co_name == "alignment_metrics"
    ):
        v = np.zeros_like(v)
        calls += 1
    return r, v


with patch.object(kepler, "propagate", corrupted):
    rejected, check = cli._evaluate("m2_prograde_burn")
    print(
        json.dumps(
            {
                "kepler_outputs_corrupted": calls,
                "rejected": rejected,
                "passed": check is not None and check.passed,
            }
        ),
        flush=True,
    )
    assert not rejected and check.passed
    spec = importlib.util.spec_from_file_location("proof", "toolbox/validators/m2_proof.py")
    proof = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(proof)
    rc = proof.main(["--out", "review_scratch/kepler_velocity_m2.json"])
    print("proof exit:", rc, "corrupted Kepler outputs:", calls)
    assert rc == 0
clean = json.load(open("review_scratch/m2.json"))
bad = json.load(open("review_scratch/kepler_velocity_m2.json"))
print("all check records identical:", clean["results"] == bad["results"])
assert clean["results"] == bad["results"]
