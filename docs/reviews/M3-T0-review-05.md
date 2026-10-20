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
