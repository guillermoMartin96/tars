"""Approved reference snapshot tooling for the M2 Proof (DR-0021 option A).

Usage:
    uv run python toolbox/scripts/reference_snapshot.py generate --out PATH [--measurement]
    uv run python toolbox/scripts/reference_snapshot.py verify-baseline PATH
    uv run python toolbox/scripts/reference_snapshot.py compare OLD NEW
    uv run python toolbox/scripts/reference_snapshot.py measure-deviation CANDIDATE --out JSON

``generate`` records every reference value of the M2 Proof and of the GMAT M2
evaluation into a CANDIDATE file. It never writes the approved artifact and never
changes the pinned digest (DR-0021 condition 3): installing a new baseline is a
reviewed commit that copies the candidate, updates
``tars.validation.approved_digests.APPROVED_REFERENCE_SNAPSHOT_SHA256``, and records
the justification, the comparison with the previous baseline (``compare``) and an
independent review. A baseline candidate requires a clean git tree (the pinned
commit), a passing Proof and GMAT evaluation, and ``verify-baseline`` to pass;
``--measurement`` drops the clean-tree requirement and marks the file as a
cross-platform measurement, not a candidate (VAL-0015).

``verify-baseline`` checks a snapshot against the committed GMAT evidence and the
physical invariants, from the snapshot's own values (DR-0021 condition 2).

``compare`` reports the largest |a - b| per value class and any keys present in only
one file (the baseline-change comparison).

``measure-deviation`` runs the Proof and the GMAT evaluation in VERIFY mode against a
candidate with unlimited tolerances, so every within-run value is substituted exactly
as in a real verification, and reports the largest |runtime - approved| per value class:
the quantity the reproducibility tolerances bound (VAL-0015, DR-0021 condition 4).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from collections import defaultdict
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np

from tars.validation import reference_snapshot as snap
from tars.validation.thresholds import REPO_ROOT


def _load_module(name: str, rel: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def _environment() -> dict[str, Any]:
    import platform

    import scipy

    from tars.validation.cross_platform import platform_info

    lock = REPO_ROOT / "uv.lock"
    return {
        **platform_info(),
        "python_full": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "uv_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest() if lock.exists() else None,
    }


def merge(sessions: list[snap.Session]) -> dict[str, dict[str, Any]]:
    """One record set from several entrypoints. A key computed by two entrypoints must
    be bit-identical (same process, same inputs): anything else is non-determinism."""
    records: dict[str, dict[str, Any]] = {}
    for s in sessions:
        for key, rec in s.recorded.items():
            if key in records:
                old = records[key]
                if (old["seed"], old["exact"], old["parts"]) != (
                    rec["seed"],
                    rec["exact"],
                    rec["parts"],
                ):
                    raise SystemExit(f"non-deterministic reference value {key}")
                old["entrypoints"].append(s.entrypoint)
            else:
                records[key] = {**rec, "entrypoints": [s.entrypoint]}
    return dict(sorted(records.items()))


def cmd_generate(args: argparse.Namespace) -> int:
    out = Path(args.out).resolve()
    if out == snap.snapshot_path().resolve():
        print("refusing to write the approved artifact; write a candidate", file=sys.stderr)
        return 2
    dirty = _git("status", "--porcelain")
    if dirty and not args.measurement:
        print("a baseline candidate needs a clean tree (pinned commit):\n" + dirty, file=sys.stderr)
        return 2

    proof = _load_module("m2_proof", "toolbox/validators/m2_proof.py")
    cli = _load_module("gmat_m2_cli", "toolbox/scripts/gmat_m2.py")
    sessions = [snap.Session("record", "m2_proof")]
    report_path = out.parent / (out.name.split(".")[0] + ".proof.json")
    rc = proof.main(["--out", str(report_path)], recorder=sessions[0])
    failures = [] if rc == 0 else ["M2 Proof failed"]
    for name in cli.gmat_m2.GMAT_MISSIONS:
        rec = snap.Session("record", f"gmat_m2:{name}")
        reasons, check = cli._evaluate(name, recorder=rec)
        sessions.append(rec)
        if reasons or check is None or not check.passed:
            failures.append(f"GMAT M2 {name}: {reasons[:5] or 'O9 check failed'}")
    for s in sessions:
        failures += [f"{s.entrypoint}: {p}" for p in s.finish(complete=False)]
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    records = merge(sessions)
    data = {
        "schema": snap.SCHEMA,
        "artifact": "M2 approved reference snapshot (DR-0021 option A)",
        "kind": "measurement" if args.measurement else "baseline candidate",
        "provenance": {
            "tars_git_revision": _git("rev-parse", "HEAD"),
            "tree_clean": not dirty,
            "environment": _environment(),
            "proof_report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
            "gmat_m2_manifest_sha256": hashlib.sha256(
                (REPO_ROOT / "toolbox/references/gmat/m2/APPROVED_DIGESTS.json").read_bytes()
            ).hexdigest(),
            "entrypoints": [s.entrypoint for s in sessions],
        },
        "records": records,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    snap.write_json(out, data)
    problems = verify_baseline(data)
    if problems and not args.measurement:
        out.unlink()  # never leave a failed candidate behind
        print("baseline verification failed:\n" + "\n".join(problems), file=sys.stderr)
        return 1
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    values = sum(len(p["values"]) for r in records.values() for p in r["parts"].values())
    print(f"{data['kind']}: {out} ({len(records)} records, {values} values)")
    print(f"sha256 {digest}")
    if problems:
        print("baseline verification (measurement only, not a candidate):")
        print("\n".join(problems))
    elif not args.measurement:
        print("baseline verification: PASS")
    return 0


# --------------------------------------------------------------- baseline verification
#
# DR-0021 condition 2 (and review M2-T6 F53): every pinned value is recomputed from its
# pinned inputs and the scenario with implementations independent of the runtime
# references (tars.astro.kepler, SciPy DOP853, the validator's RK4 anchor), and
# checked against the committed GMAT evidence and the physical invariants.

# Agreement limits between the snapshot and the independent recomputation. Measured
# on baseline 2 (VAL-0015): universal-variable Kepler vs tars Kepler <= 2.9e-7 m and
# 4.1e-10 m/s (the longest O5 and GMAT arcs; 2.8e-9 m on <= 60 s segments); LSODA vs
# the RK4 anchors in burns <= 6.5e-7 m and 1.1e-9 m/s; node crossings on z = 0 to
# 2.2e-8 m; scenario-only values exact or <= 1e-15 relative. Each limit sits above the
# measured agreement and far below any physical corruption and the O9 gates.
INDEP_POS_M = 1e-6
INDEP_VEL_MPS = 2e-9
INDEP_BURN_POS_M = 1e-5
INDEP_BURN_VEL_MPS = 1e-8
INDEP_MASS_KG = 1e-9
INDEP_REL = 1e-12
NODE_Z_M = 1e-5  # |z| at a pinned node crossing (v_z ~ 5 km/s: 2e-9 s)


def _stumpff(z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    c, s = np.empty_like(z), np.empty_like(z)
    pos, neg = z > 1e-6, z < -1e-6
    small = ~(pos | neg)
    sz = np.sqrt(z[pos])
    c[pos], s[pos] = (1.0 - np.cos(sz)) / z[pos], (sz - np.sin(sz)) / sz**3
    sn = np.sqrt(-z[neg])
    c[neg], s[neg] = (np.cosh(sn) - 1.0) / -z[neg], (np.sinh(sn) - sn) / sn**3
    zs = z[small]
    c[small] = 0.5 - zs / 24.0 + zs**2 / 720.0
    s[small] = 1.0 / 6.0 - zs / 120.0 + zs**2 / 5040.0
    return c, s


def kepler_uv(r0, v0, dts, mu: float) -> tuple[np.ndarray, np.ndarray]:
    """Two-body states at every dt from (r0, v0): universal variables with Lagrange
    f and g (Curtis, Orbital Mechanics, Algorithms 3.3-3.4), vectorized. Written here,
    independent of tars.astro.kepler."""
    r0, v0 = np.asarray(r0, dtype=float), np.asarray(v0, dtype=float)
    dts = np.atleast_1d(np.asarray(dts, dtype=float))
    rn0 = float(np.linalg.norm(r0))
    vr0 = float(r0 @ v0) / rn0
    alpha = 2.0 / rn0 - float(v0 @ v0) / mu
    smu = math.sqrt(mu)
    chi = smu * abs(alpha) * dts
    for _ in range(100):
        z = alpha * chi**2
        c, s = _stumpff(z)
        f = rn0 * vr0 / smu * chi**2 * c + (1.0 - alpha * rn0) * chi**3 * s + rn0 * chi - smu * dts
        df = rn0 * vr0 / smu * chi * (1.0 - z * s) + (1.0 - alpha * rn0) * chi**2 * c + rn0
        step = f / df
        chi = chi - step
        if np.all(np.abs(step) <= 1e-14 * np.maximum(np.abs(chi), 1.0)):
            break
    z = alpha * chi**2
    c, s = _stumpff(z)
    f = 1.0 - chi**2 / rn0 * c
    g = dts - chi**3 / smu * s
    r = f[:, None] * r0 + g[:, None] * v0
    rn = np.linalg.norm(r, axis=1)
    fdot = smu / (rn * rn0) * (z * s - 1.0) * chi
    gdot = 1.0 - chi**2 / rn * c
    v = fdot[:, None] * r0 + gdot[:, None] * v0
    return r, v


def _burn_path(y0, times, mu: float, veh, sign: float) -> np.ndarray:
    """Powered two-body states at ``times`` (the first is the start): ODEPACK LSODA via
    scipy.integrate.odeint, with its own equations of motion -- independent of the
    runtime DOP853 reference and of the validator's RK4 anchor."""
    from scipy.integrate import odeint

    from tars.sim.constants import STANDARD_GRAVITY

    mdot = veh.thrust_n / (veh.isp_s * STANDARD_GRAVITY)

    def rhs(y, t):
        r, v = y[:3], y[3:6]
        m = veh.dry_mass_kg + y[6]
        a = -mu * r / np.linalg.norm(r) ** 3 + sign * veh.thrust_n / m * v / np.linalg.norm(v)
        return np.concatenate([v, a, [-mdot]])

    return odeint(
        rhs, np.asarray(y0, float), np.asarray(times, float), rtol=1e-13, atol=1e-12, mxstep=100000
    )


