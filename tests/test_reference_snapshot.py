"""Approved reference snapshot (DR-0021 option A): ledger mechanics, authentication and
immutability, margins, and the coordinated-corruption regressions (F50, F51)."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

from tars.astro import kepler
from tars.sim.runner import run_scenario
from tars.validation import approved_digests, m2
from tars.validation import reference_snapshot as snap
from tars.validation.m2_missions import MISSIONS
from tars.validation.thresholds import M2_THRESHOLDS, REPO_ROOT

BY_NAME = {m.name: m for m in MISSIONS}
TOOL = REPO_ROOT / "toolbox" / "scripts" / "reference_snapshot.py"
CLI = REPO_ROOT / "toolbox" / "scripts" / "gmat_m2.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------------ ledger mechanics


def _artifact(tmp_path, monkeypatch, record):
    """Write a recorded session as an artifact and pin its digest (test-local)."""
    data = {
        "schema": snap.SCHEMA,
        "records": {
            k: {**v, "entrypoints": [record.entrypoint]} for k, v in record.recorded.items()
        },
    }
    path = tmp_path / "snap.json.gz"
    snap.write_json(path, data)
    monkeypatch.setattr(
        approved_digests,
        "APPROVED_REFERENCE_SNAPSHOT_SHA256",
        hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    return path


def _record(entrypoint="ep", **values):
    rec = snap.Session("record", entrypoint)
    with snap.session(entrypoint, rec), snap.scope("mission", "audit"):
        for label, (seed, exact, parts) in values.items():
            snap.pin(label, seed, exact, **parts)
    return rec


@pytest.fixture
def tolerances(monkeypatch):
    table = {k: 1e-9 for k in snap.TOLERANCES}
    monkeypatch.setattr(snap, "TOLERANCES", table)
    return table


def test_pin_outside_a_session_returns_its_inputs():
    assert snap.active() is None
    out = snap.pin("x", "ref", a_m=[1.0, 2.0])
    assert out["a_m"].tolist() == [1.0, 2.0]


def test_verify_round_trip_and_substitution(tmp_path, monkeypatch, tolerances):
    rec = _record(r=("ref", False, {"x_m": [1.0, 2.0]}), s=("sim", False, {"y_m": [3.0]}))
    path = _artifact(tmp_path, monkeypatch, rec)
    with snap.session("ep", path=path) as s, snap.scope("mission", "audit"):
        ref = snap.pin("r", "ref", x_m=[1.0 + 5e-10, 2.0])
        sim = snap.pin("s", "sim", y_m=[3.0 + 5e-10])
    assert s.finish() == []
    assert ref["x_m"].tolist() == [1.0, 2.0]  # approved value consumed (ref seed)
    assert sim["y_m"].tolist() == [3.0 + 5e-10]  # verified only (sim seed)
    assert s.report()["values_verified"] == 3


@pytest.mark.parametrize(
    "value",
    [1.0 + 2e-9, 1.0 - 2e-9, math.nan, math.inf, -math.inf, 1e300],
)
def test_out_of_tolerance_or_non_finite_is_rejected(tmp_path, monkeypatch, tolerances, value):
    rec = _record(r=("ref", False, {"x_m": [1.0]}))
    path = _artifact(tmp_path, monkeypatch, rec)
    with snap.session("ep", path=path) as s, snap.scope("mission", "audit"):
        out = snap.pin("r", "ref", x_m=[value])
    problems = s.finish()
    assert problems and any("tolerance" in p or "non-finite" in p for p in problems)
    assert out["x_m"][0] == value or math.isnan(value)  # runtime value, not the approved


def test_non_finite_is_rejected_even_with_an_infinite_tolerance(tmp_path, monkeypatch):
    monkeypatch.setattr(snap, "TOLERANCES", {k: math.inf for k in snap.TOLERANCES})
    rec = _record(r=("ref", False, {"x_m": [1.0]}))
    path = _artifact(tmp_path, monkeypatch, rec)
    with snap.session("ep", path=path) as s, snap.scope("mission", "audit"):
        snap.pin("r", "ref", x_m=[math.nan])
    assert s.finish()


def test_exact_values_must_match_bit_for_bit(tmp_path, monkeypatch, tolerances):
    rec = _record(t=("ref", True, {"ticks_s": [10.0, 20.0]}))
    path = _artifact(tmp_path, monkeypatch, rec)
    with snap.session("ep", path=path) as s, snap.scope("mission", "audit"):
        snap.pin("t", "ref", True, ticks_s=[10.0, math.nextafter(20.0, 30.0)])
    assert any("tolerance" in p for p in s.finish())


@pytest.mark.parametrize(
    "runtime",
    [
        ("ref", False, {"x_m": [1.0, 2.0]}),  # shape
        ("sim", False, {"x_m": [1.0]}),  # seed
        ("ref", True, {"x_m": [1.0]}),  # exactness
        ("ref", False, {"x_kg": [1.0]}),  # part name / unit
    ],
)
def test_changed_kind_is_rejected(tmp_path, monkeypatch, tolerances, runtime):
    rec = _record(r=("ref", False, {"x_m": [1.0]}))
    path = _artifact(tmp_path, monkeypatch, rec)
    seed, exact, parts = runtime
    with snap.session("ep", path=path) as s, snap.scope("mission", "audit"):
        snap.pin("r", seed, exact, **parts)
    assert s.finish()


def test_unexpected_and_missing_values_are_rejected(tmp_path, monkeypatch, tolerances):
    rec = _record(a=("ref", False, {"x_m": [1.0]}), b=("ref", False, {"x_m": [2.0]}))
    path = _artifact(tmp_path, monkeypatch, rec)
    with snap.session("ep", path=path) as s, snap.scope("mission", "audit"):
        snap.pin("a", "ref", x_m=[1.0])
        snap.pin("c", "ref", x_m=[1.0])  # not in the artifact
    problems = s.finish(complete=True)
    assert any("unexpected" in p for p in problems)
    assert any("not reproduced" in p and "/b#0" in p for p in problems)
    # A repeated computation is a new key (counter), so it cannot hide a missing one.
    with snap.session("ep", path=path) as s, snap.scope("mission", "audit"):
        snap.pin("a", "ref", x_m=[1.0])
        snap.pin("a", "ref", x_m=[1.0])
    assert any("unexpected" in p and "/a#1" in p for p in s.finish())


def test_incomplete_sessions_check_values_only(tmp_path, monkeypatch, tolerances):
    rec = _record(a=("ref", False, {"x_m": [1.0]}), b=("ref", False, {"x_m": [2.0]}))
    path = _artifact(tmp_path, monkeypatch, rec)
    with snap.session("ep", path=path) as s, snap.scope("mission", "audit"):
        snap.pin("a", "ref", x_m=[1.0])
    assert s.finish(complete=False) == []
    assert s.finish(complete=True)


def test_other_entrypoints_values_are_not_required(tmp_path, monkeypatch, tolerances):
    rec = _record(a=("ref", False, {"x_m": [1.0]}))
    path = _artifact(tmp_path, monkeypatch, rec)
    with snap.session("other", path=path) as s:
        pass
    assert s.finish(complete=True) == []


def test_tampered_artifact_is_rejected(tmp_path, monkeypatch, tolerances):
    rec = _record(a=("ref", False, {"x_m": [1.0]}))
    path = _artifact(tmp_path, monkeypatch, rec)
    data = snap.read_json(path)
    data["records"]["mission/audit/a#0"]["parts"]["x_m"]["values"] = [1.5]
    snap.write_json(path, data)  # digest no longer the pinned one
    with snap.session("ep", path=path) as s, snap.scope("mission", "audit"):
        snap.pin("a", "ref", x_m=[1.5])
    assert any("not the approved one" in p for p in s.finish())


def test_missing_artifact_is_rejected(tmp_path):
    with snap.session("ep", path=tmp_path / "absent.json.gz") as s:
        pass
    assert any("missing" in p for p in s.finish())


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(schema=99),
        lambda d: d.update(records={}),
        lambda d: d["records"]["k#0"].update(seed="other"),
        lambda d: d["records"]["k#0"].update(exact="no"),
        lambda d: d["records"]["k#0"].update(entrypoints=[]),
        lambda d: d["records"]["k#0"]["parts"]["x_m"].update(shape=[2]),
        lambda d: d["records"]["k#0"]["parts"]["x_m"].update(values=[float("nan")]),
        lambda d: d["records"]["k#0"]["parts"]["x_m"].update(values=[1]),
        lambda d: d["records"]["k#0"]["parts"].update(x=dict(shape=[1], values=[1.0])),
    ],
)
def test_malformed_artifacts_are_rejected(mutate):
    data = {
        "schema": snap.SCHEMA,
        "records": {
            "k#0": {
                "seed": "ref",
                "exact": False,
                "entrypoints": ["ep"],
                "parts": {"x_m": {"shape": [1], "values": [1.0]}},
            }
        },
    }
    mutate(data)
    with pytest.raises((snap.SnapshotError, ValueError)):
        snap._check_structure(data)


def test_write_is_deterministic(tmp_path):
    data = {"schema": 1, "records": {"b": 1, "a": 2}}
    snap.write_json(tmp_path / "a.json.gz", data)
    snap.write_json(tmp_path / "b.json.gz", dict(reversed(list(data.items()))))
    assert (tmp_path / "a.json.gz").read_bytes() == (tmp_path / "b.json.gz").read_bytes()


# ------------------------------------------------------------------ immutability (cond. 3)


def test_generate_refuses_to_write_the_approved_artifact():
    tool = _load(TOOL, "reference_snapshot_tool")
    assert tool.main(["generate", "--out", str(snap.snapshot_path())]) == 2


def test_only_the_tool_writes_snapshots_and_ci_only_measures():
    """No test, CI job or Proof path writes or regenerates the approved snapshot."""
    writers = []
    for path in [*REPO_ROOT.glob("src/**/*.py"), *REPO_ROOT.glob("toolbox/**/*.py")]:
        text = path.read_text()
        if "write_json(" in text and path.name != "reference_snapshot.py":
            writers.append(str(path.relative_to(REPO_ROOT)))
        if 'Session("record"' in text and path != TOOL:
            writers.append(str(path.relative_to(REPO_ROOT)))
    assert writers == []
    for wf in (REPO_ROOT / ".github" / "workflows").glob("*.yml"):
        for line in wf.read_text().splitlines():
            if "reference_snapshot.py generate" in line:
                assert "--measurement" in line, (wf.name, line)
                assert "references/snapshot" not in line
    # Only the tool records or skips authentication; the Proof and the GMAT CLI have no
    # option to record, bypass or point verification at another artifact.
    for path in [*REPO_ROOT.glob("src/**/*.py"), *REPO_ROOT.glob("toolbox/**/*.py")]:
        text = path.read_text()
        if path not in (TOOL, REPO_ROOT / "src/tars/validation/reference_snapshot.py"):
            assert "authenticate=False" not in text or "thresholds" in path.name, path
    for cli in ("toolbox/validators/m2_proof.py", "toolbox/scripts/gmat_m2.py"):
        text = (REPO_ROOT / cli).read_text()
        assert "--record" not in text and "--snapshot" not in text and "--no-snapshot" not in text


# ------------------------------------------------------------------ margins (cond. 4)


def test_margin_problems():
    limits = {"a": 1.0, "b": 1.0, "c": 1.0}
    shifts = {"a": 0.1, "b": 0.1, "c": 0.1}
    problems = snap.margin_problems("g", {"a": 0.95, "b": 0.5, "c": 1.5}, limits, shifts)
    assert len(problems) == 1 and "a=" in problems[0]  # c already fails: nothing to hide
    assert snap.margin_problems("g", {"a": 0.5}, {"a": 1.0}, {"a": math.nan})


def test_o6_shifts_bound_the_metric_changes():
    """Brute force: moving every impulsive SMA by up to delta changes the gated O6
    metrics by at most the computed shifts."""
    rng = np.random.default_rng(1)
    rows = [
        {
            "sma_finite_minus_impulsive_m": -0.13 / 4**k,
            "sma_change_finite_m": 50521.03,
            "sma_change_impulsive_m": 50521.16,
        }
        for k in range(5)
    ]
    delta = 1e-5
    shifts = m2.o6_snapshot_shifts(rows, delta)
    base = m2.impulsive_metrics(rows)
    for _ in range(2000):
        e = rng.uniform(-delta, delta, size=len(rows))
        moved = [
            {
                **r,
                "sma_finite_minus_impulsive_m": r["sma_finite_minus_impulsive_m"] - x,
                "sma_change_impulsive_m": r["sma_change_impulsive_m"] + x,
            }
            for r, x in zip(rows, e, strict=True)
        ]
        got = m2.impulsive_metrics(moved)
        for k, s in shifts.items():
            assert abs(got[k] - base[k]) <= s * (1 + 1e-9)


# ------------------------------------------------------------------ approved baseline


def test_approved_artifact_is_pinned_and_verified():
    data = snap.load_approved()  # authenticates against the pinned digest
    assert data["kind"] == "baseline candidate"
    prov = data["provenance"]
    assert prov["tree_clean"] is True
    for key in ("numpy", "scipy", "python_full", "uv_lock_sha256"):
        assert prov["environment"][key]


def test_tolerances_are_finite_positive_and_small():
    """Every class used by a non-exact approved value has a finite positive tolerance
    (VAL-0015); counts and unused classes are exact."""
    for tol in snap.TOLERANCES.values():
        assert math.isfinite(tol) and tol >= 0.0
    used = {
        (rec["seed"], snap.unit_of(name))
        for rec in snap.load_approved()["records"].values()
        if not rec["exact"]
        for name in rec["parts"]
    }
    for cls in used - {("ref", "1")}:
        assert snap.TOLERANCES[cls] > 0.0, cls
    assert snap.TOLERANCES[("ref", "1")] == 0.0  # the powered-crossing count
    # Far below the GMAT noise floor (11-15 um) for every reference-seeded length.
    assert snap.TOLERANCES[("ref", "m")] < 1.5e-5 / 100


# ------------------------------------------------------------------ F50 / F51 regressions


def _gmat_cli():
    return _load(CLI, "gmat_m2_cli_snap")


def _joint_corruption(monkeypatch, scenario, burns, factor=1.001):
    """Review F50: Kepler states for the anchor's interior coast ticks AND the DOP853
    dense positions at those ticks return the state at factor x the flight time, so
    the two references agree with each other (F49 passes) on a wrong trajectory."""
    import scipy.integrate

    mu, dt = scenario.constants.mu, scenario.dt_s
    lines, start = inspect.getsourcelines(m2._anchor_segment)
    target = start + next(i for i, ln in enumerate(lines) if "rows = [kepler_state" in ln)
    original_kepler, original_ivp = m2.kepler_state, scipy.integrate.solve_ivp
    hits = {"kepler": 0, "dense": 0}

    def coast(a, b):
        return not any(i < b and a < c for i, c in burns)

    def poisoned_kepler(r, v, dt_, mu_):
        f = sys._getframe(1)
        if f.f_code.co_name == "_anchor_segment" and f.f_lineno == target:
            a, b = f.f_locals["a"], f.f_locals["b"]
            if coast(a, b) and 0.0 < dt_ < b - a:
                hits["kepler"] += 1
                return original_kepler(r, v, dt_ * factor, mu_)
        return original_kepler(r, v, dt_, mu_)

    def poisoned_ivp(fun, t_span, y0, **kw):
        sol = original_ivp(fun, t_span, y0, **kw)
        a, b = float(t_span[0]), float(t_span[1])
        if not coast(a, b):
            return sol
        dense, y0 = sol.sol, np.array(y0, dtype=float)

        class Joint:
            def __call__(self, t):
                out = dense(t)
                tt = np.atleast_1d(t)
                for j, tj in enumerate(tt):
                    on_tick = abs(tj / dt - round(tj / dt)) < 1e-12 and a < tj < b
                    if on_tick:
                        hits["dense"] += 1
                        out[:3, j] = original_kepler(y0[:3], y0[3:6], (tj - a) * factor, mu)[0]
                return out

        sol.sol = Joint()
        return sol

    monkeypatch.setattr(m2, "kepler_state", poisoned_kepler)
    monkeypatch.setattr(scipy.integrate, "solve_ivp", poisoned_ivp)
    return hits


def test_joint_corruption_defeats_the_runtime_checks_without_the_snapshot(monkeypatch):
    """The F50 corruption passes every runtime check of the reference (F47, F49) and
    moves the altitude extremum: only the snapshot can detect it."""
    mission = BY_NAME["m2_prograde_burn"]
    scenario = mission.build()
    predicted = m2.predict_burns(scenario, mission.expected)
    burns = [(b.ignition_t_s, b.cutoff_t_s) for b in predicted]
    marks = [scenario.stop.duration_s]  # the whole mission, as in the F50 probe
    clean = m2.dop853_reference(scenario, *m2.expected_initial_state(scenario), predicted, marks)
    hits = _joint_corruption(monkeypatch, scenario, burns)
    dirty = m2.dop853_reference(scenario, *m2.expected_initial_state(scenario), predicted, marks)
    assert hits["kepler"] and hits["dense"]
    assert dirty.alt_max != clean.alt_max or dirty.alt_min != clean.alt_min


def test_f50_acceptance_flip_is_rejected(monkeypatch):
    """F50 regression: identical simulator data is rejected with clean references
    (max altitude 1e-5 m beyond its limit) and still rejected under the coordinated
    Kepler + DOP853 corruption, now by the reference snapshot."""
    cli = _gmat_cli()
    name = "m2_prograde_burn"
    mission = BY_NAME[name]
    scenario = mission.build()
    limit = json.loads(M2_THRESHOLDS.read_text())["limits"]["orbit_events"]["all"][
        "max_altitude_error_m"
    ]
    reasons, check = cli._evaluate(name)
    assert reasons == [] and check is not None and check.passed  # clean baseline passes
    ref_alt_max = snap.load_approved()["records"][f"{name}/audit/dop853.extrema#0"]["parts"][
        "altitude_m"
    ]["values"][1]
    real_run = cli.run_scenario

    def overstated(sc, *a, **k):
        run = real_run(sc, *a, **k)
        done = run.events[-1]
        run.events[-1] = done.model_copy(update={"max_altitude_m": ref_alt_max + limit + 1e-5})
        return run

    monkeypatch.setattr(cli, "run_scenario", overstated)
    reasons, check = cli._evaluate(name)
    assert check is None and any("max_altitude_error_m" in r for r in reasons)
    assert not any("reference snapshot" in r for r in reasons)  # clean references
    predicted = m2.predict_burns(scenario, mission.expected)
    hits = _joint_corruption(
        monkeypatch, scenario, [(b.ignition_t_s, b.cutoff_t_s) for b in predicted]
    )
    reasons, check = cli._evaluate(name)
    assert hits["kepler"] and hits["dense"]
    assert check is None
    assert any("reference snapshot" in r and "dop853" in r for r in reasons)


def test_f51_wrong_time_kepler_in_o6_is_rejected(monkeypatch):
    """F51 regression: Kepler returns at 10x the requested flight time in O6, forward
    and in the round trip (invariants and round trip still hold), are rejected by the
    snapshot within the M2 Proof's session."""
    mission = BY_NAME["m2_prograde_burn"]
    scenario = mission.build()
    variants = m2.impulsive_variants(scenario)
    runs = [run_scenario(v) for v in variants]
    with snap.session("m2_proof") as s:
        for v, r in zip(variants, runs, strict=True):
            m2.impulsive_row(scenario, v, r)
    assert s.finish(complete=False) == []  # clean: every O6 value reproduces

    original = kepler.propagate

    def wrong_time(r, v, dt, mu):
        f = sys._getframe(1)
        while f:
            if f.f_code.co_name == "impulsive_row":
                return original(r, v, dt * 10, mu)
            f = f.f_back
        return original(r, v, dt, mu)

    monkeypatch.setattr(kepler, "propagate", wrong_time)
    with snap.session("m2_proof") as s:
        for v, r in zip(variants, runs, strict=True):
            m2.impulsive_row(scenario, v, r)
    problems = s.finish(complete=False)
    assert any("o6.midpoint" in p and "tolerance" in p for p in problems)


