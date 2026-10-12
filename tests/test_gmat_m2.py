"""T6: GMAT M2 reference (O9). The committed references verify and pass; corrupted
references are rejected; simulator physics mutants are caught against GMAT."""

from __future__ import annotations

import dataclasses
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tars.sim import propulsion as propulsion_module
from tars.sim import simulator as simulator_module
from tars.sim.propulsion import Prograde
from tars.sim.runner import run_scenario
from tars.validation import gmat_m2, m2
from tars.validation.m2_missions import MISSIONS
from tars.validation.thresholds import M2_THRESHOLDS, REPO_ROOT, load_thresholds

BY_NAME = {m.name: m for m in MISSIONS}
LIMITS = json.loads(M2_THRESHOLDS.read_text())["limits"]["o9_gmat"]
GATES_M1 = load_thresholds().for_validator("gmat_reference")
TOL = (
    GATES_M1["script_initial_position_difference_m"],
    GATES_M1["script_initial_velocity_difference_mps"],
)
GMAT_CONSOLE = Path.home() / "Applications" / "GMAT R2026a" / "bin" / "GmatConsole"
CLI = REPO_ROOT / "toolbox" / "scripts" / "gmat_m2.py"


def _limits(name):
    return {**LIMITS["all"], **LIMITS.get(name, {})}


def _failures(name, metrics):
    return [k for k, lim in _limits(name).items() if not metrics[k] <= lim]


def _compare(name, events=None):
    mission = BY_NAME[name]
    scenario = mission.build()
    events = run_scenario(scenario).events if events is None else events
    return gmat_m2.compare_committed(name, scenario, mission.expected, events, *TOL)


def _labelled(name):
    mission = BY_NAME[name]
    scenario = mission.build()
    predicted = m2.predict_burns(scenario, mission.expected)
    arcs = gmat_m2.plan_arcs(scenario, predicted, scenario.stop.duration_s)
    rows = gmat_m2.parse_stream(gmat_m2.reference_files(name)["report"].read_text())
    return scenario, predicted, arcs, rows


# ------------------------------------------------------------------ generator


def test_slice_arc_plan_is_aligned():
    _, _, arcs, _ = _labelled("m2_prograde_burn")
    got = [(a.start_s, a.end_s, a.step_s, a.direction) for a in arcs]
    assert got == [
        (0.0, 600.0, 60.0, None),
        (600.0, 677.3, 1.0, "prograde"),
        (677.3, 720.0, 720.0 - 677.3, None),
        (720.0, 53700.0, 60.0, None),
    ]
    # Every telemetry time is a row time, so every sample has a GMAT state.
    times = {t for i, a in enumerate(arcs) for t in a.row_times(first=i == 0)}
    assert {k * 60.0 for k in range(896)} <= times


def test_adjacent_burns_switch_thrusters_without_a_coast():
    _, _, arcs, _ = _labelled("m2_invalid_commands")
    burns = [(a.start_s, a.end_s, a.direction) for a in arcs if a.direction]
    assert burns == [
        (1200.0, 1230.0, "prograde"),
        (1230.0, 1240.0, "retrograde"),
        (2400.0, 2420.0, "retrograde"),
    ]
    script = gmat_m2.reference_files("m2_invalid_commands")["script"].read_text()
    assert "EndFiniteBurn FBPro(Sat);\nBeginFiniteBurn FBRetro(Sat);" in script


def test_script_pins_every_engine_coefficient_and_g0():
    """VAL-0009: GMAT's default GravitationalAccel is 9.81; thrust and Isp polynomials
    have defaults. The generated script fixes every one from the scenario."""
    script = gmat_m2.reference_files("m2_retrograde_burn")["script"].read_text()
    assert "GMAT EngRetro.GravitationalAccel = 9.80665;" in script
    assert "GMAT EngRetro.C1 = 490.0;" in script and "GMAT EngRetro.K1 = 312.0;" in script
    assert all(
        f"GMAT EngRetro.C{k} = 0;" in script and f"GMAT EngRetro.K{k} = 0;" in script
        for k in range(2, 17)
    )
    assert (
        "GMAT EngRetro.ThrustDirection1 = -1;" in script and "GMAT EngRetro.Axes = VNB;" in script
    )
    assert "GMAT Sat.DryMass = 1000.0;" in script and "GMAT Tank1.FuelMass = 300.0;" in script


def test_generator_is_deterministic_and_matches_the_committed_scripts():
    for name in gmat_m2.GMAT_MISSIONS:
        mission = BY_NAME[name]
        scenario = mission.build()
        predicted = m2.predict_burns(scenario, mission.expected)
        a = gmat_m2.m2_script(scenario, predicted, scenario.stop.duration_s, f"{name}_report.txt")
        b = gmat_m2.m2_script(scenario, predicted, scenario.stop.duration_s, f"{name}_report.txt")
        assert a == b
        committed = gmat_m2.reference_files(name)["script"].read_text()
        assert gmat_m2.split_script(a)[0] == gmat_m2.split_script(committed)[0]


def test_generator_refuses_unsupported_scenarios():
    no_prop = BY_NAME["m2_invalid_commands_no_propulsion"].build()
    with pytest.raises(ValueError, match="spacecraft"):
        gmat_m2.m2_script(no_prop, [], 53700.0)


def test_depletion_is_not_a_gmat_mission():
    """VAL-0009 finding 4 / T6 measurement: GMAT cannot propagate to exact depletion."""
    assert "m2_burn_to_depletion" not in gmat_m2.GMAT_MISSIONS


# ------------------------------------------------------------------ committed references


@pytest.mark.parametrize("name", gmat_m2.GMAT_MISSIONS)
def test_committed_reference_verifies_and_passes(name):
    result = _compare(name)
    assert result.violations == []
    assert _failures(name, result.metrics) == []
    # Classification: ours vs GMAT is our RK4 error (equal to ours vs DOP853).
    assert (
        result.metrics["gmat_vs_dop853_final_position_error_m"]
        < 1e-4 * result.metrics["ours_vs_gmat_final_position_error_m"]
    )


def test_tampered_report_is_rejected(tmp_path, monkeypatch):
    name = "m2_prograde_burn"
    src = gmat_m2.reference_dir()
    dst = tmp_path / "m2"
    shutil.copytree(src, dst)
    report = dst / f"{name}_report.txt"
    report.write_text(report.read_text().replace("1300 ", "1299 ", 1))
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    assert any("report_sha256" in v or "approved manifest" in v for v in _compare(name).violations)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("GravitationalAccel = 9.80665;", "GravitationalAccel = 9.81;"),
        ("C1 = 490.0;", "C1 = 491.0;"),
        ("K3 = 0;", "K3 = 1;"),
        ("Accuracy = 1e-13;", "Accuracy = 1e-11;"),
    ],
)
def test_configuration_change_in_the_committed_script_is_rejected(tmp_path, monkeypatch, old, new):
    name = "m2_prograde_burn"
    dst = tmp_path / "m2"
    shutil.copytree(gmat_m2.reference_dir(), dst)
    script = dst / f"{name}.script"
    script.write_text(script.read_text().replace(old, new, 1))
    meta = dst / f"{name}_metadata.json"
    data = json.loads(meta.read_text())
    import hashlib

    data["script_sha256"] = hashlib.sha256(script.read_bytes()).hexdigest()  # even if re-hashed
    meta.write_text(json.dumps(data))
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    assert any("regenerated script" in v for v in _compare(name).violations)


def test_wrong_metadata_constants_are_rejected(tmp_path, monkeypatch):
    name = "m2_retrograde_burn"
    dst = tmp_path / "m2"
    shutil.copytree(gmat_m2.reference_dir(), dst)
    meta = dst / f"{name}_metadata.json"
    data = json.loads(meta.read_text())
    data["constants"]["standard_gravity_mps2"] = 9.81
    meta.write_text(json.dumps(data))
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    assert any("metadata constants" in v for v in _compare(name).violations)


def test_missing_row_breaks_the_alignment_count():
    _, _, arcs, rows = _labelled("m2_prograde_burn")
    _, v = gmat_m2.label_rows(rows[:500] + rows[501:], arcs)
    assert any("not step-aligned" in x for x in v)


def test_unaligned_step_is_detected():
    """An adaptive step cut (row epochs off the schedule by 1 s) fails verification."""
    scenario, predicted, arcs, rows = _labelled("m2_prograde_burn")
    shifted = [
        dataclasses.replace(r, a1mjd=r.a1mjd + 1.0 / 86400.0) if i == 300 else r
        for i, r in enumerate(rows)
    ]
    labelled, _ = gmat_m2.label_rows(shifted, arcs)
    metrics = gmat_m2.alignment_metrics(
        labelled, arcs, predicted, scenario.constants.mu, m2.vehicle(scenario).mass_flow_kgps
    )
    assert metrics["step_spacing_error_max_s"] > LIMITS["all"]["step_spacing_error_max_s"]


