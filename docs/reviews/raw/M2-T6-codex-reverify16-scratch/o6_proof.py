# ruff: noqa
import importlib.util
import sys
import json
import numpy as np
import scipy.integrate
from tars.astro import kepler


def module(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


cli = module("cli", "toolbox/scripts/gmat_m2.py")
mode = sys.argv[1]
counts = {"corrupted": 0}
if mode in ("dense", "solver", "stencil"):
    original = scipy.integrate.solve_ivp

    def solver(*a, **k):
        sol = original(*a, **k)
        # Only segments not ending on the tick grid; preserve raw terminal states.
        if mode == "solver":
            sol.y[:6, 1:-1] *= -1
            counts["corrupted"] += max(0, sol.y.shape[1] - 2)
        elif mode == "stencil":
            dense = sol.sol

            def output(t):
                out = dense(t)
                mask = np.abs(np.asarray(t) / 2.5 - np.rint(np.asarray(t) / 2.5)) > 1e-7
                out[3:7, mask] = np.nan
                counts["corrupted"] += int(np.sum(mask))
                return out

            sol.sol = output
        elif a[1][1] - a[1][0] >= 30:
            dense = sol.sol
            lo, hi = a[1]

            def output(t):
                out = dense(t)
                mask = (np.asarray(t) > lo + 1) & (np.asarray(t) < hi - 1)
                out[:6, mask] *= -1
                counts["corrupted"] += int(np.sum(mask))
                return out

            sol.sol = output
        return sol

    scipy.integrate.solve_ivp = solver
else:
    original = kepler.propagate

    def propagate(*a, **k):
        r, v = original(*a, **k)
        # Mutate only raw independent-reference return arrays consumed by O6.
        frame = sys._getframe(1)
        while frame:
            if frame.f_code.co_name == "impulsive_row":
                r, v = original(a[0], a[1], a[2] * 10.0, a[3])
                counts["corrupted"] += 1
                break
            frame = frame.f_back
        return r, v

    kepler.propagate = propagate
rejected, check = cli._evaluate("m2_prograde_burn")
print("standalone", rejected, check.passed if check else None, counts, flush=True)
proof = module("proof", "toolbox/validators/m2_proof.py")
rc = proof.main(["--out", f"review_scratch/{mode}_phase_m2.json"])
print("proof", rc, counts)
clean = json.load(open("review_scratch/m2.json"))
bad = json.load(open(f"review_scratch/{mode}_phase_m2.json"))
print("identical results", clean["results"] == bad["results"])
for a, b in zip(clean["results"], bad["results"]):
    if a != b:
        print("changed", a["validator"], a["metrics"], b["metrics"])
