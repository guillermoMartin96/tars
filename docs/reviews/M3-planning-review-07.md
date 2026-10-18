# M3 Planning Review 07 (targeted, independent)

**Scope:** the corrections authorized by the Tech Lead's instruction "Continue M3 planning on `milestone-3-planning` from commit `dcabcb2`" (I-6), in commit `f999626`. They cover:
- M3P6-F1: the domain of the line-of-nodes identity;
- M3P6-F2: the asserted node discontinuity;
- M3P6-F3: wrapping to (−π, π].

The review also covered regression, preservation of the scientific baselines, and scope. No M3 implementation exists.

**Reviewer:** Codex (separate provider), session `01a146dd-c528-7ee3-abfd-65020e73d6e6`, run at `cf5fc71` on a git clone with metadata.

**Prompt and output:**
- Prompt: `raw/M3-planning-codex-review07-prompt.md`. It carries I-1 to I-6 verbatim, the full review history and the implementer's validation evidence, and requires independent derivation and defect reproduction.
- Raw output: `raw/M3-planning-codex-review07.md`.

**Instruction for this outcome (I-6 §5):** "If review 07 returns REQUEST_CHANGES: Record all findings and raw review output. Do not automatically fix them. Do not initiate review 08. Do not prepare an M3 planning acceptance report. Stop and request my authorization."
- **The finding below has not been applied.**
- No review 08 has been started, and no acceptance report has been prepared.
- The planning branch is not merged, and T0, T1 and T2 have not begun.

## Verdict
**REQUEST_CHANGES:** one new MINOR finding, with no BLOCKER or MAJOR finding. **All three review-06 findings are RESOLVED.**

### Dispositions of the review-06 findings (reviewer)
| ID | Disposition | Reviewer's evidence |
|---|---|---|
| M3P6-F1 | **RESOLVED** | Derived the identity and all five rows independently. Recomputed i = 2°, δ = 5°: Δi = +1°, ΔΩ = +180°. Restoring the unrestricted claim makes the script exit 1 |
| M3P6-F2 | **RESOLVED** | 73 executed jump assertions per tilt sign. Suppressing the jump, or deleting E5a, E5b or E5c separately, each makes the script exit 1 |
| M3P6-F3 | **RESOLVED** | ±π both map to +π, and exact rational comparisons confirm the reduction of finite inputs. Restoring the previous wrap makes the script exit 1, with 28 designated failures. The input-domain wording is the subject of M3P7-F1 |

### The reviewer also confirmed independently
- **Geometry:** ĥ_B = sin(i − δ) u + cos(i − δ) ẑ.
  - All regimes and endpoints are correct, and the node reverses at crossings, giving +π.
  - 10 000 identity cases agree to 6.11e-16.
  - The 48 endpoints, checked with a separate implementation, have a largest transverse residual of 0.8125 ε.
- **Signed formulas:** rederived as Δi ≈ −δ cos(Ω − φ) and ΔΩ ≈ +δ cot i sin(Ω − φ). They are consistent with the passive convention of DR-0024 revision 2.
- **Tolerances and coverage:** the two-frame tolerance, the circular distance and the 32 ε endpoint bound are sound. The cases are not vacuous: 168 interior, 144 crossing and 48 endpoint, with 73 jump assertions per sign.
- **Wrapping:** 99 962 finite floats, plus the extreme, minimum-normal and subnormal inputs, match the exact rational reduction.
- **Mutations:** all eight file-level mutations exit 1. All five built-in exact mutants and all four formula mutants are rejected by their required checks.
- **Research reruns:** all three research scripts reproduce byte-for-byte, and the first-order sections are identical to `bcb7f9b`. The sensitivity script's internal [−π, π) convention creates no contradiction.
- **Baselines:**
  - M1 Proof 7/7, and the full M2 Proof 228/228;
  - both GMAT comparisons, the reference-snapshot verify-baseline, the cross-platform check and determinism;
  - the reviewer's own pytest run was interrupted after 856 passed, so the reviewer claims no full-suite rerun.
