# ruff: noqa
import sys, json
import numpy as np
from unittest.mock import patch
from tars.astro import kepler
from tars.sim.runner import run_scenario
from tars.validation import m2, reference_snapshot as snap
from tars.validation.m2_missions import MISSIONS
from tars.validation.thresholds import Check

mission = next(x for x in MISSIONS if x.name == "m2_invalid_commands_no_propulsion")
sc = mission.build()
run = run_scenario(sc)
original = kepler.propagate
start = run.events[0]
chosen = None
for i, e in enumerate(run.events):
    if e.type != "StateSampled" or not 0 < e.t < 5900:
        continue
    dt = e.t
    r, v = original(np.array(start.r), np.array(start.v), dt, sc.constants.mu)
    rr, vv = original(np.array(start.r), np.array(start.v), dt + 1.6e-9, sc.constants.mu)
    shift = rr - r
    if max(abs(shift)) < 1e-5 and max(abs(vv - v)) < 1e-8 and np.linalg.norm(shift) > 1.1e-5:
        chosen = (i, e, r, shift)
        break
assert chosen
idx, e, r, shift = chosen
run.events[idx] = e.model_copy(update={"r": tuple(r + shift / np.linalg.norm(shift) * 0.600001)})


def poison(r, v, dt, mu):
    f = sys._getframe(1)
    while f:
        if f.f_code.co_name == "coast_metrics" and abs(dt - e.t) < 1e-10:
            return original(r, v, dt + 1.6e-9, mu)
        f = f.f_back
    return original(r, v, dt, mu)


limits = {"coast_position_error_max_m": 0.6, "coast_velocity_error_max_mps": 0.0007}
for label in ("clean", "dirty"):
    with patch.object(kepler, "propagate", side_effect=poison if label == "dirty" else original):
        with snap.session("m2_proof") as s, snap.scope(sc.name, "audit"):
            metrics = m2.coast_metrics(sc, run.events)
        probs = s.finish(complete=False)
        margins = snap.margin_problems("o5", metrics, limits, m2.o5_snapshot_shifts())
        print(
            label,
            "t",
            e.t,
            "shift",
            shift.tolist(),
            "norm",
            np.linalg.norm(shift),
            "metrics",
            metrics,
            "snapshot",
            probs,
            "margins",
            margins,
            "pass",
            Check("o5", metrics, limits, "provisional").passed,
        )
