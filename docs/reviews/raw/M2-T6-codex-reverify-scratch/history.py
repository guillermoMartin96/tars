# ruff: noqa
from pathlib import Path
import subprocess, hashlib, json

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"
results = {}
for p in sorted(Path("toolbox/references/gmat/m2").glob("*_report.txt")):
    old = subprocess.check_output(["git", "-C", repo, "show", "1de827e:" + str(p)])
    new = p.read_bytes()
    results[p.name] = {"byte_identical": old == new, "sha256": hashlib.sha256(new).hexdigest()}
print(json.dumps(results, indent=2))
print("T5 baseline diff:")
print(
    subprocess.check_output(
        [
            "git",
            "-C",
            repo,
            "diff",
            "a0169e7",
            "94f0e75",
            "--",
            "src/tars/validation/m2.py",
            "proof/thresholds/m1.json",
            "toolbox/references/golden",
            "src/tars/sim",
        ],
        text=True,
    )
)
