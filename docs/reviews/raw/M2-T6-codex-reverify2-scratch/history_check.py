# ruff: noqa
import subprocess, hashlib, json
from pathlib import Path

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"
reports = {}
for p in Path("toolbox/references/gmat/m2").glob("*_report.txt"):
    old = subprocess.check_output(["git", "-C", repo, "show", "1de827e:" + str(p)])
    reports[p.name] = {
        "byte_identical": old == p.read_bytes(),
        "sha256": hashlib.sha256(old).hexdigest(),
    }
print(json.dumps(reports, indent=2))
print(
    subprocess.check_output(
        [
            "git",
            "-C",
            repo,
            "diff",
            "94f0e75",
            "2d33617",
            "--",
            "src/tars/validation/m2.py",
            "toolbox/validators/m2_proof.py",
            "proof/thresholds",
            "src/tars/sim",
            "toolbox/references/golden",
        ],
        text=True,
    )
)
