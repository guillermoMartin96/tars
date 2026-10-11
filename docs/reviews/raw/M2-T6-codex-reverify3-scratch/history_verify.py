# ruff: noqa
import subprocess, json, hashlib, io, tarfile
from pathlib import Path

repo = "/Users/guillermomartin/.superset/worktrees/tars/actually-splash-f90f9ba4"


def git(*args):
    return subprocess.check_output(["git", "-C", repo, *args])


base = Path("toolbox/references/gmat/m2")
manifest = json.loads((base / "APPROVED_DIGESTS.json").read_text())
expected = []
for commit in ["1de827e", "a346fbe", "94f0e75", "2d33617"]:
    for name in ["m2_prograde_burn", "m2_retrograde_burn", "m2_invalid_commands"]:
        meta = json.loads(git("show", f"{commit}:{base}/{name}_metadata.json"))
        h = dict(
            mission=name,
            generated_utc=meta["generated_utc"],
            tars_git_revision=meta["tars_git_revision"],
            reason=meta.get("replace_reason") or "initial reference",
            report_sha256=meta["report_sha256"],
        )
        expected.append(h)
        print(
            commit,
            name,
            "metadata matched",
            h
            == {
                k: v
                for k, v in manifest["history"][len(expected) - 1].items()
                if k != "previous_record_sha256"
            },
        )
assert expected == [
    {k: v for k, v in h.items() if k != "previous_record_sha256"} for h in manifest["history"]
]
for p in base.glob("*_report.txt"):
    assert p.read_bytes() == git("show", f"1de827e:{p}")
    print(p.name, "byte identical", hashlib.sha256(p.read_bytes()).hexdigest())
print(
    "T5 protected diff:",
    git(
        "diff",
        "a0169e7",
        "4cd3669",
        "--",
        "src/tars/sim",
        "scenarios",
        "toolbox/references/golden",
        "proof/thresholds/m1.json",
    ).decode(),
)
print(
    "fix3 protected diff:",
    git(
        "diff",
        "2d33617",
        "4cd3669",
        "--",
        "src/tars/validation/m2.py",
        "toolbox/validators/m2_proof.py",
        "proof/thresholds",
    ).decode(),
)
archive = tarfile.open(fileobj=io.BytesIO(git("archive", "4cd3669")))
changed = []
for entry in archive.getmembers():
    if entry.isfile():
        p = Path(entry.name)
        if not p.exists() or p.read_bytes() != archive.extractfile(entry).read():
            changed.append(entry.name)
print("Snapshot differences:", changed)
assert not changed
