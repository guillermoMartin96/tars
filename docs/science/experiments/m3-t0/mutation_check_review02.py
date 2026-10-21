"""Mutation evidence for M3T0-R2-F3, R3-F1, R4-F1, R5-F1, R5-F2, R6-F1 ... F3, R7-F1, R7-F2
R8-F1, R9-F1 and R9-F2 (research only).

Review 02 R2-F3: replacing the sweep and the stage floors with zeros passed every check in
`check_review01.py`. Review 03 R3-F1: the drag envelope ignored the computed-height error at
density discontinuities, and the Review 02 adversarial check hid it. Review 04 R4-F1: the
envelope's rounding model dropped the absolute errors of subnormal results. Review 05
R5-F1: the conversion between the ballistic coefficient and the mass was bounded by a
relative factor only; R5-F2: an empirical maximum was quoted for the wrong population.
Review 06 R6-F1: C1's b = 0 was outside the conversion bound; R6-F2: the rounding helpers
mishandled infinite and out-of-range values; R6-F3: E4b's cap was classified as
libm-independent. Review 07 R7-F1: the stage condition's non-certification was documented
as need = +inf only; R7-F2: "b_R <= b" was stated without b > 0 (both documentation
defects: the R7 mutants corrupt the implementation behind the corrected contract, or revert
the corrected text). Review 08 R8-F1: the finite need was documented without the
precondition computed h0 > beta (documentation); its reviewer also found that dropping M3
from the stage minimum passed every check (the R8 mutants hide the lower-edge rejection,
drop M3, or revert the corrected text). Review 09 R9-F1: a mutant that drops M3 only when
it is finite passed every check; R9-F2: the pole check's reference was the A (1 - F)
ellipsoid, not the model's (the R9 mutants drop a finite or positive M3, move a reference
back to A (1 - F), or revert the corrected text). This harness corrupts copies of the T0
result files, scripts, model, oracle, checks and records, runs `check_review01.py` to
`check_review09.py` on each copy, and classifies the outcome:

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
R4REV = "test_r4f1_reviewer_counterexample_is_reproduced_and_covered"
SCAN = "test_r4f1_normal_to_subnormal_transition_scan"
NEIGH = "test_r4f1_binary64_neighbours_of_the_critical_boundaries"
ZERO = "test_r4f1_zero_density_height"
STAGES4 = "test_r4f1_rk4_stages_at_high_altitude"
ENV2 = "test_r4f1_envelope_recomputed_by_a_second_implementation"
UCONST = "test_r4f1_underflow_constants_recomputed_by_a_second_implementation"
STATIC4 = "test_stage_condition_uses_the_corrected_envelope"
R5CE = "test_r5f1_review05_counterexamples_are_covered"
R5LEM = "test_r5f1_conversion_bound_holds_for_both_constructions"
R5SEC = "test_r5f1_conversion_bound_recomputed_by_a_second_implementation"
R5SWITCH = "test_r5f1_dominance_switch_between_relative_and_absolute_terms"
R5GRID = "test_r5f1_model_drag_within_envelope_for_subnormal_conversions"
R5ENV = "test_r5f1_envelope_recomputed_by_a_second_implementation"
R5SCAN = "test_r5f2_transition_scan_maximum_is_quoted_and_near_one"
R5SUB = "test_r5f2_coefficient_rounding_subset_maximum_is_quoted_with_its_scope"
R5REC = "test_r5f2_records_no_longer_scope_0983_to_the_subnormal_regime"
DR29 = "../../../decisions/requests/DR-0029-m3-t0-proposals.md"
REV04 = "../../../reviews/M3-T0-review-04.md"
REV05 = "../../../reviews/M3-T0-review-05.md"
R6CE = "test_r6f1_reviewer_counterexample_masses_are_covered"
R6SUP = "test_r6f1_zero_b_bound_covers_every_c1_mass"
R6EXH = "test_r6f1_exhaustive_small_masses_on_adversarial_shapes"
R6TRANS = "test_r6f1_transition_from_zero_b_on_each_shape"
R6FORCE = "test_r6f1_model_drag_within_envelope_at_zero_b"
R6ENV = "test_r6f1_zero_b_envelope_recomputed_by_a_second_implementation"
R6BR = "test_r6f1_zero_b_ballistic_coefficient_is_positive_and_rounded_down"
R6DOM = "test_r6f1_invalid_vehicles_are_rejected_not_bounded"
R6EXT = "test_r6f2_up_and_dn_at_extremes"
R6RAND = "test_r6f2_up_and_dn_bracket_random_rationals"
R6NONCERT = "test_r6f2_unbounded_stage_enclosure_is_an_explicit_non_certification"
R6NANEQ = "test_r6f2_float_nan_is_rejected_even_without_the_explicit_guard"
R6ENVIN = "test_r6f2_invalid_envelope_inputs_are_rejected"
R6CAP = "test_r6f3_e4b_cap_depends_on_libm_ulp"
R6CAPREC = "test_r6f3_records_classify_e4b_under_a_fp_2"
R6BSTAR = "test_switch_point_stored_and_exact_phi_are_distinguished"
R6SEARCH = "test_random_search_is_marked_unreproduced"
REV06 = "../../../reviews/M3-T0-review-06.md"
VAL = "../../../science/validation.md"
R7CE = "test_r7f1_review07_counterexample_has_finite_positive_need"
R7EARLY = "test_r7f1_early_return_need_is_minus_m2_for_every_vehicle"
R7EDGE = "test_r7f1_early_return_edge_quoted_in_the_docstring"
R7INF = "test_r7f1_unbounded_envelope_with_m2_positive_gives_infinite_need"
R7OVF = "test_r7f1_stage_value_outside_the_binary64_range_gives_infinite_need"
R7NOCERT = "test_r7f1_no_finite_bound_is_ever_certified"
R7DOC = "test_r7f1_docstring_states_both_non_certification_paths"
R7REC = "test_r7f1_records_state_both_paths"
R7BZERO = "test_r7f2_review07_counterexample_b_r_positive_at_zero_b"
R7BLEB = "test_r7f2_b_r_at_most_b_for_positive_b"
R7F2DOC = "test_r7f2_docstrings_qualify_b_r_at_most_b"
R7DOCONLY = "test_r7_correction_is_documentation_only"
R7F1_NEW = "        and need(h0) = -M2, finite and >= 0. M2 depends"
REV07 = "../../../reviews/M3-T0-review-07.md"
REPORT = "../../../milestones/M3-T0-report.md"
R8BETAGRID = "test_r8f1_beta_grid_transition_is_k9_to_k10"
R8SURF = "test_r8f1_ellipsoid_surface_raises"
R8SUCC = "test_r8f1_successive_floats_above_the_equatorial_radius"
R8CE = "test_r8f1_review08_counterexample"
R8POLE = "test_r8f1_computed_height_differs_from_mathematical_at_the_pole"
R8BETA = "test_r8f1_binary64_transition_at_beta"
R8NEG = "test_r8f1_very_negative_height_raises_decimal_error"
R8CERT = "test_r8f1_valid_finite_certification_still_returned"
R8INJ = "test_r8_first_stage_infinite_envelope_gives_infinite_need"
R8FIN = "test_r8_finite_injected_envelope_certifies"
R8DOC = "test_r8f1_docstring_states_the_lower_edge_rejection"
R8REC = "test_r8f1_records_amended"
R8LOW = (R8SURF, R8SUCC, R8CE, R8POLE, R8BETA)
REV08 = "../../../reviews/M3-T0-review-08.md"
REV09 = "../../../reviews/M3-T0-review-09.md"
R9CE = "test_r9f1_review09_counterexample"
R9BIND = "test_r9f1_finite_m3_minimum_decides_need"
R9SIGNS = "test_r9f1_m3_minimum_cases_cover_both_signs"
R9THREE = "test_r9_three_outcomes_distinguished"
R9RADIUS = "test_r9f2_model_polar_radius_is_a_sqrt_1_minus_e2"
R9REF = "test_r9f2_pole_reference_matches_the_model_ellipsoid"
R9DOC = "test_r9f2_docstrings_quote_the_model_ellipsoid"
R9REC = "test_r9_records_amended"
NEED_MIN = '    return -min(s["M2"], s["M3"], s["M4"])  # >= 0: a stage may leave the domain\n'
R7F1_OLD = "        and need(h0) = +inf, as for an unbounded envelope. M2 depends"
SCOPED = (
    "Over the coefficient-rounding subset (equatorial points from 300 km below to 10 km above "
    "the position where the model's drag coefficient rounds up from about 0.5 × 2^-1074 to "
    "2^-1074, retrograde speeds 0, 2 and 11 km/s; `check_review05.py`), the largest ratio of "
    "model drag to envelope is 0.983 (B 100; 0.953 for B 25.8)."
)
EQUIVALENT = "equivalent"
ALLOWANCE = "    alpha_sel = alpha * (1 + U) + U\n    beta_sel = beta * (1 + U) + 1000 * ETA0\n"
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
            'v = (2 * mu / (Decimal(fp["b_lower_m"]) + big_h0)).sqrt()',
            'v = (1 * mu / (Decimal(fp["b_lower_m"]) + big_h0)).sqrt()',
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
        edit_text(
            "t0_termination.py",
            ALLOWANCE,
            ALLOWANCE.replace("beta * (1 + U)", "beta * (1 + U) / 10"),
        ),
        (REVIEWER, JUMPS, BOUNDARY),
    ),
    # below the justified bound but above every observed error: no sampled point can
    # violate it, so only the recomputation of the derivation is declared
    "r3_height_allowance_slightly_below_bound": (
        edit_text(
            "t0_termination.py",
            ALLOWANCE,
            ALLOWANCE.replace("beta * (1 + U)", "beta * (1 + U) * 9 / 10"),
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
    # ---- Review 04 M3T0-R4-F1
    # the original defect: the Review 03 envelope, without the absolute (underflow) part
    "r4_absolute_part_removed": (
        edit_text(
            "t0_termination.py",
            "return _up((rel + _envelope_absolute(s, b_r, cd, area, fp)) * (1 + PAD))",
            "return _up(rel * (1 + PAD))",
        ),
        (R4REV, SCAN, NEIGH, STAGES4, ENV2),
    ),
    "r4_coefficient_underflow_term_removed": (
        edit_text(
            "t0_termination.py",
            "w_coef = eta0 * (1 + phi / b_d",
            "w_coef = 0 * eta0 * (1 + phi / b_d",
        ),
        (R4REV, SCAN, NEIGH, ENV2),
    ),
    # the term of R4-F1's mechanism: the underflow of the coefficient's last division
    "r4_coefficient_last_division_term_removed": (
        edit_text("t0_termination.py", "w_coef = eta0 * (1 + phi", "w_coef = eta0 * (0 + phi"),
        (R4REV, SCAN, NEIGH, ENV2),
    ),
    # too small for any constructed point (the coefficient term dominates): declared for
    # the second implementation of the envelope only
    "r4_density_underflow_term_removed": (
        edit_text(
            "t0_termination.py",
            'n_rho = Decimal(fp["N_rho_in_2^-1074"]) * TINY_D',
            "n_rho = 0 * TINY_D",
        ),
        (ENV2,),
    ),
    "r4_zero_density_height_too_low": (
        edit_text(
            "t0_termination.py",
            'fpa["h_zero_m"] = zero_density_height(fpa)',
            'fpa["h_zero_m"] = zero_density_height(fpa) - 2_000_000',
        ),
        (ZERO, ENV2, UCONST),
    ),
    "r4_libm_absolute_term_ignored": (
        edit_text("t0_termination.py", "    nu = libm_ulp * TINY\n", "    nu = 0 * TINY\n"),
        (UCONST, ENV2),
    ),
    # about 1e-323 m and m/s^2: declared for the recomputed constants only
    "r4_gravity_and_stage_underflow_terms_removed": (
        both(
            edit_text("t0_termination.py", "g_uf = 4 * ETA0", "g_uf = 0 * ETA0"),
            edit_text(
                "t0_termination.py",
                '"stage_abs_in_2^-1074": 2 * ETA0 / TINY',
                '"stage_abs_in_2^-1074": 0 * ETA0 / TINY',
            ),
        ),
        (UCONST,),
    ),
    "r4_height_underflow_terms_removed": (
        both(
            edit_text("t0_termination.py", "alpha = alpha_rel + h_uf_r", "alpha = alpha_rel"),
            edit_text("t0_termination.py", "beta = beta_rel + beta_uf", "beta = beta_rel"),
        ),
        (UCONST,),
    ),
    # numerically equivalent for the floors (1e-315 m/s^2 against G ~ 9.9 m/s^2): declared
    # for the static guard
    "r4_stage_condition_uses_superseded_envelope": (
        edit_text(
            "t0_termination.py",
            "env = (lambda low, s, b: drag_envelope(low, s, b, fp=fp)) if envelope is None",
            "env = (lambda low, s, b: drag_envelope_relative_only(low, s, b)) if envelope is None",
        ),
        (STATIC4,),
    ),
    "r4_oracle_density_in_binary64": (
        edit_text(
            "t0_oracle.py",
            "        return rho0 * (-(h - base) / scale).exp()\n",
            "        return D(float(rho0 * (-(h - base) / scale).exp()))\n",
        ),
        (R4REV,),
    ),
    # ---- Review 05 M3T0-R5-F1
    # the original defect: cd area / mass bounded by phi_B / b, a relative-only conversion
    "r5_conversion_bound_relative_only": (
        edit_text(
            "t0_termination.py", "    return max(phi / bq, r1, r2)\n", "    return phi / bq\n"
        ),
        (R5CE, R5LEM, R5SEC, R5SWITCH, R5GRID, R5ENV),
    ),
    # C1's quotient may underflow (subnormal b): removed, and halved
    "r5_c1_quotient_absolute_term_removed": (
        edit_text(
            "t0_termination.py",
            "max((1 + U) / bq, 1 / (bq - ETA0))",
            "(1 + U) / bq",
        ),
        (R5CE, R5LEM, R5SEC, R5SWITCH, R5GRID, R5ENV),
    ),
    "r5_c1_quotient_absolute_term_halved": (
        edit_text("t0_termination.py", "1 / (bq - ETA0))", "1 / (bq - ETA0 / 2))"),
        (R5CE, R5LEM, R5SEC),
    ),
    # C1's product may underflow (subnormal cd area): the force comparison cannot see it
    # (the coefficient's own underflow term W exceeds it); declared for the lemma checks
    "r5_c1_product_absolute_term_removed": (
        edit_text(
            "t0_termination.py",
            "p_ratio = min(max(1 / (1 - U), prod / (prod - ETA0)), prod / tiny)",
            "p_ratio = 1 / (1 - U)",
        ),
        (R5LEM, R5SEC),
    ),
    # C2's products may underflow (subnormal b cd or mass)
    "r5_c2_absolute_terms_removed": (
        both(
            edit_text(
                "t0_termination.py",
                "q_lo = max(tiny, min(bcd * (1 - U), bcd - ETA0))",
                "q_lo = bcd * (1 - U)",
            ),
            edit_text(
                "t0_termination.py",
                "min(q_lo * Fraction(area) * (1 - U), q_lo * Fraction(area) - ETA0)",
                "q_lo * Fraction(area) * (1 - U)",
            ),
        ),
        (R5LEM, R5SEC),
    ),
    # the corrected b_R applied to the relative part only
    "r5_bound_applied_to_relative_part_only": (
        edit_text(
            "t0_termination.py",
            "_envelope_absolute(s, b_r, cd, area, fp)",
            "_envelope_absolute(s, b, cd, area, fp)",
        ),
        (R5GRID, R5ENV),
    ),
    # ---- Review 05 M3T0-R5-F2: a return to the superseded characterisation
    "r5f2_superseded_sentence_restored": (
        edit_text(
            DR29,
            SCOPED,
            "The tightest observed case is where the coefficient rounds up from just above "
            "0.5 × 2^-1074. There the largest observed ratio of model drag to envelope is "
            "0.983 (B 100), an empirical figure.",
        ),
        (R5SUB, R5REC),
    ),
    "r5f2_subset_presented_as_the_subnormal_regime": (
        edit_text(
            DR29,
            "Over the coefficient-rounding subset (equatorial points",
            "In the subnormal regime (equatorial points",
        ),
        (R5SUB,),
    ),
    "r5f2_transition_scan_maximum_hidden": (
        edit_text(DR29, "it is 0.99999999999886 (B 25.8)", "it is below 0.983 (B 25.8)"),
        (R5SCAN,),
    ),
    "r5f2_review04_rewritten_instead_of_amended": (
        edit_text(
            REV04,
            "The largest observed ratio of model drag to envelope in the subnormal regime is 0.983",
            "The largest observed ratio of model drag to envelope in the coefficient-rounding "
            "subset is 0.983",
        ),
        (R5REC,),
    ),
    # ---- Review 06 M3T0-R6-F1: the original defect, b = 0 divided by
    "r6_zero_b_case_removed": (
        edit_text(
            "t0_termination.py",
            "    if b == 0.0:  # every positive binary64 mass is >= tiny\n",
            "    if False:  # mutant: b = 0 falls through to the b > 0 derivation\n",
        ),
        (R6CE, R6SUP, R6EXH, R6TRANS, R6FORCE, R6ENV, R6BR),
    ),
    # the positive-mass bound halved (as if mass >= 2 x 2^-1074)
    "r6_zero_b_bound_halved": (
        edit_text("t0_termination.py", "return max(prod / tiny,", "return max(prod / (2 * tiny),"),
        (R6CE, R6SUP, R6EXH, R6FORCE),
    ),
    # the max that keeps R non-increasing in b dropped
    "r6_zero_b_monotone_max_dropped": (
        edit_text(
            "t0_termination.py",
            "inverse_ballistic_bound(math.ulp(0.0), cd, area, phi))",
            "Fraction(0))",
        ),
        (R6SUP, R6TRANS),
    ),
    # b_R rounded the unsafe way (above phi_B / R)
    "r6_b_r_rounded_up": (
        edit_text(
            "t0_termination.py",
            "        return Decimal(q.numerator) / Decimal(q.denominator)\n",
            "        return Decimal(q.numerator) / Decimal(q.denominator)"
            ' * (1 + Decimal("1e-50"))\n',
        ),
        (R6BR,),
    ),
    # an invalid vehicle bounded instead of rejected
    "r6_domain_check_removed": (
        edit_text(
            "t0_termination.py",
            "    if not (0.0 <= b < math.inf):\n"
            '        raise ValueError(f"b = {b!r} is outside E4a\'s domain")\n',
            "",
        ),
        (R6DOM,),
    ),
    # ---- Review 06 M3T0-R6-F2
    "r6f2_up_overflow_restored": (
        edit_text(
            "t0_termination.py",
            "    if x > FLOAT_MAX:\n        return math.inf\n    if x < -FLOAT_MAX:\n"
            "        return -sys.float_info.max\n",
            "",
        ),
        (R6EXT, R6RAND),
    ),
    "r6f2_up_negative_overflow_to_minus_inf": (
        edit_text(
            "t0_termination.py",
            "        return -sys.float_info.max\n",
            "        return -math.inf\n",
        ),
        (R6EXT, R6RAND),
    ),
    # the Review 06 symptom: an infinite Decimal (the stage enclosure's -inf) raises
    "r6f2_decimal_infinity_raises": (
        edit_text(
            "t0_termination.py",
            "            return -math.inf if q.is_signed() else math.inf\n",
            '            raise OverflowError("cannot convert Infinity to integer ratio")\n',
        ),
        (R6EXT, R6NONCERT),
    ),
    # Equivalent: Fraction(nan) raises ValueError itself; the guard states the semantics
    "r6f2_float_nan_accepted": (
        edit_text("t0_termination.py", "        if math.isnan(q):\n", "        if False:\n"),
        (EQUIVALENT, R6NANEQ),
    ),
    "r6f2_negative_zero_escapes": (
        edit_text(
            "t0_termination.py",
            "    return (f if Fraction(f) >= x else math.nextafter(f, math.inf)) + 0.0\n",
            "    return f if Fraction(f) >= x else math.nextafter(f, math.inf)\n",
        ),
        (R6EXT,),
    ),
    "r6f2_infinite_speed_unhandled": (
        edit_text("t0_termination.py", "    if math.isinf(s):\n        return math.inf\n", ""),
        (R6NONCERT,),
    ),
    "r6f2_envelope_input_validation_removed": (
        edit_text(
            "t0_termination.py",
            '    if not s >= 0.0:\n        raise ValueError(f"speed bound {s!r} is not >= 0")\n',
            "",
        ),
        (R6ENVIN,),
    ),
    # ---- Review 06 M3T0-R6-F3: the cap computed without the libm allowance
    "r6f3_cap_libm_independent": (
        edit_text(
            "t0_termination.py",
            "    c0_max = (f_rho * exp_eta * rho0_max + n_rho) / 2 + ETA0\n",
            "    c0_max = ((1 + U) ** 2 * exp_eta * rho0_max + ETA0) / 2 + ETA0\n",
        ),
        (R6CAP,),
    ),
    "r6f3_amendment_removed": (
        edit_text(
            REV05,
            "### Amendment (Authorization I-8, Review 06 M3T0-R6-F3)",
            "### Note",
        ),
        (R6CAPREC,),
    ),
    # ---- records: provenance and the switch point
    "r6_random_search_mark_removed": (
        edit_text(REV04, "UNREPRODUCED", "reproduced"),
        (R6SEARCH,),
    ),
    "r6_b_star_phi_unlabelled": (
        edit_text(REV05, "1.1125369292536007e-308", "1.11e-308"),
        (R6BSTAR,),
    ),
    # ---- Review 07 M3T0-R7-F1: the contract behind the corrected documentation
    "r7f1_early_return_normalised_to_inf": (
        edit_text(
            "t0_termination.py",
            '        return -s["M2"]  # >= 0 already',
            "        return math.inf  # mutant",
        ),
        (R7CE, R7EARLY),
    ),
    "r7f1_early_return_sign_flipped": (
        edit_text(
            "t0_termination.py",
            '        return -s["M2"]  # >= 0 already',
            '        return s["M2"]  # mutant',
        ),
        (R7CE, R7EARLY, R7NOCERT),
    ),
    "r7f1_early_return_removed": (
        edit_text("t0_termination.py", '        if out["M2"] <= 0.0:', "        if False:"),
        (R7CE, R7EARLY, R7EDGE),
    ),
    "r7f1_infinite_need_clamped": (
        edit_text(
            "t0_termination.py",
            '    return -min(s["M2"], s["M3"], s["M4"])',
            '    return min(-min(s["M2"], s["M3"], s["M4"]), sys.float_info.max)',
        ),
        (R7INF, R7OVF),
    ),
    "r7f1_dn_overflow_not_outward": (
        edit_text(
            "t0_termination.py",
            "    if x < -FLOAT_MAX:\n        return -math.inf\n",
            "    if x < -FLOAT_MAX:\n        return -sys.float_info.max\n",
        ),
        (R7INF, R7OVF),
    ),
    # the corrected text reverted
    "r7f1_docstring_universal_claim_restored": (
        edit_text("t0_termination.py", R7F1_NEW, R7F1_OLD),
        (R7DOC,),
    ),
    "r7f1_docstring_edge_misquoted": (
        edit_text("t0_termination.py", "up to h0 = 55 749.393 m", "up to h0 = 56 003.395 m"),
        (R7DOC,),
    ),
    "r7f1_review06_amendment_removed": (
        edit_text(REV06, "### Amendment (Authorization I-10, Review 07 M3T0-R7-F1)", "### Note"),
        (R7REC,),
    ),
    "r7f1_val0019_body_reverted": (
        edit_text(
            VAL,
            "an envelope of +∞ certifies nothing (need ≥ 0; corrected after Review 07 "
            "M3T0-R7-F1: need = −M2, finite and ≥ 0,",
            "an envelope of +∞ certifies nothing (need = +∞; corrected after Review 07 "
            "M3T0-R7-F1: need = −M2 when",
        ),
        (R7REC,),
    ),
    "r7f1_dr0029_body_reverted": (
        edit_text(
            DR29,
            "(the stage condition then reports need ≥ 0, not certified;",
            "(the stage condition then reports need = +∞, not certified;",
        ),
        (R7REC,),
    ),
    # ---- Review 07 M3T0-R7-F2
    "r7f2_e4_summary_reverted": (
        edit_text(
            "t0_termination.py",
            "(b_R <= b for b > 0, and b_R = b wherever the conversion is\n"
            "    normal; at b = 0, b_R = phi_B / R(0) > 0, Review 07 M3T0-R7-F2):",
            "(b_R <= b; b_R = b wherever the conversion is normal):",
        ),
        (R7F2DOC,),
    ),
    "r7f2_drag_envelope_summary_reverted": (
        edit_text(
            "t0_termination.py",
            "    Both parts use b_R = phi_B / R (E4a), which",
            "    Both parts use b_R = phi_B / R <= b (E4a), which",
        ),
        (R7F2DOC,),
    ),
    "r7f2_zero_b_returns_b": (
        edit_text(
            "t0_termination.py",
            "    if b > 0.0 and r == phi / Fraction(b):\n",
            "    if b == 0.0 or r == phi / Fraction(b):\n",
        ),
        (R7BZERO,),
    ),
    "r7f2_b_r_above_b": (
        edit_text(
            "t0_termination.py",
            "    if b > 0.0 and r == phi / Fraction(b):\n        return b\n",
            "    if b > 0.0 and r == phi / Fraction(b):\n"
            "        return math.nextafter(b, math.inf)\n",
        ),
        (R7BLEB, R7DOCONLY),
    ),
    # ---- Review 08: the M3 term (the reviewer's own_M3_ignored) and the lower-edge rejection
    "r8_m3_dropped_from_the_minimum": (
        edit_text(
            "t0_termination.py",
            '    return -min(s["M2"], s["M3"], s["M4"])  # >= 0',
            '    return -min(s["M2"], s["M4"])  # mutant',
        ),
        (R8INJ,),
    ),
    "r8f1_lower_edge_clamped_to_zero": (
        edit_text(
            "t0_termination.py",
            "    if not 0.0 <= low < math.inf:\n",
            "    low = max(low, 0.0)  # mutant (NaN stays NaN)\n"
            "    if not 0.0 <= low < math.inf:\n",
        ),
        R8LOW,
    ),
    "r8f1_drag_free_skips_the_envelope": (
        edit_text(
            "t0_termination.py",
            "        a0 = one_u * (g_hat + Decimal(env(_dn(big_h0), _up(v), b))) * (1 + PAD)",
            "        a0 = one_u * (g_hat + Decimal(0 if b == math.inf else env(_dn(big_h0), "
            "_up(v), b))) * (1 + PAD)",
        ),
        R8LOW,
    ),
    # the corrected text reverted
    "r8f1_docstring_precondition_removed": (
        edit_text(
            "t0_termination.py",
            "    Every returned value needs a computed h0 > beta (beta",
            "    Every returned value is a bound (beta",
        ),
        (R8DOC,),
    ),
    "r8f1_docstring_universal_finite_claim_restored": (
        edit_text(
            "t0_termination.py",
            "    the stage condition does not return a finite need for every state outside the\n",
            "    the stage condition returns a finite need for every state outside the\n",
        ),
        (R8DOC,),
    ),
    "r8f1_docstring_vehicle_scope_dropped": (
        edit_text(
            "t0_termination.py",
            "for b = B_V1 and for the\n    drag-free b = +inf alike.",
            "for b = B_V1.",
        ),
        (R8DOC,),
    ),
    "r8f1_docstring_drag_free_unqualified": (
        edit_text(
            "t0_termination.py",
            "has a finite need on both paths for\n    h0 > beta. A non-finite",
            "has a finite need on both paths.\n    A non-finite",
        ),
        (R8DOC,),
    ),
    "r8f1_docstring_beta_misquoted": (
        edit_text("t0_termination.py", "(beta = 8.877691069434738e-09 m)", "(beta = 9.02e-09 m)"),
        (R8DOC,),
    ),
    "r8f1_review07_amendment_removed": (
        edit_text(REV07, "### Amendment (Authorization I-11, Review 08 M3T0-R8-F1)", "### Note"),
        (R8REC,),
    ),
    "r8f1_review07_false_sentence_rewritten": (
        edit_text(
            REV07,
            "Such an h0 is not the computed height of a state in the domain (outside the "
            "ellipsoid), and the docstring claims nothing for it.\n",
            "Such an h0 can be the computed height of an exterior state.\n",
        ),
        (R8REC,),
    ),
    "r8f1_review06_amendment_removed": (
        edit_text(
            REV06, "### Amendment 2 (Authorization I-11, Review 08 M3T0-R8-F1)", "### Note 2"
        ),
        (R8REC,),
    ),
    "r8f1_val0019_qualification_removed": (
        edit_text(
            VAL, "Qualified after Review 08 M3T0-R8-F1 (documentation", "Note (documentation"
        ),
        (R8REC,),
    ),
    "r8f1_dr0029_qualification_removed": (
        edit_text(
            DR29,
            " **Qualified after Review 08 M3T0-R8-F1:** every value the stage condition returns "
            "needs a computed h0 > β (8.88e-9 m);",
            " Every value the stage condition returns is finite;",
        ),
        (R8REC,),
    ),
    "r8f1_report_note_reverted": (
        edit_text(
            REPORT,
            "- R8-F1: every value the stage condition returns needs a computed h0 > β (8.88e-9 m).",
            "- R8-F1: the stage condition returns a finite need above the ellipsoid.",
        ),
        (R8REC,),
    ),
    # ---- Review 09: a finite binding M3 (R9-F1) and the pole reference (R9-F2)
    "r9f1_m3_dropped_when_finite": (  # the Review 09 reviewer's mutant
        edit_text(
            "t0_termination.py",
            NEED_MIN,
            '    if math.isfinite(s["M3"]):\n        return -min(s["M2"], s["M4"])  # mutant\n'
            + NEED_MIN,
        ),
        (R9CE, R9BIND, R9THREE),
    ),
    "r9f1_m3_dropped_when_positive": (
        edit_text(
            "t0_termination.py",
            NEED_MIN,
            '    if s["M3"] > 0.0:\n        return -min(s["M2"], s["M4"])  # mutant\n' + NEED_MIN,
        ),
        (R9BIND,),
    ),
    "r9f1_binding_cases_negative_m3_only": (
        edit_text(
            "check_review09.py",
            "    for first in (1e4, 1e5, 1e6, 1e7, 1e8)\n",
            "    for first in (1e6, 1e7, 1e8)\n",
        ),
        (R9SIGNS,),
    ),
    "r9f2_pole_reference_reverted_to_flattening": (
        edit_text(
            "check_review08.py",
            "B2_EXACT = A * A * (1 - Fraction(m.E2_WGS84))\n",
            "B2_EXACT = (A * (1 - Fraction(m.F_WGS84))) ** 2  # mutant: the A (1 - F) ellipsoid\n",
        ),
        (R8POLE, R9REF),
    ),
    "r9f2_oracle_polar_radius_from_flattening": (
        edit_text(
            "t0_oracle.py",
            "    B2 = A2 * (1 - E2)\n",
            "    B2 = (A * (1 - D(m.F_WGS84))) ** 2  # mutant\n",
        ),
        (R9REF,),
    ),
    "r9f2_docstring_quote_reverted": (
        edit_text(
            "t0_termination.py",
            "(mathematical height -2.04e-10 m on the model ellipsoid, polar\n",
            "(mathematical height -2.03e-10 m on the model ellipsoid, polar\n",
        ),
        (R9DOC,),
    ),
    "r9f2_pole_check_docstring_reverted": (
        edit_text(
            "check_review08.py",
            "    ellipsoid (mathematical height -2.04e-10 m on the model ellipsoid, polar radius\n",
            "    ellipsoid (mathematical height -2.03e-10 m on the model ellipsoid, polar radius\n",
        ),
        (R9DOC,),
    ),
    "r9f2_review07_amendment_removed": (
        edit_text(
            REV07, "### Amendment 2 (Authorization I-12, Review 09 M3T0-R9-F2)", "### Note 2"
        ),
        (R9REC,),
    ),
    "r9f2_review08_amendment_removed": (
        edit_text(REV08, "### Amendment (Authorization I-12, Review 09 M3T0-R9-F2)", "### Note"),
        (R9REC,),
    ),
    "r9f2_review07_original_sentence_rewritten": (
        edit_text(
            REV07,
            "[0, 0, fl(b)] lies inside the ellipsoid (mathematical height −2.03e-10 m) with "
            "computed height 0, and",
            "[0, 0, fl(b)] lies inside the ellipsoid (mathematical height −2.04e-10 m) with "
            "computed height 0, and",
        ),
        (R9REC,),
    ),
    "r9f2_val0019_amendment_removed": (
        edit_text(VAL, "Amended after Review 09 M3T0-R9-F2 and M3T0-R9-F1", "Note"),
        (R9REC,),
    ),
    "r9_review09_correction_section_removed": (
        edit_text(REV09, "## Correction pass (Authorization I-12", "## Notes (Authorization I-12"),
        (R9REC,),
    ),
    "r9f1_report_note_reverted": (
        edit_text(
            REPORT,
            "- R9-F1: a finite M3 that is the minimum decides need = −M3",
            "- R9-F1: M3 is checked",
        ),
        (R9REC,),
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
                str(d / "check_review04.py"),
                str(d / "check_review05.py"),
                str(d / "check_review06.py"),
                str(d / "check_review07.py"),
                str(d / "check_review08.py"),
                str(d / "check_review09.py"),
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
