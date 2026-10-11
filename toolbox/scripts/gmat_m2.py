"""GMAT finite-burn reference workflow for Milestone 2 (T6; DR-0015 A, DR-0016 A).

Subcommands:
  generate  Write toolbox/references/gmat/m2/<mission>.script for each GMAT mission.
  run       Generate, run GmatConsole, verify alignment, and store report, console log
            and provenance metadata. Refuses to replace a committed reference without
            --replace-reason (DR-0009 policy: references are evidence, not fixtures).
  compare   Verify provenance and alignment of the committed references and compute
            O9 (JSON; exit 1 if a gate in proof/thresholds/m2.json fails, 2 if a
            reference is rejected). GMAT is not needed.

Examples:
  uv run python toolbox/scripts/gmat_m2.py generate
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
    gmat_m2.reference_dir().mkdir(parents=True, exist_ok=True)
    for name in args.missions:
        path = gmat_m2.reference_files(name)["script"]
        path.write_text(_script(name, f"{name}_report.txt"))
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


def _script_tolerances() -> tuple[float, float]:
    # DR-0009 (approved): bounds on platform-dependent last bits of the state literals.
    gates = load_thresholds().for_validator("gmat_reference")
    return gates["script_initial_position_difference_m"], gates[
        "script_initial_velocity_difference_mps"
    ]


def cmd_run(args: argparse.Namespace) -> int:
    console = Path(args.gmat_console).expanduser()
    if not console.exists():
        print(f"GmatConsole not found: {console}", file=sys.stderr)
        return 2
    status = 0
    for name in args.missions:
        files = gmat_m2.reference_files(name)
        if files["report"].exists() and not args.replace_reason:
            print(
                f"{name}: a committed GMAT reference exists; replacing it requires "
                "--replace-reason and explicit Tech Lead review (DR-0009)",
                file=sys.stderr,
            )
            status = 2
            continue
        mission = BY_NAME[name]
        scenario = mission.build()
        files["script"].parent.mkdir(parents=True, exist_ok=True)
        files["script"].write_text(_script(name, f"{name}_report.txt"))
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / f"{name}_report.txt"
            run_script = Path(tmp) / f"{name}.script"
            run_script.write_text(_script(name, str(report)))
            command = [str(console), "--run", str(run_script)]
            proc = subprocess.run(
                command, cwd=console.parent, capture_output=True, text=True, timeout=args.timeout
            )
            log = proc.stdout + proc.stderr
            # Paths are scrubbed: the log is evidence of the run, not of the host layout.
            files["console"].write_text(log.replace(tmp, "<tmp>").replace(str(Path.home()), "~"))
            if proc.returncode != 0 or "Execution Failed" in log or not report.exists():
                print(f"{name}: GMAT run failed (exit {proc.returncode})", file=sys.stderr)
                status = 1
                continue
            shutil.copyfile(report, files["report"])
        build = re.search(r"Build Date: (.+)", proc.stdout)
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True
        ).stdout.strip()
        veh = m2.vehicle(scenario)
        c = scenario.constants
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
            "tars_git_revision": revision,
            "generated_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            "replace_reason": args.replace_reason,
            "scenario": scenario.name,
            "scenario_hash": scenario.config_hash(),
            "script_sha256": _sha256(files["script"]),
            "report_sha256": _sha256(files["report"]),
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
            "model": "Earth point mass; ChemicalThruster VNB +-1, C1 = F, K1 = Isp, other "
            "coefficients 0, GravitationalAccel = g0, DecrementMass; PrinceDormand78, "
            "Accuracy 1e-13; aligned stepping (DR-0016): coasts 60 s, burns 1 s, "
            "realignment arcs one step",
        }
        files["metadata"].write_text(json.dumps(metadata, indent=2) + "\n")
        # Verify before trusting (DR-0016 mandatory alignment verification).
        result = _compare(name)
        if result.violations:
            print(f"{name}: reference rejected: {result.violations}", file=sys.stderr)
            status = 1
            continue
        rows = int(result.metrics["gmat_rows"])
        print(f"{name}: GMAT reference stored ({rows} rows)")
    return status


def _compare(name: str) -> gmat_m2.O9Result:
    mission = BY_NAME[name]
    scenario = mission.build()
    run = run_scenario(scenario)
    pos_tol, vel_tol = _script_tolerances()
    return gmat_m2.compare_committed(name, scenario, mission.expected, run.events, pos_tol, vel_tol)


def cmd_compare(args: argparse.Namespace) -> int:
    thresholds = load_scoped_thresholds(missions=frozenset(BY_NAME))
    status = 0
    for name in args.missions:
        result = _compare(name)
        if result.violations:
            print(json.dumps({"mission": name, "rejected": result.violations}, indent=2))
            status = max(status, 2)
            continue
        check = Check(
            f"o9_gmat[{name}]",
            result.metrics,
            thresholds.for_validator("o9_gmat", name),
            thresholds.status,
            "GMAT R2026a, aligned stepping (DR-0016)",
        )
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
