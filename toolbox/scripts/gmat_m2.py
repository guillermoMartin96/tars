"""GMAT finite-burn reference workflow for Milestone 2 (T6; DR-0015 A, DR-0016 A).

Subcommands:
  generate  Write preview scripts to --out (never into the committed references).
  run       Run GmatConsole and stage script, report, console log, metadata and an
            updated approved-digest manifest; validate the staged reference completely
            (provenance, alignment, coverage, every O9 gate, gate coverage, a clean
            audit of the simulator run); only then commit it atomically, manifest last.
            Refuses to touch an existing reference without --replace-reason (DR-0009:
            references are evidence, not fixtures).
  compare   Verify provenance and alignment of the committed references and compute
            O9 (JSON; exit 1 if a gate fails, 2 if a reference, the simulator audit or
            the threshold coverage is rejected). GMAT is not needed.

Examples:
  uv run python toolbox/scripts/gmat_m2.py generate --out runs/gmat_m2_preview
  uv run python toolbox/scripts/gmat_m2.py run --gmat-console "$HOME/Applications/GMAT R2026a/bin/GmatConsole" --gmat-version R2026a
  uv run python toolbox/scripts/gmat_m2.py compare
"""  # noqa: E501

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tars.sim.constants import STANDARD_GRAVITY
from tars.sim.runner import run_scenario
from tars.validation import gmat_m2, m2
from tars.validation.m2_missions import MISSIONS
from tars.validation.thresholds import REPO_ROOT, Check, load_scoped_thresholds, load_thresholds

BY_NAME = {m.name: m for m in MISSIONS}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _script(name: str, report_path: str) -> str:
    mission = BY_NAME[name]
    scenario = mission.build()
    predicted = m2.predict_burns(scenario, mission.expected)
    return gmat_m2.m2_script(scenario, predicted, scenario.stop.duration_s, report_path)


def cmd_generate(args: argparse.Namespace) -> int:
    out = Path(args.out).resolve()
    ref = gmat_m2.reference_dir().resolve()
    if out == ref or out.is_relative_to(ref):
        print("generate never writes into the committed references; use run", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)
    for name in args.missions:
        path = out / f"{name}.script"
        # Never follow an existing destination (symlink) into protected files (F11):
        # write a fresh temporary file and rename it over the destination entry.
        if path.is_symlink() or path.resolve().is_relative_to(ref):
            print(f"refusing to write through {path}", file=sys.stderr)
            return 2
        tmp = out / f".{name}.script.tmp"
        tmp.unlink(missing_ok=True)
        tmp.write_text(_script(name, f"{name}_report.txt"))
        tmp.replace(path)
        print(f"wrote preview {path}")
    return 0


def _script_tolerances() -> tuple[float, float]:
    # DR-0009 (approved): bounds on platform-dependent last bits of the state literals.
    gates = load_thresholds().for_validator("gmat_reference")
    return (
        gates["script_initial_position_difference_m"],
        gates["script_initial_velocity_difference_mps"],
    )


def _evaluate(name: str, base: Path | None = None) -> tuple[list[str], Check | None]:
    """Full O9 evaluation: simulator audit, reference verification, gate coverage."""
    mission = BY_NAME[name]
    scenario = mission.build()
    run = run_scenario(scenario)
    audit = m2.audit_run(scenario, mission.expected, run)
    rejected = [f"simulator audit {k}: {x}" for k, xs in audit.violations.items() for x in xs]
    # The audit's numerical T5 gates count too, fail-closed on missing limits (F12).
    t5 = load_scoped_thresholds(missions=frozenset(BY_NAME))
    for group, metrics in audit.metrics.items():
        limits = t5.for_validator(group, name)
        missing = m2.ungated_metrics(metrics, limits)
        if missing:
            rejected.append(f"simulator audit {group}: metrics without a threshold {missing}")
            continue
        failed = Check(group, metrics, limits, t5.status).failures
        rejected += [f"simulator audit {group}: {f}" for f in failed]
    result = gmat_m2.compare_committed(
        name, scenario, mission.expected, run.events, *_script_tolerances(), base=base
    )
    rejected += result.violations
    if rejected:
        return rejected, None
    thresholds = load_scoped_thresholds(missions=frozenset(BY_NAME))
    limits = thresholds.for_validator("o9_gmat", name)
    missing = gmat_m2.missing_gates(result.metrics, limits)
    if missing:
        return [f"O9 metrics without a threshold: {missing}"], None
    check = Check(
        f"o9_gmat[{name}]",
        result.metrics,
        limits,
        thresholds.status,
        "GMAT R2026a, aligned stepping (DR-0016)",
    )
    return [], check