- **History and scope:**
  - `docs/` only; registers 218/0 and 43/0, with every baseline line in order;
  - the only removed lines are status/index cells;
  - earlier findings and amendments are preserved;
  - constants, FC-1…FC-10, frozen artifacts, validation semantics and decision statuses are unchanged;
  - Ruff, links and `git diff --check` pass.
- **Not verified by the reviewer:** CI (no GitHub API access).

## Dispositions (recorded; not applied)

### M3P7-F1 (MINOR, mathematical consistency): the exact wrapping guarantee needs a finite-input restriction
**Where:** the `wrap()` docstring in `dr0028_node_signed_verification.py`, and DR-0028 "Resolution amendment 3", item 3.

**Finding.** Both texts state that the result is "the unique float in (−π, π] that differs from a by an exact integer multiple of 2π" for any float input. That guarantee holds only for finite inputs. The reviewer measured:

| Input | Result |
|---|---|
| wrap(+∞) | raises ValueError |
| wrap(−∞) | raises ValueError |
| wrap(NaN) | NaN, outside the interval |

The fmod/Sterbenz argument is correct for finite binary64 inputs, so this is a defect in the stated domain, not a numerical defect.

**Disposition: ACCEPTED.** The implementer reproduced all three results. The amendment-3 text says "for every float input" is not stated literally, but "the result is the unique float in (−π, π]" with no restriction carries the same meaning. No computation in the script passes a non-finite angle.

**Proposed change (not made):**
- Restrict the exactness and interval guarantee explicitly to finite float angles, in both the docstring and an appended DR-0028 correction.
- Either document non-finite inputs as unsupported, or define their rejection (for example, ValueError for ±∞ and NaN) and test it.

## Validation evidence at the reviewed commits (implementer)
- **`f999626`**, isolated clone:
  - M1 Proof PASS, with full pytest (1185 passed);
  - M2 Proof PASS (21 steps, exit 0), with the GMAT M1/M2 comparisons, the reference-snapshot verify-baseline and m2_proof;
  - the evidence differs only in run metadata, and `src/`, `tests/`, `scenarios/` and `toolbox/references` are unchanged.
- **CI** for `f999626`: run 38970769894, all four jobs success.

## Status after this review
- This is not an unconditional PASS, so the I-6 §5 stop condition applies.
- **No acceptance report has been prepared, and no review 08 has been started.** The branch is not merged, and T0, T1 and T2 have not started.
- **Returned to the Tech Lead:** authorization to correct M3P7-F1, and whether to run a further review.

## Resolution of findings (appended 2026-10-16; the sections above are unchanged)
**Authority:** the Tech Lead's instruction "Continue the TARS spacecraft simulator M3 planning work from branch `milestone-3-planning`, currently at commit `0dac6d3`" (2026-10-16), referred to as **I-7**. It authorizes:
- the narrow M3P7-F1 correction;
- exactly one further review (review 08), conditional on successful local validation.

It does not authorize planning acceptance, a merge or any implementation.

### M3P7-F1 (MINOR): the exact wrapping guarantee needs a finite-input restriction
- **Correction:** DR-0028 "Resolution amendment 4" (appended), with a pointer under amendment 3, item 3. In `dr0028_node_signed_verification.py`:
  - `wrap()` documents finite floats as its domain;
  - it raises `ValueError("wrap: non-finite angle: …")` for NaN, +∞ and −∞;
  - its finite-input behaviour is unchanged.
- **Tests:** `wrap_nonfinite_tests` covers NaN, −NaN, +∞ and −∞, checking both the exception type and the guard's message.
- **New mutant:** `M3P7-F1_nonfinite_guard_removed` (the `f999626` implementation) is rejected in 4 of 4 non-finite categories, with no finite-wrap failures.
- **Evidence:**
  - every pre-existing output section is identical to `f999626`, and all earlier mutant counts are unchanged;
  - 200 001 finite floats are bitwise identical to the previous implementation;
  - two runs are byte-identical;
  - ten file-level mutations each exit 1, including removing the guard and weakening its test to a type-only check.
- **Residual uncertainty:** none.
- **Changes an acceptance decision?** No.
