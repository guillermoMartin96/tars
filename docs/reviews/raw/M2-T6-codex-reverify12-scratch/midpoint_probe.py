# ruff: noqa
import importlib.util, inspect, json, sys
import numpy as np
import scipy.integrate
from tars.validation import m2


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


source, start = inspect.getsourcelines(m2._check_dense_consistency)
line = start + next(i for i, s in enumerate(source) if "mid = sol.sol(mid_t)" in s)
original = scipy.integrate.solve_ivp
counts = {"states": 0}


def solver(*a, **k):
    sol = original(*a, **k)
    dense = sol.sol

    def output(t):
        out = dense(t)
        caller = sys._getframe(1)
        if caller.f_code.co_name == "_check_dense_consistency" and caller.f_lineno == line:
            out[3:6] = 1e200
            assert np.all(np.isfinite(out))
            counts["states"] += out.shape[1]
        return out

    sol.sol = output
    return sol


scipy.integrate.solve_ivp = solver
cli = module("cli", "toolbox/scripts/gmat_m2.py")
reasons, check = cli._evaluate("m2_prograde_burn")
print("standalone", reasons, check.passed if check else None, counts, flush=True)
proof = module("proof", "toolbox/validators/m2_proof.py")
rc = proof.main(["--out", "review_scratch/midpoint_m2.json"])
print("proof", rc, counts)
clean = json.load(open("review_scratch/m2.json"))
bad = json.load(open("review_scratch/midpoint_m2.json"))
print("identical results", clean["results"] == bad["results"])