def test_coordinated_radial_shift_of_both_references_is_rejected(monkeypatch):
    """Condition 5: Kepler anchor ticks AND DOP853 dense positions raised together by
    1 cm at every interior coast tick. The two references still agree (F49), the
    derivative stencil never samples a tick, and the extrema move: every runtime check
    passes, and the snapshot rejects it inside the Proof's session."""
    import scipy.integrate

    mission = BY_NAME["m2_invalid_commands_no_propulsion"]
    scenario = mission.build()
    run = run_scenario(scenario)
    dt, dr = scenario.dt_s, 0.01
    lines, start = inspect.getsourcelines(m2._anchor_segment)
    target = start + next(i for i, ln in enumerate(lines) if "rows = [kepler_state" in ln)
    original_kepler, original_ivp = m2.kepler_state, scipy.integrate.solve_ivp

    def raise_r(r):
        return r * (1.0 + dr / np.linalg.norm(r))

    def shifted_kepler(r, v, dt_, mu):
        rr, vv = original_kepler(r, v, dt_, mu)
        f = sys._getframe(1)
        in_anchor = f.f_code.co_name == "_anchor_segment" and f.f_lineno == target
        if in_anchor and 0.0 < dt_ < f.f_locals["b"] - f.f_locals["a"]:
            return raise_r(rr), vv
        return rr, vv

    def shifted_ivp(fun, t_span, y0, **kw):
        sol = original_ivp(fun, t_span, y0, **kw)
        dense, (a, b) = sol.sol, t_span

        class Shifted:
            def __call__(self, t):
                out = dense(t)
                tt = np.atleast_1d(t)
                for j, tj in enumerate(tt):
                    if a < tj < b and abs(tj / dt - round(tj / dt)) < 1e-12:
                        out[:3, j] = raise_r(out[:3, j])
                return out

        sol.sol = Shifted()
        return sol

    with snap.session("m2_proof") as s:
        clean = m2.audit_run(scenario, mission.expected, run)
    assert s.finish(complete=False) == []
    monkeypatch.setattr(m2, "kepler_state", shifted_kepler)
    monkeypatch.setattr(scipy.integrate, "solve_ivp", shifted_ivp)
    outside = m2.dop853_reference(
        scenario, *m2.expected_initial_state(scenario), [], [scenario.stop.duration_s]
    )  # no session: every runtime check passes on the shifted references
    assert outside.alt_max == pytest.approx(clean.reference.alt_max + dr, abs=1e-6)
    with snap.session("m2_proof") as s:
        m2.audit_run(scenario, mission.expected, run)
    problems = s.finish(complete=False)
    assert any("dop853.segment" in p and "anchor_ticks_m" in p for p in problems)


