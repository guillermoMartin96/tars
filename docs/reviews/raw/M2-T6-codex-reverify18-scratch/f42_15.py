# ruff: noqa
import sys
from unittest.mock import patch
from tars.astro import kepler
from tars.validation import m2, reference_snapshot as snap
from tars.validation.m2_missions import MISSIONS
from tars.sim.runner import run_scenario

mission = next(m for m in MISSIONS if m.name == "m2_prograde_burn")
base = mission.build()
variants = m2.impulsive_variants(base)
runs = [run_scenario(v) for v in variants]
original = kepler.propagate
clean = [m2.impulsive_row(base, v, r) for v, r in zip(variants, runs)]


def negate(r, v, dt, mu):
    rr, vv = original(r, v, dt, mu)
    f = sys._getframe(1)
    while f:
        if f.f_code.co_name == "impulsive_row":
            return -rr, -vv
        f = f.f_back
    return rr, vv


with patch.object(kepler, "propagate", side_effect=negate):
    with snap.session("m2_proof") as s:
        dirty = [m2.impulsive_row(base, v, r) for v, r in zip(variants, runs)]
print("F42 reported metrics unchanged", m2.impulsive_metrics(clean) == m2.impulsive_metrics(dirty))
print("snapshot", s.finish(complete=False))
assert s.finish(complete=False)
