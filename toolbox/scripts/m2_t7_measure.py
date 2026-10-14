"""M2 T7 three-platform measurement (DR-0015 threshold method, DR-0008 precedent).

Usage:
    uv run python toolbox/scripts/m2_t7_measure.py collect --out DIR --label LABEL
    uv run python toolbox/scripts/m2_t7_measure.py analyze BUNDLE_DIR [BUNDLE_DIR ...] --out DIR

``collect`` runs, on the current platform, everything the threshold decision needs and
writes a self-describing bundle (``bundle.json`` plus raw outputs):

- the environment: OS, CPU, Python build and compiler, NumPy and SciPy versions,
  NumPy SIMD dispatch and BLAS, ``uv.lock`` digest, git revision;
- digests of every input: scenarios, threshold files, the reference snapshot, the GMAT
  manifest, ``uv.lock``;
- the full M2 Proof report (every O1-O9 metric, verified against the snapshot);
- per-mission final states and event-log digests, plus cross-process determinism of
  every M2 scenario file;
- M1 cross-platform agreement and determinism (regression evidence);
- reference variation, kept separate from simulator error: the verify-mode deviation
  from the approved snapshot (``reference_snapshot.py measure-deviation``) and a
  record-mode recording (raw reference values, so platform drift can be measured
  without substitution);
- the exact commands run and digests of every output.

``analyze`` aggregates bundles from several platforms into the threshold matrix data:
per gated metric, the value on each platform, the worst case, the cross-platform
spread and the margin to the provisional limit; final-state drift between platforms;
reference variation by class, verify mode and record mode, including per-label figures
(e.g. the O6 impulsive SMA). It changes nothing: it measures and reports.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def environment() -> dict[str, Any]:
    import scipy

    sys.path.insert(0, str(REPO_ROOT / "src"))
    from tars.validation.cross_platform import platform_info

    cfg = np.show_config(mode="dicts")
    simd = cfg.get("SIMD Extensions", {})
    blas = cfg.get("Build Dependencies", {}).get("blas", {})
    return {
        **platform_info(),
        "os": platform.platform(),
        "python_full": platform.python_version(),
        "python_compiler": platform.python_compiler(),
        "python_build": " ".join(platform.python_build()),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "numpy_simd_baseline": simd.get("baseline"),
        "numpy_simd_found": simd.get("found"),
        "numpy_blas": blas.get("name"),
        "uv_lock_sha256": _sha(REPO_ROOT / "uv.lock"),
        "git_revision": _git("rev-parse", "HEAD"),
        "git_tree_clean": _git("status", "--porcelain") == "",
    }


def input_digests() -> dict[str, str]:
    paths = [
        *sorted((REPO_ROOT / "scenarios").glob("m2_*.json")),
        REPO_ROOT / "scenarios" / "m1_leo_250km.json",
        REPO_ROOT / "proof" / "thresholds" / "m1.json",
        REPO_ROOT / "proof" / "thresholds" / "m2.json",
        REPO_ROOT / "toolbox" / "references" / "snapshot" / "m2" / "REFERENCE_SNAPSHOT.json.gz",
        REPO_ROOT / "toolbox" / "references" / "gmat" / "m2" / "APPROVED_DIGESTS.json",
        REPO_ROOT / "uv.lock",
    ]
    return {str(p.relative_to(REPO_ROOT)): _sha(p) for p in paths}


def _run(cmd: list[str], log: list[dict[str, Any]], out: Path | None = None) -> str:
    """Run one command from the repository root; record it and its exit code."""
    proc = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, env={**_env(), "PYTHONPATH": "src"}
    )
    text = proc.stdout + proc.stderr
    if out is not None:
        out.write_text(text)
    log.append({"command": " ".join(cmd).replace(PY, "python"), "exit_code": proc.returncode})
    return text


def _env() -> dict[str, str]:
    import os

    return dict(os.environ)


def mission_finals() -> dict[str, Any]:
    """Final state and event-log digest of every M2 mission (in process)."""
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from tars.sim.runner import run_scenario
    from tars.validation import m2
    from tars.validation.m2_missions import MISSIONS

    out = {}
    for mission in MISSIONS:
        run = run_scenario(mission.build())
        out[mission.name] = {
            "events_sha256": m2.events_sha256(run.events),
            "t": run.final.t,
            "r": run.final.r.tolist(),
            "v": run.final.v.tolist(),
            "status": run.status,
        }
    return out


def cmd_collect(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    log: list[dict[str, Any]] = []
    bundle: dict[str, Any] = {
        "label": args.label,
        "environment": environment(),
        "inputs_sha256": input_digests(),
    }
    # 1. The M2 Proof (verify mode against the approved reference snapshot).
    _run([PY, "toolbox/validators/m2_proof.py", "--out", str(out / "m2_proof.json")], log,
         out / "m2_proof_stdout.txt")  # fmt: skip
    # 2. Cross-process determinism of every M2 scenario file, and of M1.
    det = {}
    for sc in [*sorted((REPO_ROOT / "scenarios").glob("m2_*.json")), None]:
        cmd = [PY, "toolbox/validators/determinism.py"]
        if sc is not None:
            cmd += ["--scenario", str(sc)]
        text = _run(cmd, log)
        name = "m1_leo_250km" if sc is None else sc.stem
        det[name] = json.loads(text.strip().splitlines()[-1])
    bundle["determinism"] = det
    # 3. Final states of every M2 mission (cross-platform drift).
    bundle["mission_finals"] = mission_finals()
    # 4. M1 cross-platform agreement (regression).
    text = _run([PY, "toolbox/validators/cross_platform.py"], log)
    bundle["m1_cross_platform"] = json.loads(text.strip().splitlines()[-1])
    # 5. Reference variation: verify-mode deviation, and raw record-mode values.
    _run([PY, "toolbox/scripts/reference_snapshot.py", "measure-deviation",
          "toolbox/references/snapshot/m2/REFERENCE_SNAPSHOT.json.gz",
          "--out", str(out / "deviation.json")], log, out / "deviation_stdout.txt")  # fmt: skip
    _run([PY, "toolbox/scripts/reference_snapshot.py", "generate", "--measurement",
          "--out", str(out / "record.json.gz")], log, out / "record_stdout.txt")  # fmt: skip
    bundle["commands"] = log
    bundle["outputs_sha256"] = {
        p.name: _sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name != "bundle.json"
    }
    (out / "bundle.json").write_text(json.dumps(bundle, indent=2) + "\n")
    failed = [c for c in log if c["exit_code"] != 0 and "measure-deviation" not in c["command"]]
    print(json.dumps({"label": args.label, "failed_commands": failed}, indent=2))
    return 1 if failed else 0


# --------------------------------------------------------------- analysis


def _load(d: Path) -> dict[str, Any]:
    b = json.loads((d / "bundle.json").read_text())
    b["dir"] = d
    b["proof"] = json.loads((d / "m2_proof.json").read_text())
    b["deviation"] = json.loads((d / "deviation.json").read_text())
    return b


def _group(validator: str) -> str:
    return validator.split("[", 1)[0]


def gated_table(bundles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per (group, metric, limit): every platform's worst value, the worst case, the
    largest cross-platform spread of any single check, and the margin to the limit."""
    rows: dict[tuple, dict[str, Any]] = {}
    for b in bundles:
        for r in b["proof"]["results"]:
            for k, lim in r["thresholds"].items():
                if r["threshold_status"] == "approved":
                    continue  # exact contract checks are not tolerances
                key = (_group(r["validator"]), k, lim)
                row = rows.setdefault(key, {"per_platform": {}, "checks": defaultdict(dict)})
                v = r["metrics"].get(k)
                if v is None:
                    continue
                row["per_platform"][b["label"]] = max(row["per_platform"].get(b["label"], 0.0), v)
                row["checks"][r["validator"]][b["label"]] = v
    out = []
    for (group, metric, lim), row in sorted(rows.items()):
        spread = 0.0
        for per in row["checks"].values():
            if len(per) > 1:
                spread = max(spread, max(per.values()) - min(per.values()))
        worst = max(row["per_platform"].values()) if row["per_platform"] else None
        out.append({
            "group": group, "metric": metric, "provisional_limit": lim,
            "per_platform_worst": row["per_platform"], "worst": worst,
            "max_cross_platform_spread": spread, "checks": len(row["checks"]),
            "margin_ratio": (lim / worst) if worst else None,
        })  # fmt: skip
    return out


