# ruff: noqa
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from tars.validation.thresholds import load_thresholds, load_scoped_thresholds
from tars.validation.m2_missions import MISSIONS

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"


def old(rev, path):
    return subprocess.check_output(["git", "-C", repo, "show", rev + ":" + path])


paths = subprocess.check_output(
    [
        "git",
        "-C",
        repo,
        "ls-tree",
        "-r",
        "--name-only",
        "1270b09",
        "src",
        "tests",
        "toolbox",
        "scenarios",
        "proof",
    ],
    text=True,
).splitlines()
for p in paths:
    assert Path(p).read_bytes() == old("1270b09", p), p
print("Snapshot protected files identical to 1270b09:", len(paths))
a = load_thresholds()
b = load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS))
assert a.limits == json.loads(old("a0169e7", "proof/thresholds/m1.json"))["limits"]
d = dict(b.limits)
d.pop("o9_gmat")
assert d == json.loads(old("a0169e7", "proof/thresholds/m2.json"))["limits"]
print("M1 and T5 loaded limits unchanged:", a.status, b.status)
for k, v in b.limits["o9_gmat"]["all"].items():
    if "position" in k:
        assert v >= 15e-6
        print("O9 position floor:", k, v)
for p in Path("toolbox/references/gmat/m2").glob("*_report.txt"):
    assert p.read_bytes() == old("1de827e", str(p))
    print("GMAT report identical to 1de827e:", p, hashlib.sha256(p.read_bytes()).hexdigest())
base_paths = subprocess.check_output(
    ["git", "-C", repo, "ls-tree", "-r", "--name-only", "a0169e7"], text=True
).splitlines()
selected = [
    p
    for p in base_paths
    if p.startswith(
        (
            "src/tars/sim/",
            "src/tars/astro/",
            "scenarios/",
            "proof/references/",
            "toolbox/references/gmat/",
        )
    )
    and not p.startswith("toolbox/references/gmat/m2/")
    and p != "toolbox/references/gmat/README.md"
]
for p in selected:
    assert Path(p).read_bytes() == old("a0169e7", p), p
print("Protected T5 baseline and M1 golden assets unchanged:", len(selected))
x = json.load(open("previous-m2-report.json"))["results"]
y = json.load(open("review_scratch/m2.json"))["results"]
by = {r["validator"]: r for r in y}
assert len(x) == 212 and len(y) == 213
count = 0
for r in x:
    assert r == by[r["validator"]], r["validator"]
    for k, v in r["metrics"].items():
        assert struct.pack("!d", v) == struct.pack("!d", by[r["validator"]]["metrics"][k])
        count += 1
print("212 prior check records identical, metric bits:", count)
print("Added:", [r["validator"] for r in y if r["validator"] not in {s["validator"] for s in x}])