# ------------------------------------------------------------------ re-verification 15


def test_o5_margin_uses_the_vector_norm_bound():
    """F52: per-component tolerances let a Kepler vector move by sqrt(3) x tol, so a
    passing O5 metric closer than that to its limit is flagged."""
    tol = snap.TOLERANCES[("sim", "m")]
    shifts = m2.o5_snapshot_shifts()
    assert shifts["coast_position_error_max_m"] == pytest.approx(math.sqrt(3.0) * tol)
    limits = {"coast_position_error_max_m": 0.6, "coast_velocity_error_max_mps": 7e-4}
    metrics = {"coast_position_error_max_m": 0.6 - 1.5 * tol, "coast_velocity_error_max_mps": 0.0}
    assert snap.margin_problems("o5", metrics, limits, shifts)  # 1.5 tol < sqrt(3) tol


@pytest.fixture(scope="module")
def baseline():
    return snap.load_approved()


def _verify(data):
    return _load(TOOL, "reference_snapshot_tool_v").verify_baseline(data)


def _copy(data):
    return json.loads(json.dumps(data))


def _set(rec, name, values):
    part = rec["parts"][name]
    arr = np.asarray(values, dtype=float).reshape(part["shape"])
    part["values"] = [float(x) for x in arr.ravel()]


