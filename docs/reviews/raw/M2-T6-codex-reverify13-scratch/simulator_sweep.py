# ruff: noqa
import dataclasses, importlib.util, math
from unittest.mock import patch
from tars.sim.runner import run_scenario
from tars.validation import m2

spec = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
name = "m2_prograde_burn"
s = cli.BY_NAME[name].build()
original = run_scenario(s)


def evaluate():
    try:
        return cli._evaluate(name)
    except (KeyError, ValueError, RuntimeError, IndexError) as e:
        return [f"rejected by exception: {type(e).__name__}: {e}"], None


for tag, kind, field, value in [
    ("state-position", "StateSampled", "r", (1e9, 1e9, 1e9)),
    ("state-nan", "StateSampled", "v", (math.nan, 0.0, 0.0)),
    ("thrust-direction", "PropulsionSampled", "thrust_acceleration_mps2", (1.0, 1.0, 1.0)),
    ("mass", "PropulsionSampled", "total_mass_kg", 1e9),
    ("propellant-inf", "PropulsionSampled", "propellant_kg", math.inf),
    ("delta-v", "PropulsionSampled", "delta_v_sensed_mps", 1e9),
    ("engine-state", "PropulsionSampled", "engine_state", "burning"),
    ("cutoff-state", "BurnEnded", "r", (1e9, 1e9, 1e9)),
    ("ignition-time", "BurnStarted", "event_t_s", 650.0),
    ("crossing-time", "OrbitCompleted", "crossing_t", 1.0),
    ("completion-extrema", "SimulationCompleted", "min_altitude_m", -1e9),
    (
        "start-mu",
        "SimulationStarted",
        "earth_constants",
        {**original.events[0].earth_constants, "mu": 1.0},
    ),
]:
    ev = list(original.events)
    i = next(i for i, e in enumerate(ev) if e.type == kind)
    ev[i] = ev[i].model_copy(update={field: value})
    bad = dataclasses.replace(original, events=ev)
    with patch.object(cli, "run_scenario", return_value=bad):
        reasons, check = evaluate()
        passed = not reasons and check is not None and check.passed
        print(tag, "accepted", passed, "reasons", reasons[:2], flush=True)
        assert not passed, tag
for kind in ["StateSampled", "PropulsionSampled", "BurnStarted", "BurnEnded", "OrbitCompleted"]:
    ev = list(original.events)
    ev.pop(next(i for i, e in enumerate(ev) if e.type == kind))
    bad = dataclasses.replace(original, events=ev)
    with patch.object(cli, "run_scenario", return_value=bad):
        reasons, check = evaluate()
        passed = not reasons and check is not None and check.passed
        print("missing-" + kind, "accepted", passed, flush=True)
        assert not passed
for field, value in [("status", "failure"), ("crossing_times", ()), ("failure_cause", "invented")]:
    bad = dataclasses.replace(original, **{field: value})
    with patch.object(cli, "run_scenario", return_value=bad):
        reasons, check = evaluate()
        passed = not reasons and check is not None and check.passed
        print("result-" + field, "accepted", passed, flush=True)
        assert not passed
