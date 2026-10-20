# M3 T0 Review 05 (independent review of the R4-F1 correction pass)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a15695-d0be-7f41-a94e-8ad6e1e0dcd1`.
- **Sandbox:** `workspace-write`, no network.
- **Invocation:** `codex exec -C snap -s workspace-write --add-dir "<private GMAT copy>" --json -o codex_last_message.md - < M3-T0-codex-review05-prompt.md`.

**Reviewed commit:** **`88f9752ad03283e56f1c20d79bd28574f493e8a8`** (the validation record of the correction commit `a1feb79385a9dcba4b129a503afceebff6e7ae81`).
- The review ran in a fresh clone with its own `uv sync --locked` environment and a private GMAT R2026a copy, whose console digest matches the installation.
- The prompt was kept outside the repository during the review. It reproduces Authorization I-5 and Authorization I-4 verbatim, and points to the earlier prompts, which hold the earlier Tech Lead texts verbatim. Every commit identifier in it is a full SHA.
- CI on the reviewed commit (run 39337161329) passed all 4 jobs before the review started. The reviewer had no network and states that it did not verify CI.

**Authority:** "Authorization I-5 — M3 T0 R4-F1 Correction and Independent Review 05" (Tech Lead, 2026-10-19), §7–§8.

**Files:**
- prompt: `raw/M3-T0-codex-review05-prompt.md`;
- raw output: `raw/M3-T0-codex-review05.md`, the CLI's final message plus a trailing newline. The reviewer's saved report `review_scratch/M3-T0-codex-review05.md` differs from it only in six typographic apostrophes (’ against '). Absolute paths are redacted to `<snap>`/`<scratch>`/`<gmat>`/`<home>`/`<tmp>`; the review itself contains none;
- reviewer scripts and logs: `raw/M3-T0-codex-review05-evidence/` (`*.py.txt`; `command-ledger.md`; `execution.json`; `adversarial_runs.json`; `independent.json`; `SHA256SUMS`);
- the implementer's reproduction: `raw/M3-T0-codex-review05-evidence/implementer-reproduction/`.

**Omitted** as large or derivable:
- the reviewer's copies of the two diffs;
- its red-before tree (`c15fbd4` plus the shim) and its ten mutant trees (about 27 MB each);
- its rerun result JSON files, which it reports byte-identical to the committed ones;
- `m2.json` (the M2 validator output; `m2.log` is kept);
- `inspections.log` (1.1 MB: the full text of the inspected records at the reviewed commit; the inventory `inspected_files.json` is kept);
- `__pycache__`.

**Verdict:** **REQUEST_CHANGES**, with two new MINOR findings.

**Stop rule applied (authorization §8):**
- Every finding is recorded with its severity, and both were independently reproduced by the implementer.
- The complete output is preserved.
- **The new findings are not fixed, Review 06 is not started, and T0 is not accepted.** Authorization is requested.
- Not merged; T1 and T2 not started; DR-0029 P1–P10 and DR-0028 P6(b) not approved; branch protection and the M1/M2 baselines unchanged.

## Resolution assessed by Review 05
| Item | Review 05 | Basis (reviewer) |
|---|---|---|
| M3T0-R4-F1 | **PARTIALLY RESOLVED** | The original point and both fixed vehicles pass the underflow checks. The unrestricted conversion from vehicle parameters still fails, through R5-F1 |
| M3T0-R3-F1 | **PARTIALLY RESOLVED** | The height widening, the independent oracle and all downward-jump checks pass. The replacement global force-enclosure contract is still incomplete |
| M3T0-R2-F1 | **RESOLVED** | The rerun and the checks keep the sampled-estimate labels and separate the certified two-body result |
| M3T0-R2-F2 | **PARTIALLY RESOLVED** | The radius-product correction, the candidate maximisation and the original counterexample pass. The unrestricted global enclosure is still affected by R5-F1 |
| M3T0-R2-F3 | **RESOLVED** | The recomputing checks pass, and the mutation classification requires declared failures. The new parameter coverage gap is reported separately |
| IM-1 | **RESOLVED** | A byte-identical axis-ablation rerun reproduces 0.9856650955520649 m RMS; the procedure remains documented |
| IM-2 | **RESOLVED** | The governing bracket ends are explicit. The tests confirm that 111 511.96 m fails the condition and 111 511.97 m satisfies it |
| M3T0-F1 | **RESOLVED** | The chord/curvature reasoning remains sound; the sweep and two-body recomputation checks pass |
| M3T0-F2 | **PARTIALLY RESOLVED** | The thresholds, speed bound and counterexamples reproduce. The unrestricted sufficient-condition evidence still depends on the incomplete global contract |
| M3T0-F3 | **RESOLVED** | Reproduced stage offsets identify the k3 input as the inward stage |
| M3T0-F4 | **RESOLVED** | The GMAT rerun reproduces the corrected residual of about 6.95e-6 m, and the gates are unchanged |
| M3T0-F5 | **RESOLVED** | The records preserve the owner's gates: P10 before T1, and P1–P10 before T2 |

The reviewer states that the partial dispositions concern the unrestricted statement, not an observed failure at the two illustrative vehicles' floors.

**The reviewer also reports:**
- **A-FP-1 (mixed model):** valid for finite binary64 operations under round-to-nearest-even with gradual underflow, including the δη = 0 form, the exact underflowing sums, the non-subnormal square root, multiplication by 0.5 and the tie at half the smallest subnormal.
- **E1, E2:** the support-function, stationary-latitude and contraction argument, with its explicit underflow terms, is sound. Its own heights use a separate 90-digit foot-point **bisection**, not the committed Newton oracle; no fixed-vehicle counterexample was found.
- **E3:** N_ρ is correct. Its own decimal top-band inversion gives the exact half-subnormal onset 191 735 430.719878400062… m; the stored outward bound 191 735 430.7198785 m lies 9.468e-8 m above it. The cutoff is a derived zero-force property, not an altitude restriction.
- **E4:** W, the dot product, the square root, the products with v_rel and τ give the stated decomposition **provided the inequality mass/(cd·area) ≥ b/φ_B holds** (R5-F1). Maximising the absolute part at S_max is conservative.
- **E5, E6:** consistent with the operation order; no further defect found. The constant-only mutants protect agreement with the derivation; they are not behavioural demonstrations of errors of order 1e-323.
- **Reviewer's point:** drag 1.02021454616158e-315; superseded envelope 5.0632192e-316; corrected envelope 1.110700085e-315 m/s².
- **Floors:** the brackets are recomputed and coincide before and after the correction. The margins are 7.17072e-7 m (B 25.8), 1.00390e-6 m (B 100) and 8.42794e-7 m (drag-free). The monotonicity in h0 holds. The libm-sensitivity limits reproduce: 2^5, 2^6 and 2^7 for the published ends, and 2^19, 2^17 and 2^20 for the 2-decimal values rounded up.
- **A-FP-2:** necessary and unproved, and the records state it honestly. Neither the finite samples nor the glibc statement of intent establishes a universal bound, and the quotation could not be checked offline. A-FP-1's operating mode and A-FP-3 are probed on this host only.
- **Mutation:** all ten rerun R4 mutants fail their declared checks, with failure sets equal to the supplied matrix (8/8/8/1/3/3/1/1/1/1). The other 25 mutants were inspected but not rerun.
- **Its own runs:**
  - checks 140/140;
  - all nine T0 experiments, including GMAT, reproduce the committed bytes;
  - the M1 validator PASS, and the M2 validator PASS with 228 checks (not `--quick`);
  - the GMAT M1/M2 compares pass;
  - the seven digests match, as do the 17 VAL-0019 digest assertions;
  - red-before on `c15fbd4` with the documented shim: 17 failed, 31 passed;
  - 3 200 further constructions on both vehicles: no corrected-envelope violation, and 17 violations of the superseded envelope;
  - a partial project pytest run, interrupted at 285 passed (not a full-suite PASS).
- **Scope:** only `docs/` changed. There is no production, dependency, physics, constant, table, frame, threshold, golden, reference or M1/M2-semantics change. DR-0029 P1–P10 and DR-0028 P6(b) remain open, and the geodetic-drag discrepancy stays escalated.
- **Not verified by the reviewer:**
  - the Proof wrappers (prohibited), the complete 1185-test run, and a second fresh-clone reproduction;
  - CI (no network);
  - 25 of the 35 mutants (inspected, not rerun);
  - other platforms, a universal libm theorem, the external source provenance and remote synchronisation or protection;
  - the cause of the escalated geodetic-drag discrepancy.

## New findings
| ID | Severity | Finding (reviewer) | Implementer's independent reproduction | Disposition |
|---|---|---|---|---|
| M3T0-R5-F1 | MINOR | **The rounded ballistic-coefficient construction is not underflow-safe** (`t0_termination.py:570–571`, the claimed prerequisite; `:639`, the relative-only φ_B; `:804–806`, the public envelope contract; DR-0029 `:102` and `:453`, the unrestricted domain). The E4 derivation requires mass/(cd·area) ≥ b/φ_B. The docstring asserts that b = fl(mass/fl(cd·area)) and mass = fl(fl(b·cd)·area) supply it, but neither does when the quotient is subnormal, and the envelope's contract does not state the prerequisite. Counterexample: r = [186378137.0, 0, 0] m, v = 0, true height = computed height = 180 000 000 m, cd 2.2, area 15 m², mass 17 × 2^-1074 kg, so b = 2^-1074 in binary64 against an exact quotient of about 2.545e-324. Computed drag 9.328000516634905e26 m/s² against `drag_envelope(180000000, 0, b)` 4.805333599484291e26: **1.94117647058593×**. Position exterior, energy negative, parameters positive, every intermediate finite, exp and pow within A-FP-2. The second construction (mass = 30 × 2^-1074) gives 1.09999999999869×. The reviewer states that this is an extreme positive mass, not either illustrative vehicle, and disproves the unrestricted contract without showing an unsafe published floor | **VERIFIED** (`implementer-reproduction/repro_r5.py.txt`, `.log`). The point, with the committed `t0_model.acceleration` and `drag_envelope`, gives drag/envelope 1.941176470586 (mass 17 × 2^-1074) and 1.099999999999 (mass 30 × 2^-1074). In exact arithmetic the prerequisite fails for both: mass/(cd·area) = 2.545186660394e-324 and 4.491505871284e-324, against b/φ_B = 4.940656458412e-324. So the docstring's claim that both constructions satisfy it is false for both. The B 25.8 and B 100 vehicles (b normal) and the drag-free limit are unaffected.<br>**Root cause:** the R4-F1 class at the vehicle-parameter level. φ_B treats the conversion to B as a relative rounding (1 + u)/(1 − u)², which fails once b is subnormal, and no check exercised a subnormal b | **ACCEPTED**; not applied |
| M3T0-R5-F2 | MINOR | **The empirical maximum 0.983 is incorrectly scoped** (`docs/reviews/M3-T0-review-04.md:141`; DR-0029 `:102`; the transition scan in `check_review04.py:210` onward). The records call 0.983 the largest observed model-drag/envelope ratio "in the subnormal regime" and the coefficient-rounding point the tightest observed case. Replaying the committed scan's seed and first point gives ratios 0.999999999998695 (B 25.8, density 2.135e-308) and 0.999999999998814 (B 100, density 1.307e-308), both at subnormal densities. These are covered points, not violations | **VERIFIED** (`implementer-reproduction/repro_r5.log`). Over every subnormal-density point of the committed transition scan, the maximum is 0.999999999998859 (B 25.8, density 2.141e-308) and 0.999999999998852 (B 100, density 1.340e-308). Just below 2^-1022 the absolute terms are negligible and the ratio is the relative envelope's near-unity tightness, already present for normal densities. 0.983 is the maximum over the coefficient-rounding subset, where the absolute part matters. No floor change is implied | **ACCEPTED**; not applied |

**Implementer's preliminary observation (not a disposition and not reviewed):**
- R5-F1 needs a subnormal b: a ballistic coefficient below 2^-1022 ≈ 2.2e-308 kg/m². For normal b, the relative factor φ_B holds.
- The P1 floors are computed for B 25.8, B 100 and the drag-free limit only, and every check uses those vehicles. The published floors therefore do not depend on the defect. Their unchanged values are a property of those vehicles, not of an unrestricted lemma.
- The correction concerns the envelope's general contract, either through an absolute term in the conversion or through a stated vehicle prerequisite. The proposal below lists both. Choosing between them is the owner's scope decision.

## Proposed correction (for authorization; none applied)
1. **R5-F1, one of:**
   - (a) state the vehicle prerequisite as the envelope's exact-arithmetic condition, for example mass/(cd·area) ≥ b/φ_B checked in exact rationals from the binary64 values. Have `drag_envelope` refuse a vehicle that does not meet it. This is a disclosed restriction of the lemma, not of the model, and needs the owner's scope agreement;
   - (b) carry the conversion's absolute error by using the exact mass/(cd·area), or a derived lower bound on it, in place of b/φ_B in W and the relative factor. This keeps the domain unrestricted.

   Either way, correct the false docstring claim at `t0_termination.py:570–571`. Add the reviewer's two constructions as regressions, together with a mutant that restores the relative-only φ_B for a subnormal b. Do not change the floors or the vehicles.
2. **R5-F2:** scope 0.983 to the coefficient-rounding subset in DR-0029 P1 and in the Review 04 correction section, by an append-only correction note, as Review 04's text is preserved. Report the transition scan's near-unity maximum separately as an observation. Assert the stated maxima in a check that recomputes them.
3. **Update** DR-0029 P1/P4, VAL-0019, the T0 report and the decision matrix. Rerun the checks, mutation, M1/M2 Proof, the digests, reproducibility and CI. Any Review 06 needs authorization.

## Lessons (proposed, not yet codified)
- An underflow-aware derivation must cover every derived input, not only the state-dependent arithmetic. Here the vehicle-parameter conversion kept a relative-only factor.
- A claim such as "both constructions satisfy it" is a lemma and needs its own check at the extremes of its domain (subnormal b).
- Scope an empirical maximum to the population actually measured, and check it against every population the text names.

## Correction pass (Authorization I-6, 2026-10-19)
**Authority:** "Authorization I-6 — M3 T0 Review 05 corrections only" (Tech Lead), §1–§9. The scope is R5-F1 and R5-F2 only. T0 remains BLOCKED and NOT ACCEPTED. DR-0029 P1–P10 and DR-0028 P6(b) stay OPEN, and the GMAT geodetic-drag discrepancy stays ESCALATED_FOR_INVESTIGATION. The findings above and the reviewer's language are preserved unchanged. The superseded state is `17b2229`.

**R5-F1 approach: option (b), as decided by the Tech Lead (I-6 §1).** The envelope keeps its unrestricted domain. The conversion between the ballistic coefficient and the mass now carries its absolute floating-point error. No vehicle prerequisite is introduced, and no assumption is added or strengthened.

| ID | Disposition | Correction |
|---|---|---|
| M3T0-R5-F1 | **ACCEPTED; CORRECTED** (for an independent review to assess) | cd·area/mass is bounded by R(b, cd, area), derived for both constructions with the absolute error of every rounding that may underflow (E4a, `inverse_ballistic_bound`). The envelope uses b_R = φ_B/R ≤ b in both its relative and absolute parts. For normal conversions R = φ_B/b and b_R is the same binary64 b, so the B 25.8 and B 100 envelopes, and every termination result, are unchanged to the last bit. The false claim in the E4 docstring ("both satisfy it") is removed. The superseded envelope is kept as `drag_envelope_relative_conversion` to reproduce the finding |
| M3T0-R5-F2 | **ACCEPTED; CORRECTED** | 0.983 is scoped to the coefficient-rounding subset (0.983 for B 100, 0.953 for B 25.8) in DR-0029 P1. The transition scan's maximum at subnormal densities, 0.99999999999886 (B 25.8) and 0.99999999999885 (B 100), is stated next to it. The Review 04 record is amended by an appended note; its original row is preserved. `check_review05.py` recomputes both maxima and checks how the records quote them |

### Mathematical justification (R5-F1)
- **Operations (A-FP-1, mixed model).** The model takes the mass; the envelope takes b. T0 forms one from the other in two ways:
  - **C1 (B 25.8):** P = fl(cd·area), b = fl(mass/P).
  - **C2 (B 100):** Q = fl(b·cd), mass = fl(Q·area).

  Each of these products and quotients is (x op y)(1 + δ) + η, with |δ| ≤ u, |η| ≤ η₀ = 2^-1075 and δη = 0. A result of magnitude ≤ η₀ rounds to 0, and a positive binary64 is ≥ 2η₀.
- **C1.** A finite b with a positive mass needs P > 0. So P ≥ 2η₀ and cd·area > η₀.
  - From P: cd·area/P ≤ min(max(1/(1 − u), cd·area/(cd·area − η₀)), cd·area/(2η₀)).
  - From b: mass/P ≥ min(b/(1 + u), b − η₀), so P/mass ≤ max((1 + u)/b, 1/(b − η₀)).
  - R1 is the product of the two bounds.
- **C2.** A positive mass needs Q > 0, so Q ≥ 2η₀ and mass ≥ 2η₀.
  - Q ≥ Q_lo = max(2η₀, min(b·cd(1 − u), b·cd − η₀)).
  - mass ≥ M_lo = max(2η₀, min(Q_lo·area(1 − u), Q_lo·area − η₀)).
  - R2 = cd·area/M_lo.
- **The bound.** R = max(φ_B/b, R1, R2) holds for either construction, so no vehicle condition is needed.
  - **Normal conversions:** R1 = (1 + u)/((1 − u)b) and R2 = 1/((1 − u)²b), both below φ_B/b = (1 + u)/((1 − u)²b). So R = φ_B/b, the Review 04 bound.
  - **Where the absolute terms take over:** with the V1 shape, R1 exceeds φ_B/b exactly when b < b* = cη₀/(c − 1), with c = φ_B(1 − u): b* ≈ 7.42e-309, two thirds of 2^-1023. They also take over for a subnormal P, b·cd or mass.
  - **Monotonicity:** R is non-increasing in b, so "the bound for a B also covers every larger B" still holds.
- **Composition with the R4-F1 terms.** In E4 the vehicle enters only through cd·area/mass. That covers the relative factor F_D/(2b), the density term F_A·N_ρ/(2b), and every term of W (area/mass = (cd·area/mass)/cd and 1/mass = (cd·area/mass)/(cd·area)). Replacing φ_B/b by R in all of them is the same as evaluating the Review 04 envelope at b_R = φ_B/R. h_zero, S_max, τ and the gravity and stage terms do not depend on the vehicle. The supremum over heights, the candidate set and the monotonicity in h0 are unchanged.
- **b = +∞ (E4b).** C1 gives b = +∞ only when P = 0 (cd·area ≤ η₀), or when mass/P overflows, which is outside the domain like every overflow. With cd·area ≤ η₀ the model's force is exactly 0:
  - c₀ = fl(0.5ρ̂) ≤ 5/8, a derived constant check;
  - if area ≤ 1/4, fl(c₀·cd)·area ≤ (5/8)(1 + u)η₀ + η₀/4 < η₀, which rounds to 0;
  - otherwise cd = 2η₀ and area ≤ 1/2, so fl(c₀·cd) ≤ 2η₀ and the product with area is ≤ η₀, which rounds to 0.

  The drag-free envelope 0 therefore covers it. C2 with b = +∞ gives mass = +∞ and a zero coefficient.
- **Outward rounding.** b_R is rounded down in 60-digit decimals (ROUND_FLOOR). `_up` now returns +∞ when the exact bound exceeds the largest binary64; before, it raised OverflowError for such vehicles. That is still an upper bound, and such forces overflow, which the domain excludes.

### Effect on P1
- **Floors.** The three published floors are unchanged to the last bit: 124 456.68544510857, 118 633.50894662621 and 111 511.96182508787 m. B 25.8 and B 100 have normal conversions, so the envelope receives the same b.
- **Other results.** Every pre-existing value in `t0_termination_results.json` is bit-identical, including the root brackets of `floor_comparison` and the margins 7.2e-7, 1.0e-6 and 8.4e-7 m. Only two keys are added: `review05_counterexamples` and `zero_force_c0_max`.
- **Recommendation.** The P1 recommendation is unchanged.

### Counterexamples
At r = (186 378 137, 0, 0) m (true and computed height 180 000 000 m), v = 0, cd 2.2, area 15 m², b = 2^-1074:

| Construction | Mass | Model drag (m/s²) | Superseded envelope | Corrected envelope | Ratio before → after |
|---|---|---|---|---|---|
| C1 | 17 × 2^-1074 kg | 9.328000516634907e26 | 4.805333599484291e26 | 9.610667198968579e26 | 1.941 → 0.971 |
| C2 | 30 × 2^-1074 kg | 5.285866959426447e26 | 4.805333599484291e26 | 9.610667198968579e26 | 1.100 → 0.550 |

### A-FP status (unchanged by this pass)
- **A-FP-1** (IEEE binary64, round to nearest, gradual underflow): standard. Probed at run time on macOS x86_64 only; CI does not collect the T0 checks.
- **A-FP-2** (libm accuracy): required and unresolved. The published bounds tolerate up to 2^5 to 2^7 ulps (derived). The measured values are host measurements, not platform guarantees. E4a and E4b use no libm call.
- **A-FP-3** (dot product): standard; unchanged.

No assumption was added or strengthened.

### Evidence classification
| Class | Items |
|---|---|
| **Derived under A-FP-1** | E4a (R1, R2, R), its relative/absolute switch at b*, its monotonicity in b; E4b (zero force for cd·area ≤ η₀, with c₀ ≤ 5/8 checked from the derived constants) |
| **Numerically verified** (exact rationals, not a proof) | 243 vehicles of either construction against the exact cd·area/mass and the rounding interval of b; a second implementation of R and of the envelope; both counterexamples; the model's drag within the corrected envelope for subnormal conversions from 100 000 to 191 700 km; zero force without area at sea level and above (`check_review05.py`). Also, as implementer evidence only, an exhaustive check over masses and coefficients k × 2^-1074 (k ≤ 20 000) on eight shapes: 219 983 vehicles, no violation |
| **Empirical observations** | R5-F2: 0.983 (B 100) and 0.953 (B 25.8) over the coefficient-rounding subset; 0.99999999999886 and 0.99999999999885 over the transition scan's subnormal-density points |
| **Unresolved assumptions** | A-FP-2, as before; A-FP-1's gradual underflow and A-FP-3, probed on the host only |
| **Owner decisions still required** | DR-0029 P1–P10; whether a guarantee conditional on A-FP-2 is acceptable; how bounds are quoted (IM-2); DR-0028 P6(b); the escalated GMAT geodetic-drag discrepancy |

### Regression and mutation evidence
Evidence: `raw/M3-T0-review05-findings-correction-evidence/`.
- **Red before.** The new `check_review05.py` on the unmodified `17b2229` tree (no shim needed) fails all 17 checks:
  - 4 behavioural: both counterexamples, the force grid, and the envelope against its second implementation;
  - 4 because E4a does not exist;
  - 5 on the new E4b constant only (the force without area was already exactly 0);
  - 4 record checks.
- **Green after.** `check_review01.py` … `check_review05.py` pass 157/157.
- **Mutation.** 45 mutants plus a control, run against all five check files, in 31 min. The control passes. 44 mutants are detected by a declared check, including all 10 R4-F1 mutants rerun, and the two-body stationary-point mutant is equivalent. The R5 mutants and the checks that detect them:
  - **relative-only conversion (the original defect) and C1 quotient term removed:** the counterexamples, the lemma, its second implementation, the switch, the force grid and the envelope recomputation;
  - **C1 quotient term halved:** the counterexamples and both lemma checks;
  - **C1 product term removed, and C2 terms removed:** the lemma checks only. In the force, the coefficient's own underflow term W exceeds them;
  - **b_R applied to the relative part only:** the envelope recomputation only;
  - **the four R5-F2 record corruptions:** the R5-F2 checks.
- **A survivor in the first run.** The first mutation run left `r5f2_transition_scan_maximum_hidden` undetected. The check accepted the value anywhere in DR-0029, and the new correction log also contains it. The check now reads the P1 sentence itself, and the rerun detects the mutant. Both runs are kept in the evidence.

### R4-F1 and the related items after this pass (implementer's assessment, for an independent review)
- **Review 05's grounds.** Review 05 marked R4-F1, R3-F1, R2-F2 and F2 PARTIALLY RESOLVED. For all four, the ground it gave was the unrestricted contract failing through R5-F1. The R4-F1 regressions (48 checks) and its 10 mutants pass and are detected again on the corrected tree.
- **Remaining conditions I know of.** I know of no other condition specific to these items, but three remain:
  - the guarantee stays conditional on A-FP-2, which is unresolved;
  - the C1 overflow of mass/fl(cd·area) to +∞ is excluded only by the existing "no overflow" domain condition. This is now stated explicitly;
  - the contract covers ballistic coefficients formed by C1 or C2, the two constructions T0 uses.
- **Status.** Whether these items are now RESOLVED is for an independent review to judge. This pass does not change their status.

### Validation
Recorded in the validation commit that follows this correction commit (I-6 §9).

### Validation of the correction commit `411cabd` (appended 2026-10-19)
Evidence is in `docs/reviews/raw/M3-T0-review05-findings-correction-evidence/`. Scratch, home and temporary paths are redacted. Environment: macOS 26.2 x86_64 (the M1/M2 reference host), Python 3.12.15, the locked `uv` environment.

| Check | Result |
|---|---|
| Focused R5 checks, R4-F1 checks and the existing T0 suite | `check_review01.py` … `check_review05.py`: 157/157 pass (`checks_after.log`; again in the reproducibility clone). Red before, at `17b2229` with no shim: `check_review05.py` 17 of 17 fail (`checks05_before_17b2229.log`) |
| Mutation tests | `mutation_check_review02.py`: the control passes 157/157; 44/44 corruptions detected by a declared check, including all 10 R4-F1 mutants and the 10 new R5 mutants; 1 declared equivalent; about 31 min (`mutation_check_review05.json`). The first run, with one survivor that was explained and fixed, is kept as `mutation_run1_with_survivor.json` |
| Floors and termination results | `t0_termination_results.json` regenerated: only two keys added (`zero_force_c0_max`, `review05_counterexamples`); every other value is bit-identical, including the three floors, the root brackets and the margins (`termination_results_diff.txt`) |
| M1 Proof (`run_m1_proof.sh`, fresh clone at `411cabd`) | PASS, 9/9 steps; `working_tree_clean_excluding_evidence: yes` (`m1_proof_run.log`). A separate full pytest run in the same clone after the Proof: 1185 passed, 3 warnings (`pytest_full.log`) |
| M2 Proof (`run_m2_proof.sh`, a separate fresh clone) | PASS, 20/20 steps; m2_proof 228 PASS, 0 FAIL; clean: yes (`m2_proof_run.log`, `m2_proof_stdout.txt`) |
| Five pinned digests | All match (`pinned_digests.log`) |
| Production and protected files | `git diff --name-only 86df2c3 411cabd -- src proof toolbox scenarios tests .github uv.lock pyproject.toml` is empty |
| T0 reproducibility | A third fresh clone ran every T0 experiment twice, including the GMAT harness, `t0_height_error.py` and `t0_axis_ablation.py`. `git status` is empty after each run, so all 95 tracked experiment files are byte-identical; the checks then pass 157/157 (`reproducibility_twice.log`) |
| CI on `411cabd` | Run 39361891229 (https://github.com/guillermoMartin96/tars/actions/runs/39361891229): all four jobs succeeded (`check (ubuntu-latest)`, `check (macos-latest)`, `check (macos-15-intel)`, `m2-cross-platform`), verified via the GitHub API after completion. CI does not collect the T0 checks (`testpaths = ["tests"]`) |
| A-FP-2 | Not affected by this validation: the host measurements above are macOS x86_64 only and are not a platform guarantee |

### Amendment (Authorization I-8, Review 06 M3T0-R6-F3)
Two statements above are preserved as written: "E4a and E4b use no libm call." under A-FP-2, and the classification of E4b in the row "Derived under A-FP-1". Review 06 found the classification of E4b incomplete (M3T0-R6-F3). This amendment corrects it.
- **E4a** uses no libm call. It is derived under A-FP-1 only. That statement stands.
- **E4b's cap c₀ ≤ 5/8 depends on A-FP-2.** The cap is c₀ = fl(0.5·ρ̂) ≤ (F_ρ·e^η₀·ρ₀,max + N_ρ)/2 + η₀, with F_ρ = (1 + UF)(1 + u)² and N_ρ = (1 + u)²·ρ₀,max·ν + η₀. UF = LIBM_ULP × 2^-52 and ν = LIBM_ULP × 2^-1074 are the libm allowance of the density's exp (A-FP-2, through E3). E4b is therefore derived under A-FP-1 and A-FP-2.
- **How far it can be weakened [derived].** c₀ is affine in LIBM_ULP. It is 0.6125000000000005 at LIBM_ULP = 2 (rounded up). The cap holds while LIBM_ULP ≤ 91910196476947 (about 2^46.4), and fails above it. `rounding_allowances` refuses to derive the constants there.
  - This limit is far above the 2^5 to 2^7 ulps that the published bounds tolerate, so it does not narrow the guarantee. It is still a dependency, not libm-independence.
  - `check_review06.py` computes the limit from a second implementation and checks the boundary on either side.
- **What the zero-force result covers.** It holds for every state in the domain, under A-FP-1 and A-FP-2. A-FP-2 is not strengthened and no platform guarantee is claimed.

### Amendment (Authorization I-8, switch point b*)
The derivation above quotes "b* ≈ 7.42e-309, two thirds of 2^-1023". That is preserved as written. It does not say which φ_B it uses. Review 06 noted this. b* = cη₀/(c − 1) with c = φ(1 − u) depends on φ:
- **with the stored φ_B** (`FP["phi_B"]`, the binary64 rounded up from (1 + u)/(1 − u)², i.e. 1 + 4u; the value the envelope and `inverse_ballistic_bound` use): b* = 7.416912861690675e-309, about 2^-1022/3. This is the switch the implementation shows, and the figure quoted above;
- **with the exact φ_B** = (1 + u)/(1 − u)²: c − 1 = 2u/(1 − u), so b* = (1 + u)·2^-1023 = 1.1125369292536007e-308. This is the switch of the bound as derived on paper.

R = max(φ/b, R1, R2) is an upper bound for any φ ≥ the exact φ_B; the switch only says which term is the largest. So both figures describe valid bounds, and the implementation's is the stored one. No constant changes; `check_review06.py` checks both switches.
- **Record:** `docs/reviews/M3-T0-review-06.md`.
