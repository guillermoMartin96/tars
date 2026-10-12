# ruff: noqa
import importlib.util
import json
from unittest.mock import patch
import scipy.integrate
from tars.validation import m2

spec = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
original = scipy.integrate.solve_ivp
calls = 0


def corrupted(*args, **kwargs):
    global calls
    sol = original(*args, **kwargs)
    # Corrupt only raw independent solver DATA, keeping every helper unchanged.
    # At the observation horizon, corrupt terminal output data only.
    if args[1][1] == 53700.0 and 0.0 < args[2][6] < 300.0:
        sol.t[-1] = float("nan")
        sol.y[6, -1] = 299.0
        calls += 1
    return sol


with patch.object(scipy.integrate, "solve_ivp", corrupted):
    rejected, check = cli._evaluate("m2_prograde_burn")
    print(
        json.dumps(
            {
                "solver_outputs_corrupted": calls,
                "rejected": rejected,
                "passed": check is not None and check.passed,
            }
        )
    )
    assert not rejected and check.passed
    spec = importlib.util.spec_from_file_location("proof", "toolbox/validators/m2_proof.py")
    proof = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(proof)
    rc = proof.main(["--out", "review_scratch/time_poison_m2.json"])
    print("proof exit:", rc, "corrupted solver outputs:", calls)
    assert rc == 0
clean = json.load(open("review_scratch/m2.json"))
bad = json.load(open("review_scratch/time_poison_m2.json"))
print("report keys", list(clean))
print("all check records identical:", clean["results"] == bad["results"])
assert clean["results"] == bad["results"]
