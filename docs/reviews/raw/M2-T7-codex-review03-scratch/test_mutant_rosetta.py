"""M2 cross-platform final-state gate (DR-0023 decision 4): boundaries, perturbations,
missing platforms, mismatched inputs, malformed evidence, the committed golden and the
archived three-platform evidence."""

from __future__ import annotations

import copy
import importlib.util
import json
import math

import numpy as np
import pytest

import sys
_spec = importlib.util.spec_from_file_location("mutant_rosetta", '/private/tmp/claude-501/-Users-guillermomartin--superset-worktrees-tars-actually-splash-f90f9ba4/70aaf0ee-578a-4f8e-b31a-278306be87a9/scratchpad/t7-snap3/review_scratch/mutant_rosetta.py')
xp = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = xp
_spec.loader.exec_module(xp)
from tars.validation.m2_missions import MISSIONS
from tars.validation.thresholds import REPO_ROOT, Check, load_scoped_thresholds

REV = "a" * 40
INPUTS = xp.canonical_inputs()
LOCK = "b" * 64
# A realistic final state (m, m/s); every platform starts from it.
R0 = [6.123456789e6, -2.987654321e6, 1.234567e5]
V0 = [3.21e3, 6.54e3, -1.2e1]
PLATFORMS = {
    "macos-x86_64": ("Darwin", "x86_64", "Intel(R) Core(TM) i9-9880H CPU @ 2.30GHz", None),
    "linux-x86_64": ("Linux", "x86_64", "AMD EPYC 7763 64-Core Processor", "X64"),
    "macos-arm64": ("Darwin", "arm64", "Apple M1 (Virtual)", "ARM64"),
}
LIMITS = load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS)).for_validator(
    "cross_platform"
)
ARCHIVE = REPO_ROOT / "proof" / "records" / "evidence" / "M2-T7" / "cross-platform"


def sign(record: dict) -> dict:
    record["sha256"] = xp.record_digest(record)
    return record


def record(pid: str, r=R0, v=V0, run_id: str | None = "42") -> dict:
    system, machine, cpu, arch = PLATFORMS[pid]
    ci = None
    if arch is not None:
        ci = {"github_run_id": run_id, "github_run_attempt": "1", "github_sha": REV,
              "github_job": "check", "runner_os": system, "runner_arch": arch}  # fmt: skip
    return sign(
        {
            "schema": xp.SCHEMA,
            "revision": REV,
            "tree_clean": True,
            "platform": {
                "id": pid,
                "system": system,
                "machine": machine,
                "cpu": cpu,
                "translated": False,
            },
            "environment": {"python": "3.12.8", "uv_lock_sha256": LOCK},
            "ci": ci,
            "inputs": dict(INPUTS),
            "missions": {
                name: {
                    "status": "success",
                    "final_tick": 5370,
                    "final_t": 53700.0,
                    "r": list(r),
                    "v": list(v),
                    "events_sha256": "c" * 64,
                }
                for name in INPUTS
            },
        }
    )


def three(**overrides: dict) -> list[tuple[str, dict]]:
    return [(pid, overrides.get(pid.replace("-", "_")) or record(pid)) for pid in PLATFORMS]


def verdict(records, **kwargs) -> tuple[bool, xp.Comparison]:
    kwargs.setdefault("revision", REV)
    result = xp.gate(records, expected_inputs=INPUTS, **kwargs)
    passed = Check("m2_cross_platform", result.metrics, LIMITS, "approved").passed
    return passed and not result.violations, result


# ------------------------------------------------------------------ approved limits


def test_gate_uses_the_approved_m1_bounds():
    assert LIMITS == {xp.POSITION: 1e-4, xp.VELOCITY: 1e-7}


def test_identical_evidence_from_three_platforms_passes():
    ok, result = verdict(three())
    assert ok and result.metrics == {xp.POSITION: 0.0, xp.VELOCITY: 0.0}
    assert len(result.pairs) == 3 * len(INPUTS)  # every pair of platforms, every mission


# ------------------------------------------------------------------ boundaries


@pytest.mark.parametrize(("key", "limit"), [("r", 1e-4), ("v", 1e-7)])
def test_threshold_boundary_is_inclusive_and_the_next_float_fails(key, limit):
    zero = [0.0, 0.0, 0.0]
    for value, expect in ((limit, True), (np.nextafter(limit, 1.0), False)):
        moved = [float(value), 0.0, 0.0]
        a = record("macos-arm64", r=zero if key == "r" else R0, v=zero if key == "v" else V0)
        b = record("linux-x86_64", r=moved if key == "r" else R0, v=moved if key == "v" else V0)
        c = record("macos-x86_64", r=zero if key == "r" else R0, v=zero if key == "v" else V0)
        ok, result = verdict([("a", a), ("b", b), ("c", c)])
        metric = xp.POSITION if key == "r" else xp.VELOCITY
        assert result.metrics[metric] == float(value)
        assert ok is expect


