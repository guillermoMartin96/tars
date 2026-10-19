"""Mutation evidence for M3T0-R2-F3 (research only).

Review 02 R2-F3: replacing the sweep and the stage floors with zeros passed every check in
`check_review01.py`. This harness corrupts copies of the T0 result files and scripts, runs
`check_review01.py` and `check_review02.py` on each copy, and classifies the outcome:

- detected:      pytest reports failures and no collection error, and at least one of the
                 checks declared for that mutant is among the failures (a failure elsewhere
                 alone is not counted as detection);
- not detected:  every check passes;
- error:         anything else (collection error, crash, or failures outside the declared
                 checks only);
- equivalent:    declared in advance as an equivalent mutant with a reason and a check that
                 establishes the equivalence. It must not be detected, and the control run
                 must pass that check.

Each corruption is applied to its own copy of `docs/` in a temporary directory; the working
tree is never modified. A negative control (no corruption) must pass every check.
Usage: uv run --no-sync python mutation_check_review02.py [out.json]
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REL = HERE.relative_to(ROOT)
TERM = "t0_termination_results.json"


def edit_json(name: str, fn: Callable[[dict], None]) -> Callable[[Path], None]:
    def apply(d: Path) -> None:
        p = d / name
        data = json.loads(p.read_text())
        fn(data)
        p.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    return apply


def edit_text(name: str, old: str, new: str) -> Callable[[Path], None]:
    def apply(d: Path) -> None:
        p = d / name
        text = p.read_text()
        if text.count(old) != 1:
            raise ValueError(f"mutation point not unique in {name}: {old!r}")
        p.write_text(text.replace(old, new))

    return apply


def sweep(fn: Callable[[dict], None]) -> Callable[[dict], None]:
    def apply(data: dict) -> None:
        for row in data["missed_crossing"]["sweep"]:
            fn(row)

    return apply


def floors(fn: Callable[[float], float]) -> Callable[[dict], None]:
    def apply(data: dict) -> None:
        for row in data["sufficient_stage_condition"]["rows"]:
            row["h_f_sufficient_at_least_m"] = fn(row["h_f_sufficient_at_least_m"])

    return apply


def reviewer_mutant(data: dict) -> None:
    """The exact Review 02 R2-F3 mutant."""
    data["missed_crossing"]["sweep"] = [{"max_dip_m": 0.0, "bound_m": 0.0}]
    data["sufficient_stage_condition"]["rows"] = [
        {"vehicle": "x", "h_f_sufficient_at_least_m": 0.0}
    ]


def relabel_perturbed_as_bound(row: dict) -> None:
    if row["physics"] == "j2drag":
        row["bound_m"] = row["sampled_estimate_m"]
        row["bound_kind"] = "certified: two-body orbit bound, maximised in closed form"
        row.pop("estimate_kind")


def drop_last_row(data: dict) -> None:
    data["missed_crossing"]["sweep"].pop()


def inflate_kepler_bound(row: dict) -> None:
    if row["physics"] == "kepler":
        row["bound_m"] *= 2.0


def shift_quadratic_rms(data: dict) -> None:
    data["fits"]["quadratic_only"]["rms_residual_m"] += 1e-3


SWEEP_DIP = "test_r2f1_stored_dip_is_recomputed_at_its_location_and_bounds_other_phases"
COVER = "test_r2f1_sweep_covers_the_declared_matrix"
LABEL = "test_r2f1_perturbed_values_are_labelled_estimates_not_bounds"
FLOOR = "test_r2f2_floors_recomputed_by_a_second_implementation"
RK4 = "test_r2f2_rk4_steps_from_bound_states_at_the_floor_stay_in_the_domain"
QUOTE = "test_r2f2_records_quote_the_recomputed_floors_and_the_corrected_derivation"
PROV = "test_provenance_rerun_reproduces_the_committed_termination_results"
ENV = "test_r2f2_envelope_bounds_adversarial_drag_points"
CEX = "test_r2f2_review02_counterexample_is_covered"
TWOBODY = "test_r2f1_certified_bound_function_matches_a_second_maximisation"
IM1 = "test_im1_axis_fit_residual_is_reproduced_from_the_committed_gmat_report"
ENDPOINT = "test_r2f1_two_body_maximum_is_at_an_endpoint_on_a_domain_scan"
EQUIVALENT = "equivalent"

# name -> (corruption, checks expected to detect it)
MUTANTS: dict[str, tuple[Callable[[Path], None] | None, tuple[str, ...]]] = {
    "control_unmodified": (None, ()),
    "json_reviewer_R2F3_mutant": (edit_json(TERM, reviewer_mutant), (COVER, SWEEP_DIP, FLOOR)),
    "json_sweep_dips_zeroed": (
        edit_json(TERM, sweep(lambda r: r.update(max_dip_m=0.0))),
        (SWEEP_DIP, PROV),
    ),
    "json_sweep_dips_halved": (
        edit_json(TERM, sweep(lambda r: r.update(max_dip_m=r["max_dip_m"] / 2))),
        (SWEEP_DIP,),
    ),
    "json_sweep_row_dropped": (edit_json(TERM, drop_last_row), (COVER, SWEEP_DIP)),
    "json_kepler_bound_inflated": (edit_json(TERM, sweep(inflate_kepler_bound)), (SWEEP_DIP,)),
    "json_perturbed_relabelled_as_bound": (
        edit_json(TERM, sweep(relabel_perturbed_as_bound)),
        (LABEL,),
    ),
    "json_floors_zeroed": (edit_json(TERM, floors(lambda h: 0.0)), (FLOOR, RK4, QUOTE)),
    "json_floors_minus_10km": (edit_json(TERM, floors(lambda h: h - 10e3)), (FLOOR, RK4)),
    "json_floors_plus_10km": (edit_json(TERM, floors(lambda h: h + 10e3)), (FLOOR, QUOTE)),
    "json_floors_in_km": (edit_json(TERM, floors(lambda h: h / 1000.0)), (FLOOR, RK4)),
    "json_im1_quadratic_rms_shifted": (
        edit_json("t0_axis_ablation_results.json", shift_quadratic_rms),
        (IM1,),
    ),
    "script_envelope_rotation_at_lower_end": (
        edit_text(
            "t0_termination.py",
            "vr = s + m.OMEGA_E * (m.A_WGS84 + h)",
            "vr = s + m.OMEGA_E * (m.A_WGS84 + low)",
        ),
        (ENV, CEX, PROV),
    ),
    "script_envelope_without_band_bases": (
        edit_text("t0_termination.py", "+ [f(base) for base in BASES_M if base > low]", "+ []"),
        (ENV, CEX, PROV),
    ),
    # Equivalent: g never has an interior maximum above both endpoints on the scanned
    # domain, so dropping the stationary points changes no output there.
    "script_two_body_without_stationary_points": (
        edit_text(
            "t0_termination.py",
            "cands += [float(z.real) for z in np.roots(coeffs) if abs(z.imag) < 1e-9 * abs(z)]",
            "pass",
        ),
        (EQUIVALENT, ENDPOINT),
    ),
    "script_sampled_label_says_certified": (
        edit_text(
            "t0_termination.py",
            'SAMPLED = "sampled estimate of dt^2/8 sup U on a numerical trajectory; not a bound"',
            'SAMPLED = "certified bound"',
        ),
        (PROV,),
    ),
    "script_stage_speed_circular": (
        edit_text(
            "t0_termination.py",
            "v = math.sqrt(2.0 * m.MU / (m.B_WGS84 + h0))  # |v0|^2",
            "v = math.sqrt(1.0 * m.MU / (m.B_WGS84 + h0))  # |v0|^2",
        ),
        (PROV,),
    ),
}


def run(name: str) -> dict:
    corruption, expected = MUTANTS[name]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        shutil.copytree(
            ROOT / "docs",
            root / "docs",
            ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"),
        )
        d = root / REL
        if corruption is not None:
            corruption(d)
        res = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "-rf",
                str(d / "check_review01.py"),
                str(d / "check_review02.py"),
            ],
            capture_output=True,
            text=True,
            cwd=root,
        )
    failed = sorted(set(re.findall(r"^FAILED \S+::(\w+)", res.stdout, re.M)))
    tail = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else res.stderr[-300:]
    if EQUIVALENT in expected:
        outcome = "equivalent" if res.returncode == 0 else "error"
    elif res.returncode == 0:
        outcome = "not detected"
    elif res.returncode == 1 and failed and set(failed) & set(expected):
        outcome = "detected"
    else:
        outcome = "error"
    return {
        "outcome": outcome,
        "expected_checks": list(expected),
        "failed_checks": failed,
        "pytest_exit": res.returncode,
        "pytest_summary": tail,
    }


def main() -> None:
    with ThreadPoolExecutor(max_workers=4) as pool:
        out = dict(zip(MUTANTS, pool.map(run, MUTANTS), strict=True))
    ok = out["control_unmodified"]["outcome"] == "not detected" and all(
        r["outcome"] in ("detected", "equivalent")
        for k, r in out.items()
        if k != "control_unmodified"
    )
    report = {"mutants": out, "control_passes_and_every_mutant_detected_or_equivalent": ok}
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(text)
    print(text)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
