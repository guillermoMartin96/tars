"""Cross-platform agreement (DR-0006, DR-0008).

Same-platform replay must be byte-identical (see ``determinism``). Across
CPUs/OSes, last-bit floating-point differences are expected, so the final state
is compared with a committed golden state from the reference platform within the
approved, measured bound.
"""

from __future__ import annotations

import json
import platform
import subprocess
from pathlib import Path

import numpy as np

from tars.sim.runner import RunResult
from tars.sim.scenario import Scenario
from tars.validation.determinism import event_log_sha256
from tars.validation.thresholds import REPO_ROOT

GOLDEN_M1 = REPO_ROOT / "proof" / "references" / "m1_final_state.json"


def platform_info() -> dict[str, str]:
    """Identify the execution platform, including the CPU model.

    CPU matters: CI 'ubuntu-latest' runners with different CPUs produced different
    last bits (NumPy selects SIMD code paths at runtime), see VAL-0003.
    """
    cpu = platform.processor()
    try:
        if platform.system() == "Linux":
            for line in Path("/proc/cpuinfo").read_text().splitlines():
                if line.startswith("model name"):
                    cpu = line.split(":", 1)[1].strip()
                    break
        elif platform.system() == "Darwin":
            cpu = (
                subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True
                ).stdout.strip()
                or cpu
            )
    except OSError:
        pass
    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "cpu": cpu,
        "python": platform.python_version(),
        "numpy": np.__version__,
    }


def golden_record(result: RunResult) -> dict:
    final = result.final
    return {
        "scenario": result.scenario.name,
        "scenario_hash": result.scenario.config_hash(),
        "platform": platform_info(),
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
