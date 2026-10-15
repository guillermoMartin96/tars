# ruff: noqa
import hashlib, json, subprocess, struct
from pathlib import Path
from tars.validation.thresholds import load_thresholds, load_scoped_thresholds
from tars.validation.m2_missions import MISSIONS

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"


def old(rev, path):
    return subprocess.check_output(["git", "-C", repo, "show", rev + ":" + path])


def paths(rev):
    return subprocess.check_output(
        ["git", "-C", repo, "ls-tree", "-r", "--name-only", rev], text=True
    ).splitlines()


protected = [
    p
    for p in paths("1a11ff7")
    if p.startswith(("src/", "tests/", "toolbox/", "scenarios/", "proof/"))
]
for p in protected:
    assert Path(p).read_bytes() == old("1a11ff7", p), p
print("protected snapshot files identical", len(protected))
a = load_thresholds()
b = load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS))
assert a.limits == json.loads(old("a0169e7", "proof/thresholds/m1.json"))["limits"]
d = dict(b.limits)
d.pop("o9_gmat")
assert d == json.loads(old("a0169e7", "proof/thresholds/m2.json"))["limits"]
print("M1 and T5 loaded thresholds unchanged", a.status, b.status)
for k, v in b.limits["o9_gmat"]["all"].items():
    if "position" in k:
        assert v >= 15e-6
        print("position gate", k, v)
for p in Path("toolbox/references/gmat/m2").glob("*_report.txt"):
    assert p.read_bytes() == old("1de827e", str(p))
    print("GMAT report identical", p, hashlib.sha256(p.read_bytes()).hexdigest())
selected = [
    p
    for p in paths("a0169e7")
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
print("baseline/golden unchanged", len(selected))
for key, path in [("m1", "proof/thresholds/m1.json"), ("m2", "proof/thresholds/m2.json")]:
    from tars.validation.approved_digests import APPROVED_THRESHOLD_SHA256

    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == APPROVED_THRESHOLD_SHA256[key]
print("threshold approval anchors match")