def _free_space_closed_form(veh, t: float) -> tuple[float, float]:
    """Free-space delta-v and displacement, re-derived in 40-digit decimal (the float
    form cancels): dv = c ln(m0/m), x = c (m/mdot) (m0/m - 1 - ln(m0/m))."""
    from decimal import Decimal, localcontext

    from tars.sim.constants import STANDARD_GRAVITY

    with localcontext() as ctx:
        ctx.prec = 40
        c = Decimal(veh.isp_s) * Decimal(STANDARD_GRAVITY)
        mdot = Decimal(veh.thrust_n) / c
        m0 = Decimal(veh.initial_mass_kg)
        m = m0 - mdot * Decimal(t)
        ratio = m0 / m
        ln = ratio.ln()
        return float(c * ln), float(c * (m / mdot) * (ratio - 1 - ln))


def _independent_burns(scenario, expected) -> list[dict[str, float]]:
    """Accepted burns from the scenario and DR-0017 D1a, re-derived here."""
    from tars.sim.constants import STANDARD_GRAVITY

    sc = scenario.spacecraft
    out: list[dict[str, float]] = []
    if sc is None:
        return out
    c = sc.engine.isp_s * STANDARD_GRAVITY
    mdot = sc.engine.thrust_n / c
    prop = sc.propellant_kg
    for entry, exp in zip(scenario.commands, expected, strict=True):
        if exp.status != "accepted":
            continue
        cmd = entry.command
        ign, dur = float(cmd["ignition_t_s"]), float(cmd["duration_s"])
        depl = prop / mdot
        intended = dur if dur <= depl else depl
        cut = ign + intended
        while cut - ign > depl:
            cut = math.nextafter(cut, -math.inf)
        executed = cut - ign
        used = min(mdot * executed, prop)
        after = 0.0 if used >= prop else prop - used
        m0, mf = sc.dry_mass_kg + prop, sc.dry_mass_kg + after
        out.append(
            {"ign": ign, "dur": dur, "intended": intended, "cut": cut, "executed": executed,
             "before": prop, "used": used, "after": after, "m0": m0, "mf": mf,
             "dv": c * math.log(m0 / mf), "sign": 1.0 if cmd["direction"] == "prograde" else -1.0}
        )  # fmt: skip
        prop = after
    return out