def final_drift(bundles: list[dict[str, Any]], ref: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for b in bundles:
        if b is ref:
            continue
        per = {}
        for name, f in b["mission_finals"].items():
            g = ref["mission_finals"][name]
            per[name] = {
                "dr_m": float(np.linalg.norm(np.subtract(f["r"], g["r"]))),
                "dv_mps": float(np.linalg.norm(np.subtract(f["v"], g["v"]))),
                "events_identical": f["events_sha256"] == g["events_sha256"],
            }
        out[b["label"]] = per
    return out


def record_drift(bundles: list[dict[str, Any]], ref: dict[str, Any]) -> dict[str, Any]:
    """Raw reference values (no substitution) against the reference host: by class and
    by label; the O6 impulsive SMA is reported on its own (O6 investigation)."""
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from tars.validation import reference_snapshot as snap

    base = snap.read_json(ref["dir"] / "record.json.gz")["records"]
    out: dict[str, Any] = {}
    for b in bundles:
        if b is ref:
            continue
        rec = snap.read_json(b["dir"] / "record.json.gz")["records"]
        by_class: dict[str, float] = defaultdict(float)
        by_label: dict[str, float] = defaultdict(float)
        for key, r in rec.items():
            g = base.get(key)
            if g is None:
                continue
            label = key.rpartition("#")[0].rpartition("/")[2]
            for name, part in r["parts"].items():
                a = np.asarray(part["values"], float)
                c = np.asarray(g["parts"][name]["values"], float)
                if a.shape != c.shape or not a.size:
                    continue
                d = float(np.max(np.abs(a - c)))
                by_class[f"{r['seed']}:{snap.unit_of(name)}"] = max(
                    by_class[f"{r['seed']}:{snap.unit_of(name)}"], d
                )
                by_label[f"{label}.{name}"] = max(by_label[f"{label}.{name}"], d)
        out[b["label"]] = {"by_class": dict(sorted(by_class.items())),
                           "by_label": dict(sorted(by_label.items()))}  # fmt: skip
    return out


_PLATFORM_KEYS = (
    "system", "machine", "cpu", "os", "python_full", "python_compiler", "numpy", "scipy",
    "numpy_simd_found", "numpy_blas", "git_revision", "git_tree_clean",
)  # fmt: skip


def _platform_row(b: dict[str, Any]) -> dict[str, Any]:
    return {k: b["environment"].get(k) for k in _PLATFORM_KEYS}


def cmd_analyze(args: argparse.Namespace) -> int:
    bundles = [_load(Path(d)) for d in args.bundles]
    ref = next(b for b in bundles if b["label"] == args.reference)
    analysis = {
        "reference": args.reference,
        "platforms": {b["label"]: _platform_row(b) for b in bundles},
        "inputs_identical": len({json.dumps(b["inputs_sha256"], sort_keys=True) for b in bundles})
        == 1,
        "proof_passed": {b["label"]: b["proof"]["passed"] for b in bundles},
        "proof_checks": {b["label"]: len(b["proof"]["results"]) for b in bundles},
        "determinism": {
            b["label"]: all(d["passed"] for d in b["determinism"].values()) for b in bundles
        },
        "m1_cross_platform": {b["label"]: b["m1_cross_platform"]["metrics"] for b in bundles},
        "gated": gated_table(bundles),
        "final_state_drift_vs_reference": final_drift(bundles, ref),
        "reference_verify_deviation": {
            b["label"]: b["deviation"]["max_deviation_by_class"] for b in bundles
        },
        "reference_record_drift_vs_reference": record_drift(bundles, ref),
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "analysis.json").write_text(json.dumps(analysis, indent=2) + "\n")
    print(f"{len(bundles)} bundles -> {out / 'analysis.json'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--out", required=True)
    c.add_argument("--label", required=True)
    c.set_defaults(func=cmd_collect)
    a = sub.add_parser("analyze")
    a.add_argument("bundles", nargs="+")
    a.add_argument("--out", required=True)
    a.add_argument("--reference", default="reference-host")
    a.set_defaults(func=cmd_analyze)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
