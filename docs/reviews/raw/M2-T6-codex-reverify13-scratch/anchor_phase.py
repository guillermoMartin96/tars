# ruff: noqa
import importlib.util, sys, inspect
from tars.validation import m2
from unittest.mock import patch
from tars.astro import kepler

s = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
cli = importlib.util.module_from_spec(s)
s.loader.exec_module(cli)
original = kepler.propagate
count = 0
lines, start = inspect.getsourcelines(m2._anchor_segment)
target = start + next(i for i, l in enumerate(lines) if "rows = [kepler_state" in l)


def poisoned(r, v, dt, mu):
    global count
    frame = sys._getframe(1)
    while frame:
        if (
            frame.f_code.co_name == "_anchor_segment"
            and frame.f_lineno == target
            and frame.f_back.f_locals["scenario"].name == "m2_prograde_burn"
        ):
            count += 1
            return original(r, v, dt * 1.001, mu)
        frame = frame.f_back
    return original(r, v, dt, mu)


name = "m2_prograde_burn"
mission = cli.BY_NAME[name]
scenario = mission.build()
run = cli.run_scenario(scenario)
predicted = m2.predict_burns(scenario, mission.expected)


def evaluate():
    _, ref = m2.reference_metrics(scenario, run.events, predicted)
    metrics, violations = m2.orbit_checks(scenario, run.events, ref, predicted)
    return metrics, violations, ref.alt_min, ref.alt_max


print("clean", evaluate(), flush=True)
with patch.object(kepler, "propagate", side_effect=poisoned):
    print("dirty", evaluate(), "calls", count, flush=True)
with patch.object(kepler, "propagate", side_effect=poisoned):
    reasons, check = cli._evaluate(name)
    print(
        "standalone", reasons, "PASS", check.passed if check else None, "calls", count, flush=True
    )
s = importlib.util.spec_from_file_location("proof", "toolbox/validators/m2_proof.py")
proof = importlib.util.module_from_spec(s)
s.loader.exec_module(proof)
with patch.object(kepler, "propagate", side_effect=poisoned):
    rc = proof.main(["--out", "review_scratch/anchor_phase_m2.json"])
    print("proof exit", rc, "calls", count, flush=True)
import json

clean = json.load(open("review_scratch/m2.json"))
dirty = json.load(open("review_scratch/anchor_phase_m2.json"))
for a, b in zip(clean["results"], dirty["results"], strict=True):
    if a != b:
        print(
            "CHANGED", a["validator"], a["metrics"], b["metrics"], "PASS", b["passed"], flush=True
        )