def _first(data, label, scope=None):
    for key, rec in data["records"].items():
        if f"/{label}#" in key and (scope is None or key.startswith(scope + "/")):
            return key, rec
    raise KeyError(label)


def test_baseline_verification_rejects_invalid_o6_values(baseline):
    """F53, second probe: zero O6 midpoints with an absurd impulsive SMA."""
    data = _copy(baseline)
    for key, rec in data["records"].items():
        if "/o6.midpoint#" in key:
            _set(rec, "r_m", [0.0, 0.0, 0.0])
            _set(rec, "v_mps", [0.0, 0.0, 0.0])
            _set(rec, "sma_impulsive_m", [-1e30])
    problems = _verify(data)
    assert sum("O6 midpoint" in p for p in problems) == 10


def test_baseline_verification_rejects_wrong_time_o6_recording(baseline):
    """F53, first probe: a recording made under F51's 10x flight-time corruption has
    self-consistent O6 values (state and SMA agree) at the wrong time."""
    tool = _load(TOOL, "reference_snapshot_tool_v")
    data = _copy(baseline)
    key, rec = _first(data, "o6.midpoint")
    mu = BY_NAME["m2_prograde_burn"].build().constants.mu
    seed_r, seed_v = tool._arr(rec, "seed_r_m"), tool._arr(rec, "seed_v_mps")
    flight = tool._arr(rec, "flight_s")
    r, v = tool.kepler_uv(seed_r, seed_v, flight * 10, mu)
    dv = tool._arr(data["records"][key.replace("o6.midpoint", "o6.delta_v")], "dv_mps")[0]
    v_imp = v[0] + dv * v[0] / np.linalg.norm(v[0])
    a = -mu / (2.0 * (v_imp @ v_imp / 2.0 - mu / np.linalg.norm(r[0])))
    _set(rec, "r_m", r[0])
    _set(rec, "v_mps", v[0])
    _set(rec, "sma_impulsive_m", [a])
    problems = _verify(data)
    assert any(key in p and "independent propagation" in p for p in problems)
    assert not any("impulsive SMA inconsistent" in p for p in problems)  # self-consistent


