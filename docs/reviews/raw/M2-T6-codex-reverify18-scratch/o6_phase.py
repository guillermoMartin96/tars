# ruff: noqa
import sys, json
from unittest.mock import patch
from tars.astro import kepler
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS
from tars.sim.runner import run_scenario

mission = next(m for m in MISSIONS if m.name == "m2_prograde_burn")
base = mission.build()
variants = m2.impulsive_variants(base)
runs = [run_scenario(v) for v in variants]
clean = [m2.impulsive_row(base, v, r) for v, r in zip(variants, runs)]
original = kepler.propagate
counts = 0


def phase(r, v, dt, mu):
    global counts
    f = sys._getframe(1)
    while f:
        if f.f_code.co_name == "impulsive_row":
            counts += 1
            return original(r, v, dt * 10, mu)
        f = f.f_back
    return original(r, v, dt, mu)


with patch.object(kepler, "propagate", side_effect=phase):
    dirty = [m2.impulsive_row(base, v, r) for v, r in zip(variants, runs)]
print("calls", counts)
print("clean", json.dumps(m2.impulsive_metrics(clean), sort_keys=True))
print("dirty", json.dumps(m2.impulsive_metrics(dirty), sort_keys=True))
assert all(__import__("math").isfinite(x) for x in m2.impulsive_metrics(dirty).values())
assert m2.impulsive_metrics(clean) != m2.impulsive_metrics(dirty)
