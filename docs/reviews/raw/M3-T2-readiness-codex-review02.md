VERDICT: REQUEST_CHANGES

## Summary

Reviewed pinned HEAD `f44a94fb09101f99dc380eaf1cff701a217b79d0`, with correction scope `d8270c2..f44a94f`.

The pass resolves the principal continuity, geodetic-domain, lower-edge and trajectory-regularity defects. It preserves documentation-only scope and unresolved owner decisions.

Two proposed conditional gates remain insufficiently justified: exact geodetic reflection symmetry omits cosine evenness, and strict density decrease cites an E3 error allowance that the cited derivation does not provide in the required form. These require correction before the package passes readiness review.

No tracked files were modified. No decision is approved by this review.

## Findings

Here, **strategy** means `docs/milestones/M3-T2-validation-strategy.md`; **packet** means `docs/decisions/requests/DR-0029-P1-P9-owner-decision-packet.md`.

| ID | Severity | Location | Finding | Evidence | Proposed disposition/correction |
|---|---|---|---|---|---|
| M3T2R-R2-F1 | MAJOR | Strategy U-19, A-LM-1, B-11 | Exact z-reflection symmetry requires **cosine evenness**, which A-LM-1 does not assume. Consequently, B-11’s claim that the height sequence receives identical operands up to sign does not follow from its stated assumptions. | `t0_model.py:161–162` evaluates `p*cos(lat)`. Reflection changes `lat` to `-lat`. A-LM-1 covers hypot symmetry and sin/atan2 oddness, but not `cos(-lat) == cos(lat)`. A-FP-2 accuracy alone permits asymmetric cosine errors. The independent sensitivity computation below changes height by `9.313225746154785e-10 m` using a permitted two-ulp cosine perturbation at latitude approximately `0.6`. | Add and explicitly justify cosine evenness as a conditional assumption, or report z-reflection until an error bound is derived. Update B-11 and the conditional-gate description consistently. |
| M3T2R-R2-F2 | MAJOR | Strategy PM-4(b), B-9, G-T2-2 | The strict-decrease criterion uses “ε the E3 relative allowance,” but the cited E3 derivation supplies neither the specified two-sided relative allowance nor its extension to the input heights used in the ratio. Calling this criterion derived is unsupported. | `t0_termination.py:593–598` gives the **one-sided** enclosure `ρ̂ ≤ Fρ·exp(η₀)·ρ(h_s)·exp(θ_x X) + Nρ`, at rounded selection height `h_s`. PM-4(b) needs upper **and lower** bounds relative to the same exact formula at its two input heights. Its condition omits an explicit conversion-error treatment and the additive term. Normal output density does not eliminate those obligations. | Make strict decrease a Deliverable/reported check until a two-sided bound is written down. Alternatively derive explicit input-dependent allowances, including km conversion, constants, exponent evaluation, libm error and additive rounding terms, and prove the separation criterion from them. Retain the justified non-increase check. |
| M3T2R-R2-F3 | MINOR | Packet P4 item 8, line 219 | The first raising input is incorrectly called the “largest-magnitude negative h whose quotient is the smallest subnormal.” It is the **smallest-magnitude** negative input with a nonzero quotient. | Independent computation: both `-2.475e-321 / 1000` and the larger-magnitude input `-4.94e-321 / 1000` equal `-5e-324`. The documented trap interval and proposed guard remain correct. | Correct the extremum wording without changing the interval or tests. |

F1’s perturbation is an assumption counterexample, **not** a claim that this host’s cosine implementation exhibits asymmetry.

## Resolution of Review 01 findings

| Review 01 finding | Status | Checks and result |
|---|---|---|
| F1 — continuity at 1000 km | RESOLVED | Independently reproduced the left limit, row value, relative jump and both routes’ ±1 ulp outputs. Strategy §3.5 expressly removes continuity requirements at every base. DR-0029’s existing P5 table is unchanged; its appended amendment remains proposed. |
| F2 — E1 outside its domain | RESOLVED | Compared E1’s derivation and committed domain record with U-17/U-18, PM-5/PM-6 and packet P8. E1 is restricted to exterior points and the spike algorithm. Forward construction and negative-height comparisons are reported pending derivation. Model-ellipsoid axis/equator references are sound when evaluated exactly or with outward-rounded oracle handling. |
| F3 — strict binary64 monotonicity | PARTIALLY RESOLVED | General strict decrease was correctly replaced with non-increase conditional on exp monotonicity. Equal adjacent values and the zero tail reproduce. The remaining strict-decrease gate needs the derivation identified in R2-F2. |
| F4 — lower-domain edge | RESOLVED | Confirmed all 500 negative subnormals immediately below zero are accepted by the spike’s km route, followed by the first raising value. ±0 handling, metres-first proposed guard and separation of T0 behaviour from T2 requirements are correct. R2-F3 is a wording defect only. |
| F5 — global C² claim | RESOLVED | Checked the replacement regularity assumptions and essential-supremum chord derivation. They suffice; no perturbed-motion bound is newly claimed. Certified two-body numbers are unaffected. |
| F6 — unsupported bounds and zero cases | PARTIALLY RESOLVED | The audit substantially improves classification, domains and zero handling. B-1 and B-2 are sound on their stated structural/normal-range domains. B-3…B-8 appropriately remain Deliverables. B-10, B-12…B-15 are defensible with their qualifications. B-9 and B-11 retain the gaps identified above. |

## Evaluation items 2–7

**2. New mathematical or numerical defects.**  
R2-F1 and R2-F2 concern newly stated conditional derivations. The related corrections otherwise check out:

