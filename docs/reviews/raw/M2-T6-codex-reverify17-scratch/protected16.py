# ruff: noqa
from pathlib import Path
import subprocess, json

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"
paths = subprocess.check_output(
    ["git", "-C", repo, "ls-tree", "-r", "--name-only", "8cd661d"], text=True
).splitlines()
selected = [
    p for p in paths if p.startswith(("src/", "tests/", "toolbox/", "scenarios/", "proof/"))
]
for p in selected:
    assert Path(p).read_bytes() == subprocess.check_output(
        ["git", "-C", repo, "show", "8cd661d:" + p]
    ), p
print("protected tracked files unchanged", len(selected))
