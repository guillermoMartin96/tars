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
    problems = verify_baseline(data)
    if problems and not args.measurement:
        print("baseline verification failed:\n" + "\n".join(problems), file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    snap.write_json(out, data)
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


def _chains(records: dict[str, dict[str, Any]]) -> dict[str, list[tuple[str, dict]]]:
    """DOP853 records grouped by scope, in call order."""
    out: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    for key, rec in records.items():
        prefix, _, n = key.rpartition("#")
        scope, _, label = prefix.rpartition("/")
        if label.startswith("dop853."):
            out[scope].append((f"{label}#{int(n):09d}", rec))
    return {k: sorted(v, key=lambda x: (x[0].split("#")[0], x[0])) for k, v in out.items()}


def _arr(rec: dict, name: str) -> np.ndarray:
    part = rec["parts"][name]
    return np.asarray(part["values"], dtype=float).reshape(part["shape"])


def _energy_h(r: np.ndarray, v: np.ndarray, mu: float) -> tuple[float, np.ndarray]:
    return float(v @ v) / 2.0 - mu / float(np.linalg.norm(r)), np.cross(r, v)


def verify_baseline(data: dict[str, Any]) -> list[str]:
    """Independent checks on the snapshot's own values (DR-0021 condition 2).

    1. GMAT evidence: every O9 DOP853 state at a GMAT row agrees with the committed
       GMAT report within the O9 gates (3e-5 m, 3.5e-8 m/s); every pinned GMAT-seeded
       Kepler state agrees with its GMAT row within the alignment gates.
    2. Physics: along every DOP853 chain, two-body energy and angular momentum are
       conserved on coast segments (relative 1e-11; DOP853 rtol 1e-13 over <= 60 s),
       propellant is constant on coasts and non-increasing in burns, each segment end
       agrees with its anchor (F47 limits), and the pinned altitude extrema are those of
       the pinned anchor ticks.
    """
    from tars.validation import gmat_m2, m2
    from tars.validation.m2_missions import MISSIONS
    from tars.validation.thresholds import load_scoped_thresholds

    problems: list[str] = []
    records = data["records"]
    by_name = {m.name: m for m in MISSIONS}
    scenario0 = MISSIONS[0].build()
    mu, radius = scenario0.constants.mu, scenario0.constants.equatorial_radius
    limits = load_scoped_thresholds(missions=frozenset(by_name))

    # 2. Physics along every chain.
    for scope, items in _chains(records).items():
        bounds = [rec for label, rec in items if label.startswith("dop853.bounds")]
        segments = [rec for label, rec in items if label.startswith("dop853.segment")]
        starts = [rec for label, rec in items if label.startswith("dop853.start")]
        extrema = [rec for label, rec in items if label.startswith("dop853.extrema")]
        # Several references can share a scope (e.g. an audit and its O8 final): walk
        # them in call order, splitting the segments by each call's bound count.
        cursor = 0
        for k, (b_rec, s_rec) in enumerate(zip(bounds, starts, strict=True)):
            b = _arr(b_rec, "bounds_s")
            n = len(b) - 1
            segs = segments[cursor : cursor + n]
            cursor += n
            if len(segs) != n:
                problems.append(f"{scope}: reference {k}: {len(segs)} segments for {n} bounds")
                continue
            y = np.concatenate(
                [_arr(s_rec, "r_m"), _arr(s_rec, "v_mps"), _arr(s_rec, "propellant_kg")]
            )
            alt = [float(np.linalg.norm(y[:3])) - radius]
            for j, seg in enumerate(segs):
                end = np.concatenate(
                    [_arr(seg, "end_r_m"), _arr(seg, "end_v_mps"), _arr(seg, "end_propellant_kg")]
                )
                coast = _arr(seg, "anchor_end_propellant_kg").size == 0
                where = f"{scope}: reference {k} segment {j} [{b[j]}, {b[j + 1]}]"
                if coast:
                    e0, h0 = _energy_h(y[:3], y[3:6], mu)
                    e1, h1 = _energy_h(end[:3], end[3:6], mu)
                    if not (
                        abs(e1 - e0) <= 1e-11 * abs(e0)
                        and np.linalg.norm(h1 - h0) <= 1e-11 * np.linalg.norm(h0)
                    ):
                        problems.append(f"{where}: coast does not conserve energy/momentum")
                    if end[6] != y[6]:
                        problems.append(f"{where}: propellant changed on a coast")
                    pos_tol, vel_tol = m2.ANCHOR_POS_TOL_M, m2.ANCHOR_VEL_TOL_MPS
                else:
                    if not end[6] <= y[6]:
                        problems.append(f"{where}: propellant increased in a burn")
                    pos_tol, vel_tol = m2.ANCHOR_BURN_POS_TOL_M, m2.ANCHOR_BURN_VEL_TOL_MPS
                a_r, a_v = _arr(seg, "anchor_end_r_m"), _arr(seg, "anchor_end_v_mps")
                if not (
                    np.linalg.norm(end[:3] - a_r) <= pos_tol
                    and np.linalg.norm(end[3:6] - a_v) <= vel_tol
                ):
                    problems.append(f"{where}: segment end disagrees with its anchor")
                ticks = _arr(seg, "anchor_ticks_m")
                if ticks.size:
                    alt += list(np.linalg.norm(ticks, axis=1) - radius)
                y = end
            if k < len(extrema):
                ext = _arr(extrema[k], "altitude_m")
                if (float(ext[0]), float(ext[1])) != (min(alt), max(alt)):
                    problems.append(f"{scope}: reference {k}: extrema are not the ticks' extrema")

    # 1. GMAT evidence.
    for name in gmat_m2.GMAT_MISSIONS:
        mission = by_name[name]
        scenario = mission.build()
        predicted = m2.predict_burns(scenario, mission.expected)
        horizon = scenario.stop.duration_s
        files = gmat_m2.reference_files(name)
        arcs = gmat_m2.plan_arcs(scenario, predicted, horizon)
        labelled, label_v = gmat_m2.label_rows(
            gmat_m2.parse_stream(files["report"].read_text()), arcs
        )
        if label_v:
            problems.append(f"{name}: committed GMAT rows do not label: {label_v[:3]}")
            continue
        lim = limits.for_validator("o9_gmat", name)
        scope = f"{name}/o9"
        items = _chains(records).get(scope, [])
        bounds = [r for label, r in items if label.startswith("dop853.bounds")]
        segs = [r for label, r in items if label.startswith("dop853.segment")]
        if len(bounds) != 1:
            problems.append(f"{name}: expected one O9 DOP853 reference, found {len(bounds)}")
            continue
        b = _arr(bounds[0], "bounds_s")
        pos = vel = 0.0
        compared = 0
        for t, seg in zip(b[1:], segs, strict=True):
            row = labelled.get(float(t))
            if row is None:
                continue
            pos = max(pos, float(np.linalg.norm(row.r - _arr(seg, "end_r_m"))))
            vel = max(vel, float(np.linalg.norm(row.v - _arr(seg, "end_v_mps"))))
            compared += 1
        if compared != len(labelled) - (1 if 0.0 in labelled else 0):
            problems.append(f"{name}: {compared} GMAT rows compared of {len(labelled)}")
        if not (
            pos <= lim["gmat_vs_dop853_position_error_max_m"]
            and vel <= lim["gmat_vs_dop853_velocity_error_max_mps"]
        ):
            problems.append(f"{name}: snapshot DOP853 vs GMAT {pos:.3g} m, {vel:.3g} m/s")
        kep = [
            rec for key, rec in records.items() if key.startswith(f"{scope}/o9.alignment_kepler#")
        ]
        times = sorted(labelled)
        k_pos = k_vel = 0.0
        coast_arcs = [a for a in arcs if a.direction is None and a.start_s in labelled]
        if len(kep) != len(coast_arcs):
            problems.append(
                f"{name}: {len(kep)} alignment records for {len(coast_arcs)} coast arcs"
            )
        for arc, rec in zip(coast_arcs, kep, strict=False):
            in_arc = [t for t in times if arc.start_s < t <= arc.end_s]
            for t, r, v in zip(in_arc, _arr(rec, "r_m"), _arr(rec, "v_mps"), strict=True):
                k_pos = max(k_pos, float(np.linalg.norm(labelled[t].r - r)))
                k_vel = max(k_vel, float(np.linalg.norm(labelled[t].v - v)))
        if not (
            k_pos <= lim["coast_vs_kepler_position_error_max_m"]
            and k_vel <= lim["coast_vs_kepler_velocity_error_max_mps"]
        ):
            problems.append(f"{name}: snapshot Kepler vs GMAT {k_pos:.3g} m, {k_vel:.3g} m/s")
        print(
            f"{name}: snapshot DOP853 vs GMAT max {pos:.3g} m / {vel:.3g} m/s over {compared} "
            f"rows; Kepler vs GMAT max {k_pos:.3g} m / {k_vel:.3g} m/s"
        )
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
