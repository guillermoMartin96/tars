"""Run a scenario headlessly and write machine-readable outputs.

Usage:
    uv run python toolbox/scripts/run_mission.py --scenario scenarios/m1_leo_250km.json \
        [--out runs/m1_leo_250km]

Writes:
    events.jsonl  one validated event per line (ADR-0005)
    summary.json  status, failure cause, orbit count, crossing times, final state, log hash;
                  for schema-version-2 scenarios also command outcomes and final propulsion

Each file is written atomically (temporary file, then rename), so an interrupted run
never leaves a truncated file. events.jsonl is written first; summary.json records its
sha256.

Exit code: 0 on mission success, 1 on mission failure, 2 on invalid input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

from pydantic import ValidationError

from tars.events import to_jsonl
from tars.sim.runner import run_scenario
from tars.sim.scenario import ScenarioV2, load_scenario


def _write_atomic(path: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        umask = os.umask(0)
        os.umask(umask)
        os.chmod(tmp, 0o666 & ~umask)  # mkstemp creates 0600; match a plain write
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def _propulsion_summary(result) -> dict:
    final = result.final_propulsion
    return {
        "commands": [
            {
                "command_id": r.command_id,
                "status": r.status.value,
                "reason": None if r.reason is None else r.reason.value,
                "burn_id": r.burn_id,
                "submit_tick": r.tick,
            }
            for r in result.receipts
        ],
        "unsubmitted_command_ids": result.unsubmitted_command_ids,
        "final_propellant_kg": None if final is None else final.propellant_kg,
        "final_total_mass_kg": None if final is None else final.total_mass_kg,
        "final_engine_state": None if final is None else final.engine_state.value,
        "active_burn_id_at_stop": None if final is None else final.active_burn_id,
        "pending_burn_ids_at_stop": [] if final is None else list(final.pending_burn_ids),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        scenario = load_scenario(args.scenario)
    except (OSError, ValidationError) as exc:
        print(f"invalid scenario: {exc}", file=sys.stderr)
        return 2

    out = args.out or Path("runs") / scenario.name
    out.mkdir(parents=True, exist_ok=True)
    result = run_scenario(scenario, record_samples=False)
    log = to_jsonl(result.events).encode()
    _write_atomic(out / "events.jsonl", log)

    done = result.completed
    summary = {
        "scenario": scenario.name,
        "scenario_hash": scenario.config_hash(),
        "status": done.status,
        "failure_cause": done.failure_cause,
        "orbits_completed": done.orbits_completed,
        "crossing_times_s": result.crossing_times,
        "final_tick": done.tick,
        "final_t_s": done.t,
        "final_r_m": done.r,
        "final_v_mps": done.v,
        "min_altitude_m": done.min_altitude_m,
        "max_altitude_m": done.max_altitude_m,
        "events_sha256": hashlib.sha256(log).hexdigest(),
        "event_count": len(result.events),
    }
    if isinstance(scenario, ScenarioV2):
        summary["schema_version"] = 2
        summary["stop_duration_s"] = scenario.stop.duration_s
        summary.update(_propulsion_summary(result))
    _write_atomic(out / "summary.json", (json.dumps(summary, indent=2) + "\n").encode())
    print(
        f"{scenario.name}: {done.status}"
        + (f" ({done.failure_cause})" if done.failure_cause else "")
        + f", {done.orbits_completed} orbits, events sha256 {summary['events_sha256'][:16]}..."
        + f" -> {out}"
    )
    return 0 if done.status == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