@pytest.mark.parametrize(
    ("key", "axis", "delta", "passes"),
    [
        ("r", 0, 5e-5, True), ("r", 2, 2e-4, False), ("r", 1, 1.5e-4, False),
        ("v", 1, 5e-8, True), ("v", 0, 2e-7, False),
    ],
)  # fmt: skip
def test_deliberate_perturbation_of_one_platform(key, axis, delta, passes):
    """A perturbation at realistic magnitudes, in one mission on one platform."""
    bad = record("macos-arm64")
    mission = "m2_retrograde_burn"
    bad["missions"][mission][key][axis] += delta
    sign(bad)
    ok, result = verdict(three(macos_arm64=bad))
    assert ok is passes
    metric = xp.POSITION if key == "r" else xp.VELOCITY
    assert result.metrics[metric] == pytest.approx(delta, rel=1e-4)  # coordinate ulp
    assert result.per_mission[mission][metric] == result.metrics[metric]
    assert result.per_mission["m2_prograde_burn"][metric] == 0.0


def test_euclidean_norm_not_largest_component():
    """0.8e-4 on two axes: each component passes, the Euclidean norm 1.13e-4 fails."""
    bad = record("linux-x86_64")
    for m in bad["missions"].values():
        m["r"][0] += 8e-5
        m["r"][1] += 8e-5
    ok, result = verdict(three(linux_x86_64=sign(bad)))
    assert not ok and result.metrics[xp.POSITION] == pytest.approx(math.hypot(8e-5, 8e-5), rel=1e-4)


def test_discrete_outcomes_must_agree_exactly():
    bad = record("macos-x86_64")
    bad["missions"]["m2_burn_to_depletion"]["final_tick"] = 5369
    bad["missions"]["m2_burn_to_depletion"]["final_t"] = 53690.0
    ok, result = verdict(three(macos_x86_64=sign(bad)))
    assert not ok
    assert any("final_tick" in v for v in result.violations)


# ------------------------------------------------------------------ completeness, identity


@pytest.mark.parametrize("missing", list(PLATFORMS))
def test_missing_required_platform_fails_closed(missing):
    records = [(pid, record(pid)) for pid in PLATFORMS if pid != missing]
    ok, result = verdict(records)
    assert not ok and math.isinf(result.metrics[xp.POSITION])
    assert any(missing in v for v in result.violations)


def test_two_records_of_one_platform_do_not_replace_a_missing_one():
    second = record("linux-x86_64", run_id="42")
    second["platform"]["cpu"] = "Intel(R) Xeon(R) Platinum 8573C"
    ok, result = verdict([*three()[:2], ("linux-2", sign(second))])
    assert not ok and any("macos-arm64" in v for v in result.violations)


def test_additional_record_of_a_required_platform_is_compared():
    extra = record("macos-x86_64", r=[R0[0] + 3e-5, R0[1], R0[2]], run_id="42")
    extra["platform"]["cpu"] = "Intel(R) Xeon(R) W-3245 (GitHub macos-15-intel)"
    extra["ci"] = {**record("linux-x86_64")["ci"], "runner_os": "macOS"}
    ok, result = verdict([*three(), ("macos-intel-ci", sign(extra))])
    assert ok and result.metrics[xp.POSITION] == pytest.approx(3e-5, rel=1e-4)


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda p: p.update(system="Linux", machine="aarch64", id="linux-aarch64"),
         "not a required platform"),
        (lambda p: p.update(id="macos-x86_64"), "not a required platform"),  # id mislabelled
        (lambda p: p.update(translated=True), "Rosetta"),
        (lambda p: p.update(cpu=""), "CPU model"),
        (lambda p: p.pop("translated"), "malformed platform"),
    ],
)  # fmt: skip
def test_platform_identity_is_validated(edit, message):
    bad = record("macos-arm64")
    edit(bad["platform"])
    ok, result = verdict(three(macos_arm64=sign(bad)))
    assert not ok and any(message in v for v in result.violations)


def test_runner_architecture_must_match_the_machine():
    bad = record("linux-x86_64")
    bad["ci"]["runner_arch"] = "ARM64"
    ok, result = verdict(three(linux_x86_64=sign(bad)))
    assert not ok and any("runner architecture" in v for v in result.violations)


