# ruff: noqa
import math, copy
from unittest.mock import patch
import numpy as np
from tars.validation import m2, gmat_m2 as g
from tars.validation.m2_missions import MISSIONS
from tars.validation.thresholds import load_scoped_thresholds, Check
from tars.sim.runner import run_scenario

mission = next(m for m in MISSIONS if m.name == "m2_prograde_burn")
s = mission.build()
ev = run_scenario(s).events
pred = m2.predict_burns(s, mission.expected)
arcs = g.plan_arcs(s, pred, s.stop.duration_s)
rows = g.parse_stream(g.reference_files(mission.name)["report"].read_text())
labelled, _ = g.label_rows(rows, arcs)
ref = m2.dop853_reference(s, *m2.expected_initial_state(s), pred, sorted(labelled))
limits = load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS)).for_validator(
    "o9_gmat", mission.name
)
for i in range(7):
    for val in [math.nan, math.inf, -math.inf]:
        bad = copy.deepcopy(ref)
        bad[650.0][i] = val
        metrics = {
            **g.alignment_metrics(
                labelled, arcs, pred, s.constants.mu, m2.vehicle(s).mass_flow_kgps
            ),
            **g.o9_metrics(s, pred, ev, labelled, bad),
        }
        assert not Check("o9", metrics, limits, "provisional").passed, (i, val)
print("All 21 intermediate reference component/nonfinite mutations rejected by O9")
orig = m2.kepler.propagate
for index in [0, 1]:

    def badkep(*a, **k):
        r, v = orig(*a, **k)
        if a[2] == 60.0:
            if index == 0:
                r = np.full_like(r, math.nan)
            else:
                v = np.full_like(v, math.nan)
        return r, v

    with patch.object(m2.kepler, "propagate", badkep):
        metrics = m2.coast_metrics(s, ev)
        lim = load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS)).for_validator(
            "o5_coast_kepler", mission.name
        )
        assert not Check("o5", metrics, lim, "provisional").passed
print("O5 NaN Kepler position and velocity reductions reject")
