# ruff: noqa
import subprocess, json
from tars.validation.thresholds import load_thresholds, load_scoped_thresholds
from tars.validation.m2_missions import MISSIONS

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"


def old(p):
    return json.loads(subprocess.check_output(["git", "-C", repo, "show", "a0169e7:" + p]))


a = load_thresholds()
assert a.limits == old("proof/thresholds/m1.json")["limits"]
print("M1 loaded limits unchanged")
b = load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS))
d = dict(b.limits)
d.pop("o9_gmat")
assert d == old("proof/thresholds/m2.json")["limits"]
print("T5 loaded limits unchanged; O9 only addition")
print("M1 status", a.status, "M2 status", b.status)
for k, v in b.limits["o9_gmat"]["all"].items():
    if "position" in k:
        print(k, v, "above floor", v >= 15e-6)
        assert v >= 15e-6
