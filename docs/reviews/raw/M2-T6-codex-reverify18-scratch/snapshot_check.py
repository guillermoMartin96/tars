# ruff: noqa
from pathlib import Path
import subprocess, json

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"
paths = subprocess.check_output(
    ["git", "-C", repo, "ls-tree", "-r", "--name-only", "683a224"], text=True
).splitlines()
selected = [
    p for p in paths if p.startswith(("src/", "tests/", "toolbox/", "scenarios/", "proof/"))
]
for p in selected:
    assert Path(p).read_bytes() == subprocess.check_output(
        ["git", "-C", repo, "show", "683a224:" + p]
    ), p
print("protected tracked files unchanged", len(selected))
a = json.loads(Path("previous-m2-report.json").read_text())
b = json.loads(Path("review_scratch/m2.json").read_text())
print("different fields", [k for k in a if a[k] != b.get(k)])
for k in a:
    if k != "platform":
        assert a[k] == b[k], k
print("previous platform", a.get("platform"), "fresh platform", b.get("platform"))
