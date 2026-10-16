# M3 planning checkpoint — independent review 06 (targeted)

**Scope:** the correction authorized by the Tech Lead's instruction "M3 Planning — M3P5-F1 Correction and Review 06" (I-5), in commit `bcb7f9b`. The review covered:
- the M3P5-F1 sign correction (DR-0028 "Resolution amendment 2");
- the new signed verification script `dr0028_node_signed_verification.py`;
- regression, planning-package consistency and authorization boundaries.

No M3 implementation exists.

**Reviewer:** Codex (separate provider), session `01a1462d-c55d-7be2-ae77-20d277db48a2`, run at `2ec8f87` on a git clone with metadata.

**Prompt and output:**
- Prompt: `raw/M3-planning-codex-review06-prompt.md`. It carries I-1 to I-5 verbatim, the full review history and the implementer's validation evidence, and instructs independent derivation and mutation.
- Raw output: `raw/M3-planning-codex-review06.md`.

**Instruction for this outcome (I-5 §5):** "If Codex returns REQUEST_CHANGES: Record the findings. Do not fix them. Do not start review 07. Stop for my decision."
- **No finding below has been applied.**
- No further review has been run.
- The planning branch is not merged, T0 has not begun, and M3 planning is not accepted.

## Verdict
**REQUEST_CHANGES:** three MINOR findings, with no BLOCKER or MAJOR finding.
- **The M3P5-F1 correction itself is confirmed.** The reviewer independently derived Δi = −δ cos(Ω − φ) and ΔΩ = +δ cot i sin(Ω − φ) with its own matrix, R_z(φ) R_x(−δ) R_z(−φ), and found them consistent with DR-0024's passive transformation.
- **What the findings concern:** one exact-result statement in amendment 2 that lacks its domain, and two weaknesses in the new verification script.

**The reviewer confirmed independently:**
- **Signs and derivation:** confirmed as above.
- **Perpendicular-axis closed form:** within 8.7e-16 over 1000 cases.
- **Review-04 example:** ΔΩ = +0.259805543688°, Δi = +0.000340085438°.
- **The signed script:**
  - exit 0, with byte-identical JSON;
  - sample counts reproduced: 506 order samples for Δi, 532 for ΔΩ, 1064 sign checks;
  - the grid, the orders and the tolerance treatment are sound.
- **Mutations:**
  - the reviewer's own live mutations (Δi sign, ΔΩ sign) gave exit 1, with 1120 and 1008 failing checks;
  - a zero-formula mutant was also rejected.
- **Research reruns:** `dr0028_node_sensitivity.py` and `q10_residual_consequences.py` reproduce byte-for-byte. All 27 atmosphere jumps were recomputed with zero discrepancy.
- **Local regression:**
  - pytest: 1185 passed;
  - M1 Proof 7/7 and M2 Proof 228/228;
  - cross-platform check and both GMAT comparisons;
  - M1 golden differences zero.
- **History:**
  - only three index/status lines removed since `cf0e24f`;
  - earlier review records intact, including the 558-byte Q4 row;
  - registers additions only (218/0, 43/0).
- **Consistency:** J-ax-1, the identity transformation, co-rotation, FC-1…FC-10, the constants, the digests, the local-solar-time correction, earlier dispositions and the authorization boundaries are intact. Docs only; Ruff and links pass.
- **Not verified by the reviewer:** CI (no GitHub API access).

## Dispositions (recorded; none applied)

### M3P6-F1 (MINOR, mathematical consistency): exact line-of-nodes result needs a domain restriction
**Where:** DR-0028 "Resolution amendment 2", the exact-results table row "Tilt about the line of nodes (φ = Ω), any finite δ", and verification property E2.

**Finding.** For φ = Ω, ĥ_B = (sin(i − δ) sin Ω, −sin(i − δ) cos Ω, cos(i − δ)). So Δi = −δ and ΔΩ = 0 hold only while 0 < i − δ < π. If the tilt carries the orbit across the equator, the inclination folds back and the node changes by 180°. The E2 grid never crosses that boundary, so it cannot validate the unrestricted "any finite δ".

**Disposition: ACCEPTED.**
- Implementer's check with the committed oracle: i = 2°, Ω = φ = 0, δ = +5° gives Δi = +1.000000° and ΔΩ = −180.000000°, not −5° and 0.
- The statement is true only on the stated domain.

**Proposed change (not made):**
- Append a linked correction: "for 0 < i − δ < π"; at an endpoint the orbit is equatorial in B and the node is undefined; beyond it, i_B = |i − δ| (folded) and ΔΩ = ±180°.
- Add crossing and endpoint cases to E2.

### M3P6-F2 (MINOR, verification adequacy): E5's node-jump result is reported but never asserted
**Where:** `dr0028_node_signed_verification.py`, `exact_properties()`, E5.

**Finding.** The script records the largest node jump at i = 0.1°, δ = 0.15° (180°). It never asserts that value, and never requires defined samples. When the reviewer forced a zero node change at that inclination, the script still exited 0 with verdict PASS.

**Disposition: ACCEPTED.** Implementer's check: of the script's `failures.append` calls, the only E5 one concerns the equatorial node being undefined; there is no jump assertion. The DR-0028 amendment 2 text lists E5 among the "exact properties" as if it were checked.

**Proposed change (not made):**
- Assert the jump against the analytic value, with a documented tolerance.
- Require a minimum number of defined samples.
- Demonstrate that suppressing the jump makes the script exit 1.

### M3P6-F3 (MINOR, mathematical consistency): the implemented wrapping interval contradicts the declared convention
**Where:** `dr0028_node_signed_verification.py`, `wrap()`, compared with its module docstring and DR-0028 amendment 2 ("ΔΩ wrapped to (−π, π]").

**Finding.** `wrap()` returns values in [−π, π): wrap(+π) = wrap(−π) = −π. In the crossing example of M3P6-F1, the oracle returns −180° where the declared interval requires +180°. E5 takes absolute values, which hides the difference.

**Disposition: ACCEPTED.** The implementer reproduced wrap(+π) = wrap(−π) = −3.141592653589793. The first-order checks are not affected, because their ΔΩ values are far from ±π, but the oracle and its declared convention disagree.

**Proposed change (not made):** make `wrap()` return values in (−π, π], and check both antipodal endpoints explicitly.

## Validation evidence at the reviewed commits (implementer)
- **`bcb7f9b`**, isolated clone:
  - M1 Proof overall PASS (exit 0), including full pytest: 1185 passed;
  - M2 Proof overall PASS (21 steps, exit 0);
  - regenerated evidence differs only in run metadata.
- **CI** for `bcb7f9b`: run 38947344104, all jobs success.
- **Worktree checks:** docs only; registers 218/0 and 43/0; relative links (0 broken); Ruff pass; all research scripts reproduce byte-for-byte; live sign mutations exit 1.

## Status after this review
- This is not an unconditional PASS, so the I-5 §5 stop condition applies.
- **No acceptance report has been prepared.** The branch is not ready for acceptance, it is not merged, and T0, T1 and T2 have not started.
- **Returned to the Tech Lead:** authorization to correct M3P6-F1 to F3, and whether to run review 07.