# ------------------------------------------------------------------ revision, inputs, staleness


def test_records_from_another_revision_are_stale():
    old = record("linux-x86_64")
    old["revision"] = old["ci"]["github_sha"] = "d" * 40
    ok, result = verdict(three(linux_x86_64=sign(old)))
    assert not ok and any("stale: revision" in v for v in result.violations)


def test_ci_commit_must_equal_the_recorded_revision():
    bad = record("macos-arm64")
    bad["ci"]["github_sha"] = "e" * 40
    ok, result = verdict(three(macos_arm64=sign(bad)))
    assert not ok and any("CI commit" in v for v in result.violations)


def test_records_from_another_ci_run_are_rejected():
    other = record("macos-arm64", run_id="41")
    ok, result = verdict(three(macos_arm64=other), run_id="42")
    assert not ok and any("not produced by CI run 42" in v for v in result.violations)
    # The local reference-host record has no CI provenance: not acceptable for a CI run.
    ok, result = verdict(three(), run_id="42")
    expected = "macos-x86_64: not produced by CI run"
    assert not ok and any(v.startswith(expected) for v in result.violations)


def test_mismatched_inputs_fail():
    bad = record("linux-x86_64")
    bad["inputs"]["m2_prograde_burn"] = "f" * 64
    ok, result = verdict(three(linux_x86_64=sign(bad)))
    assert not ok and any("digest differs ['m2_prograde_burn']" in v for v in result.violations)


def test_evidence_for_a_changed_scenario_is_stale():
    """All three records agree with each other but not with the current checkout."""
    changed = dict(INPUTS, m2_retrograde_burn="0" * 64)
    result = xp.gate(three(), revision=REV, expected_inputs=changed)
    assert result.violations and all("stale or mismatched inputs" in v for v in result.violations)


@pytest.mark.parametrize("change", ["missing", "extra"])
def test_incomplete_or_extra_missions_fail(change):
    bad = record("macos-x86_64")
    if change == "missing":
        del bad["missions"]["m2_invalid_commands_no_propulsion"]
        del bad["inputs"]["m2_invalid_commands_no_propulsion"]
    else:
        bad["missions"]["m2_extra"] = bad["missions"]["m2_prograde_burn"]
        bad["inputs"]["m2_extra"] = "1" * 64
    ok, result = verdict(three(macos_x86_64=sign(bad)))
    assert not ok and any("incomplete mission set" in v for v in result.violations)


def test_different_locked_environments_fail():
    bad = record("macos-arm64")
    bad["environment"]["uv_lock_sha256"] = "9" * 64
    ok, result = verdict(three(macos_arm64=sign(bad)))
    assert not ok and any("locked environments" in v for v in result.violations)


# ------------------------------------------------------------------ malformed evidence


def _mission(r):
    return r["missions"]["m2_prograde_burn"]


@pytest.mark.parametrize(
    ("edit", "message", "resign"),
    [
        (lambda r: _mission(r)["r"].__setitem__(0, 1.0), "digest mismatch", False),
        (lambda r: r.update(schema="tars.m2.final-state-evidence/0"), "schema", True),
        (lambda r: r.update(tree_clean=False), "modified working tree", True),
        (lambda r: r.update(tree_clean="yes"), "modified working tree", True),
        (lambda r: r.update(revision="HEAD"), "not a git commit id", True),
        (lambda r: r.pop("environment"), "missing or unexpected", True),
        (lambda r: r.update(extra=1), "missing or unexpected", True),
        (lambda r: r.update(environment={}), "environment provenance", True),
        (lambda r: r.update(inputs=[]), "malformed inputs", True),
        (lambda r: r.update(missions={}), "incomplete mission set", True),
        (lambda r: _mission(r).update(r=[1.0, 2.0]), "3 finite numbers", True),
        (lambda r: _mission(r).update(v=[1.0, float("nan"), 0.0]), "3 finite numbers", True),
        (lambda r: _mission(r).update(r=[1.0, float("inf"), 0.0]), "3 finite numbers", True),
        (lambda r: _mission(r).update(r=["1", 2.0, 3.0]), "3 finite numbers", True),
        (lambda r: _mission(r).update(v=[True, 0.0, 0.0]), "3 finite numbers", True),
        (lambda r: _mission(r).update(final_tick=5370.0), "not an integer", True),
        (lambda r: _mission(r).update(final_tick=True), "not an integer", True),
        (lambda r: _mission(r).update(final_t=None), "final time", True),
        (lambda r: _mission(r).update(status="failure"), "run status", True),
        (lambda r: _mission(r).update(events_sha256=""), "event-log digest", True),
        (lambda r: _mission(r).pop("v"), "malformed final state", True),
        (lambda r: r.update(platform="macos-arm64"), "malformed platform", True),
        (lambda r: r.update(ci="run 42"), "malformed CI provenance", True),
    ],
)  # fmt: skip
def test_malformed_or_corrupted_evidence_fails_closed(edit, message, resign):
    bad = copy.deepcopy(record("macos-arm64"))
    edit(bad)
    if resign:
        sign(bad)
    ok, result = verdict(three(macos_arm64=bad))
    assert not ok and math.isinf(result.metrics[xp.POSITION])
    assert any(message in v for v in result.violations), result.violations


