# ruff: noqa
import subprocess, tarfile, io, json
from pathlib import Path

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"
data = subprocess.check_output(["git", "-C", repo, "archive", "2d33617"])
changes = []
with tarfile.open(fileobj=io.BytesIO(data)) as a:
    for e in a:
        if e.isfile():
            p = Path(e.name)
            if not p.exists() or p.read_bytes() != a.extractfile(e).read():
                changes.append(e.name)
print(json.dumps({"snapshot_changes": changes}))