def _scenarios() -> dict[str, tuple[Any, Any]]:
    """Every audited scenario by name, with its expectations."""
    from tars.validation import m2
    from tars.validation.m2_missions import ACCEPT, MISSIONS

    out: dict[str, tuple[Any, Any]] = {}
    for mission in MISSIONS:
        base = mission.build()
        out[base.name] = (base, mission.expected)
        for dt in m2.O8_DTS[1:]:
            v = m2.convergence_variant(base, dt)
            out[v.name] = (v, mission.expected)
        if mission.impulsive_limit:
            for v in m2.impulsive_variants(base):
                out[v.name] = (v, (ACCEPT,))
        if mission.name == "m2_prograde_burn":
            for case in m2.BOUNDARY_CASES:
                v = m2.boundary_variant(base, case)
                out[v.name] = (v, (ACCEPT,))
    return out


def _arr(rec: dict, name: str) -> np.ndarray:
    part = rec["parts"][name]
    return np.asarray(part["values"], dtype=float).reshape(part["shape"])


def _split(key: str) -> tuple[str, str, int]:
    prefix, _, n = key.rpartition("#")
    scope, _, label = prefix.rpartition("/")
    return scope, label, int(n)


def _rel(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        return math.inf
    return float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-300))) if a.size else 0.0


