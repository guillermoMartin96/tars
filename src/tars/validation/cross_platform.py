"""Cross-platform agreement (DR-0006, DR-0008).

Same-platform replay must be byte-identical (see ``determinism``). Across
CPUs/OSes, last-bit floating-point differences are expected, so the final state
is compared with a committed golden state from the reference platform within the
approved, measured bound.
"""

from __future__ import annotations

import json
import platform
from pathlib import Path

import numpy as np

from tars.sim.runner import RunResult
from tars.sim.scenario import Scenario
from tars.validation.determinism import event_log_sha256
from tars.validation.thresholds import REPO_ROOT

GOLDEN_M1 = REPO_ROOT / "proof" / "references" / "m1_final_state.json"


def golden_record(result: RunResult) -> dict:
    final = result.final
    return {
        "scenario": result.scenario.name,
        "scenario_hash": result.scenario.config_hash(),
        "platform": {
            "system": platform.system(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "events_sha256": event_log_sha256(result),
        "final_tick": final.tick,
        "final_r_m": final.r.tolist(),
        "final_v_mps": final.v.tolist(),
    }


def compare_to_golden(result: RunResult, golden: dict) -> dict[str, float]:
    scenario: Scenario = result.scenario
    if golden["scenario_hash"] != scenario.config_hash():
        raise ValueError("golden reference is stale: scenario hash differs")
    if golden["final_tick"] != result.final.tick:
        raise ValueError("final tick differs from golden reference")
    return {
        "final_position_difference_m": float(
            np.linalg.norm(result.final.r - np.array(golden["final_r_m"]))
        ),
        "final_velocity_difference_mps": float(
            np.linalg.norm(result.final.v - np.array(golden["final_v_mps"]))
        ),
        "bit_identical_to_golden": float(event_log_sha256(result) == golden["events_sha256"]),
    }


def load_golden(path: Path = GOLDEN_M1) -> dict:
    return json.loads(path.read_text())