@pytest.mark.parametrize(("field", "delta"), [("r", 1e-3), ("mass_kg", 1e-6)])
def test_corrupted_gmat_rows_fail_against_independent_references(field, delta):
    """GMAT itself is checked: a 1 mm state or 1 mg mass error fails GMAT vs DOP853 or
    GMAT vs the mass law, so a bad reference cannot vouch for the simulator."""
    name = "m2_prograde_burn"
    mission = BY_NAME[name]
    scenario, predicted, arcs, rows = _labelled(name)

    def bump(r):
        return dataclasses.replace(r, **{field: getattr(r, field) + delta})

    rows = [bump(r) if 100 <= i < 102 else r for i, r in enumerate(rows)]
    labelled, _ = gmat_m2.label_rows(rows, arcs)
    ref = m2.dop853_reference(
        scenario, *m2.expected_initial_state(scenario), predicted, sorted(labelled)
    )
    events = run_scenario(scenario).events
    metrics = gmat_m2.o9_metrics(scenario, predicted, events, labelled, ref)
    limits = _limits(name)
    failed = [k for k, x in metrics.items() if k in limits and not x <= limits[k]]
    assert any(k.startswith("gmat_") for k in failed)  # GMAT vs an independent reference
    del mission


# ------------------------------------------------------------------ simulator mutants vs GMAT


def _mutant_failures(name, monkeypatch, apply):
    """Gate failures, plus coverage violations (e.g. a burn boundary at the wrong time)."""
    apply(monkeypatch)
    result = _compare(name)
    if result.violations:
        assert all("!=" in v or "expected" in v or "differ" in v for v in result.violations)
        return ["coverage", *result.violations]
    return _failures(name, result.metrics)


def test_thrust_scale_mutant_fails_o9(monkeypatch):
    original = simulator_module.thrust_acceleration
    failures = _mutant_failures(
        "m2_prograde_burn",
        monkeypatch,
        lambda mp: mp.setattr(
            simulator_module, "thrust_acceleration", lambda *a: original(*a) * (1 + 1e-5)
        ),
    )
    assert "ours_vs_gmat_final_position_error_m" in failures


def test_wrong_g0_mutant_fails_o9_mass(monkeypatch):
    failures = _mutant_failures(
        "m2_prograde_burn",
        monkeypatch,
        lambda mp: mp.setattr(propulsion_module, "STANDARD_GRAVITY", 9.81),
    )
    assert "ours_vs_gmat_mass_error_max_kg" in failures


def test_frozen_pointing_mutant_fails_o9(monkeypatch):
    held = {}

    def frozen(self, t, r, v):
        held.setdefault("u", np.array(v) / np.linalg.norm(v))
        return held["u"]

    failures = _mutant_failures(
        "m2_prograde_burn", monkeypatch, lambda mp: mp.setattr(Prograde, "direction", frozen)
    )
    assert "ours_vs_gmat_final_position_error_m" in failures


def test_swapped_direction_mutant_fails_o9(monkeypatch):
    laws = dict(simulator_module.DIRECTION_LAWS)
    laws["retrograde"] = laws["prograde"]
    failures = _mutant_failures(
        "m2_retrograde_burn",
        monkeypatch,
        lambda mp: mp.setattr(simulator_module, "DIRECTION_LAWS", laws),
    )
    assert "ours_vs_gmat_burn_boundary_position_error_max_m" in failures


def test_cutoff_timing_mutant_fails_o9(monkeypatch):
    original = simulator_module.plan_burn

    def late(engine, propellant, ignition, duration, *a, **k):
        return original(engine, propellant, ignition, duration * (1 + 1e-9), *a, **k)

    failures = _mutant_failures(
        "m2_prograde_burn", monkeypatch, lambda mp: mp.setattr(simulator_module, "plan_burn", late)
    )
    assert {"ours_vs_gmat_mass_error_max_kg", "coverage"} & set(failures)


# ------------------------------------------------------------------ workflow


