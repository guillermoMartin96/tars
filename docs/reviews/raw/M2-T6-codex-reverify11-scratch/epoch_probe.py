# ruff: noqa
import hashlib, json, shutil, importlib.util
from pathlib import Path
from tars.validation import gmat_m2 as g

name = "m2_prograde_burn"
dst = Path("review_scratch/epoch_stage")
shutil.copytree(g.reference_dir(), dst, dirs_exist_ok=True)
f = g.reference_files(name, dst)
lines = []
for line in f["report"].read_text().splitlines():
    if not line.strip():
        lines.append(line)
        continue
    cols = line.split()
    cols[1] = repr(float(cols[1]) + 1.0)
    lines.append(" ".join(cols))
f["report"].write_text("\n".join(lines) + "\n")
meta = json.loads(f["metadata"].read_text())
meta["report_sha256"] = hashlib.sha256(f["report"].read_bytes()).hexdigest()
f["metadata"].write_text(json.dumps(meta, indent=2) + "\n")
man = json.loads(g.approved_manifest_path(dst).read_text())
man["references"][name]["report_sha256"] = meta["report_sha256"]
man["references"][name]["metadata_sha256"] = hashlib.sha256(f["metadata"].read_bytes()).hexdigest()
latest = [h for h in man["history"] if h["mission"] == name][-1]
latest["report_sha256"] = meta["report_sha256"]
prev = None
for h in man["history"]:
    h["previous_record_sha256"] = prev
    prev = g.record_digest(h)
g.approved_manifest_path(dst).write_text(json.dumps(man, indent=2) + "\n")
spec = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)
rejected, check = cli._evaluate(name, base=dst)
print(
    "all GMAT epochs shifted by 86400 s; rejected",
    rejected,
    "passed",
    check.passed if check else None,
)
print("failures", check.failures if check else None)
print("spacing", check.metrics["step_spacing_error_max_s"] if check else None)