def verify_baseline(data: dict[str, Any]) -> list[str]:
    """Independent verification of every pinned value (DR-0021 condition 2, F53).

    - Scenario-only values (initial state, predicted burns, Simpson and DR-0017
      bounds, O3 closed forms, O6 delta-v, O9 expected mass, epoch, tick grids and
      segment bounds) are re-derived here from the scenario.
    - Propagated values are recomputed from their pinned seeds: coast segments,
      anchor ticks, O5 and O6 Kepler states and GMAT alignment states by the
      universal-variable Kepler above; burn segments by LSODA; node crossings must sit
      on z = 0 of the independent propagation.
    - DOP853 against the committed GMAT rows within the O9 gates; coast energy and
      angular momentum conserved; extrema equal to the pinned anchor ticks'.
    """
    from tars.astro.elements import circular_orbit_state
    from tars.validation import gmat_m2, m2
    from tars.validation.thresholds import load_scoped_thresholds

    problems: list[str] = []
    records = data["records"]
    scen = _scenarios()
    stats: dict[str, float] = defaultdict(float)

    def note(kind: str, value: float) -> None:
        stats[kind] = max(stats[kind], value)

    def bad(where: str, what: str) -> None:
        problems.append(f"{where}: {what}")

    by_scope: dict[str, list[tuple[str, int, str, dict]]] = defaultdict(list)
    for key, rec in records.items():
        scope, label, n = _split(key)
        by_scope[scope].append((label, n, key, rec))
    for items in by_scope.values():
        items.sort(key=lambda x: (x[0], x[1]))

    def scenario_of(scope: str):
        return scen.get(scope.split("/")[0])

    covered: set[str] = set()

    for scope, items in sorted(by_scope.items()):
        found = scenario_of(scope)
        if scope.startswith("o3_free_space/"):
            veh = m2.vehicle(scen["m2_prograde_burn"][0])
            sign = 1.0 if scope.endswith("/prograde") else -1.0
            from tars.sim.constants import STANDARD_GRAVITY

            c = veh.isp_s * STANDARD_GRAVITY
            mdot = veh.thrust_n / c
            closed = {n: rec for label, n, key, rec in items if label == "o3.closed_form"}
            for label, n, key, rec in items:
                covered.add(key)
                if label == "o3.closed_form":
                    continue
                cf = closed.get(n)
                if cf is None:
                    bad(key, "no closed form for this expected cutoff")
                    continue
                t = float(_arr(rec, "duration_s")[0])
                dv, disp = _free_space_closed_form(veh, t)
                x0, v0 = _arr(rec, "start_r_m"), _arr(rec, "start_v_mps")
                u = v0 / np.linalg.norm(v0)
                want_v, want_r = v0 + sign * dv * u, x0 + v0 * t + sign * disp * u
                err = max(
                    _rel(_arr(rec, "v_mps"), want_v),
                    float(np.max(np.abs(_arr(rec, "r_m") - want_r)))
                    / max(float(np.linalg.norm(want_r)), 1.0),
                    _rel(_arr(rec, "propellant_kg"), [veh.propellant_kg - mdot * t]),
                    _rel(_arr(cf, "dv_mps"), [dv]),
                    _rel(_arr(cf, "disp_m"), [disp]),
                )
                note("closed form rel", err)
                if not err <= INDEP_REL:
                    bad(key, f"O3 closed form differs from the independent one ({err:.3g})")
            continue
        if found is None:
            bad(scope, "no scenario for this scope")
            continue
        scenario, expected = found
        mu = scenario.constants.mu
        radius = scenario.constants.equatorial_radius
        veh = m2.vehicle(scenario)
        burns = _independent_burns(scenario, expected)
        grid, dt = scenario.telemetry.sample_interval_s, scenario.dt_s

        for label, _n, key, rec in items:
            if label == "initial_state":
                covered.add(key)
                o = scenario.initial_orbit
                r, v = circular_orbit_state(
                    radius + o.altitude_m, math.radians(o.inclination_deg),
                    math.radians(o.raan_deg), math.radians(o.arg_latitude_deg), mu,
                )  # fmt: skip
                err = max(_rel(_arr(rec, "r_m"), r), _rel(_arr(rec, "v_mps"), v))
                note("initial state rel", err)
                if not err <= INDEP_REL:
                    bad(key, f"initial state differs from elements_to_rv ({err:.3g})")
            elif label == "predicted_burns":
                covered.add(key)
                want_t = [
                    [b["ign"], b["dur"], b["intended"], b["cut"], b["executed"]] for b in burns
                ]
                want_m = [[b["before"], b["used"], b["after"], b["m0"], b["mf"]] for b in burns]
                t, m_, dv = _arr(rec, "times_s"), _arr(rec, "masses_kg"), _arr(rec, "delta_v_mps")
                if t.shape != (len(burns), 5) or not np.array_equal(
                    t, np.array(want_t).reshape(-1, 5)
                ):
                    bad(key, "predicted burn times differ from the independent derivation")
                if _rel(m_, np.array(want_m).reshape(-1, 5)) > INDEP_REL:
                    bad(key, "predicted burn masses differ from the independent derivation")
                if _rel(dv, [b["dv"] for b in burns]) > INDEP_REL:
                    bad(key, "predicted burn delta-v differs from the rocket equation")
            elif label == "simpson_bound":
                covered.add(key)
                a, e = _arr(rec, "window_s")
                b = next((x for x in burns if x["ign"] == a), None)
                total = 0.0
                if b is not None and e > a:
                    mdot = veh.mass_flow_kgps
                    pts = sorted(
                        {
                            a,
                            e,
                            *(
                                k * dt
                                for k in range(math.ceil(a / dt), math.floor(e / dt) + 1)
                                if a < k * dt < e
                            ),
                        }
                    )
                    for p, q in pairwise(pts):
                        m_end = b["m0"] - mdot * (q - a)
                        total += (q - p) ** 5 / 2880.0 * 24.0 * veh.thrust_n * mdot**4 / m_end**5
                elif b is None:
                    bad(key, "Simpson window does not start at a predicted ignition")
                err = (
                    _rel(_arr(rec, "bound_mps"), [total])
                    if total
                    else float(_arr(rec, "bound_mps")[0] != 0.0)
                )
                note("simpson rel", err)
                if not err <= INDEP_REL:
                    bad(key, f"Simpson bound differs from the independent one ({err:.3g})")
            elif label == "timing_bound":
                covered.add(key)
                ex, it = _arr(rec, "durations_s")
                pb = float(_arr(rec, "propellant_before_kg")[0])
                if not any(
                    x["executed"] == ex and x["intended"] == it and x["before"] == pb for x in burns
                ):
                    bad(key, "DR-0017 bound inputs are not a predicted burn")
                d = abs(ex - it)
                want = 0.0
                if d:
                    m_end = veh.dry_mass_kg + max(pb - veh.mass_flow_kgps * max(ex, it), 0.0)
                    want = veh.thrust_n * d / m_end
                if _rel(_arr(rec, "bound_mps"), [want]) > INDEP_REL and want != float(
                    _arr(rec, "bound_mps")[0]
                ):
                    bad(key, "DR-0017 timing bound differs from the independent one")
            elif label == "o5.kepler":
                covered.add(key)
                fl = _arr(rec, "flight_s")
                r, v = kepler_uv(_arr(rec, "seed_r_m"), _arr(rec, "seed_v_mps"), fl, mu)
                ep = float(np.max(np.linalg.norm(r - _arr(rec, "r_m"), axis=1))) if fl.size else 0.0
                ev = (
                    float(np.max(np.linalg.norm(v - _arr(rec, "v_mps"), axis=1)))
                    if fl.size
                    else 0.0
                )
                note("o5 kepler m", ep), note("o5 kepler m/s", ev)
                if not (ep <= INDEP_POS_M and ev <= INDEP_VEL_MPS):
                    bad(
                        key,
                        f"O5 Kepler differs from the independent one ({ep:.3g} m, {ev:.3g} m/s)",
                    )
            elif label == "o6.delta_v":
                covered.add(key)
                base, _ = scen[scope.split("/")[0].rsplit("_o6_", 1)[0]]
                bveh = m2.vehicle(base)
                dur = float(base.commands[0].command["duration_s"])
                m0 = bveh.initial_mass_kg
                want = bveh.exhaust_velocity_mps * math.log(m0 / (m0 - bveh.mass_flow_kgps * dur))
                if _rel(_arr(rec, "dv_mps"), [want]) > INDEP_REL:
                    bad(key, "O6 delta-v differs from the rocket equation")
                o6_dv = float(_arr(rec, "dv_mps")[0])
            elif label == "o6.midpoint":
                covered.add(key)
                base, _ = scen[scope.split("/")[0].rsplit("_o6_", 1)[0]]
                cmd = base.commands[0].command
                sign = 1.0 if cmd["direction"] == "prograde" else -1.0
                fl = _arr(rec, "flight_s")
                want_flight = float(cmd["ignition_t_s"]) + float(cmd["duration_s"]) / 2.0
                r, v = kepler_uv(_arr(rec, "seed_r_m"), _arr(rec, "seed_v_mps"), fl, mu)
                ep = float(np.linalg.norm(r[0] - _arr(rec, "r_m")))
                ev = float(np.linalg.norm(v[0] - _arr(rec, "v_mps")))
                note("o6 kepler m", ep), note("o6 kepler m/s", ev)
                if not (ep <= INDEP_POS_M and ev <= INDEP_VEL_MPS):
                    bad(
                        key,
                        f"O6 midpoint differs from the independent propagation ({ep:.3g} m)",
                    )
                # The flight ends at the commanded burn midpoint (ignition from the variant).
                vign = float(scenario.commands[0].command["ignition_t_s"])
                if not abs(vign + float(fl[0]) - want_flight) <= 1e-9:
                    bad(key, "O6 flight does not end at the commanded burn midpoint")
                vm, rm = _arr(rec, "v_mps"), _arr(rec, "r_m")
                v_imp = vm + sign * o6_dv * vm / np.linalg.norm(vm)
                a_imp = -mu / (2.0 * (float(v_imp @ v_imp) / 2.0 - mu / float(np.linalg.norm(rm))))
                err = _rel(_arr(rec, "sma_impulsive_m"), [a_imp])
                note("o6 sma rel", err)
                if not err <= INDEP_REL:
                    bad(key, f"O6 impulsive SMA inconsistent with its state ({err:.3g})")

        # DOP853 chains in this scope.
        starts = [it for it in items if it[0] == "dop853.start"]
        bounds = [it for it in items if it[0] == "dop853.bounds"]
        segs = [it for it in items if it[0] == "dop853.segment"]
        ticks = [it for it in items if it[0] == "dop853.ticks"]
        extrema = [it for it in items if it[0] == "dop853.extrema"]
        for it in starts + bounds + segs + ticks + extrema:
            covered.add(it[2])
        if not (len(starts) == len(bounds) == len(extrema)) or len(segs) != len(ticks):
            bad(scope, "inconsistent DOP853 record counts")
            continue
        init = next((it[3] for it in items if it[0] == "initial_state"), None)
        cursor = 0
        chain_states: list[dict[float, np.ndarray]] = []
        for (_, _, skey, s_rec), (_, _, bkey, b_rec), (_, _, ekey, e_rec) in zip(
            starts, bounds, extrema, strict=True
        ):
            b = _arr(b_rec, "bounds_s")
            horizon = float(b[-1])
            want_cuts = {0.0, *(g * grid for g in range(1, math.floor(horizon / grid) + 1))}
            want_cuts |= {x["ign"] for x in burns if x["ign"] <= horizon}
            want_cuts |= {x["cut"] for x in burns if x["cut"] <= horizon}
            if not (np.all(np.diff(b) > 0) and b[0] == 0.0 and want_cuts <= set(b.tolist())):
                bad(bkey, "segment bounds miss a grid, ignition or cutoff time")
            y = np.concatenate(
                [_arr(s_rec, "r_m"), _arr(s_rec, "v_mps"), _arr(s_rec, "propellant_kg")]
            )
            if init is not None and not (
                np.array_equal(y[:3], _arr(init, "r_m"))
                and np.array_equal(y[3:6], _arr(init, "v_mps"))
            ):
                bad(skey, "DOP853 start is not the pinned initial state")
            if y[6] != (0.0 if veh is None else veh.propellant_kg):
                bad(skey, "DOP853 start propellant is not the tank load")
            alt = [float(np.linalg.norm(y[:3])) - radius]
            states = {0.0: y.copy()}
            n = len(b) - 1
            for j in range(n):
                _, _, gkey, g = segs[cursor + j]
                _, _, tkey, t_rec = ticks[cursor + j]
                a_, b_ = float(b[j]), float(b[j + 1])
                k0, k1 = (int(x) for x in _arr(t_rec, "index_1"))
                lo_k = math.floor(a_ / dt) + 1
                cand = [q for q in range(lo_k, math.floor(b_ / dt) + 1) if a_ < q * dt <= b_]
                want_k = (cand[0], cand[-1]) if cand else (lo_k, lo_k - 1)
                if _arr(t_rec, "dt_s")[0] != dt or (k0, k1) != want_k:
                    bad(tkey, "tick index range is not the dt grid of its segment")
                tt = np.arange(k0, k1 + 1) * dt
                end = np.concatenate(
                    [_arr(g, "end_r_m"), _arr(g, "end_v_mps"), _arr(g, "end_propellant_kg")]
                )
                at = _arr(g, "anchor_ticks_m")
                burn = next((x for x in burns if x["ign"] <= a_ and b_ <= x["cut"]), None)
                if burn is None:
                    times = np.concatenate([tt, [b_]]) - a_
                    r, v = kepler_uv(y[:3], y[3:6], times, mu)
                    e_pos, e_vel = INDEP_POS_M, INDEP_VEL_MPS
                    kind = "coast"
                    if end[6] != y[6]:
                        bad(gkey, "propellant changed on a coast")
                    e0 = float(y[3:6] @ y[3:6]) / 2 - mu / float(np.linalg.norm(y[:3]))
                    e1 = float(end[3:6] @ end[3:6]) / 2 - mu / float(np.linalg.norm(end[:3]))
                    if not abs(e1 - e0) <= 1e-11 * abs(e0):
                        bad(gkey, "coast does not conserve energy")
                else:
                    path = _burn_path(y, np.concatenate([[a_], tt, [b_]]), mu, veh, burn["sign"])
                    r, v = path[1:, :3], path[1:, 3:6]
                    e_pos, e_vel = INDEP_BURN_POS_M, INDEP_BURN_VEL_MPS
                    kind = "burn"
                    want_p = burn["before"] - veh.mass_flow_kgps * (b_ - burn["ign"])
                    if not abs(end[6] - want_p) <= INDEP_MASS_KG:
                        bad(gkey, "burn propellant off the mass law")
                ep = float(np.linalg.norm(end[:3] - r[-1]))
                ev = float(np.linalg.norm(end[3:6] - v[-1]))
                et = float(np.max(np.linalg.norm(at - r[:-1], axis=1))) if at.size else 0.0
                if at.shape != (len(tt), 3):
                    bad(gkey, "anchor tick count is not the tick grid")
                    et = math.inf
                ea = float(np.linalg.norm(_arr(g, "anchor_end_r_m") - r[-1]))
                note(f"{kind} segment end m", ep), note(f"{kind} segment end m/s", ev)
                note(f"{kind} anchor ticks m", et), note(f"{kind} anchor end m", ea)
                if not (ep <= e_pos and ev <= e_vel and et <= e_pos and ea <= e_pos):
                    bad(
                        gkey,
                        f"{kind} segment differs from the independent propagation "
                        f"({ep:.3g}, {et:.3g}, {ea:.3g} m; {ev:.3g} m/s)",
                    )
                if at.size:
                    alt += list(np.linalg.norm(at, axis=1) - radius)
                y = end
                states[b_] = end.copy()
            cursor += n
            ext = _arr(e_rec, "altitude_m")
            if (float(ext[0]), float(ext[1])) != (min(alt), max(alt)):
                bad(ekey, "extrema are not the pinned ticks' extrema")
            chain_states.append(states)
        if cursor != len(segs):
            bad(scope, "DOP853 segments without a reference")

        # Node crossings: on z = 0 of the independent propagation from the reference.
        for label, _n, key, rec in items:
            if label != "orbit.node_crossings":
                continue
            covered.add(key)
            states = chain_states[0] if chain_states else {}
            ts = sorted(states)
            for c in _arr(rec, "crossings_s"):
                a_ = max((t for t in ts if t < c), default=None)
                if a_ is None:
                    bad(key, f"crossing {c} before the reference")
                    continue
                r, v = kepler_uv(states[a_][:3], states[a_][3:6], [c - a_], mu)
                note("node z m", abs(float(r[0, 2])))
                if not (abs(float(r[0, 2])) <= NODE_Z_M and v[0, 2] > 0.0):
                    bad(key, f"crossing {c} is not an ascending node (z = {r[0, 2]:.3g} m)")

    # O9: GMAT-seeded values and the committed GMAT evidence.
    limits = load_scoped_thresholds(missions=frozenset(scen))
    for name in gmat_m2.GMAT_MISSIONS:
        scenario, expected = scen[name]
        mu = scenario.constants.mu
        burns = _independent_burns(scenario, expected)
        predicted = m2.predict_burns(scenario, expected)
        horizon = scenario.stop.duration_s
        files = gmat_m2.reference_files(name)
        arcs = gmat_m2.plan_arcs(scenario, predicted, horizon)
        labelled, label_v = gmat_m2.label_rows(
            gmat_m2.parse_stream(files["report"].read_text()), arcs
        )
        if label_v:
            bad(name, f"committed GMAT rows do not label: {label_v[:3]}")
            continue
        times = sorted(labelled)
        scope = f"{name}/o9"
        recs = {
            (_split(k)[1], _split(k)[2]): (k, r)
            for k, r in records.items()
            if k.startswith(scope + "/")
        }
        lim = limits.for_validator("o9_gmat", name)
        for (label, _n), (key, rec) in sorted(recs.items()):
            covered.add(key)
            if label == "o9.arcs":
                bnd = _arr(rec, "bounds_s")
                ok = (
                    bnd.size
                    and bnd[0, 0] == 0.0
                    and bnd[-1, 1] == horizon
                    and np.all(bnd[1:, 0] == bnd[:-1, 1])
                )
                cuts = {x["ign"] for x in burns} | {x["cut"] for x in burns}
                ok = ok and {c for c in cuts if c < horizon} <= set(bnd.ravel().tolist())
                if not ok:
                    bad(key, "GMAT arcs are not a contiguous schedule over the burns")
            elif label == "o9.label_times":
                if _arr(rec, "times_s").tolist() != times:
                    bad(key, "label times are not the committed GMAT rows' schedule")
            elif label == "o9.epoch_anchor":
                import datetime as _dt

                ep = _dt.datetime.fromisoformat(scenario.epoch)
                jd = (ep - _dt.datetime(2000, 1, 1, 12)).total_seconds() / 86400.0 + 2451545.0
                want = jd - 2430000.0 - (32.184 - 0.0343817) / 86400.0
                if abs(float(_arr(rec, "a1_mjd_1")[0]) - want) * 86400.0 > 1e-6:
                    bad(key, "epoch anchor differs from the configured TT epoch in A.1")
            elif label == "o9.expected_mass":
                veh = m2.vehicle(scenario)
                want = []
                for t in times:
                    p = veh.propellant_kg
                    for x in burns:
                        if t <= x["ign"]:
                            break
                        if t >= x["cut"]:
                            p = x["after"]
                            continue
                        p = x["before"] - veh.mass_flow_kgps * (t - x["ign"])
                        break
                    want.append(veh.dry_mass_kg + p)
                err = float(np.max(np.abs(_arr(rec, "mass_kg") - want)))
                if not err <= INDEP_MASS_KG:
                    bad(key, f"expected mass differs from the mass law ({err:.3g} kg)")
            elif label == "o9.alignment_kepler":
                pass  # below, in arc order
            elif label == "o9.gmat_node_crossings":
                for c in _arr(rec, "crossings_s"):
                    a_ = max(t for t in times if t < c)
                    r, v = kepler_uv(labelled[a_].r, labelled[a_].v, [c - a_], mu)
                    note("gmat node z m", abs(float(r[0, 2])))
                    if not (abs(float(r[0, 2])) <= NODE_Z_M and v[0, 2] > 0.0):
                        bad(key, f"GMAT crossing {c} is not an ascending node")
        coast_arcs = [a for a in arcs if a.direction is None and a.start_s in labelled]
        kep = [recs[k] for k in sorted(k for k in recs if k[0] == "o9.alignment_kepler")]
        if len(kep) != len(coast_arcs):
            bad(name, f"{len(kep)} alignment records for {len(coast_arcs)} coast arcs")
        for arc, (key, rec) in zip(coast_arcs, kep, strict=False):
            in_arc = [t for t in times if arc.start_s < t <= arc.end_s]
            s0 = labelled[arc.start_s]
            r, v = kepler_uv(s0.r, s0.v, np.array(in_arc) - arc.start_s, mu)
            ep = float(np.max(np.linalg.norm(r - _arr(rec, "r_m"), axis=1))) if in_arc else 0.0
            ev = float(np.max(np.linalg.norm(v - _arr(rec, "v_mps"), axis=1))) if in_arc else 0.0
            note("gmat kepler m", ep), note("gmat kepler m/s", ev)
            if not (ep <= INDEP_POS_M and ev <= INDEP_VEL_MPS):
                bad(key, f"alignment Kepler differs from the independent propagation ({ep:.3g} m)")
        # The snapshot's DOP853 states against the committed GMAT rows (O9 gates).
        segs = sorted(
            (
                (_split(k)[2], r)
                for k, r in records.items()
                if k.startswith(scope + "/dop853.segment#")
            ),
        )
        bkey = f"{scope}/dop853.bounds#0"
        if bkey not in records:
            bad(name, "no O9 DOP853 reference")
            continue
        b = _arr(records[bkey], "bounds_s")
        pos = vel = 0.0
        compared = 0
        for t, (_, seg) in zip(b[1:], segs, strict=True):
            row = labelled.get(float(t))
            if row is None:
                continue
            pos = max(pos, float(np.linalg.norm(row.r - _arr(seg, "end_r_m"))))
            vel = max(vel, float(np.linalg.norm(row.v - _arr(seg, "end_v_mps"))))
            compared += 1
        note("dop853 vs gmat m", pos), note("dop853 vs gmat m/s", vel)
        if compared != len(times) - 1:
            bad(name, f"{compared} GMAT rows compared of {len(times) - 1}")
        if not (
            pos <= lim["gmat_vs_dop853_position_error_max_m"]
            and vel <= lim["gmat_vs_dop853_velocity_error_max_mps"]
        ):
            bad(name, f"snapshot DOP853 vs GMAT {pos:.3g} m, {vel:.3g} m/s")

    uncovered = sorted(set(records) - covered)
    if uncovered:
        bad(
            "coverage", f"{len(uncovered)} records not independently verified, e.g. {uncovered[:3]}"
        )
    for k, v in sorted(stats.items()):
        print(f"  independent agreement, max {k}: {v:.3g}")
    return problems