def test_run_refuses_to_replace_a_committed_reference():
    proc = subprocess.run(
        [sys.executable, str(CLI), "run", "--gmat-console", sys.executable, "--gmat-version", "x"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2 and "--replace-reason" in proc.stderr


def test_cli_refuses_missions_without_a_reference():
    proc = subprocess.run(
        [sys.executable, str(CLI), "compare", "--missions", "m2_burn_to_depletion"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2


@pytest.mark.slow
@pytest.mark.skipif(
    not GMAT_CONSOLE.exists(), reason="GMAT R2026a not installed (CI never runs GMAT)"
)
@pytest.mark.parametrize("name", gmat_m2.GMAT_MISSIONS)
def test_gmat_reproduces_the_committed_report(tmp_path, name):
    """Authenticated reproduction (review F10): the executable must be the approved GMAT
    (pinned sha256) and must report success; its report must equal the committed bytes.
    This is independent reproducibility evidence for the committed reference; by itself
    it cannot prove the historical origin of stored bytes."""
    assert gmat_m2.is_approved_console(GMAT_CONSOLE), "installed GmatConsole is not approved"
    files = gmat_m2.reference_files(name)
    report = tmp_path / "report.txt"
    script = tmp_path / "case.script"
    script.write_text(files["script"].read_text().replace(f"'{name}_report.txt'", f"'{report}'"))
    proc = subprocess.run(
        [str(GMAT_CONSOLE), "--run", str(script)],
        cwd=GMAT_CONSOLE.parent,
        capture_output=True,
        text=True,
    )
    log = proc.stdout + proc.stderr
    assert proc.returncode == 0 and gmat_m2.CONSOLE_SUCCESS in log
    assert "Execution Failed" not in log
    assert report.read_bytes() == files["report"].read_bytes()


def test_unapproved_executables_are_not_authenticated(tmp_path):
    fake = tmp_path / "GmatConsole"
    fake.write_text(
        "#!/bin/sh\necho '*** GMAT Integration test (Console version) successful! ***'\n"
    )
    assert not gmat_m2.is_approved_console(fake)
    assert not gmat_m2.is_approved_console(sys.executable)


# ------------------------------------------------------------------ review M2-T6 fixes


def _cli():
    import importlib.util

    spec = importlib.util.spec_from_file_location("gmat_m2_cli", CLI)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_refs(tmp_path):
    dst = tmp_path / "m2"
    shutil.copytree(gmat_m2.reference_dir(), dst)
    return dst


def _rehash(dst, name, manifest=True):
    """Make metadata (and optionally the approved manifest, digests and latest history
    record) consistent with edited files."""
    import hashlib

    files = gmat_m2.reference_files(name, dst)
    meta = json.loads(files["metadata"].read_text())
    for key in ("script", "report", "console"):
        meta[f"{key}_sha256"] = hashlib.sha256(files[key].read_bytes()).hexdigest()
    files["metadata"].write_text(json.dumps(meta))
    if manifest:
        man = json.loads((dst / "APPROVED_DIGESTS.json").read_text())
        entry = {k: meta[k] for k in ("script_sha256", "report_sha256", "console_sha256")}
        entry["metadata_sha256"] = hashlib.sha256(files["metadata"].read_bytes()).hexdigest()
        man["references"][name] = entry
        latest = [h for h in man["history"] if h["mission"] == name][-1]
        latest["report_sha256"] = meta["report_sha256"]
        _rechain(man["history"])
        (dst / "APPROVED_DIGESTS.json").write_text(json.dumps(man))


def test_run_validates_a_staged_reference_and_replaces_nothing_on_failure(tmp_path, monkeypatch):
    """F1: a numerically bad GMAT output is rejected before anything is committed."""
    name = "m2_prograde_burn"
    dst = _copy_refs(tmp_path)
    before = {p.name: p.read_bytes() for p in dst.iterdir()}
    bad = tmp_path / "bad_report.txt"
    lines = gmat_m2.reference_files(name)["report"].read_text().splitlines()
    fields = lines[400].split()
    fields[2] = repr(float(fields[2]) + 1e-3)  # +1 m in x (km)
    lines[400] = " ".join(fields)
    bad.write_text("\n".join(lines) + "\n")
    console = tmp_path / "GmatConsole"
    console.write_text(
        "#!/bin/sh\n"
        'out=$(sed -n "s/^GMAT S.Filename = \'\\(.*\\)\';$/\\1/p" "$2")\n'
        f"cp '{bad}' \"$out\"\n"
        "echo '*** GMAT Integration test (Console version) successful! ***'\n"
    )
    console.chmod(0o755)
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    cli = _cli()
    args = ["run", "--missions", name, "--gmat-console", str(console)]
    code = cli.main([*args, "--gmat-version", "R2026a", "--replace-reason", "test"])
    assert code == 1
    assert {p.name: p.read_bytes() for p in dst.iterdir()} == before


def test_numerical_gates_apply_to_a_consistent_but_wrong_reference(tmp_path, monkeypatch):
    """F1: the evaluation used by run and compare applies the numerical O9 gates."""
    name = "m2_prograde_burn"
    dst = _copy_refs(tmp_path)
    report = dst / f"{name}_report.txt"
    lines = report.read_text().splitlines()
    fields = lines[400].split()
    fields[2] = repr(float(fields[2]) + 1e-3)
    lines[400] = " ".join(fields)
    report.write_text("\n".join(lines) + "\n")
    _rehash(dst, name)
    rejected, check = _cli()._evaluate(name, base=dst)
    assert rejected == [] and check is not None and not check.passed


@pytest.mark.parametrize("edit", ["move", "duplicate", "drop"])
def test_state_assignments_must_stay_in_place_once(tmp_path, monkeypatch, edit):
    """F2: moving, duplicating or dropping an initial-state assignment is rejected."""
    name = "m2_prograde_burn"
    dst = _copy_refs(tmp_path)
    script = dst / f"{name}.script"
    lines = script.read_text().splitlines()
    state = [
        ln
        for ln in lines
        if ln.startswith("GMAT Sat.") and ln.split()[1][4:] in gmat_m2._STATE_KEYS
    ]
    if edit == "move":
        lines = [ln for ln in lines if ln not in state] + state
    elif edit == "duplicate":
        lines.append(state[0])
    else:
        lines.remove(state[0])
    script.write_text("\n".join(lines) + "\n")
    _rehash(dst, name)
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    assert _compare(name).violations


@pytest.mark.parametrize(
    "change", ["drop_fields", "failed_console", "other_binary", "unapproved_digest"]
)
def test_provenance_is_required(tmp_path, monkeypatch, change):
    """F3: provenance fields, the approved binary, a successful bound console log and the
    approved-digest manifest are all required."""
    name = "m2_retrograde_burn"
    dst = _copy_refs(tmp_path)
    files = gmat_m2.reference_files(name, dst)
    if change == "drop_fields":
        meta = json.loads(files["metadata"].read_text())
        keep = ("scenario_hash", "constants", "script_sha256", "report_sha256")
        files["metadata"].write_text(json.dumps({k: meta[k] for k in keep}))
    elif change == "failed_console":
        files["console"].write_text("Execution Failed: not GMAT\n")
        _rehash(dst, name)
    elif change == "other_binary":
        meta = json.loads(files["metadata"].read_text())
        meta["gmat_console_sha256"] = "0" * 64
        files["metadata"].write_text(json.dumps(meta))
    else:
        lines = files["report"].read_text().splitlines()
        files["report"].write_text("\n".join(lines) + "\n\n")  # same rows, new digest
        _rehash(dst, name, manifest=False)
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    assert _compare(name).violations


def test_fabricated_reference_needs_a_manifest_change(tmp_path, monkeypatch):
    """F3: DOP853 rows passed off as GMAT are numerically consistent; the reviewed
    manifest (and the reproduction test, where GMAT exists) are what reject them."""
    name = "m2_prograde_burn"
    dst = _copy_refs(tmp_path)
    scenario, predicted, arcs, rows = _labelled(name)
    labelled, _ = gmat_m2.label_rows(rows, arcs)
    ref = m2.dop853_reference(
        scenario, *m2.expected_initial_state(scenario), predicted, sorted(labelled)
    )
    veh = m2.vehicle(scenario)
    out = []
    for t, row in sorted(labelled.items()):
        y = ref[t]
        mass = gmat_m2._expected_mass(t, veh, predicted)
        vals = [row.arc, row.a1mjd, *(y[:3] / 1e3), *(y[3:6] / 1e3), mass]
        out.append(" ".join(repr(float(x)) for x in vals))
    (dst / f"{name}_report.txt").write_text("\n".join(out) + "\n")
    _rehash(dst, name, manifest=False)
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    violations = _compare(name).violations
    assert violations and all("manifest" in v or "history" in v for v in violations)


def test_generate_never_writes_into_the_references(tmp_path, monkeypatch):
    """F4: generate writes previews only; run guards every existing artifact."""
    cli = _cli()
    assert cli.main(["generate", "--out", str(gmat_m2.reference_dir())]) == 2
    out = tmp_path / "preview"
    assert cli.main(["generate", "--out", str(out), "--missions", "m2_prograde_burn"]) == 0
    assert (out / "m2_prograde_burn.script").exists()
    dst = tmp_path / "m2"
    dst.mkdir()
    shutil.copy(gmat_m2.reference_files("m2_prograde_burn")["script"], dst)  # script only
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    code = cli.main(
        [
            "run",
            "--missions",
            "m2_prograde_burn",
            "--gmat-console",
            sys.executable,
            "--gmat-version",
            "x",
        ]
    )
    assert code == 2


@pytest.mark.parametrize("drop", ["StateSampled", "BurnEnded", "PropulsionSampled"])
def test_missing_observations_are_not_vacuous_passes(drop):
    """F5: O9 requires every expected observation, from the scenario."""
    name = "m2_prograde_burn"
    run = run_scenario(BY_NAME[name].build())
    keep_first = drop == "PropulsionSampled"
    events, seen = [], False
    for e in run.events:
        if e.type == drop and (not keep_first or seen):
            continue
        seen = seen or e.type == drop
        events.append(e)
    assert any(
        "expected" in v or "differ" in v or "!=" in v for v in _compare(name, events).violations
    )


def test_standalone_compare_fails_closed_without_thresholds(tmp_path, monkeypatch):
    """F6: missing O9 limits reject the comparison instead of passing it."""
    from tars.validation.thresholds import ScopedThresholds

    data = json.loads(M2_THRESHOLDS.read_text())
    del data["limits"]["o9_gmat"]["all"]["coast_vs_kepler_position_error_max_m"]
    cli = _cli()
    monkeypatch.setattr(
        cli, "load_scoped_thresholds", lambda **_: ScopedThresholds("provisional", data["limits"])
    )
    rejected, check = cli._evaluate("m2_prograde_burn")
    assert check is None and any("without a threshold" in r for r in rejected)


def _event_edit(events, kind, **update):
    first = next(i for i, e in enumerate(events) if kind(e))
    return [e.model_copy(update=update) if i == first else e for i, e in enumerate(events)]


ROW_CASES = {
    "step_spacing_error_max_s": ("a1mjd", 300, 1.0 / 86400.0),
    "burn_duration_from_mass_error_max_s": ("mass_kg", 88, -1e-6),  # burn-end row, 677.3 s
    "coast_vs_kepler_position_error_max_m": ("r", 300, 1e-3),
    "coast_vs_kepler_velocity_error_max_mps": ("v", 300, 1e-6),
    "gmat_vs_dop853_position_error_max_m": ("r", 500, 1e-3),
    "gmat_vs_dop853_velocity_error_max_mps": ("v", 500, 1e-6),
    "gmat_vs_dop853_final_position_error_m": ("r", -1, 1e-3),
    "gmat_mass_vs_analytic_error_max_kg": ("mass_kg", 500, 1e-6),
}


def _at(kind, tick=None):
    return lambda e: e.type == kind and (tick is None or e.tick == tick)


_FAR = [1e7, 0.0, 0.0]
_FAST = [1e4, 0.0, 0.0]
EVENT_CASES = {
    "ours_vs_gmat_sample_position_error_max_m": (_at("StateSampled", 600), {"r": _FAR}),
    "ours_vs_gmat_sample_velocity_error_max_mps": (_at("StateSampled", 600), {"v": _FAST}),
    "ours_vs_gmat_burn_boundary_position_error_max_m": (_at("BurnEnded"), {"r": tuple(_FAR)}),
    "ours_vs_gmat_burn_boundary_velocity_error_max_mps": (_at("BurnEnded"), {"v": tuple(_FAST)}),
    "ours_vs_gmat_final_position_error_m": (_at("SimulationCompleted"), {"r": _FAR}),
    "ours_vs_gmat_final_velocity_error_mps": (_at("SimulationCompleted"), {"v": _FAST}),
    "ours_vs_gmat_mass_error_max_kg": (_at("PropulsionSampled", 64), {"total_mass_kg": 1290.0}),
    "ours_vs_gmat_node_crossing_error_max_s": (_at("OrbitCompleted"), {"crossing_t": 5000.0}),
}


def test_every_o9_metric_has_a_targeted_test():
    """F7: each gated O9 metric is exercised by its own corruption below."""
    assert set(ROW_CASES) | set(EVENT_CASES) == set(LIMITS["all"])


@pytest.mark.parametrize("metric", sorted(ROW_CASES))
def test_each_reference_metric_fails_on_its_corruption(metric):
    name = "m2_prograde_burn"
    scenario, predicted, arcs, rows = _labelled(name)
    field, index, delta = ROW_CASES[metric]
    index = index % len(rows)
    rows = [
        dataclasses.replace(r, **{field: getattr(r, field) + delta}) if i == index else r
        for i, r in enumerate(rows)
    ]
    labelled, _ = gmat_m2.label_rows(rows, arcs)
    metrics = gmat_m2.alignment_metrics(
        labelled, arcs, predicted, scenario.constants.mu, m2.vehicle(scenario).mass_flow_kgps
    )
    ref = m2.dop853_reference(
        scenario, *m2.expected_initial_state(scenario), predicted, sorted(labelled)
    )
    metrics |= gmat_m2.o9_metrics(scenario, predicted, run_scenario(scenario).events, labelled, ref)
    assert metrics[metric] > _limits(name)[metric]


@pytest.mark.parametrize("metric", sorted(EVENT_CASES))
def test_each_simulator_metric_fails_on_its_corruption(metric):
    name = "m2_prograde_burn"
    kind, update = EVENT_CASES[metric]
    events = _event_edit(run_scenario(BY_NAME[name].build()).events, kind, **update)
    scenario, predicted, arcs, rows = _labelled(name)
    labelled, _ = gmat_m2.label_rows(rows, arcs)
    ref = m2.dop853_reference(
        scenario, *m2.expected_initial_state(scenario), predicted, sorted(labelled)
    )
    metrics = gmat_m2.o9_metrics(scenario, predicted, events, labelled, ref)
    assert metrics[metric] > _limits(name)[metric]


def test_split_script_requires_each_state_component_exactly_once():
    """F2 defense in depth: the position-preserving comparison also rejects these."""
    script = gmat_m2.reference_files("m2_prograde_burn")["script"].read_text()
    x_line = next(ln for ln in script.splitlines() if ln.startswith("GMAT Sat.X = "))
    with pytest.raises(ValueError, match="more than once"):
        gmat_m2.split_script(script + x_line + "\n")
    with pytest.raises(ValueError, match="incomplete"):
        gmat_m2.split_script(script.replace(x_line + "\n", ""))


# ------------------------------------------------------------------ re-verification fixes


@pytest.mark.parametrize("change", ["metadata", "host", "history"])
def test_metadata_and_history_are_bound_to_the_manifest(tmp_path, monkeypatch, change):
    """F8: changed metadata, or this reference's latest history record disagreeing with
    its metadata, is rejected."""
    name = "m2_prograde_burn"
    dst = _copy_refs(tmp_path)
    files = gmat_m2.reference_files(name, dst)
    if change == "metadata":
        meta = json.loads(files["metadata"].read_text())
        meta["tars_git_revision"] = "1" * 40
        files["metadata"].write_text(json.dumps(meta))
    elif change == "host":  # a field only the manifest's metadata digest binds
        meta = json.loads(files["metadata"].read_text())
        meta["host_platform"] = "invented"
        files["metadata"].write_text(json.dumps(meta))
    else:
        man = json.loads((dst / "APPROVED_DIGESTS.json").read_text())
        mine = [h for h in man["history"] if h["mission"] == name][-1]
        mine["report_sha256"] = "0" * 64
        (dst / "APPROVED_DIGESTS.json").write_text(json.dumps(man))
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    violations = _compare(name).violations
    assert violations
    if change == "history":
        # The history check fires; the manifest anchor (F32) rejects the edit too.
        assert any("history" in v for v in violations)
        assert all("history" in v or "manifest" in v for v in violations)
    if change == "host":
        assert violations == ["reference digests are not in the approved manifest"]


def _staged_copy(tmp_path, name):
    """A complete, valid new generation of the reference (new timestamp) in a stage."""
    import hashlib

    stage = _copy_refs(tmp_path / "stage")
    files = gmat_m2.reference_files(name, stage)
    meta = json.loads(files["metadata"].read_text())
    meta["generated_utc"] = "2026-10-12T00:00:00+00:00"
    files["metadata"].write_text(json.dumps(meta, indent=2) + "\n")
    man = json.loads((stage / "APPROVED_DIGESTS.json").read_text())
    man["references"][name]["metadata_sha256"] = hashlib.sha256(
        files["metadata"].read_bytes()
    ).hexdigest()
    man["history"].append(
        {
            "mission": name,
            "generated_utc": meta["generated_utc"],
            "tars_git_revision": meta["tars_git_revision"],
            "reason": meta["replace_reason"] or "initial reference",
            "report_sha256": meta["report_sha256"],
            "previous_record_sha256": gmat_m2.record_digest(man["history"][-1]),
        }
    )
    (stage / "APPROVED_DIGESTS.json").write_text(json.dumps(man, indent=2) + "\n")
    return stage, files, man


@pytest.mark.parametrize("fail_at", range(7))
def test_interrupted_publication_never_leaves_an_accepted_mix(tmp_path, monkeypatch, fail_at):
    """F9: interrupt publication at every step; the result is the old reference intact,
    the new one complete, or rejected -- never an accepted partial replacement."""
    name = "m2_prograde_burn"
    live = _copy_refs(tmp_path / "live")
    old = {p.name: p.read_bytes() for p in live.iterdir()}
    stage, staged_files, manifest = _staged_copy(tmp_path, name)
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: live)
    cli = _cli()
    calls = {"n": 0}
    original = cli._atomic_write

    def flaky(dst, data):
        if calls["n"] == fail_at:
            raise OSError("interrupted")
        calls["n"] += 1
        original(dst, data)

    monkeypatch.setattr(cli, "_atomic_write", flaky)
    try:
        cli._publish(name, staged_files, stage / "APPROVED_DIGESTS.json", manifest)
        interrupted = False
    except OSError:
        interrupted = True
    now = {p.name: p.read_bytes() for p in live.iterdir() if not p.name.startswith(".")}
    violations = _compare(name).violations
    if not interrupted:
        # A complete new generation is accepted only after a reviewed change pins its
        # manifest digest (F32): until then the anchor alone rejects it.
        assert len(violations) == 1 and "manifest is not the approved one" in violations[0]
    elif now == old:
        assert violations == []  # nothing changed
    else:
        assert violations  # any partial state is rejected
    if interrupted and fail_at >= 1:
        # Withdraw-first: approval is gone as soon as publication starts (defense in
        # depth beyond the metadata digest binding).
        man = json.loads((live / "APPROVED_DIGESTS.json").read_text())
        assert name not in man["references"]


def test_generate_refuses_symlinks_into_the_references(tmp_path):
    """F11: a preview path that is a symlink is never written through."""
    cli = _cli()
    out = tmp_path / "preview"
    out.mkdir()
    target = tmp_path / "victim.script"
    target.write_text("committed")
    (out / "m2_prograde_burn.script").symlink_to(target)
    assert cli.main(["generate", "--out", str(out), "--missions", "m2_prograde_burn"]) == 2
    assert target.read_text() == "committed"


@pytest.mark.parametrize(
    "update",
    [{"thrust_acceleration_mps2": (1.0, 1.0, 1.0)}, {"delta_v_sensed_mps": 1000.0}],
)
def test_standalone_evaluation_applies_the_audit_gates(monkeypatch, update):
    """F12: numerical T5 audit failures reject the standalone comparison."""
    from tars.sim import runner as runner_module

    cli = _cli()
    original = runner_module.run_scenario

    def corrupted(scenario, *a, **k):
        run = original(scenario, *a, **k)
        i = next(
            i for i, e in enumerate(run.events) if e.type == "PropulsionSampled" and e.tick == 64
        )
        run.events[i] = run.events[i].model_copy(update=update)
        return run

    monkeypatch.setattr(cli, "run_scenario", corrupted)
    rejected, check = cli._evaluate("m2_prograde_burn")
    assert check is None and any("simulator audit" in r for r in rejected)


def test_coverage_uses_the_same_tick_report_rule():
    """F13: a burn submitted and ignited at 600 s is reported at tick 61. Observed to a
    600 s horizon (the log truncated at tick 60), no BurnStarted is expected; to 610 s it
    is. A valid scenario cannot stop at its own submission tick, so the 600 s horizon is
    exercised at the function level."""
    from tars.sim.scenario import ScenarioV2
    from tars.validation.m2 import predict_burns

    mission = BY_NAME["m2_burn_to_depletion"]
    raw = mission.build().model_dump(mode="json")
    raw["stop"] = {"duration_s": 610.0}
    raw["commands"] = raw["commands"][:1]
    scenario = ScenarioV2.model_validate(raw)
    events = run_scenario(scenario).events
    predicted = predict_burns(scenario, mission.expected[:1])
    started = next(e for e in events if e.type == "BurnStarted")
    assert (started.tick, started.event_t_s) == (61, 600.0)
    full = gmat_m2.coverage_problems(scenario, predicted, events, {}, 610.0)
    assert not any("burn boundaries" in p for p in full)
    cut = [e for e in events if e.tick <= 60]
    early = gmat_m2.coverage_problems(scenario, predicted, cut, {}, 600.0)
    assert not any("burn boundaries" in p for p in early)


# ------------------------------------------------------------------ re-verification 2 fixes


def _with_history(tmp_path, monkeypatch, edit):
    dst = _copy_refs(tmp_path)
    path = dst / "APPROVED_DIGESTS.json"
    man = json.loads(path.read_text())
    edit(man["history"])
    path.write_text(json.dumps(man))
    monkeypatch.setattr(gmat_m2, "reference_dir", lambda: dst)
    return _compare("m2_prograde_burn").violations


def _rechain(history):
    previous = None
    for h in history:
        h["previous_record_sha256"] = previous
        previous = gmat_m2.record_digest(h)


def _then_rechain(edit):
    """Apply an edit and re-chain, so only the value check under test can catch it."""

    def run(history):
        edit(history)
        _rechain(history)

    return run


@pytest.mark.parametrize(
    "edit",
    [
        _then_rechain(lambda h: h[0].update(generated_utc="1900-01-01T00:00:00+00:00")),
        _then_rechain(lambda h: h[0].update(tars_git_revision="0" * 40)),
        _then_rechain(lambda h: h[0].update(reason=None)),
        _then_rechain(lambda h: h[0].update(report_sha256="not-a-digest")),
        _then_rechain(lambda h: h.append({**h[-1], "mission": "invented"})),
        _then_rechain(lambda h: h.__setitem__(slice(0, 2), [h[1], h[0]])),  # latest kept
        lambda h: h.__delitem__(slice(0, 3)),  # deletion without re-chaining: chain breaks
        lambda h: h[0].update(reason="edited"),  # any unchained edit: chain breaks
    ],
    ids=["old-timestamp", "zero-revision", "null-reason", "bad-digest", "unknown-mission",
         "reordered", "deleted", "edited"],
)  # fmt: skip
def test_every_history_record_is_validated(tmp_path, monkeypatch, edit):
    """F14: each value rule, chronology, and the chain itself reject their case."""
    assert _with_history(tmp_path, monkeypatch, edit)


def test_wholesale_history_rewrite_is_rejected_by_the_anchor(tmp_path, monkeypatch):
    """F32: deleting records AND consistently re-chaining the rest (formerly the
    documented limit, F14) is rejected by the manifest digest pinned in reviewed
    source."""

    def rewrite(history):
        del history[:3]
        _rechain(history)

    violations = _with_history(tmp_path, monkeypatch, rewrite)
    assert violations and all("manifest is not the approved one" in v for v in violations)


@pytest.mark.parametrize("bad", ["1e999", "-1.0", "NaN", '"0.6"'])
def test_threshold_loaders_reject_non_finite_or_negative_limits(tmp_path, bad):
    """F15: an overflowing, negative, NaN or non-numeric limit cannot disable a gate."""
    from tars.validation.thresholds import M1_THRESHOLDS, load_scoped_thresholds, load_thresholds

    text = M2_THRESHOLDS.read_text().replace(
        '"gmat_vs_dop853_position_error_max_m": 3e-05',
        f'"gmat_vs_dop853_position_error_max_m": {bad}',
    )
    assert text != M2_THRESHOLDS.read_text()
    path = tmp_path / "m2.json"
    path.write_text(text)
    with pytest.raises(ValueError, match="threshold"):
        load_scoped_thresholds(path, missions=frozenset(BY_NAME), authenticate=False)
    m1 = M1_THRESHOLDS.read_text().replace(
        '"position_error_max_m": 0.6', f'"position_error_max_m": {bad}', 1
    )
    path1 = tmp_path / "m1.json"
    path1.write_text(m1)
    with pytest.raises(ValueError, match="threshold"):
        load_thresholds(path1, authenticate=False)


def test_committed_thresholds_load():
    from tars.validation.thresholds import load_scoped_thresholds, load_thresholds

    assert load_thresholds().status == "approved"
    assert load_scoped_thresholds(missions=frozenset(BY_NAME)).status == "provisional"


# ------------------------------------------------------------------ re-verification 3 fixes


def test_worst_never_discards_nan():
    """F16: builtin max(x, nan) returns x; worst() fails instead."""
    assert max(0.1, math.nan) == 0.1  # the hazard
    assert m2.worst(0.1, math.nan) == math.inf
    assert m2.worst(math.nan, 0.1) == math.inf
    assert m2.worst(0.1, 0.2) == 0.2


def _nan_reference(monkeypatch, at=650.0):
    original = m2.dop853_reference

    def poisoned(*a, **k):
        ref = original(*a, **k)
        if at in ref:
            ref[at] = np.full_like(ref[at], math.nan)
        return ref

    monkeypatch.setattr(m2, "dop853_reference", poisoned)


def test_nan_reference_state_fails_o9(monkeypatch):
    """F16: an invalid intermediate GMAT-vs-DOP853 reference state fails O9."""
    _nan_reference(monkeypatch)
    result = _compare("m2_prograde_burn")
    assert result.metrics["gmat_vs_dop853_position_error_max_m"] == math.inf
    assert "gmat_vs_dop853_position_error_max_m" in _failures("m2_prograde_burn", result.metrics)


def test_nan_reference_state_fails_o4(monkeypatch):
    """F16 (T5 correction): the same hazard in O4 fails every O4 metric."""
    mission = BY_NAME["m2_prograde_burn"]
    scenario = mission.build()
    events = run_scenario(scenario).events
    _nan_reference(monkeypatch, at=660.0)
    metrics, _ = m2.reference_metrics(
        scenario, events, m2.predict_burns(scenario, mission.expected)
    )
    assert all(v == math.inf for v in metrics.values())


def test_nan_reference_state_fails_the_integrated_proof(monkeypatch):
    """F16: through m2_proof's mission checks, the poisoned reference fails gates."""
    import importlib.util

    from tars.validation.thresholds import load_scoped_thresholds

    spec = importlib.util.spec_from_file_location(
        "m2_proof", REPO_ROOT / "toolbox" / "validators" / "m2_proof.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _nan_reference(monkeypatch)
    gates = module.Gates(load_scoped_thresholds(missions=frozenset(BY_NAME)))
    checks, _ = module.mission_checks(BY_NAME["m2_prograde_burn"], gates, quick=True)
    failed = {c.validator for c in checks if not c.passed}
    assert "o9_gmat[m2_prograde_burn]" in failed and "o4_reference[m2_prograde_burn]" in failed


def test_dop853_reference_rejects_non_finite_integration(monkeypatch):
    """F16: the reference never hands on a non-finite state."""
    import scipy.integrate

    original = scipy.integrate.solve_ivp

    def broken(*a, **k):
        sol = original(*a, **k)
        sol.y[:, -1] = math.nan
        return sol

    monkeypatch.setattr(scipy.integrate, "solve_ivp", broken)
    scenario = BY_NAME["m2_prograde_burn"].build()
    with pytest.raises(RuntimeError, match="non-finite"):
        m2.dop853_reference(scenario, *m2.expected_initial_state(scenario), [], [600.0])


def test_threshold_loaders_reject_object_limits(tmp_path):
    """F17: an object where a limit belongs is rejected at load, not a later crash."""
    from tars.validation.thresholds import M1_THRESHOLDS, load_scoped_thresholds, load_thresholds

    m2_text = M2_THRESHOLDS.read_text().replace(
        '"gmat_vs_dop853_position_error_max_m": 3e-05', '"gmat_vs_dop853_position_error_max_m": {}'
    )
    (tmp_path / "m2.json").write_text(m2_text)
    with pytest.raises(ValueError, match="not a number"):
        load_scoped_thresholds(
            tmp_path / "m2.json", missions=frozenset(BY_NAME), authenticate=False
        )
    m1_text = M1_THRESHOLDS.read_text().replace(
        '"position_error_max_m": 0.6', '"position_error_max_m": {}', 1
    )
    (tmp_path / "m1.json").write_text(m1_text)
    with pytest.raises(ValueError, match="not a number"):
        load_thresholds(tmp_path / "m1.json", authenticate=False)


def test_nan_in_an_unreduced_reference_component_fails_o9(monkeypatch):
    """F16: every reference component must be finite, including the propellant entry
    that no O9 reduction reads."""
    original = m2.dop853_reference

    def poisoned(*a, **k):
        ref = original(*a, **k)
        ref[650.0] = ref[650.0].copy()
        ref[650.0][6] = math.nan
        return ref

    monkeypatch.setattr(m2, "dop853_reference", poisoned)
    result = _compare("m2_prograde_burn")
    assert result.metrics["gmat_vs_dop853_position_error_max_m"] == math.inf


def test_threshold_loaders_reject_a_wrong_structure(tmp_path):
    """F17: a value where a group or scope object belongs is rejected at load."""
    from tars.validation.thresholds import M1_THRESHOLDS, load_scoped_thresholds, load_thresholds

    data = json.loads(M2_THRESHOLDS.read_text())
    data["limits"]["o9_gmat"]["all"] = 5
    (tmp_path / "m2.json").write_text(json.dumps(data))
    with pytest.raises(ValueError, match="must be an object"):
        load_scoped_thresholds(
            tmp_path / "m2.json", missions=frozenset(BY_NAME), authenticate=False
        )
    data1 = json.loads(M1_THRESHOLDS.read_text())
    data1["limits"]["kepler_reference"] = 5
    (tmp_path / "m1.json").write_text(json.dumps(data1))
    with pytest.raises(ValueError, match="must be an object"):
        load_thresholds(tmp_path / "m1.json", authenticate=False)


# ------------------------------------------------------------------ re-verification 4 fixes


def test_worst_of_never_discards_nan():
    assert m2.worst_of([0.1, math.nan, 0.2]) == math.inf
    assert m2.worst_of([math.nan]) == math.inf
    assert m2.worst_of([], default=0.0) == 0.0
    assert m2.worst_of([0.3, 0.1]) == 0.3
    assert max([0.1, math.nan]) == 0.1  # the builtin hazard it replaces


def test_dense_output_must_be_finite(monkeypatch):
    """F18: non-finite dense-output altitudes are rejected at the source."""
    import scipy.integrate

    original = scipy.integrate.solve_ivp

    def poisoned(*a, **k):
        sol = original(*a, **k)
        dense = sol.sol

        class Bad:
            def __call__(self, t):
                out = dense(t)
                out[0, :] = math.nan
                return out

        sol.sol = Bad()
        return sol

    monkeypatch.setattr(scipy.integrate, "solve_ivp", poisoned)
    scenario = BY_NAME["m2_prograde_burn"].build()
    with pytest.raises(RuntimeError, match="dense output"):
        m2.dop853_reference(scenario, *m2.expected_initial_state(scenario), [], [600.0])


def _proof_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "m2_proof", REPO_ROOT / "toolbox" / "validators" / "m2_proof.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_merging_auxiliary_audits_keeps_nan(monkeypatch):
    """F19: a NaN metric in any auxiliary run survives merging as a failure."""
    module = _proof_module()
    good = m2.Audit({}, {"o4_reference": {"sample_position_error_max_m": 0.1}}, {})
    bad = m2.Audit({}, {"o4_reference": {"sample_position_error_max_m": math.nan}}, {})
    for order in ([good, bad], [bad, good]):
        merged = module._merge_audits([(f"r{i}", a) for i, a in enumerate(order)])
        assert merged.metrics["o4_reference"]["sample_position_error_max_m"] == math.inf


@pytest.mark.slow
@pytest.mark.parametrize("bad", [math.nan, -math.inf])
def test_nan_in_an_auxiliary_audit_fails_the_mission(monkeypatch, bad):
    """F19/F20 integrated: NaN or -inf O4/O5 metrics in the dt = 2.5 s auxiliary audit
    fail the mission."""
    from tars.validation.thresholds import load_scoped_thresholds

    module = _proof_module()
    original = m2.audit_run

    def poisoned(scenario, expected, run):
        audit = original(scenario, expected, run)
        if scenario.dt_s == 2.5:
            audit.metrics["o4_reference"]["sample_position_error_max_m"] = bad
            audit.metrics["o5_coast_kepler"]["coast_position_error_max_m"] = bad
        return audit

    monkeypatch.setattr(m2, "audit_run", poisoned)
    gates = module.Gates(load_scoped_thresholds(missions=frozenset(BY_NAME)))
    checks, _ = module.mission_checks(BY_NAME["m2_burn_to_depletion"], gates, quick=False)
    failed = {c.validator for c in checks if not c.passed}
    assert {
        "o4_reference[m2_burn_to_depletion/o8_aux]",
        "o5_coast_kepler[m2_burn_to_depletion/o8_aux]",
    } <= failed


_GUARDED = (
    "src/tars/validation/m2.py",
    "src/tars/validation/gmat_m2.py",
    "toolbox/validators/m2_proof.py",
    "toolbox/scripts/gmat_m2.py",
    "src/tars/validation/thresholds.py",
)
_REDUCERS = {
    "max", "min", "nanmax", "nanmin", "amax", "amin", "fmax", "fmin", "maximum", "minimum",
}  # fmt: skip
_UFUNC_METHODS = {"reduce", "accumulate", "reduceat", "outer", "at"}
# Every max/min-style call in the validators, reviewed (review M2-T6 F21). Anything else
# fails this test: metric accumulators must use worst/worst_of, which never drop
# non-finite values.
_ALLOWED = {
    ("m2.py", "predict_burns", "min(mdot * executed, propellant)"): "scenario inputs",
    ("m2.py", "worst", "max(values)"): "after its own finiteness check",
    ("m2.py", "simpson_bound", "min(until, burn.cutoff_t_s)"): "predicted times",
    ("m2.py", "excess_over", "max(err - allowance, 0.0)"):
        "both arguments verified finite first (F23: max(err - inf, 0.0) would hide errors)",
    ("m2.py", "dop853_reference", "max(marks)"): "scenario and sample times",
    ("m2.py", "dop853_reference", "alts.min()"): "after the dense-output finiteness check",
    ("m2.py", "dop853_reference", "alts.max()"): "after the dense-output finiteness check",
    (
        "m2.py",
        "_timing_bound",
        "max(b.propellant_before_kg - veh.mass_flow_kgps * max(b.executed_s, b.intended_s), 0.0)",
    ): "predicted values",
    ("m2.py", "_timing_bound", "max(b.executed_s, b.intended_s)"): "predicted values",
    ("m2.py", "orbit_checks", "min(alts)"): "schema-valid event values (round-trip check)",
    ("m2.py", "_check_dense_consistency", "np.maximum(np.abs(terminal), 1.0)"):
        "elementwise tolerance floor on values already validated finite",
    ("m2.py", "orbit_checks", "max(alts)"): "schema-valid event values (round-trip check)",
    ("gmat_m2.py", "plan_arcs", "min(b.cutoff_t_s, horizon_s)"): "predicted times",
    ("gmat_m2.py", "plan_arcs", "min(BURN_STEP_S, b - a)"): "predicted times",
    ("gmat_m2.py", "cmd_compare", "max(status, 2)"): "exit codes",
    ("gmat_m2.py", "cmd_compare", "max(status, 1)"): "exit codes",
}  # fmt: skip


def _reducer_calls(source: str, filename: str) -> set[tuple[str, str, str]]:
    import ast

    found: set[tuple[str, str, str]] = set()
    stack: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        def visit_Call(self, node):
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
            # np.maximum.reduce(...) and friends: the reducer is the ufunc (F24).
            if name in _UFUNC_METHODS and isinstance(fn, ast.Attribute):
                inner = fn.value
                name = getattr(inner, "attr", getattr(inner, "id", None))
            if name in _REDUCERS:
                found.add((filename, stack[-1] if stack else "<module>", ast.unparse(node)))
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            # `from numpy import fmax as reducer`: importing a reducer at all (F27).
            for alias in node.names:
                if alias.name in _REDUCERS:
                    found.add(
                        (filename, stack[-1] if stack else "<module>", f"import {alias.name}")
                    )
            self.generic_visit(node)

        def visit_Assign(self, node):
            # `reducer = np.fmax` / `reducer = max`: binding a reducer to a name (F27).
            value = node.value
            name = value.id if isinstance(value, ast.Name) else getattr(value, "attr", None)
            if name in _REDUCERS:
                found.add((filename, stack[-1] if stack else "<module>", f"bind {name}"))
            self.generic_visit(node)

    Visitor().visit(ast.parse(source))
    return found


def test_every_max_min_call_in_the_validators_is_reviewed():
    """F21: an AST scan, not a regex. A new max/min-style call fails until reviewed."""
    found = set()
    for rel in _GUARDED:
        path = REPO_ROOT / rel
        found |= _reducer_calls(path.read_text(), path.name)
    assert found == set(_ALLOWED)


@pytest.mark.parametrize(
    "snippet",
    [
        "dst[k] = max(dst.get(k, -math.inf), x)",
        "out['k'] = max(x, out['k'])",
        "e = max(abs(p) for p in orders)",
        "e = np.nanmax(errors)",
        "e = errors.max()",
        "e = np.maximum.reduce(errors)",
        "e = np.minimum.reduce(errors)",
        "e = np.fmax.reduce([dst.get(k, -math.inf), x])",
        "e = np.fmin.reduce(errors)",
        "e = np.maximum(a, b)",
        "from numpy import fmax as reducer",
        "reducer = np.fmax",
        "reducer = max",
    ],
)
def test_the_guard_detects_common_unsafe_forms(snippet):
    """F21: the guard flags the original F19 expression and other common forms."""
    source = f"def merged(dst, k, x, out, orders, errors, np, math, a, b):\n    {snippet}\n"
    assert _reducer_calls(source, "m2_proof.py")


def test_non_finite_gated_metrics_fail_every_check():
    """F20: NaN, +inf and -inf all fail, even below an upper limit."""
    from tars.validation.thresholds import Check

    for bad in (math.nan, math.inf, -math.inf):
        check = Check("x", {"m": bad}, {"m": 1.0}, "provisional")
        assert not check.passed and "not finite" in check.failures[0]
    assert Check("x", {"m": 0.5}, {"m": 1.0}, "provisional").passed


def test_worst_rejects_negative_infinity():
    assert m2.worst(0.1, -math.inf) == math.inf
    assert m2.worst_of([0.1, -math.inf]) == math.inf


def test_merging_keeps_negative_infinity_as_failure():
    """F20: a -inf auxiliary metric cannot vanish in the merge."""
    module = _proof_module()
    good = m2.Audit({}, {"o4_reference": {"sample_position_error_max_m": 0.1}}, {})
    bad = m2.Audit({}, {"o4_reference": {"sample_position_error_max_m": -math.inf}}, {})
    for order in ([good, bad], [bad, good]):
        merged = module._merge_audits([(f"r{i}", a) for i, a in enumerate(order)])
        assert merged.metrics["o4_reference"]["sample_position_error_max_m"] == math.inf


def test_o9_rejects_a_negative_infinity_metric(monkeypatch):
    """F20 standalone: an O9 metric poisoned with -inf fails evaluation."""
    cli = _cli()
    original = gmat_m2.o9_metrics

    def poisoned(*a, **k):
        out = original(*a, **k)
        out["ours_vs_gmat_sample_position_error_max_m"] = -math.inf
        return out

    monkeypatch.setattr(gmat_m2, "o9_metrics", poisoned)
    rejected, check = cli._evaluate("m2_prograde_burn")
    # Rejected outright (non-finite metric) or failed by Check: never a pass.
    assert any("not finite" in r for r in rejected) or (check is not None and not check.passed)
    assert check is None or not check.passed


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_node_bisection_rejects_non_finite_oracle_output(monkeypatch, bad):
    """F22: a non-finite Kepler value inside node bisection fails both O9 and T5."""
    from tars.astro import kepler

    original = kepler.propagate
    calls = {"n": 0}

    def poisoned(r, v, dt, mu):
        calls["n"] += 1
        rr, vv = original(r, v, dt, mu)
        if calls["n"] % 80 == 0:  # the last bisection step of each crossing
            rr = np.array([rr[0], rr[1], bad])
        return rr, vv

    name = "m2_prograde_burn"
    mission = BY_NAME[name]
    scenario = mission.build()
    events = run_scenario(scenario).events
    _, predicted, arcs, rows = _labelled(name)
    labelled, _ = gmat_m2.label_rows(rows, arcs)
    monkeypatch.setattr(kepler, "propagate", poisoned)
    states = {t: (labelled[t].r, labelled[t].v) for t in sorted(labelled)}
    assert math.inf in gmat_m2._node_crossings(states, scenario.constants.mu)
    calls["n"] = 0
    ref = m2.dop853_reference(
        scenario, *m2.expected_initial_state(scenario), predicted, sorted(labelled)
    )
    metrics, _ = m2.orbit_checks(scenario, events, ref, predicted)
    assert metrics["node_crossing_time_error_max_s"] == math.inf


@pytest.mark.slow
def test_poisoned_node_oracle_fails_the_integrated_mission(monkeypatch):
    """F22/F25 integrated: poison only the final bisection step of each crossing, in
    both validators (counted per caller). Without the finiteness checks the result
    moves by ~60/2^80 s and passes; with them both node metrics are +inf."""
    import inspect

    from tars.astro import kepler
    from tars.validation.thresholds import load_scoped_thresholds

    module = _proof_module()
    original = kepler.propagate
    counts: dict[str, int] = {}

    def poisoned(r, v, dt, mu):
        rr, vv = original(r, v, dt, mu)
        stack = inspect.stack()
        caller = stack[1].function
        if caller == "kepler_state":  # validated wrapper (F36): look one frame up
            caller = stack[2].function
        if caller in ("orbit_checks", "_node_crossings"):
            counts[caller] = counts.get(caller, 0) + 1
            if counts[caller] % 80 == 0:  # the last of the 80 bisection steps
                rr = np.array([rr[0], rr[1], math.nan])
        return rr, vv

    monkeypatch.setattr(kepler, "propagate", poisoned)
    gates = module.Gates(load_scoped_thresholds(missions=frozenset(BY_NAME)))
    checks, _ = module.mission_checks(BY_NAME["m2_prograde_burn"], gates, quick=True)
    by_name = {c.validator: c for c in checks}
    assert (
        by_name["orbit_events[m2_prograde_burn]"].metrics["node_crossing_time_error_max_s"]
        == math.inf
    )
    assert (
        by_name["o9_gmat[m2_prograde_burn]"].metrics["ours_vs_gmat_node_crossing_error_max_s"]
        == math.inf
    )


# ------------------------------------------------------------------ re-verification 6 fixes


def test_excess_over_rejects_non_finite_inputs():
    """F23: max(err - inf, 0.0) == 0.0 would hide any error."""
    assert max(1.0 - math.inf, 0.0) == 0.0  # the hazard
    for err, allowance in ((1.0, math.inf), (1.0, math.nan), (math.nan, 0.0), (math.inf, 1.0)):
        assert m2.excess_over(err, allowance) == math.inf
    assert m2.excess_over(1.0, 0.25) == 0.75
    assert m2.excess_over(0.1, 0.25) == 0.0


def _inflate_sensed_delta_v(run):
    """+1e-6 m/s on the burn's sensed delta-v, everywhere it is reported."""
    end = next(e for e in run.events if e.type == "BurnEnded")
    bump = 1e-6
    run.events[:] = [
        e.model_copy(update={"sensed_delta_v_mps": e.sensed_delta_v_mps + bump})
        if e is end
        else e.model_copy(update={"delta_v_sensed_mps": e.delta_v_sensed_mps + bump})
        if e.type == "PropulsionSampled" and e.tick >= end.tick
        else e
        for e in run.events
    ]


@pytest.mark.parametrize("bound", ["normal", "infinite"])
def test_infinite_simpson_allowance_cannot_hide_an_error(monkeypatch, bound):
    """F23 standalone: the 1e-6 m/s error fails with the normal allowance and with an
    infinite one."""
    if bound == "infinite":
        monkeypatch.setattr(m2, "simpson_bound", lambda *a, **k: math.inf)
    mission = BY_NAME["m2_prograde_burn"]
    scenario = mission.build()
    run = run_scenario(scenario)
    _inflate_sensed_delta_v(run)
    predicted = m2.predict_burns(scenario, mission.expected)
    _, o2, _ = m2.mass_and_rocket_metrics(scenario, run.events, predicted)
    samples, _ = m2.propulsion_sample_checks(scenario, run.events, predicted)
    limit = json.loads(M2_THRESHOLDS.read_text())["limits"]["o2_rocket_equation"]["all"]
    assert (
        o2["sensed_delta_v_excess_over_simpson_rel_max"]
        > limit["sensed_delta_v_excess_over_simpson_rel_max"]
    )
    assert samples["sample_delta_v_excess_over_simpson_rel_max"] > 1e-12


@pytest.mark.slow
def test_infinite_simpson_allowance_fails_the_integrated_mission(monkeypatch):
    """F23 integrated: the full mission path rejects it too."""
    from tars.validation.thresholds import load_scoped_thresholds

    module = _proof_module()
    monkeypatch.setattr(m2, "simpson_bound", lambda *a, **k: math.inf)
    original = module.run_scenario

    def inflated(scenario, *a, **k):
        run = original(scenario, *a, **k)
        if scenario.name == "m2_prograde_burn":
            _inflate_sensed_delta_v(run)
        return run

    monkeypatch.setattr(module, "run_scenario", inflated)
    gates = module.Gates(load_scoped_thresholds(missions=frozenset(BY_NAME)))
    checks, _ = module.mission_checks(BY_NAME["m2_prograde_burn"], gates, quick=True)
    failed = {c.validator for c in checks if not c.passed}
    assert "o2_rocket_equation[m2_prograde_burn]" in failed


def test_report_only_metrics_must_be_finite():
    """Non-finite report-only metrics are flagged, although they are not gated."""
    from tars.validation.thresholds import load_scoped_thresholds

    module = _proof_module()
    gates = module.Gates(load_scoped_thresholds(missions=frozenset(BY_NAME)))
    gates.check(
        "o9_gmat",
        "o9",
        "m2_prograde_burn",
        {**dict.fromkeys(LIMITS["all"], 0.0), "gmat_rows": math.nan},
    )
    assert gates.non_finite_report_only == ["o9: gmat_rows=nan"]


# ------------------------------------------------------------------ re-verification 7 fixes


def _with_residual(run, kg=1e-10):
    """A bookkeeping-consistent extra residual after the depletion burn."""
    end = next(e for e in run.events if e.type == "BurnEnded")

    def more_mass(e, **extra):
        return e.model_copy(
            update={
                "propellant_kg": e.propellant_kg + kg,
                "total_mass_kg": e.total_mass_kg + kg,
                **extra,
            }
        )

    out = []
    for e in run.events:
        if e is end:
            e = more_mass(e, propellant_used_kg=e.propellant_used_kg - kg)
        elif e.type == "PropellantDepleted":
            e = e.model_copy(update={"residual_propellant_kg": e.residual_propellant_kg + kg})
        elif e.type == "PropulsionSampled" and e.tick >= end.tick:
            e = more_mass(e)
        out.append(e)
    run.events[:] = out


@pytest.mark.parametrize("ulp", [None, math.inf, -math.inf, 0.0])
def test_depletion_ratio_needs_a_finite_positive_bound(monkeypatch, ulp):
    """F26: with the normal bound the extra residual fails; an infinite, negative or
    zero bound cannot turn it into a pass."""
    if ulp is not None:
        monkeypatch.setattr(m2, "_ulp", lambda x: ulp)
    mission = BY_NAME["m2_burn_to_depletion"]
    scenario = mission.build()
    run = run_scenario(scenario)
    _with_residual(run)
    o1, _, _ = m2.mass_and_rocket_metrics(
        scenario, run.events, m2.predict_burns(scenario, mission.expected)
    )
    assert o1["depletion_residual_over_bound_max"] > 1.0


@pytest.mark.slow
def test_infinite_depletion_bound_fails_the_integrated_mission(monkeypatch):
    """F26 integrated."""
    from tars.validation.thresholds import load_scoped_thresholds

    module = _proof_module()
    monkeypatch.setattr(m2, "_ulp", lambda x: math.inf)
    original = module.run_scenario

    def with_residual(scenario, *a, **k):
        run = original(scenario, *a, **k)
        if scenario.name == "m2_burn_to_depletion":
            _with_residual(run)
        return run

    monkeypatch.setattr(module, "run_scenario", with_residual)
    gates = module.Gates(load_scoped_thresholds(missions=frozenset(BY_NAME)))
    checks, _ = module.mission_checks(BY_NAME["m2_burn_to_depletion"], gates, quick=True)
    failed = {c.validator for c in checks if not c.passed}
    assert "o1_mass_law[m2_burn_to_depletion]" in failed


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_standalone_evaluation_rejects_non_finite_report_only_audit_metrics(monkeypatch, bad):
    """F28: report-only T5 audit metrics must be finite in standalone O9 too."""
    cli = _cli()
    original = m2.audit_run

    def poisoned(scenario, expected, run):
        audit = original(scenario, expected, run)
        audit.metrics["o2_rocket_equation"]["sensed_delta_v_rel_error_max"] = bad
        return audit

    monkeypatch.setattr(m2, "audit_run", poisoned)
    rejected, check = cli._evaluate("m2_prograde_burn")
    assert check is None and any("non-finite metrics" in r for r in rejected)


@pytest.mark.slow
def test_report_only_finiteness_is_a_terminal_proof_check(monkeypatch, tmp_path):
    """F28: the terminal report_only_metrics_finite check is wired into m2_proof.main."""
    module = _proof_module()
    original = m2.audit_run

    def poisoned(scenario, expected, run):
        audit = original(scenario, expected, run)
        if "o2_rocket_equation" in audit.metrics:
            audit.metrics["o2_rocket_equation"]["sensed_delta_v_rel_error_max"] = math.nan
        return audit

    monkeypatch.setattr(m2, "audit_run", poisoned)
    out = tmp_path / "m2.json"
    assert module.main(["--quick", "--out", str(out)]) == 1
    results = {r["validator"]: r for r in json.loads(out.read_text())["results"]}
    assert not results["report_only_metrics_finite"]["passed"]


def test_threshold_files_are_authenticated(tmp_path, monkeypatch):
    """F33: finite but inflated limits (1e100) are rejected by the pinned digest, by
    default, wherever the file is read from."""
    from tars.validation import thresholds as thresholds_module
    from tars.validation.thresholds import M1_THRESHOLDS, load_scoped_thresholds, load_thresholds

    inflated = tmp_path / "m2.json"
    inflated.write_text(
        M2_THRESHOLDS.read_text().replace(
            '"final_position_error_m": 0.6', '"final_position_error_m": 1e100'
        )
    )
    with pytest.raises(ValueError, match="not the approved file"):
        load_scoped_thresholds(inflated, missions=frozenset(BY_NAME))
    m1 = tmp_path / "m1.json"
    m1.write_text(
        M1_THRESHOLDS.read_text().replace(
            '"position_error_max_m": 0.6', '"position_error_max_m": 1e100', 1
        )
    )
    with pytest.raises(ValueError, match="not the approved file"):
        load_thresholds(m1)
    # Redirecting the default path does not help: the content is authenticated.
    content = inflated.read_bytes()
    monkeypatch.setattr(thresholds_module.Path, "read_bytes", lambda self: content)
    with pytest.raises(ValueError, match="not the approved file"):
        load_scoped_thresholds(missions=frozenset(BY_NAME))


@pytest.mark.slow
def test_inflated_thresholds_cannot_pass_wrong_physics(monkeypatch, tmp_path):
    """F33 integrated: the thrust x (1 + 1e-5) mutant fails O9; with an inflated
    threshold file the evaluation is rejected instead of passing."""
    from tars.validation import thresholds as thresholds_module

    original = simulator_module.thrust_acceleration
    monkeypatch.setattr(
        simulator_module, "thrust_acceleration", lambda *a: original(*a) * (1 + 1e-5)
    )
    cli = _cli()
    _, check = cli._evaluate("m2_prograde_burn")
    assert check is None or not check.passed
    data = json.loads(M2_THRESHOLDS.read_text())
    for group in data["limits"].values():
        for scope in group.values():
            for k in scope:
                scope[k] = 1e100
    inflated = tmp_path / "m2.json"
    inflated.write_text(json.dumps(data))
    monkeypatch.setattr(thresholds_module, "M2_THRESHOLDS", inflated)
    monkeypatch.setattr(
        cli,
        "load_scoped_thresholds",
        lambda **kw: thresholds_module.load_scoped_thresholds(inflated, **kw),
    )
    with pytest.raises(ValueError, match="not the approved file"):
        cli._evaluate("m2_prograde_burn")


def test_pinned_digests_match_the_committed_files():
    import hashlib

    from tars.validation.approved_digests import (
        APPROVED_GMAT_M2_MANIFEST_SHA256,
        APPROVED_THRESHOLD_SHA256,
    )
    from tars.validation.thresholds import M1_THRESHOLDS

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    assert digest(M1_THRESHOLDS) == APPROVED_THRESHOLD_SHA256["m1"]
    assert digest(M2_THRESHOLDS) == APPROVED_THRESHOLD_SHA256["m2"]
    assert digest(gmat_m2.approved_manifest_path()) == APPROVED_GMAT_M2_MANIFEST_SHA256


@pytest.mark.parametrize("component", [3, 4, 5, 6])
@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_dense_output_state_is_validated_completely(monkeypatch, component, bad):
    """F29: velocity and propellant components of the dense output are checked too."""
    import scipy.integrate

    original = scipy.integrate.solve_ivp

    def poisoned(*a, **k):
        sol = original(*a, **k)
        dense = sol.sol

        class Bad:
            def __call__(self, t):
                out = dense(t)
                out[component, :] = bad
                return out

        sol.sol = Bad()
        return sol

    monkeypatch.setattr(scipy.integrate, "solve_ivp", poisoned)
    scenario = BY_NAME["m2_prograde_burn"].build()
    with pytest.raises(RuntimeError, match="DOP853"):
        m2.dop853_reference(scenario, *m2.expected_initial_state(scenario), [], [600.0])


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_gmat_coast_alignment_checks_kepler_velocity(monkeypatch, bad):
    """F30: an invalid Kepler velocity in the coast alignment fails, even though only
    the position is compared."""
    from tars.astro import kepler

    original = kepler.propagate

    def poisoned(r, v, dt, mu):
        rr, vv = original(r, v, dt, mu)
        return rr, np.array([vv[0], vv[1], bad])

    scenario, predicted, arcs, rows = _labelled("m2_prograde_burn")
    labelled, _ = gmat_m2.label_rows(rows, arcs)
    monkeypatch.setattr(kepler, "propagate", poisoned)
    metrics = gmat_m2.alignment_metrics(
        labelled, arcs, predicted, scenario.constants.mu, m2.vehicle(scenario).mass_flow_kgps
    )
    assert metrics["coast_vs_kepler_position_error_max_m"] == math.inf


@pytest.mark.parametrize("value", [-1.0, 299.0])
def test_reference_propellant_must_follow_the_mass_law(monkeypatch, value):
    """F31: a negative or off-law reference propellant is rejected at the source."""
    import scipy.integrate

    original = scipy.integrate.solve_ivp

    def poisoned(*a, **k):
        sol = original(*a, **k)
        sol.y[6, -1] = value
        return sol

    monkeypatch.setattr(scipy.integrate, "solve_ivp", poisoned)
    scenario = BY_NAME["m2_prograde_burn"].build()
    with pytest.raises(RuntimeError, match="propellant"):
        m2.dop853_reference(scenario, *m2.expected_initial_state(scenario), [], [600.0])


# ------------------------------------------------------------------ re-verification 9 fixes


def test_nan_solver_time_cannot_hide_off_law_propellant(monkeypatch):
    """F34: a NaN solver time with off-law propellant is rejected."""
    import scipy.integrate

    original = scipy.integrate.solve_ivp

    def poisoned(*a, **k):
        sol = original(*a, **k)
        sol.t = sol.t.copy()
        sol.t[-1] = math.nan
        sol.y[6, -1] = 299.0
        return sol

    monkeypatch.setattr(scipy.integrate, "solve_ivp", poisoned)
    scenario = BY_NAME["m2_prograde_burn"].build()
    predicted = m2.predict_burns(scenario, BY_NAME["m2_prograde_burn"].expected)
    with pytest.raises(RuntimeError, match=r"time|propellant"):
        m2.dop853_reference(scenario, *m2.expected_initial_state(scenario), predicted, [720.0])


def test_reference_mass_law_check_is_nan_safe():
    """F34: the mass-law comparison rejects NaN times directly, too. With a predicted
    burn, a NaN time makes the expectation NaN, so `err > tol` would be False."""
    mission = BY_NAME["m2_prograde_burn"]
    scenario = mission.build()
    veh = m2.vehicle(scenario)
    predicted = m2.predict_burns(scenario, mission.expected)
    assert math.isnan(m2.mass_law_propellant(math.nan, veh, predicted))  # the hazard
    states = np.zeros((7, 1))
    states[6, 0] = 299.0
    with pytest.raises(RuntimeError):
        m2._check_reference_states([math.nan], states, veh, predicted, "probe")


@pytest.mark.parametrize("corruption", ["zero_velocity", "terminal_mismatch"])
def test_dense_output_must_be_self_consistent(monkeypatch, corruption):
    """F35: finite but wrong dense velocities, or a dense state that disagrees with the
    terminal state, are rejected."""
    import scipy.integrate

    original = scipy.integrate.solve_ivp

    def poisoned(*a, **k):
        sol = original(*a, **k)
        dense = sol.sol

        class Bad:
            def __call__(self, t):
                out = dense(t)
                if corruption == "zero_velocity":
                    out[3:6, :] = 0.0
                else:
                    out[0, :] += 1.0  # positions shifted 1 m everywhere
                return out

        sol.sol = Bad()
        return sol

    monkeypatch.setattr(scipy.integrate, "solve_ivp", poisoned)
    scenario = BY_NAME["m2_prograde_burn"].build()
    with pytest.raises(RuntimeError, match="dense"):
        m2.dop853_reference(scenario, *m2.expected_initial_state(scenario), [], [600.0])


def test_kepler_outputs_must_conserve_two_body_invariants(monkeypatch):
    """F36: a finite but physically wrong Kepler output (zero velocity) is rejected by
    the invariant check, and GMAT coast alignment compares velocity too."""
    from tars.astro import kepler

    scenario, predicted, arcs, rows = _labelled("m2_prograde_burn")
    labelled, _ = gmat_m2.label_rows(rows, arcs)
    r0, v0 = labelled[0.0].r, labelled[0.0].v
    r, v = m2.kepler_state(r0, v0, 60.0, scenario.constants.mu)
    assert np.all(np.isfinite(r)) and np.all(np.isfinite(v))
    original = kepler.propagate
    monkeypatch.setattr(kepler, "propagate", lambda *a: (original(*a)[0], np.zeros(3)))
    r, v = m2.kepler_state(r0, v0, 60.0, scenario.constants.mu)
    assert np.all(r == math.inf) and np.all(v == math.inf)
    metrics = gmat_m2.alignment_metrics(
        labelled, arcs, predicted, scenario.constants.mu, m2.vehicle(scenario).mass_flow_kgps
    )
    assert metrics["coast_vs_kepler_velocity_error_max_mps"] == math.inf


def test_gmat_coast_velocity_is_gated():
    """F36: a GMAT coast row with a 1e-6 m/s velocity error fails the coast velocity gate."""
    scenario, predicted, arcs, rows = _labelled("m2_prograde_burn")
    rows = [dataclasses.replace(r, v=r.v + 1e-6) if i == 300 else r for i, r in enumerate(rows)]
    labelled, _ = gmat_m2.label_rows(rows, arcs)
    metrics = gmat_m2.alignment_metrics(
        labelled, arcs, predicted, scenario.constants.mu, m2.vehicle(scenario).mass_flow_kgps
    )
    assert (
        metrics["coast_vs_kepler_velocity_error_max_mps"]
        > LIMITS["all"]["coast_vs_kepler_velocity_error_max_mps"]
    )
