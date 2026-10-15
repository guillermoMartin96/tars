# ruff: noqa
import subprocess, tarfile, io, json
from pathlib import Path

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"
data = subprocess.check_output(["git", "-C", repo, "archive", "94f0e75"])
changed = []
with tarfile.open(fileobj=io.BytesIO(data)) as archive:
    for entry in archive:
        if entry.isfile():
            p = Path(entry.name)
            if not p.exists() or p.read_bytes() != archive.extractfile(entry).read():
                changed.append(entry.name)
print(json.dumps({"tracked_snapshot_changes": changed}))
