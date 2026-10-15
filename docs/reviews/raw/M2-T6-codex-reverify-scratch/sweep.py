# ruff: noqa
import importlib.util, json, shutil, hashlib, sys
from pathlib import Path
from unittest.mock import patch
import dataclasses
from tars.validation import gmat_m2, m2
from tars.sim.runner import run_scenario
from tars.validation.m2_missions import MISSIONS

root = Path.cwd()
scratch = root / "review_scratch"
name = "m2_prograde_burn"
spec = importlib.util.spec_from_file_location("cli", root / "toolbox/scripts/gmat_m2.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
original = gmat_m2.reference_dir()
mission = next(m for m in MISSIONS if m.name == name)


def refs(label):
    d = scratch / label
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(original, d)
    return d


def evaluate(label, edit):
    d = refs(label)
    edit(d)
    rejected, check = cli._evaluate(name, base=d)
    print(label, json.dumps({"rejected": rejected, "passed": check.passed if check else None}))


def metadata(d):
    p = d / f"{name}_metadata.json"
    m = json.loads(p.read_text())
    m.update(
        tars_git_revision="0" * 40,
        generated_utc="1900-01-01",
        host_platform="invented",
        replace_reason=None,
    )
    p.write_text(json.dumps(m))


evaluate("metadata_unbound", metadata)


def history(d):
    p = d / "APPROVED_DIGESTS.json"
    m = json.loads(p.read_text())
    m["history"] = [{"mission": name, "report_sha256": "0" * 64, "reason": None}]
    p.write_text(json.dumps(m))


evaluate("inconsistent_history", history)
run = run_scenario(mission.build())
for kind, field, val in [
    ("StateSampled", "r", [float("nan")] * 3),
    ("PropulsionSampled", "total_mass_kg", float("nan")),
    ("PropulsionSampled", "thrust_acceleration_mps2", (float("nan"),) * 3),
]:
    ev = list(run.events)
    idx = next(i for i, e in enumerate(ev) if e.type == kind and e.tick > 0)
    ev[idx] = ev[idx].model_copy(update={field: val})
    mut = dataclasses.replace(run, events=ev)
    with patch.object(cli, "run_scenario", return_value=mut):
        rejected, check = cli._evaluate(name)
        print(
            "nan_" + field,
            json.dumps({"rejected": rejected, "passed": check.passed if check else None}),
        )
# Existing preview filename may be a symlink to a committed script.
d = refs("generate_symlink")
out = scratch / "preview"
out.mkdir(exist_ok=True)
link = out / f"{name}.script"
if link.exists() or link.is_symlink():
    link.unlink()
link.symlink_to(d / f"{name}.script")
before = (d / f"{name}.script").read_bytes()
with (
    patch.object(gmat_m2, "reference_dir", return_value=d),
    patch.object(cli, "_script", return_value="WRONG GENERATOR\n"),
):
    code = cli.main(["generate", "--out", str(out), "--missions", name])
print(
    "generate_symlink",
    code,
    "committed_script_changed",
    before != (d / f"{name}.script").read_bytes(),
)
