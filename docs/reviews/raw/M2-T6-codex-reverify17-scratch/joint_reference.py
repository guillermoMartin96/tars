# ruff: noqa
import importlib.util, inspect, sys, dataclasses
import numpy as np
from unittest.mock import patch
import scipy.integrate
from tars.astro import kepler
from tars.validation import m2

spec = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
raw_kepler = kepler.propagate
raw_solver = scipy.integrate.solve_ivp
lines, start = inspect.getsourcelines(m2._anchor_segment)
target = start + next(i for i, l in enumerate(lines) if "rows = [kepler_state" in l)
counts = {"kepler": 0, "dense": 0}


def phase(r, v, dt, mu):
    f = sys._getframe(1)
    while f:
        if (
            f.f_code.co_name == "_anchor_segment"
            and f.f_lineno == target
            and 0 < abs(dt) < f.f_locals["b"] - f.f_locals["a"] - 1e-8
        ):
            counts["kepler"] += 1
            return raw_kepler(r, v, dt * 1.001, mu)
        f = f.f_back
    return raw_kepler(r, v, dt, mu)


def solver(*args, **kwargs):
    sol = raw_solver(*args, **kwargs)
    dense = sol.sol
    a, b = args[1]
    y0 = np.array(args[2], copy=True)
    frame = sys._getframe(1)
    while frame and frame.f_code.co_name != "dop853_reference":
        frame = frame.f_back
    scenario = frame.f_locals.get("scenario") if frame else None
    sign = frame.f_locals.get("sign") if frame else None
    if scenario is None or sign != 0:
        return sol

    def output(t):
        out = dense(t)
        tt = np.atleast_1d(t)
        mask = (
            (tt > a)
            & (tt < b)
            & (np.abs(tt / scenario.dt_s - np.round(tt / scenario.dt_s)) < 1e-12)
        )
        for j in np.flatnonzero(mask):
            out[:3, j] = raw_kepler(y0[:3], y0[3:6], (tt[j] - a) * 1.001, scenario.constants.mu)[0]
            counts["dense"] += 1
        return out

    sol.sol = output
    return sol


mission = cli.BY_NAME["m2_prograde_burn"]
scenario = mission.build()
run = cli.run_scenario(scenario)
pred = m2.predict_burns(scenario, mission.expected)
_, ref = m2.reference_metrics(scenario, run.events, pred)
events = list(run.events)
events[-1] = events[-1].model_copy(update={"max_altitude_m": ref.alt_max + 0.01301})
bad = dataclasses.replace(run, events=events)
with patch.object(cli, "run_scenario", return_value=bad):
    reasons, check = cli._evaluate(mission.name)
    print("clean", reasons, check, flush=True)
    with (
        patch.object(kepler, "propagate", side_effect=phase),
        patch.object(scipy.integrate, "solve_ivp", side_effect=solver),
    ):
        reasons, check = cli._evaluate(mission.name)
        print("joint", reasons, check.passed if check else None, counts, flush=True)
        assert not reasons and check and check.passed
        audit = m2.audit_run(scenario, mission.expected, bad)
        print("corrupted orbit metrics", audit.metrics["orbit_events"], flush=True)
