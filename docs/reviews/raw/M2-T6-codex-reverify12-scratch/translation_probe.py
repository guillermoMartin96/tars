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
SHIFT = np.array([0.005, 0.0, 0.0])


def solver(*a, **k):
    sol = original(*a, **k)
    dense = sol.sol
    lo, hi = a[1]
    mask = (sol.t > lo + 1) & (sol.t < hi - 1)
    sol.y[:3, mask] += SHIFT[:, None]
    counts["nodes"] += int(mask.sum())

    def output(t):
        out = dense(t)
        tt = np.asarray(t)
        mask = (tt > lo + 1) & (tt < hi - 1)
        out[:3, mask] += SHIFT[:, None]
        counts["dense"] += int(mask.sum())
        return out

    sol.sol = output
    return sol


scipy.integrate.solve_ivp = solver
cli = module("cli", "toolbox/scripts/gmat_m2.py")
reasons, check = cli._evaluate("m2_prograde_burn")
print("standalone", reasons, check.passed if check else None, counts, flush=True)
proof = module("proof", "toolbox/validators/m2_proof.py")
rc = proof.main(["--out", "review_scratch/translation_m2.json"])
print("proof", rc, counts)
clean = json.load(open("review_scratch/m2.json"))
bad = json.load(open("review_scratch/translation_m2.json"))
for x, y in zip(clean["results"], bad["results"], strict=True):
    if x != y:
        print(
            "changed",
            x["validator"],
            "clean",
            x["metrics"],
            "corrupt",
            y["metrics"],
            "passed",
            y["passed"],
        )
