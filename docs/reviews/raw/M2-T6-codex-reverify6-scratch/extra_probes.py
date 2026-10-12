# ruff: noqa
import importlib.util, math
from unittest.mock import patch
from tars.validation import m2
from tars.validation.thresholds import Check, load_scoped_thresholds
from tars.validation.m2_missions import MISSIONS
from tars.sim.runner import run_scenario

s = importlib.util.spec_from_file_location("t", "tests/test_gmat_m2.py")
t = importlib.util.module_from_spec(s)
s.loader.exec_module(t)
for snippet in [
    "e = np.maximum.reduce(errors)",
    "e = np.minimum.reduce(errors)",
    "e = np.fmax.reduce(errors)",
    "e = np.fmin.reduce(errors)",
    "e = np.maximum(a,b)",
]:
    print(
        "guard",
        snippet,
        t._reducer_calls("def unsafe(np,errors,a,b):\n    " + snippet + "\n", "m2.py"),
    )
m = next(m for m in MISSIONS if m.name == "m2_prograde_burn")
scenario = m.build()
run = run_scenario(scenario)
events = [
    e.model_copy(update={"sensed_delta_v_mps": e.sensed_delta_v_mps + 1e-6})
    if e.type == "BurnEnded"
    else e
    for e in run.events
]
pred = m2.predict_burns(scenario, m.expected)
limits = load_scoped_thresholds(missions=frozenset(x.name for x in MISSIONS)).for_validator(
    "o2_rocket_equation", m.name
)
for bound in [None, math.inf]:
    if bound is None:
        _, o2, _ = m2.mass_and_rocket_metrics(scenario, events, pred)
    else:
        with patch.object(m2, "simpson_bound", return_value=bound):
            _, o2, _ = m2.mass_and_rocket_metrics(scenario, events, pred)
    c = Check("o2", o2, limits, "provisional")
    print(
        "finite bad dv +1e-6, bound",
        bound,
        "metrics",
        o2,
        "passed",
        c.passed,
        "failures",
        c.failures,
    )
