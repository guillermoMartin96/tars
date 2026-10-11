"""Smoke tests for toolbox CLIs (they are Proof entry points)."""

import json
import subprocess
import sys

import pytest

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


@pytest.mark.parametrize(
    "section,field", [("initial_orbit", "altitude_m"), ("stop", "max_duration_periods")]
)
def test_run_mission_rejects_infinite_input_without_traceback(tmp_path, section, field):
    data = json.loads(M1_SCENARIO.read_text())
    data[section][field] = float("inf")
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(data))
    out = tmp_path / "mission"
    proc = _run("toolbox/scripts/run_mission.py", "--scenario", bad, "--out", out)
    assert proc.returncode == 2
    assert "invalid scenario:" in proc.stderr and "Traceback" not in proc.stderr
    assert not out.exists()


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


# ------------------------------------------------------------------ M2 (T4)


def test_run_mission_m2_slice(tmp_path):
    from tests.conftest import M2_SLICE_SCENARIO

    proc = _run(
        "toolbox/scripts/run_mission.py", "--scenario", M2_SLICE_SCENARIO, "--out", tmp_path
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["schema_version"] == 2 and summary["stop_duration_s"] == 53700.0
    assert summary["commands"] == [
        {
            "command_id": "slice-prograde-001",
            "status": "accepted",
            "reason": None,
            "burn_id": "burn#000001",
            "submit_tick": 0,
        }
    ]
    assert summary["final_engine_state"] == "idle" and summary["unsubmitted_command_ids"] == []
    assert 287.0 < summary["final_propellant_kg"] < 288.0
    log = (tmp_path / "events.jsonl").read_bytes()
    import hashlib

    assert hashlib.sha256(log).hexdigest() == summary["events_sha256"]
    assert sorted(p.name for p in tmp_path.iterdir()) == ["events.jsonl", "summary.json"]


def test_m2_slice_is_deterministic_across_processes(tmp_path):
    from tests.conftest import M2_SLICE_SCENARIO

    hashes = []
    for i in range(2):
        out = tmp_path / str(i)
        assert (
            _run(
                "toolbox/scripts/run_mission.py", "--scenario", M2_SLICE_SCENARIO, "--out", out
            ).returncode
            == 0
        )
        hashes.append(json.loads((out / "summary.json").read_text())["events_sha256"])
    assert hashes[0] == hashes[1]


def test_run_mission_m1_summary_has_no_m2_fields(tmp_path):
    proc = _run("toolbox/scripts/run_mission.py", "--scenario", M1_SCENARIO, "--out", tmp_path)
    assert proc.returncode == 0, proc.stderr
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert "schema_version" not in summary and "commands" not in summary


def test_run_mission_rejects_invalid_v2_scenario_without_traceback(tmp_path):
    from tests.conftest import M2_SLICE_SCENARIO

    data = json.loads(M2_SLICE_SCENARIO.read_text())
    data["stop"] = {"duration_s": 15.0}  # off the tick grid
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(data))
    out = tmp_path / "mission"
    proc = _run("toolbox/scripts/run_mission.py", "--scenario", bad, "--out", out)
    assert proc.returncode == 2 and "Traceback" not in proc.stderr
    assert not out.exists()


def test_failed_run_writes_no_outputs_and_keeps_previous_ones(tmp_path, monkeypatch):
    """Outputs are written only after the whole run; an earlier run's files survive."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_mission", REPO_ROOT / "toolbox/scripts/run_mission.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = tmp_path / "mission"
    out.mkdir()
    (out / "events.jsonl").write_text("previous\n")

    def boom(*args, **kwargs):
        raise RuntimeError("runner failure")

    monkeypatch.setattr(mod, "run_scenario", boom)
    with pytest.raises(RuntimeError):
        mod.main(["--scenario", str(M1_SCENARIO), "--out", str(out)])
    assert sorted(p.name for p in out.iterdir()) == ["events.jsonl"]
    assert (out / "events.jsonl").read_text() == "previous\n"


def test_atomic_write_never_leaves_a_partial_file(tmp_path, monkeypatch):
    import importlib.util
    import os

    spec = importlib.util.spec_from_file_location(
        "run_mission", REPO_ROOT / "toolbox/scripts/run_mission.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    target = tmp_path / "events.jsonl"
    mod._write_atomic(target, b"first\n")
    assert target.read_bytes() == b"first\n"
    plain = tmp_path / "plain"
    plain.write_bytes(b"")
    assert target.stat().st_mode & 0o777 == plain.stat().st_mode & 0o777  # as a plain write
    plain.unlink()

    def fail_replace(src, dst):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError):
        mod._write_atomic(target, b"second\n")
    assert target.read_bytes() == b"first\n"
    assert [p.name for p in tmp_path.iterdir()] == ["events.jsonl"]  # temp file removed
