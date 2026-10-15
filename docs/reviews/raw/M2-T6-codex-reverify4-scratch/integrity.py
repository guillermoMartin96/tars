# ruff: noqa
import subprocess, hashlib
from pathlib import Path

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"
paths = (
    subprocess.check_output(
        [
            "git",
            "-C",
            repo,
            "ls-tree",
            "-r",
            "--name-only",
            "7467d42",
            "src",
            "tests",
            "toolbox",
            "scenarios",
            "proof",
        ]
    )
    .decode()
    .splitlines()
)
for p in paths:
    old = subprocess.check_output(["git", "-C", repo, "show", "7467d42:" + p])
    assert Path(p).read_bytes() == old, p
print("Protected tracked files unchanged:", len(paths))
