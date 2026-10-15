# ruff: noqa
import importlib.util
import json
from unittest.mock import patch
import scipy.integrate

spec = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
original = scipy.integrate.solve_ivp
calls = 0


def corrupted(*args, **kwargs):
    sol = original(*args, **kwargs)
    dense = sol.sol

    def output(t):
        global calls
        out = dense(t)
        out[3:6, :] = 0.0
        calls += 1
        return out

    sol.sol = output
    return sol


with patch.object(scipy.integrate, "solve_ivp", corrupted):
    rejected, check = cli._evaluate("m2_prograde_burn")
    print(
        json.dumps(
            {
                "dense_outputs_corrupted": calls,
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
    rc = proof.main(["--out", "review_scratch/dense_velocity_m2.json"])
    print("proof exit:", rc, "corrupted dense outputs:", calls)
    assert rc == 0
clean = json.load(open("review_scratch/m2.json"))
bad = json.load(open("review_scratch/dense_velocity_m2.json"))
print("all check records identical:", clean["results"] == bad["results"])
assert clean["results"] == bad["results"]