@pytest.mark.parametrize("value", [None, [], "unreadable: Expecting value", 3])
def test_non_object_evidence_fails_closed(value):
    ok, result = verdict([*three()[:2], ("bad", value)])
    assert not ok and any("not a JSON object" in v for v in result.violations)


def test_duplicate_records_are_rejected():
    ok, result = verdict([*three(), ("again", record("linux-x86_64"))])
    assert not ok and "duplicate evidence records" in result.violations


def test_no_evidence_fails_closed():
    ok, result = verdict([])
    assert not ok and result.violations


# ------------------------------------------------------------------ CLI


def _cli():
    spec = importlib.util.spec_from_file_location(
        "m2_cross_platform_cli", REPO_ROOT / "toolbox" / "validators" / "m2_cross_platform.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_gate_passes_and_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(xp, "canonical_inputs", lambda: INPUTS)
    cli = _cli()
    paths = []
    for pid, rec in three():
        path = tmp_path / f"{pid}.json"
        path.write_text(json.dumps(rec))
        paths.append(str(path))
    report = tmp_path / "gate.json"
    assert cli.main(["gate", *paths, "--revision", REV, "--report", str(report)]) == 0
    data = json.loads(report.read_text())
    assert data["passed"] and data["violations"] == []
    assert {c["validator"]: c["passed"] for c in data["checks"]} == {
        "m2_cross_platform": True, "m2_cross_platform_evidence": True
    }  # fmt: skip
    # Missing platform, corrupted file, wrong revision, other CI run: all exit 1.
    assert cli.main(["gate", *paths[:2], "--revision", REV]) == 1
    (tmp_path / "broken.json").write_text("{not json")
    assert cli.main(["gate", *paths[:2], str(tmp_path / "broken.json"), "--revision", REV]) == 1
    assert cli.main(["gate", *paths, "--revision", "d" * 40]) == 1
    assert cli.main(["gate", *paths, "--revision", REV, "--run-id", "43"]) == 1
    assert cli.main(["gate", *paths, "--revision", REV, "--report", str(report)]) == 0
    missing = tmp_path / "absent.json"
    assert cli.main(["gate", *paths[:2], str(missing), "--revision", REV]) == 1


# ------------------------------------------------------------------ real runs, golden


@pytest.mark.slow
def test_collect_produces_valid_evidence_for_this_platform():
    rec = xp.collect()
    problems = xp.record_problems(rec, label="local", expected_inputs=INPUTS, revision=None)
    # A test run may happen in a modified tree; nothing else may be wrong.
    assert [p for p in problems if "modified working tree" not in p] == []
    assert rec["platform"]["id"] in xp.REQUIRED_PLATFORMS
    assert rec["sha256"] == xp.record_digest(rec)


def test_golden_is_the_approved_reference_host_record():
    golden = xp.load_golden()
    assert xp.golden_problems(golden, INPUTS) == []
    assert golden["platform"]["id"] == xp.GOLDEN_PLATFORM and golden["ci"] is None


def test_golden_with_another_digest_is_rejected(tmp_path):
    path = tmp_path / "m2_final_states.json"
    data = json.loads(xp.GOLDEN_M2.read_text())
    data["missions"]["m2_prograde_burn"]["r"][0] += 1e-3
    path.write_text(json.dumps(sign(data), indent=2) + "\n")
    with pytest.raises(ValueError, match="not the approved golden"):
        xp.load_golden(path)


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda g: g["platform"].update(id="linux-x86_64", system="Linux"), "reference host"),
        (lambda g: g.update(ci={"github_sha": g["revision"], "runner_arch": "X64"}), "CI record"),
        (lambda g: g["inputs"].update(m2_prograde_burn="0" * 64), "stale or mismatched"),
    ],
)
def test_golden_problems(edit, message):
    golden = json.loads(xp.GOLDEN_M2.read_text())
    edit(golden)
    assert any(message in p for p in xp.golden_problems(sign(golden), INPUTS))