def cmd_verify_baseline(args: argparse.Namespace) -> int:
    data = snap.read_json(Path(args.path))
    snap._check_structure(data)
    problems = verify_baseline(data)
    print("\n".join(problems) if problems else "baseline verification: PASS")
    return 1 if problems else 0


def compare(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    ra, rb = a["records"], b["records"]
    worst: dict[str, float] = {}
    where: dict[str, str] = {}
    changed_kind = []
    for key in sorted(set(ra) & set(rb)):
        x, y = ra[key], rb[key]
        if (x["seed"], x["exact"], set(x["parts"])) != (y["seed"], y["exact"], set(y["parts"])):
            changed_kind.append(key)
            continue
        for name, part in x["parts"].items():
            other = y["parts"][name]
            if part["shape"] != other["shape"]:
                changed_kind.append(f"{key}.{name}")
                continue
            d = np.abs(np.asarray(part["values"]) - np.asarray(other["values"]))
            cls = f"{x['seed']}:{snap.unit_of(name)}{':exact' if x['exact'] else ''}"
            m = float(d.max()) if d.size else 0.0
            if m >= worst.get(cls, -1.0):
                worst[cls], where[cls] = m, f"{key}.{name}"
    return {
        "max_abs_difference_by_class": dict(sorted(worst.items())),
        "argmax_by_class": dict(sorted(where.items())),
        "only_in_first": sorted(set(ra) - set(rb)),
        "only_in_second": sorted(set(rb) - set(ra)),
        "changed_kind_or_shape": changed_kind,
    }


def cmd_compare(args: argparse.Namespace) -> int:
    a, b = (snap.read_json(Path(p)) for p in (args.first, args.second))
    result = compare(a, b)
    print(json.dumps(result, indent=2))
    structural = (
        result["only_in_first"] or result["only_in_second"] or result["changed_kind_or_shape"]
    )
    return 1 if structural else 0


def cmd_measure_deviation(args: argparse.Namespace) -> int:
    candidate = Path(args.candidate).resolve()
    proof = _load_module("m2_proof", "toolbox/validators/m2_proof.py")
    cli = _load_module("gmat_m2_cli", "toolbox/scripts/gmat_m2.py")
    saved = dict(snap.TOLERANCES)
    snap.TOLERANCES.update({k: math.inf for k in snap.TOLERANCES})
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {}
    structural: list[str] = []
    try:
        with snap.session("m2_proof", path=candidate, authenticate=False) as s:
            proof.main(["--out", str(out.with_suffix(".proof.json"))])
        results["m2_proof"] = s.report()
        structural += s.finish(complete=True)
        for name in cli.gmat_m2.GMAT_MISSIONS:
            ep = f"gmat_m2:{name}"
            with snap.session(ep, path=candidate, authenticate=False) as s:
                cli._evaluate(name)
            results[ep] = s.report()
            structural += s.finish(complete=True)
    finally:
        snap.TOLERANCES.clear()
        snap.TOLERANCES.update(saved)
    overall: dict[str, float] = {}
    for rep in results.values():
        for cls, v in rep["max_deviation_by_class"].items():
            overall[cls] = max(overall.get(cls, 0.0), v)
    summary = {
        "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "environment": _environment(),
        "max_deviation_by_class": dict(sorted(overall.items())),
        "by_entrypoint": results,
        "structural_problems": structural,
    }
    out.write_text(json.dumps(summary, indent=2) + "\n")
    print(
        json.dumps(
            {k: summary[k] for k in ("max_deviation_by_class", "structural_problems")}, indent=2
        )
    )
    return 1 if structural else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--out", required=True)
    g.add_argument("--measurement", action="store_true")
    g.set_defaults(func=cmd_generate)
    v = sub.add_parser("verify-baseline")
    v.add_argument("path")
    v.set_defaults(func=cmd_verify_baseline)
    c = sub.add_parser("compare")
    c.add_argument("first")
    c.add_argument("second")
    c.set_defaults(func=cmd_compare)
    d = sub.add_parser("measure-deviation")
    d.add_argument("candidate")
    d.add_argument("--out", required=True)
    d.set_defaults(func=cmd_measure_deviation)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
