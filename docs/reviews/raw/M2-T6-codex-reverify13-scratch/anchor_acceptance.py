# ruff: noqa
import importlib.util, inspect, sys, dataclasses
from unittest.mock import patch
from tars.astro import kepler
from tars.validation import m2

s = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
cli = importlib.util.module_from_spec(s)
s.loader.exec_module(cli)
original = kepler.propagate
lines, start = inspect.getsourcelines(m2._anchor_segment)
target = start + next(i for i, l in enumerate(lines) if "rows = [kepler_state" in l)
count = 0


def poisoned(r, v, dt, mu):
    global count
    frame = sys._getframe(1)
    while frame:
        if frame.f_code.co_name == "_anchor_segment" and frame.f_lineno == target:
            count += 1
            return original(r, v, dt * 1.001, mu)
        frame = frame.f_back
    return original(r, v, dt, mu)


name = "m2_prograde_burn"
mission = cli.BY_NAME[name]
scenario = mission.build()
run = cli.run_scenario(scenario)
predicted = m2.predict_burns(scenario, mission.expected)
_, ref = m2.reference_metrics(scenario, run.events, predicted)
events = list(run.events)
events[-1] = events[-1].model_copy(update={"max_altitude_m": ref.alt_max + 0.01301})
bad = dataclasses.replace(run, events=events)
with patch.object(cli, "run_scenario", return_value=bad):
    reasons, check = cli._evaluate(name)
    print("clean reference", reasons, "PASS", check.passed if check else None, flush=True)
    assert any("max_altitude_error_m" in r for r in reasons)
    with patch.object(kepler, "propagate", side_effect=poisoned):
        reasons, check = cli._evaluate(name)
        print(
            "corrupted reference",
            reasons,
            "PASS",
            check.passed if check else None,
            "calls",
            count,
            flush=True,
        )
        assert not reasons and check.passed
