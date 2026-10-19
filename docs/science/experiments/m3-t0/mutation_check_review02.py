"""Mutation evidence for M3T0-R2-F3 and M3T0-R3-F1 (research only).

Review 02 R2-F3: replacing the sweep and the stage floors with zeros passed every check in
`check_review01.py`. Review 03 R3-F1: the drag envelope ignored the computed-height error at
density discontinuities, and the Review 02 adversarial check hid it. This harness corrupts
copies of the T0 result files, scripts, model and oracle, runs `check_review01.py`,
`check_review02.py` and `check_review03.py` on each copy, and classifies the outcome:

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


def both(*edits: Callable[[Path], None]) -> Callable[[Path], None]:
    def apply(d: Path) -> None:
        for edit in edits:
            edit(d)

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
REVIEWER = "test_r3f1_reviewer_counterexample_is_reproduced_and_covered"
JUMPS = "test_r3f1_counterexamples_at_every_downward_jump_are_covered"
BOUNDARY = "test_r3f1_boundary_points"
DERIV = "test_r3f1_derivation_constants_are_recomputed_by_a_second_implementation"
SELFTEST = "test_oracle_detects_the_r3f1_defect"
AGREE = "test_oracles_agree"
STATIC = "test_oracle_does_not_use_the_model_height_or_band_code"
GUARD = "test_review02_adversarial_check_no_longer_adapts_its_bound_to_the_model_height"
FLOOR3 = "test_r3f1_floors_recomputed_by_a_second_implementation"
EQUIVALENT = "equivalent"
ALLOWANCE = "    alpha_sel = alpha * (1 + U) + U\n    beta_sel = beta * (1 + U)\n"
ORACLE_DOC = (
    '    """Exact-arithmetic geodetic height of the binary64 point r (outside the ellipsoid)."""\n'
)
NO_ALLOWANCE = (
    "    alpha, beta = 0 * alpha, 0 * beta\n    alpha_sel, beta_sel = 0 * alpha, 0 * beta\n"
)
REVERT02 = (
    "check_review02.py",
    "                    true_h = tt._dn(o.true_height(r))",
    "                    true_h = height(r)  # reverted: the model's own height",
)

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
            "vr = Decimal(s) + w * (a + (h + be) / (1 - al))",
            "vr = Decimal(s) + w * (a + (Decimal(low) + be) / (1 - al))",
        ),
        (ENV, CEX, PROV),
    ),
    "script_envelope_without_band_bases": (
        edit_text(
            "t0_termination.py",
            "for h in [ell] + [row[0] for row in DEC_TABLE if row[0] > ell]:",
            "for h in [ell]:",
        ),
        (ENV, CEX, PROV),
    ),
    # Equivalent: every stationary point of g is a minimum (Review 03's proof: g' = 0 is
    # F(r) = 0 with F' > 0 for r > 85 396 m), so dropping them changes no output.
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
            'v = (2 * mu / (Decimal(FP["b_lower_m"]) + big_h0)).sqrt()',
            'v = (1 * mu / (Decimal(FP["b_lower_m"]) + big_h0)).sqrt()',
        ),
        (PROV, FLOOR3),
    ),
    # ---- Review 03 M3T0-R3-F1
    "r3_height_allowance_removed": (
        edit_text(
            "t0_termination.py",
            ALLOWANCE,
            NO_ALLOWANCE,
        ),
        (REVIEWER, JUMPS, BOUNDARY, DERIV),
    ),
    # below the observed error (beta_sel / 10 ~ 9e-10 m < 9.3e-10 m at the reviewer's point):
    # behavioural checks only are declared
    "r3_height_allowance_below_observed_error": (
        edit_text("t0_termination.py", ALLOWANCE, ALLOWANCE.replace("(1 + U)\n", "(1 + U) / 10\n")),
        (REVIEWER, JUMPS, BOUNDARY),
    ),
    # below the justified bound but above every observed error: no sampled point can
    # violate it, so only the recomputation of the derivation is declared
    "r3_height_allowance_slightly_below_bound": (
        edit_text(
            "t0_termination.py", ALLOWANCE, ALLOWANCE.replace("(1 + U)\n", "(1 + U) * 9 / 10\n")
        ),
        (DERIV,),
    ),
    "r3_model_exact_base_in_band_below": (
        edit_text(
            "t0_model.py", "if h_km < table[i + 1].base_km:", "if h_km <= table[i + 1].base_km:"
        ),
        (BOUNDARY,),
    ),
    "r3_envelope_band_of_unwidened_limit": (
        edit_text(
            "t0_termination.py",
            "DEC_TABLE[max(i for i, r in enumerate(DEC_TABLE) if r[0] <= h)]",
            "DEC_TABLE[max(i for i, r in enumerate(DEC_TABLE) if r[0] <= max(h, Decimal(low)))]",
        ),
        (REVIEWER, JUMPS, BOUNDARY),
    ),
    "r3_envelope_lower_limit_unwidened": (
        edit_text(
            "t0_termination.py",
            "ell = max((1 - al) * Decimal(low) - be, Decimal(0))",
            "ell = max(Decimal(low), Decimal(0))",
        ),
        (REVIEWER, JUMPS, BOUNDARY),
    ),
    "r3_oracle_returns_the_model_height": (
        edit_text(
            "t0_oracle.py", ORACLE_DOC, ORACLE_DOC + "    return D(m.geodetic_iterative(r)[1])\n"
        ),
        (SELFTEST, STATIC, AGREE),
    ),
    "r3_review02_oracle_reverted_to_model_height": (edit_text(*REVERT02), (GUARD,)),
    # the reverted Review 02 check alone is blind to the defect; check_review03 is not
    "r3_allowance_removed_and_review02_oracle_reverted": (
        both(
            edit_text(
                "t0_termination.py",
                ALLOWANCE,
                NO_ALLOWANCE,
            ),
            edit_text(*REVERT02),
        ),
        (REVIEWER, JUMPS, BOUNDARY),
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
                str(d / "check_review03.py"),
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
