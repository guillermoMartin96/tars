# M3 Planning Review 08 (independent)

**Scope:** the correction authorized by the Tech Lead's instruction "Continue the TARS spacecraft simulator M3 planning work from branch `milestone-3-planning`, currently at commit `0dac6d3`" (I-7), in commit `cf9f3d6`. That is M3P7-F1: the domain of `wrap()` is restricted to finite angles, and non-finite inputs raise ValueError. The review also covered regression protection, the whole DR-0028 amendment chain, the preservation gates, and planning readiness. No M3 implementation exists.

**Reviewer:** Codex (separate provider), session `01a1475a-cd67-7790-9bf9-48e0b5357833`, run at `491ef77` on a git clone with metadata.

**Prompt and output:**
- Prompt: `raw/M3-planning-codex-review08-prompt.md`. It carries I-1 to I-7 verbatim, the full review history, the M3P7-F1 correction, the M1/M2 preservation evidence and the decision state. It instructs the reviewer not to accept earlier conclusions.
- Raw output: `raw/M3-planning-codex-review08.md`.

**Instruction for this outcome (I-7 §5):** "If review 08 returns REQUEST_CHANGES: Record every finding with severity, evidence, and proposed disposition. Do not automatically fix findings. Do not initiate review 09. Do not prepare a planning acceptance report. Stop and request my decision."
- **The finding below has not been applied.**
- No review 09 has been started, and no acceptance report has been prepared.
- The planning branch is not merged, and T0, T1 and T2 have not begun.

## Verdict
**REQUEST_CHANGES:** one new MINOR finding, with no BLOCKER or MAJOR finding. **M3P7-F1 is RESOLVED.**

| ID | Disposition (reviewer) | Reviewer's evidence |
|---|---|---|
| M3P7-F1 | **RESOLVED** | The docstring and amendment 4 restrict the contract to finite floats. Both NaN signs and ±∞ raise the guard's ValueError. 249 901 finite inputs match the `f999626` wrap bit-for-bit and the exact rational reduction, and ±π map to +π |

### The reviewer also confirmed independently
- **Determinism and regression:** two runs are byte-identical. Every pre-existing JSON value and every earlier mutant failure count is unchanged.
- **Mutations:** each of the requested mutations exits 1:
  - guard removed; guard test weakened to type-only; non-finite tests disabled;
  - either historical defect restored;
  - E5a, E5b or E5c removed;
  - either formula sign reversed.
- **Mathematics:** the reviewer derived independently:
  - the signed formulas;
  - the five line-of-nodes regimes, the endpoints and the node reversal;
  - the perpendicular-axis closed form and the inclination bound.

  20 000 cases checked with an independent implementation agree to 4.44e-16 (matrix) and 1.14e-15 (closed form). The i = 2°, δ = 5° counterexample reproduces as Δi = +1°, ΔΩ = 180°. The tolerance derivations were reviewed.
- **Research reruns and atmosphere:** byte-identical; 27 jumps within 1.11e-16.
- **History and scope:**
  - records 01–07 are unchanged or appended only, and the 558-byte Q4 quotation is intact;
  - registers 218/0 and 43/0;
  - DR-0024…0027, ADR-0009, the constants, the digests and the protected paths are unchanged;
  - `docs/` only.
- **Preservation gates:**
  - m1_proof 7/7, and the full m2_proof 228/228;
  - both GMAT comparisons, the snapshot verify-baseline and the cross-platform golden check;
  - M1 determinism and all four M2 determinism checks; golden differences zero.
- **Partial or unavailable, as the reviewer reported:**
  - its pytest run was interrupted after 256 passed, so it is not a full-suite run;
  - the complete Proof wrapper scripts and three-platform execution were not rerun;
  - CI could not be checked (no GitHub API access);
  - external source bytes were not retrieved.

## Dispositions (recorded; not applied)

### M3P8-F1 (MINOR, verification adequacy): non-finite inclination predictions can pass the signed verification
**Where:** `dr0028_node_signed_verification.py`, `check_formulas()` (order and sign checks) and the overall verdict.

**Finding.** The order check runs only when both errors are ≥ tol, and the sign check only when |lin| ≥ tol. Comparisons with NaN are false, so a formula returning NaN skips both checks without any failure. The verdict requires no failures, but it does not require any coverage for each formula component.

The reviewer's counterexample replaced only the inclination formula with `math.nan`:

| Output | Value |
|---|---|
| Exit code | 0 |
| Verdict | PASS |
| `order_samples_delta_i` | 0 |
| `order_samples_delta_node` | 532 |
| Sign checks | 504 |
| Failures | none |

All built-in mutants were still rejected.

**Disposition: ACCEPTED.** The implementer reproduced it independently with the same substitution: exit 0, verdict PASS, 0 inclination order samples, 504 sign checks.
- **Scope of the gap:** it is a verification-adequacy gap, not a mathematical error. The committed formulas are finite and correct, and their PASS is genuine: 506 and 532 order samples, 1064 sign checks.
- **Why mutation testing missed it:** every existing mutant produces finite values, so none exercised the gap.

**Proposed change (not made):**
- Treat any non-finite oracle result, formula result or error in the first-order checks as a failure, before the conditional comparisons.
- Require a justified minimum coverage for each component, for example at least the committed 506 and 532 order samples and 1064 sign checks, or a documented lower bound.
- Add a NaN-inclination mutant, and preferably a NaN-node one, that must make the script exit 1.
- Keep the tolerances and historical evidence unchanged.

## Validation evidence at the reviewed commits (implementer)
- **`cf9f3d6`**, isolated clone:
  - M1 Proof PASS, with full pytest (1185 passed);
  - M2 Proof PASS (21 steps, exit 0), with the GMAT M1/M2 comparisons, the reference-snapshot verify-baseline, cross-platform, determinism and m2_proof;
  - the evidence differs only in run metadata, and `toolbox/`, `tests/`, `scenarios/` and `src/` are unchanged.
- **CI** for `cf9f3d6`: run 38983884953, all four jobs success.

## Status after this review
- This is not an unconditional PASS, so the I-7 §5 stop condition applies.
- **No acceptance report has been prepared, and no review 09 has been started.** The branch is not merged, and T0, T1 and T2 have not started.
- **Returned to the Tech Lead:** a decision on M3P8-F1, and on any further review.
