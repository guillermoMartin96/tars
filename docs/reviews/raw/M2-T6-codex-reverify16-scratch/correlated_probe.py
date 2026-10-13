# ruff: noqa
import importlib.util, sys, json
import numpy as np
import scipy.integrate


def module(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


mode = sys.argv[1]
counts = {"corrupted": 0}
original = scipy.integrate.solve_ivp


def solver(*a, **k):
    sol = original(*a, **k)
    dense = sol.sol
    lo, hi = a[1]
    if mode == "correlated":
        mask = (sol.t > lo + 1) & (sol.t < hi - 1)
        sol.y[:6, mask] *= -1

        def output(t):
            out = dense(t)
            mask = (np.asarray(t) > lo + 1) & (np.asarray(t) < hi - 1)
            out[:6, mask] *= -1
            counts["corrupted"] += int(np.sum(mask))
            return out
    else:

        def output(t):
            out = dense(t)
            # Only actual derivative stencil requests: do not change solver nodes/ticks.
            caller = sys._getframe(1)
            if caller.f_code.co_name == "_check_dense_consistency" and caller.f_lineno == 960:
                frac = np.abs(np.asarray(t) / 2.5 - np.rint(np.asarray(t) / 2.5))
                mask = (frac > 1e-7) & (frac < 0.001)
                out[3:7, mask] = 1e9
                counts["corrupted"] += int(np.sum(mask))
            return out

    sol.sol = output
    return sol


scipy.integrate.solve_ivp = solver
cli = module("cli", "toolbox/scripts/gmat_m2.py")
rejected, check = cli._evaluate("m2_prograde_burn")
print("standalone", rejected, check.passed if check else None, counts, flush=True)
proof = module("proof", "toolbox/validators/m2_proof.py")
rc = proof.main(["--out", f"review_scratch/{mode}_m2.json"])
print("proof", rc, counts)
clean = json.load(open("review_scratch/m2.json"))
bad = json.load(open(f"review_scratch/{mode}_m2.json"))
print("identical results", clean["results"] == bad["results"])