- U-21 correctly withdraws exact axis-normal equality: `cos(fl(π/2)) = 6.123233995736766e-17`.
- U-23 correctly separates invalid zero parameters from positive parameters whose coefficient chain produces zero under E4b.
- U-6 correctly uses IEEE equality instead of bitwise signed-zero equality.
- U-16 correctly treats transition positions as operation-sequence-specific.

For B-1, writing `a_i = c v_i(1+δ_i)` gives the stated cross-product bound and negative relative-velocity power when `c<0`. PM-1’s exact-rational margin dominates the componentwise rounding contribution. B-2’s power-of-two argument holds for a fixed homogeneous multiplication/division sequence with the stated normal, finite intermediates.

B-15’s bracket-width inequality is mathematically valid when both brackets contain the same root and each estimate lies in its bracket. Implementation should retain those brackets: the committed threshold JSON contains estimates and residuals, rather than final root brackets.

**3. Match to authoritative scientific contracts.**  
The corrected boundary treatment matches DR-0024 Q5a and DR-0025’s discontinuity-aware validation principles. P4’s fail-closed behaviour remains a proposal with the DR-0026 totality tension explicitly identified. P1–P5/P8 options and algorithm-specific numerical qualifications remain distinguishable from approvals.

The remaining conditional-gate derivation gaps conflict with the package’s own “no invented tolerance / derive before gating” rule.

**4. Unresolved decisions remain unresolved.**  
Verified P1–P9 remain OPEN with unchanged classifications:

- Ready: P1, P2, P4, P8, P9.
- Dependent: P3, P5, P7.
- Additional evidence: P6.

Q-GATE, DQ-1…DQ-6, Q-G2-1/P6, DR-0028 P6(b), and X-1 remain open. The authorization packet remains **DRAFT — NOT AUTHORIZED**. The P5 wording amendment is proposed, not adopted.

**5. Correction scope.**  
Passed local repository checks:

- Exactly 11 changed files, all under `docs/`.
- All three designated append-only files preserve their prior bytes as prefixes.
- Historical Review 01 record and raw records unchanged.
- No protected path or T0 file changed.
- Evidence-file SHA256 values match their manifest.
- Final tracked tree clean.

**6. Ready for owner decision review.**  
**Not yet as a fully validated planning package.** The decision alternatives and classifications remain usable, but the proposed validation gates need R2-F1 and R2-F2 resolved or explicitly downgraded to reported Deliverables. This does not approve or alter any owner decision or gate.

**7. Owner briefing completeness and accuracy.**  
The briefing covers all seven I-24 §3 subjects: alternatives, joint decision order, κ/v̂, fail-closed consequences, P6 evidence, gate trade-offs and approval questions. Recommendations remain labelled recommendations.

Its rounded threshold table agrees with independent calculations. Its P6 evidence gap and governing-gate discussion agree with the packet and DR-0029. The final conditional-assumptions discussion needs the cosine qualification from R2-F1. “Exact thresholds” should be understood as numerical root estimates printed to centimetres.

## Own computations

Scratch scripts and captured outputs:

- `review_scratch/review02.py` / `review02.out`
- `review_scratch/thresholds02.py` / `thresholds02.out`
- `review_scratch/symmetry02.py` / `symmetry02.out`

Executed using `.venv/bin/python -I`; scripts suppress bytecode writes and explicitly insert the T0 directory.

Selected independent output:

```text
changed_files 11 docs_only True
append-only prefix checks: all True
historical_review_diff NONE

1000_left_row_relative:
3.0190482489066533e-15
3.019e-15
-1.5981495715029756e-05

1000 km [-1 ulp, exact, +1 ulp], both routes:
[3.0190482489066557e-15, 3.019e-15, 3.0189999999999988e-15]

trap_accepted_count 500
trap_first_raise -2.475e-321
signed_zero_density 1.225
equal_adjacent True
zero_tail 0.0 0.0
base_minus_ulp_failures []

polar_delta_m:
1.7122422822420736757337280566685761876465155492753022563562E-12

axis_lat_cos:
1.5707963267948966  6.123233995736766e-17

B1_sample_failures 0
tracked_status CLEAN
```

The polar-radius calculation used 70-digit Decimal arithmetic on exact rational representations of the model constants and exact decimal WGS 84 inverse flattening.

Independent Brent root calculations reproduced the briefing’s threshold rows:

```text
κ                    B25.8 [m]    B100 [m]
2.785293563405282     54506.74     43820.78
1                    62842.26     51724.77
0.1                  78996.12     70116.76
0.01                 92282.07     84596.12
```

Maximum difference from committed full-precision estimates: `2.6193447411060333e-10 m`.

For the B-11 assumption check, retaining the spike’s computed latitude and all other final-height operations while increasing the positive-latitude cosine by two ulps produced:

```text
phi 0.6
height_original                 120000.0
height_allowed_asymmetric_cos   120000.00000000093
difference                      9.313225746154785e-10
```

At this cosine magnitude, the perturbation remains within A-FP-2’s accuracy allowance; none of A-LM-1 constrains it.

Other checks:

```text
.venv/bin/ruff check .
All checks passed!

.venv/bin/ruff format --check .
247 files already formatted
```

`git diff --check d8270c2..HEAD` reports five trailing-whitespace lines used as Markdown hard breaks. These do not affect this verdict.

## Limitations

No network, remote-head, push or CI authentication was performed. Implementer preconditions were treated as supplied claims. No M1/M2 proof scripts or complete T0 campaign were run. Finite numerical samples are corroboration, not proofs; derivation findings above follow from the stated operations and assumptions.

No fixes, approvals, commits or merges were performed. The tracked tree is clean. Per I-24, this review stops at **REQUEST_CHANGES**; no Review 03 is initiated.