def cmd_run(args: argparse.Namespace) -> int:
    console = Path(args.gmat_console).expanduser()
    if not console.exists():
        print(f"GmatConsole not found: {console}", file=sys.stderr)
        return 2
    status = 0
    for name in args.missions:
        files = gmat_m2.reference_files(name)
        approved = (gmat_m2.load_approved() or {}).get("references", {})
        exists = any(p.exists() for p in files.values()) or name in approved
        if exists and not args.replace_reason:
            print(
                f"{name}: a committed GMAT reference exists; replacing it requires "
                "--replace-reason and explicit Tech Lead review (DR-0009)",
                file=sys.stderr,
            )
            status = 2
            continue
        with tempfile.TemporaryDirectory() as tmp:
            stage = Path(tmp) / "stage"
            stage.mkdir()
            staged = gmat_m2.reference_files(name, stage)
            staged["script"].write_text(_script(name, f"{name}_report.txt"))
            report = Path(tmp) / f"{name}_report.txt"
            run_script = Path(tmp) / f"{name}.script"
            run_script.write_text(_script(name, str(report)))
            proc = subprocess.run(
                [str(console), "--run", str(run_script)],
                cwd=console.parent,
                capture_output=True,
                text=True,
                timeout=args.timeout,
            )
            log = proc.stdout + proc.stderr
            # Paths are scrubbed: the log is evidence of the run, not of the host layout.
            staged["console"].write_text(log.replace(tmp, "<tmp>").replace(str(Path.home()), "~"))
            if proc.returncode != 0 or "Execution Failed" in log or not report.exists():
                print(f"{name}: GMAT run failed (exit {proc.returncode})", file=sys.stderr)
                status = 1
                continue
            shutil.copyfile(report, staged["report"])
            mission = BY_NAME[name]
            scenario = mission.build()
            veh = m2.vehicle(scenario)
            c = scenario.constants
            build = re.search(r"Build Date: (.+)", proc.stdout)
            metadata = {
                "mission": name,
                "gmat_version": args.gmat_version,
                "gmat_build_date": build.group(1).strip() if build else None,
                "gmat_console_sha256": _sha256(console),
                "command": [
                    "GmatConsole",
                    "--run",
                    f"<temp copy of {name}.script, absolute report path>",
                ],
                "host_platform": platform.platform(),
                "tars_git_revision": subprocess.run(
                    ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True
                ).stdout.strip(),
                "generated_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
                "replace_reason": args.replace_reason,
                "scenario": scenario.name,
                "scenario_hash": scenario.config_hash(),
                "script_sha256": _sha256(staged["script"]),
                "report_sha256": _sha256(staged["report"]),
                "console_sha256": _sha256(staged["console"]),
                "constants": {
                    "name": c.name,
                    "mu_km3_s2": c.mu / 1e9,
                    "equatorial_radius_km": c.equatorial_radius / 1000.0,
                    "standard_gravity_mps2": STANDARD_GRAVITY,
                    "thrust_n": veh.thrust_n,
                    "isp_s": veh.isp_s,
                    "dry_mass_kg": veh.dry_mass_kg,
                    "propellant_kg": veh.propellant_kg,
                },
                "model": gmat_m2.MODEL,
            }
            staged["metadata"].write_text(json.dumps(metadata, indent=2) + "\n")
            manifest_path = gmat_m2.approved_manifest_path()
            manifest = (
                json.loads(manifest_path.read_text())
                if manifest_path.exists()
                else {"references": {}, "history": []}
            )
            manifest["references"][name] = {
                "script_sha256": metadata["script_sha256"],
                "report_sha256": metadata["report_sha256"],
                "console_sha256": metadata["console_sha256"],
                "metadata_sha256": _sha256(staged["metadata"]),
            }
            history = manifest["history"]
            history.append(
                {
                    "mission": name,
                    "generated_utc": metadata["generated_utc"],
                    "tars_git_revision": metadata["tars_git_revision"],
                    "reason": args.replace_reason or "initial reference",
                    "report_sha256": metadata["report_sha256"],
                    # Hash chain (review M2-T6 F14): edits or deletions inside the
                    # history break it.
                    "previous_record_sha256": gmat_m2.record_digest(history[-1])
                    if history
                    else None,
                }
            )
            staged_manifest = gmat_m2.approved_manifest_path(stage)
            staged_manifest.write_text(json.dumps(manifest, indent=2) + "\n")
            # Validate the complete staged reference before anything is committed (F1).
            rejected, check = _evaluate(name, base=stage)
            if rejected or check is None or not check.passed:
                why = rejected or (check.failures if check else ["no check"])
                print(
                    f"{name}: staged reference rejected; nothing replaced: {why}", file=sys.stderr
                )
                status = 1
                continue
            _publish(name, staged, staged_manifest, manifest)
            rows = int(check.metrics["gmat_rows"])
            print(f"{name}: GMAT reference validated and stored ({rows} rows)")
    return status


