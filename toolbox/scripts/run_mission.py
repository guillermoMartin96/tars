"""Run a scenario headlessly and write machine-readable outputs.

Usage:
    uv run python toolbox/scripts/run_mission.py --scenario scenarios/m1_leo_250km.json \
        [--out runs/m1_leo_250km]

Writes:
    events.jsonl  one validated event per line (ADR-0005)
    summary.json  status, failure cause, orbit count, crossing times, final state, log hash

Exit code: 0 on mission success, 1 on mission failure, 2 on invalid input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from tars.events import to_jsonl
from tars.sim.runner import run_scenario
from tars.sim.scenario import load_scenario


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
    (out / "events.jsonl").write_bytes(log)

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
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(
        f"{scenario.name}: {done.status}"
        + (f" ({done.failure_cause})" if done.failure_cause else "")
        + f", {done.orbits_completed} orbits, events sha256 {summary['events_sha256'][:16]}..."
        + f" -> {out}"
    )
    return 0 if done.status == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