def test_baseline_verification_rejects_an_f50_recording(baseline):
    """A recording made under F50's coordinated corruption: anchor ticks at 1.001 x
    the flight time, extrema recomputed from them so they stay consistent."""
    tool = _load(TOOL, "reference_snapshot_tool_v")
    data = _copy(baseline)
    scope = "m2_prograde_burn/audit"
    scenario = BY_NAME["m2_prograde_burn"].build()
    mu, dt = scenario.constants.mu, scenario.dt_s
    b = tool._arr(data["records"][f"{scope}/dop853.bounds#0"], "bounds_s")
    start = data["records"][f"{scope}/dop853.start#0"]
    y = np.concatenate([tool._arr(start, "r_m"), tool._arr(start, "v_mps")])
    seg = data["records"][f"{scope}/dop853.segment#0"]
    ticks = np.arange(1, int(b[1] / dt) + 1) * dt
    r, _ = tool.kepler_uv(y[:3], y[3:6], (ticks - b[0]) * 1.001, mu)
    _set(seg, "anchor_ticks_m", r)
    problems = _verify(data)
    assert any("segment#0" in p and "independent propagation" in p for p in problems)


@pytest.mark.parametrize(
    "label,part,factor",
    [
        ("predicted_burns", "delta_v_mps", 1.0 + 1e-9),
        ("simpson_bound", "bound_mps", 2.0),
        ("initial_state", "r_m", 1.0 + 1e-12 * 10),
        ("o5.kepler", "r_m", 1.0 + 1e-9),
        ("o6.delta_v", "dv_mps", 1.0 + 1e-9),
        ("orbit.node_crossings", "crossings_s", 1.0 + 1e-7),
        ("o9.alignment_kepler", "r_m", 1.0 + 1e-9),
        ("o9.gmat_node_crossings", "crossings_s", 1.0 + 1e-7),
        ("o9.expected_mass", "mass_kg", 1.0 + 1e-9),
        ("dop853.segment", "end_r_m", 1.0 + 1e-12 * 100),
        ("dop853.extrema", "altitude_m", 1.0 + 1e-12),
    ],
)
def test_baseline_verification_rejects_each_corrupted_value(baseline, label, part, factor):
    data = _copy(baseline)
    for key, rec in data["records"].items():
        if f"/{label}#" in key and rec["parts"][part]["values"]:
            vals = rec["parts"][part]["values"]
            rec["parts"][part]["values"] = [x * factor if x else 1e-3 for x in vals]
            break
    else:
        pytest.fail(f"no {label} record with values")
    assert _verify(data), label


def test_baseline_verification_requires_coverage(baseline):
    data = _copy(baseline)
    key, rec = _first(data, "o5.kepler")
    data["records"][key.replace("o5.kepler", "o5.unverified")] = rec
    assert any("not independently verified" in p for p in _verify(data))


def test_the_approved_baseline_passes_independent_verification(baseline):
    assert _verify(baseline) == []


def test_baseline_verification_fails_closed_on_unreadable_records(baseline):
    """A record the verifier cannot even evaluate (a missing part) is a problem, never
    a crash and never a silent pass."""
    data = _copy(baseline)
    _key, rec = _first(data, "dop853.segment", "m2_prograde_burn/audit")
    del rec["parts"]["anchor_ticks_m"]
    problems = _verify(data)
    assert any("verification raised" in p and "m2_prograde_burn/audit" in p for p in problems)
    data = _copy(baseline)
    _key, rec = _first(data, "o9.alignment_kepler", "m2_prograde_burn/o9")
    del rec["parts"]["r_m"]
    assert any("verification raised" in p for p in _verify(data))
