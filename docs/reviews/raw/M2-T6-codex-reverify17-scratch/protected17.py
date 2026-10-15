# ruff: noqa
from pathlib import Path
import subprocess, hashlib, json

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"
paths = subprocess.check_output(
    ["git", "-C", repo, "ls-tree", "-r", "--name-only", "9917bb7"], text=True
).splitlines()
selected = [
    p for p in paths if p.startswith(("src/", "tests/", "toolbox/", "scenarios/", "proof/"))
]
for p in selected:
    assert Path(p).read_bytes() == subprocess.check_output(
        ["git", "-C", repo, "show", "9917bb7:" + p]
    ), p
print("protected tracked files unchanged", len(selected))
for rev in ["f5a7e40", "9d49b60"]:
    print(subprocess.check_output(["git", "-C", repo, "show", "-s", "--format=%B", rev], text=True))
bases = []
import gzip

for rev in ["f5a7e40^", "f5a7e40", "9d49b60"]:
    try:
        data = subprocess.check_output(
            [
                "git",
                "-C",
                repo,
                "show",
                rev + ":toolbox/references/snapshot/m2/REFERENCE_SNAPSHOT.json.gz",
            ],
            stderr=subprocess.DEVNULL,
        )
        bases.append(json.loads(gzip.decompress(data)))
    except subprocess.CalledProcessError:
        pass
for a, b in zip(bases, bases[1:]):
    common = set(a["records"]) & set(b["records"])
    n = 0
    for k in common:
        for p, v in a["records"][k]["parts"].items():
            assert v == b["records"][k]["parts"][p], (k, p)
            n += len(v["values"])
    print("common records", len(common), "common values bit identical", n)
