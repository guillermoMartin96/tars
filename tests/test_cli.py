"""Smoke tests for toolbox CLIs (they are Proof entry points)."""

import json
import subprocess
import sys

from tests.conftest import M1_SCENARIO, REPO_ROOT


def _run(script, *args):
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / script), *map(str, args)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def test_run_mission_writes_valid_outputs(tmp_path):
    proc = _run("toolbox/scripts/run_mission.py", "--scenario", M1_SCENARIO, "--out", tmp_path)
    assert proc.returncode == 0, proc.stderr
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["status"] == "success" and summary["orbits_completed"] == 10
    from tars.events import read_jsonl

    events = read_jsonl((tmp_path / "events.jsonl").read_text())
    assert len(events) == summary["event_count"]


def test_run_mission_rejects_invalid_scenario(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"name": "x"}')
    assert _run("toolbox/scripts/run_mission.py", "--scenario", bad).returncode == 2


def test_cross_process_determinism_validator():
    proc = _run("toolbox/validators/determinism.py")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert json.loads(proc.stdout)["passed"] is True


def test_gmat_run_refuses_to_replace_committed_reference_without_reason(tmp_path):
    """DR-0009: committed reference data is never silently regenerated."""
    proc = _run(
        "toolbox/scripts/gmat_m1.py", "run", "--gmat-console", tmp_path / "GmatConsole",
        "--gmat-version", "R2026a",
    )  # fmt: skip
    assert proc.returncode == 2
    assert "--replace-reason" in proc.stderr


def test_gmat_compare_passes_against_committed_reference():
    proc = _run("toolbox/scripts/gmat_m1.py", "compare")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    result = json.loads(proc.stdout)
    assert result["passed"] is True and result["threshold_status"] == "approved"
    assert len(result["thresholds"]) == 9