def _atomic_write(dst: Path, data: bytes) -> None:
    tmp = dst.with_name(f".{dst.name}.new")
    tmp.write_bytes(data)
    tmp.replace(dst)


def _publish(name: str, staged: dict, staged_manifest: Path, manifest: dict) -> None:
    """Publish a validated reference so that no interruption leaves an accepted mix
    (review M2-T6 F9):
    1. withdraw the mission's approval (manifest without its entry), atomically;
    2. replace each artifact atomically (temp file + rename);
    3. publish the new manifest, the commit marker, atomically.
    Interrupted after 1, the mission is unapproved and every check rejects it, so a
    partial artifact set can never pass; re-running ``run`` completes it."""
    ref = gmat_m2.reference_dir()
    ref.mkdir(parents=True, exist_ok=True)
    path = gmat_m2.approved_manifest_path()
    if path.exists():
        current = json.loads(path.read_text())
        current.get("references", {}).pop(name, None)
        _atomic_write(path, (json.dumps(current, indent=2) + "\n").encode())
    files = gmat_m2.reference_files(name)
    for key in ("script", "report", "console", "metadata"):
        _atomic_write(files[key], staged[key].read_bytes())
    _atomic_write(path, staged_manifest.read_bytes())


def cmd_compare(args: argparse.Namespace) -> int:
    status = 0
    for name in args.missions:
        rejected, check = _evaluate(name)
        if rejected or check is None:
            print(json.dumps({"mission": name, "rejected": rejected}, indent=2))
            status = max(status, 2)
            continue
        print(json.dumps(check.to_event().model_dump(mode="json"), indent=2))
        if not check.passed:
            status = max(status, 1)
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for cmd, fn in (("generate", cmd_generate), ("run", cmd_run), ("compare", cmd_compare)):
        p = sub.add_parser(cmd)
        p.add_argument("--missions", nargs="+", default=list(gmat_m2.GMAT_MISSIONS))
        p.set_defaults(fn=fn)
        if cmd == "generate":
            p.add_argument("--out", default="runs/gmat_m2_preview")
        if cmd == "run":
            p.add_argument("--gmat-console", required=True)
            p.add_argument("--gmat-version", required=True)
            p.add_argument("--replace-reason", default=None)
            p.add_argument("--timeout", type=float, default=600.0)
    args = parser.parse_args(argv)
    unknown = [m for m in args.missions if m not in gmat_m2.GMAT_MISSIONS]
    if unknown:
        print(f"no GMAT reference defined for {unknown}", file=sys.stderr)
        return 2
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
