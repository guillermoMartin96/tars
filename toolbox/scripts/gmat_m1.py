"""GMAT reference workflow for Milestone 1 (DR-0005).

Subcommands:
  generate  Write toolbox/references/gmat/m1_two_body.script from the scenario.
  run       Generate the script, run GmatConsole, and store the report plus
            provenance metadata in toolbox/references/gmat/.
  compare   Compare the committed GMAT report with our simulation (JSON output;
            exit 1 if a gated threshold in proof/thresholds/m1.json fails).

Examples:
  uv run python toolbox/scripts/gmat_m1.py generate
  uv run python toolbox/scripts/gmat_m1.py run --gmat-console "$HOME/Applications/GMAT R2026a/bin/GmatConsole" --gmat-version R2026a
  uv run python toolbox/scripts/gmat_m1.py compare
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

from tars.sim.runner import run_scenario
from tars.sim.scenario import load_scenario
from tars.validation.gmat import compare, m1_script, parse_report, provenance_problems
from tars.validation.thresholds import REPO_ROOT, Check, load_thresholds

REF_DIR = REPO_ROOT / "toolbox" / "references" / "gmat"
SCRIPT = REF_DIR / "m1_two_body.script"
REPORT = REF_DIR / "m1_two_body_report.txt"
METADATA = REF_DIR / "m1_two_body_metadata.json"
DEFAULT_SCENARIO = REPO_ROOT / "scenarios" / "m1_leo_250km.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cmd_generate(args: argparse.Namespace) -> int:
    scenario = load_scenario(args.scenario)
    SCRIPT.write_text(m1_script(scenario))
    print(f"wrote {SCRIPT.relative_to(REPO_ROOT)} (scenario_hash {scenario.config_hash()[:16]}...)")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    scenario = load_scenario(args.scenario)
    console = Path(args.gmat_console).expanduser()
    if not console.exists():
        print(f"GmatConsole not found: {console}", file=sys.stderr)
        return 2
    SCRIPT.write_text(m1_script(scenario))
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "m1_two_body_report.txt"
        run_script = Path(tmp) / "m1_two_body.script"
        run_script.write_text(m1_script(scenario, report_path=str(report)))
        command = [str(console), *args.console_args, str(run_script)]
        proc = subprocess.run(
            command,
            cwd=console.parent,
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
        (REF_DIR / "m1_gmat_console.log").write_text(proc.stdout + proc.stderr)
        if proc.returncode != 0 or not report.exists():
            print(
                f"GMAT run failed (exit {proc.returncode}); see m1_gmat_console.log",
                file=sys.stderr,
            )
            return 1
        # Validate completeness before trusting and hashing the new report (REV-002).
        try:
            compare(parse_report(report.read_text()), run_scenario(scenario).samples, scenario)
        except ValueError as exc:
            print(f"GMAT report rejected: {exc}", file=sys.stderr)
            return 1
        shutil.copyfile(report, REPORT)
    build = re.search(r"Build Date: (.+)", proc.stdout)
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True
    ).stdout.strip()
    metadata = {
        "gmat_version": args.gmat_version,
        "gmat_build_date": build.group(1).strip() if build else None,
        "gmat_console": str(console),
        "gmat_console_sha256": _sha256(console),
        "command": [*command[:-1], "<temp copy of m1_two_body.script with absolute report path>"],
        "host_platform": platform.platform(),
        "tars_git_revision": revision,
        "generated_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "scenario": scenario.name,
        "scenario_hash": scenario.config_hash(),
        "script_sha256": _sha256(SCRIPT),
        "report_sha256": _sha256(REPORT),
        "constants": {
            "name": scenario.constants.name,
            "mu_km3_s2": scenario.constants.mu / 1e9,
            "equatorial_radius_km": scenario.constants.equatorial_radius / 1000.0,
        },
        "force_model": "Earth point mass only; no drag, SRP, third body, relativity",
        "integrator": "PrinceDormand78, Accuracy 1e-13, MaxStep = report interval",
    }
    METADATA.write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"GMAT reference stored: {REPORT.relative_to(REPO_ROOT)}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    scenario = load_scenario(args.scenario)
    if not (REPORT.exists() and METADATA.exists()):
        print("no committed GMAT reference; run the 'run' subcommand first", file=sys.stderr)
        return 2
    metadata = json.loads(METADATA.read_text())
    problems = provenance_problems(metadata, scenario, SCRIPT.read_text())
    if metadata["report_sha256"] != _sha256(REPORT):
        problems.append("GMAT report does not match its recorded sha256")
    if metadata["script_sha256"] != _sha256(SCRIPT):
        problems.append("GMAT script does not match its recorded sha256")
    if problems:
        print("GMAT reference rejected: " + "; ".join(problems), file=sys.stderr)
        return 2

    run = run_scenario(scenario)
    metrics = compare(parse_report(REPORT.read_text()), run.samples, scenario)
    thresholds = load_thresholds()
    check = Check(
        "gmat_reference",
        metrics,
        thresholds.for_validator("gmat_reference"),
        thresholds.status,
        f"GMAT {metadata['gmat_version']}",
    )
    print(json.dumps(check.to_event().model_dump(mode="json"), indent=2))
    return 0 if check.passed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", type=Path, default=DEFAULT_SCENARIO)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("generate").set_defaults(func=cmd_generate)
    run = sub.add_parser("run")
    run.add_argument("--gmat-console", required=True)
    run.add_argument("--gmat-version", required=True)
    run.add_argument(
        "--console-args", nargs="*", default=["--run"], help="arguments before the script path"
    )
    run.add_argument("--timeout", type=float, default=600.0)
    run.set_defaults(func=cmd_run)
    sub.add_parser("compare").set_defaults(func=cmd_compare)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
