"""Determinism checks (DR-0006): identical inputs -> byte-identical event logs."""

from __future__ import annotations

import hashlib

from tars.events.schema import to_jsonl
from tars.sim.runner import RunResult, run_scenario
from tars.sim.scenario import Scenario


def event_log_bytes(result: RunResult) -> bytes:
    return to_jsonl(result.events).encode()


def event_log_sha256(result: RunResult) -> str:
    return hashlib.sha256(event_log_bytes(result)).hexdigest()


def repeat_hashes(scenario: Scenario, runs: int = 2) -> list[str]:
    return [event_log_sha256(run_scenario(scenario, record_samples=False)) for _ in range(runs)]
