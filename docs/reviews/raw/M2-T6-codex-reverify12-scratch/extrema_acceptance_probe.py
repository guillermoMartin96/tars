# ruff: noqa
import dataclasses, importlib.util
from unittest.mock import patch
import numpy as np
import scipy.integrate
from tars.sim.runner import run_scenario

spec = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
name = "m2_prograde_burn"
run = run_scenario(cli.BY_NAME[name].build())
events = list(run.events)
done = events[-1]
events[-1] = done.model_copy(update={"max_altitude_m": done.max_altitude_m + 0.1})
bad = dataclasses.replace(run, events=events)
with patch.object(cli, "run_scenario", return_value=bad):
    reasons, check = cli._evaluate(name)
    print("bad simulator, clean reference:", reasons, check.passed if check else None, flush=True)
    assert reasons and any("max_altitude_error_m" in r for r in reasons)

original = scipy.integrate.solve_ivp
counts = {"nodes": 0, "dense": 0}
scale = 1 + 0.1 / 6628137.0


def solver(*a, **k):
    sol = original(*a, **k)
    dense = sol.sol
    lo, hi = a[1]
    mask = (sol.t > lo + 1) & (sol.t < hi - 1)
    sol.y[:6, mask] *= scale
    counts["nodes"] += int(mask.sum())

    def output(t):
        out = dense(t)
        tt = np.asarray(t)
        mask = (tt > lo + 1) & (tt < hi - 1)
        out[:6, mask] *= scale
        counts["dense"] += int(mask.sum())
        return out

    sol.sol = output
    return sol


with (
    patch.object(cli, "run_scenario", return_value=bad),
    patch.object(scipy.integrate, "solve_ivp", side_effect=solver),
):
    reasons, check = cli._evaluate(name)
    print(
        "bad simulator, corrupted reference:",
        reasons,
        check.passed if check else None,
        counts,
        flush=True,
    )
    assert not reasons and check.passed
