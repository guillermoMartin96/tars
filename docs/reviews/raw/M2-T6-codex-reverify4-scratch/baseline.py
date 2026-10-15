# ruff: noqa
import json, subprocess, hashlib, struct
from pathlib import Path
from tars.validation.thresholds import load_thresholds, load_scoped_thresholds
from tars.validation.m2_missions import MISSIONS

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"


def old(rev, p):
    return subprocess.check_output(["git", "-C", repo, "show", rev + ":" + p])


a = load_thresholds()
b = load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS))
assert a.limits == json.loads(old("a0169e7", "proof/thresholds/m1.json"))["limits"]
d = dict(b.limits)
d.pop("o9_gmat")
assert d == json.loads(old("a0169e7", "proof/thresholds/m2.json"))["limits"]
print("M1 and T5 limits unchanged", a.status, b.status)
for k, v in b.limits["o9_gmat"]["all"].items():
    if "position" in k:
        assert v >= 15e-6
        print("floor", k, v)
for p in Path("toolbox/references/gmat/m2").glob("*_report.txt"):
    assert p.read_bytes() == old("1de827e", str(p))
    print("byte-identical", p)
for root in ["proof/references", "proof/thresholds/m1.json", "toolbox/validators/m1_proof.py"]:
    paths = (
        [p for p in Path(root).rglob("*") if p.is_file()] if Path(root).is_dir() else [Path(root)]
    )
    for p in paths:
        assert p.read_bytes() == old("a0169e7", str(p))
    print("baseline bytes unchanged", root)
x = json.loads(Path("previous-m2-report.json").read_text())
y = json.loads(Path("review_scratch/m2.json").read_text())
print("report keys", x.keys())
xc = x["results"]
yc = y["results"]
assert len(xc) == len(yc) == 212
count = 0
for i, (a, b) in enumerate(zip(xc, yc)):
    assert a["metrics"].keys() == b["metrics"].keys(), i
    for k, v in a["metrics"].items():
        assert struct.pack("!d", v) == struct.pack("!d", b["metrics"][k]), (
            i,
            k,
            v,
            b["metrics"][k],
        )
        count += 1
    if a["validator"] != b["validator"]:
        assert a["validator"].startswith("orbit_events[") and b["validator"] == a[
            "validator"
        ].replace("orbit_events[", "orbit_events_contract[")
    for k in ["thresholds", "threshold_status", "passed"]:
        assert a[k] == b[k], (i, k)
assert len({c["validator"] for c in yc}) == 212
print(
    "212 checks identical metric bits; metric scalars",
    count,
    "gates/status unchanged; names unique",
)
