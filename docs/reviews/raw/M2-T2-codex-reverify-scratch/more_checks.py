# ruff: noqa
import importlib.util
import json
from pathlib import Path

import numpy as np

from reverify import Fail, sim

# Fail after the first burn's cutoff, before a second pending burn has completed.
f = Fail("raise")
f.bad = False
s = sim(force=f)
s.schedule_burn("prograde", 1, 2)
s.schedule_burn("prograde", 11, 2)
s.step()
before = (
    s._y.tobytes(),
    s.tick,
    s.propulsion_snapshot(),
    s.engine_transitions,
    s._committed_propellant_kg,
)
f.bad = True
try:
    s.step()
except RuntimeError:
    pass
assert before == (
    s._y.tobytes(),
    s.tick,
    s.propulsion_snapshot(),
    s.engine_transitions,
    s._committed_propellant_kg,
)
f.bad = False
s.step()
assert [(e.kind, e.t) for e in s.engine_transitions] == [("ignition", 11), ("cutoff", 13)]
print("rollback with retained prior events and second pending burn PASS")

spec = importlib.util.spec_from_file_location(
    "measure", "docs/science/experiments/m2-t2/measure_t2.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
rows = [mod.run(dt) for dt in (20.0, 10.0, 5.0, 2.5)]
saved = json.loads(Path("docs/science/experiments/m2-t2/results.json").read_text())["rows"]
assert all(all(row[k] == saved[i][k] for k in row) for i, row in enumerate(rows))
Path("review_scratch/val0012.json").write_text(json.dumps(rows, indent=2) + "\n")
print("VAL0012 all rerun fields identical PASS")
