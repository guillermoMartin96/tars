# ruff: noqa
import json, math, subprocess
from pathlib import Path

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"
paths = subprocess.check_output(
    [
        "git",
        "-C",
        repo,
        "ls-tree",
        "-r",
        "--name-only",
        "e9e06aa",
        "src",
        "tests",
        "toolbox",
        "scenarios",
        "proof",
    ],
    text=True,
).splitlines()
for p in paths:
    assert Path(p).read_bytes() == subprocess.check_output(
        ["git", "-C", repo, "show", "e9e06aa:" + p]
    ), p
print("Snapshot protected tracked files unchanged:", len(paths))
x = json.loads(Path("review_scratch/m1.json").read_text())
for r in x["results"]:
    assert all(math.isfinite(v) for v in r["metrics"].values())
    assert r["passed"] == all(r["metrics"][k] <= v for k, v in r["thresholds"].items())
print(
    "M1 all metrics finite, every result identical under old Check comparison:", len(x["results"])
)
