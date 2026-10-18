# M3 Planning Review 13 (independent)

**Scope:** the correction authorized by the Tech Lead's instruction "I-12 — M3 Planning: Review 12 Corrections and Review 13 Authorization" (I-12), in commits `1cef6ab`, `24c2d98` and `602ede0`. That covers M3P12-F1 (oracle values injected inside the first-order check observed at every scheduled step, with the controls and the regression demonstration against `5b12eec`) and M3P12-F2 (E6's sign assertion split into its oracle half and its first-order half, with a new built-in mutant, and the B premises re-examined). The review also covered every earlier tracked finding, the DR-0028 mathematics, M1/M2 preservation, scope and planning readiness. No M3 implementation exists.

**Reviewer:** Codex (separate provider), session `01a14cb2-26f7-7e90-ae78-ada75d0a31bb`, run at **`59c9f9ebccf489e76a8a916e273b4dc14f6868e5`** (the prompt commit; parent `602ede0`) on a fresh git clone with metadata.

**Prompt and output:**
- Prompt: `raw/M3-planning-codex-review13-prompt.md`. It carries I-1 to I-12 verbatim: I-1 to I-11 checked byte for byte against the review 12 prompt, and I-12 against the instruction text. As I-12 §7 requires, it supplies the baseline and corrected commit IDs, points to the complete correction diff (`git diff 142b9df..HEAD`), the Review 12 raw findings, the regression demonstrations, the mutation and classification evidence, the full Proof results, the CI results and the current decision matrix. It asks the reviewer to verify the eight points of I-12 §7 and does not ask the reviewer to approve the package.
- Raw output: `raw/M3-planning-codex-review13.md` (the reviewer's final message, verbatim). Its link to a "full review" file points into the reviewer's scratch clone, which is not part of the repository; that file is a draft of the same verdict, with the same content.

**Instruction for this outcome (I-12 §8):** "Even if Review 13 returns PASS, do not merge or begin M3 implementation. Prepare an acceptance recommendation for my decision." The hard boundary of I-12: "This instruction authorizes two corrections and one independent review. It does not authorize acceptance, merging, T0, T1, T2, or Review 14."
- The acceptance recommendation is `docs/reviews/M3-planning-acceptance-recommendation.md`.
- No review 14 has been started. The planning branch is not merged, and T0, T1 and T2 have not begun.

## Verdict
**PASS, unconditional.** There are no new findings, and the reviewer reports every tracked finding RESOLVED.

| ID | Disposition (reviewer) | Reviewer's evidence |
|---|---|---|
| M3P12-F1 | **RESOLVED** | Reproduced the false detection at `5b12eec` for both components; the corrected probe reports 600 intended / 2 400 missing and rejects the setup; all 3 000 scheduled inputs independently traced |
| M3P12-F2 | **RESOLVED** | Reproduced the E6 counterexample before and after; the first-order assertion now rejects it and its removal is detected; grid failures remain zero |
| M3P11-F1 | **RESOLVED** | Reassociated fallback, wrong-component, rounding-only and partial-exercise controls reproduce their historical failures and are rejected now |
| M3P11-F2 | **RESOLVED** | The five disputed assertions have genuinely exercised, exception-free targeted protection; the remaining redundancy arguments cover matching inputs |
| M3P10-F1 | **RESOLVED** | Historical exception controls reproduce and pass now; the allowances remain restricted by mutation, type, message and stack |
| M3P10-F2 | **RESOLVED** | Inventory reconciles: 19 identities mapped to 18 historical survivors; 12 A / 4 B / 3 C / 0 D |
| M3P-F1…F5, M3P2-F1…F3, M3P3-F1/F2, M3P4-F1/F2, M3P5-F1, M3P6-F1…F3, M3P7-F1, M3P8-F1, M3P9-F1…F3 | **RESOLVED** | Each rechecked; see the raw output |

### The reviewer also confirmed independently
- **Repeatability and committed results:** all five experiment tools reproduce the committed outputs byte for byte; mutation check 109 attempted / 109 exercised / 109 detected for the intended reason, every other category 0; 30/30 controls with category, exercise result and reason; 0/77 direct predicates and 22/22 oracle schedules fully observed at baseline; sweep 36 / 29 / 7 / 0 exceptions.
- **Regression demonstration:** the five M3P10-F1 controls fail at `896d52d`, the four M3P11-F1 controls at `c16b3b5`, the five M3P12-F1 controls at `5b12eec`; all 30 pass against the corrected harness.
- **Adversarial variants of the oracle probe, each failing closed:** an injection after the formula call (3 000 missing); extra steps (600 unscheduled); changed arguments or calls through another frame (3 000 unscheduled); a renamed oracle-value local (KeyError); corruption of the other component (600 unintended); a runtime exception (process failure). Reversing the step order kept complete observation and remained valid. The reviewer found that the documented exclusion of probe-aware programs does not conceal a defect in the fixed mutation inventory.
- **All 12 category A assertions**, removed independently by AST location: each targeted defect exercised without exception, rejected with its assertion, escaping without it (W2 2/0, W5 6/0, N1 4/0, E1 1/0, E2b 168/0, E2c 144/0, E2d 48/0, E2e 24/0, E5b-nonfinite 2/0, E5b-defined 2/0, E5d 1/0, E6-sign-first-order 1/0).
- **The four B classifications** hold within their documented pure-function scope; additional endpoint and E6-only defects still trigger the independent checks with the B assertion removed. The three C rationales are appropriate.
- **Preservation:** against an independent run of `5b12eec`, zero pre-existing values changed or disappeared (23 added leaf values); AST: oracle, formulas, wrapping, grid, first-order checks, tolerances and minima unchanged; order 506/532 and sign 560/504 enforced separately; the 1 % Δi oracle error still gives one E3 and one E4 failure.
- **Mathematics:** 10 000 conjugated-Cartesian rotation cases agree with the oracle within 2.22e-15 rad, with no inclination-bound excess; ΔΩ = +0.259805543688° and the crossing example reproduced; 9 994 finite random inputs match rational wrapping.
- **Research reruns:** sensitivity and atmosphere-residual outputs reproduce; all 27 density jumps within 1.11e-16; lowest-band ratio 1.0013804525694443.
- **History and scope:** all 81 whole-branch changed files under `docs/`; the correction is the stated 15 documentation files; protected paths unchanged; the five pinned hashes match and are baseline-identical; registers 218/0 and 43/0; prior records and raw outputs keep their bytes; I-1 to I-11 byte-identical; amendments 1–9 keep their pointers; Ruff and relative links pass.
- **Preservation gates (standalone validators):** m1_proof 7/7; full m2_proof 228/228; both committed-reference GMAT comparisons; snapshot verify-baseline; local cross-platform checks; five determinism runs; 13 focused pytest tests.
- **Partial or unavailable, as the reviewer reported:** complete standalone validator executions, not complete Proof-wrapper executions; the full pytest suite was not rerun by the reviewer; no run was interrupted; fresh GMAT executable runs, external-source retrieval and three-platform execution were not performed; CI could not be checked (no GitHub API access).

## Validation evidence at the reviewed commits (implementer)
- **`24c2d98`**, isolated clone:
  - M1 Proof overall PASS (9 steps, exit 0), full pytest 1185 passed, 0 failed, 0 skipped;
  - M2 Proof overall PASS (20 steps, exit 0), full pytest 1185 passed, m2_proof 228 PASS / 0 FAIL, with the GMAT M1/M2 comparisons, the reference-snapshot verify-baseline, cross-platform, determinism for four scenarios;
  - the evidence differs only in run metadata; `m2_final_states_record.json` without `revision`, `tree_clean` and `sha256` is identical to the committed record.
  - `602ede0` changes only one DR-0028 paragraph and four docstring lines; the mutation check rerun there is byte-identical to the committed output.
- **CI:**
  - `602ede0`: run 39084190524, completed, success; check ubuntu-latest (117547212389), check macos-latest (117547212242), check macos-15-intel (117547212343), m2-cross-platform (117557583723), each completed with success;
  - `24c2d98`: run 39084025411, completed, success; check ubuntu-latest (117546713872), check macos-latest (117546714005), check macos-15-intel (117546714013), m2-cross-platform (117559774285), each completed with success.
  - The reviewer could not verify CI independently.
- **Pinned references and goldens** (sha256, unchanged since `d92ab89`): `proof/references/m1_final_state.json` c1a5e01b…c45a; `proof/references/m2_final_states.json` dc3baf7a…51dc (equal to the approved digest); `toolbox/references/snapshot/m2/REFERENCE_SNAPSHOT.json.gz` a2cddf4b…448b; `toolbox/references/gmat/m2/APPROVED_DIGESTS.json` f8d6bd78…e585; `toolbox/references/gmat/m1_two_body_report.txt` 9ac597c6…fd71.

## Status after this review
- Review 13 returned an unconditional PASS, so the I-12 §8 PASS branch applies: an acceptance recommendation has been prepared for the Tech Lead's decision.
- **Planning is not accepted.** Acceptance, the planning merge, T0, T1, T2 and any review 14 each need the Tech Lead's separate authorization.

## Owner decision (appended 2026-10-17; the sections above are unchanged)
The project owner accepted the M3 planning checkpoint at `865210c` (I-13, "I-13 — M3 Planning Acceptance and Merge Readiness"). The record is in `docs/milestones/M3-decision-matrix.md`, "Owner decision: M3 planning acceptance (I-13, 2026-10-17)". The planning merge, T0, T1, T2 and any review 14 are not authorized by it.