def test_run_compared_with_golden():
    from tars.sim.runner import run_scenario

    golden = xp.load_golden()
    mission = MISSIONS[0]
    scenario = mission.build()
    run = run_scenario(scenario)
    metrics, violations = xp.compare_with_golden(mission.name, scenario.config_hash(), run, golden)
    assert violations == []
    assert Check("x", metrics, LIMITS, "approved").passed
    # A stale input has no golden: +inf, fail closed.
    metrics, violations = xp.compare_with_golden(mission.name, "0" * 64, run, golden)
    assert violations and math.isinf(metrics[xp.POSITION])
    # A perturbed golden is detected.
    moved = copy.deepcopy(golden)
    moved["missions"][mission.name]["r"][0] += 2e-4
    metrics, _ = xp.compare_with_golden(mission.name, scenario.config_hash(), run, moved)
    assert not Check("x", metrics, LIMITS, "approved").passed


# ------------------------------------------------------------------ archived evidence


def test_archived_three_platform_evidence_passes_at_its_revision():
    """The committed evidence (retained beyond the CI artifact expiry) still passes the
    gate at its recorded revision and matches the current canonical inputs."""
    import hashlib

    manifest = json.loads((ARCHIVE / "MANIFEST.json").read_text())
    for name, digest in manifest["sha256"].items():
        assert hashlib.sha256((ARCHIVE / name).read_bytes()).hexdigest() == digest
    records = [(p, json.loads((ARCHIVE / p).read_text())) for p in manifest["records"]]
    assert {r["platform"]["id"] for _, r in records} == set(xp.REQUIRED_PLATFORMS)
    result = xp.gate(records, revision=manifest["revision"], expected_inputs=INPUTS)
    assert result.violations == []
    assert Check("x", result.metrics, LIMITS, "approved").passed
    assert result.metrics == pytest.approx(manifest["metrics"], rel=0, abs=0)
    # The golden is the archived reference-host record, byte for byte.
    assert (ARCHIVE / manifest["golden"]).read_bytes() == xp.GOLDEN_M2.read_bytes()


# ------------------------------------------------------------------ M2 Proof integration


def _proof():
    spec = importlib.util.spec_from_file_location(
        "m2_proof_xp", REPO_ROOT / "toolbox" / "validators" / "m2_proof.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _proof_checks(monkeypatch, load):
    monkeypatch.setattr(xp, "load_golden", load)
    proof = _proof()
    names = frozenset(m.name for m in MISSIONS)
    gates = proof.Gates(load_scoped_thresholds(missions=names))
    mission = next(m for m in MISSIONS if m.name == "m2_invalid_commands_no_propulsion")
    checks, _ = proof.mission_checks(mission, gates, quick=True)
    return gates, {c.validator: c for c in checks}


def test_proof_compares_every_mission_with_the_golden(monkeypatch):
    gates, checks = _proof_checks(monkeypatch, xp.load_golden)
    assert gates.golden_problems == []
    tag = "m2_invalid_commands_no_propulsion"
    assert checks[f"cross_platform_golden[{tag}]"].passed
    assert checks[f"cross_platform[{tag}]"].passed
    assert checks[f"cross_platform[{tag}]"].thresholds == LIMITS


@pytest.mark.parametrize("failure", ["missing", "digest", "stale", "perturbed"])
def test_proof_fails_closed_on_an_unusable_or_disagreeing_golden(monkeypatch, failure):
    good = xp.load_golden()
    tag = "m2_invalid_commands_no_propulsion"

    def load(path=xp.GOLDEN_M2):
        if failure == "missing":
            raise FileNotFoundError(path)
        if failure == "digest":
            raise ValueError("not the approved golden record")
        data = copy.deepcopy(good)
        if failure == "stale":
            data["inputs"][tag] = "0" * 64
        else:
            data["missions"][tag]["r"][2] += 1.5e-4
        return sign(data)

    gates, checks = _proof_checks(monkeypatch, load)
    assert not checks[f"cross_platform[{tag}]"].passed
    if failure == "perturbed":
        assert gates.golden_problems == []  # valid record, disagreeing final state
        assert checks[f"cross_platform[{tag}]"].metrics[xp.POSITION] == pytest.approx(1.5e-4)
    else:
        assert gates.golden_problems and gates.golden is None
        assert not checks[f"cross_platform_golden[{tag}]"].passed
