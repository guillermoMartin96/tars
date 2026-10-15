# ruff: noqa
import importlib.util, json
import numpy as np
import scipy.integrate


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


original = scipy.integrate.solve_ivp
counts = {"nodes": 0, "dense": 0}


def solver(*a, **k):
    sol = original(*a, **k)
    dense = sol.sol
    lo, hi = a[1]
    mask = (sol.t > lo + 1) & (sol.t < hi - 1)
    sol.y[3:6, mask] = 1e200
    counts["nodes"] += int(mask.sum())

    def output(t):
        out = dense(t)
        tt = np.asarray(t)
        mask = (tt > lo + 1) & (tt < hi - 1)
        out[3:6, mask] = 1e200
        assert np.all(np.isfinite(out))
        counts["dense"] += int(mask.sum())
        return out

    sol.sol = output
    return sol


scipy.integrate.solve_ivp = solver
cli = module("cli", "toolbox/scripts/gmat_m2.py")
try:
    reasons, check = cli._evaluate("m2_prograde_burn")
except RuntimeError as e:
    print("rejected", str(e), counts, flush=True)
    raise SystemExit(0)
print("standalone", reasons, check.passed if check else None, counts, flush=True)
