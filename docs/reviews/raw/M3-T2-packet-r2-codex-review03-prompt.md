You are an independent reviewer from a separate provider. You did not write any file under review, and you have no context from earlier reviews. This is the **independent closure review (Review 03)** of the I-34A corrections to the TARS M3 T2 implementation authorization packet, revision 2: `docs/milestones/M3-T2-implementation-authorization-packet.md`.

Independent Review 02 (record `docs/reviews/M3-T2-packet-r2-review-02.md`; raw output `docs/reviews/raw/M3-T2-packet-r2-codex-review02.md`) returned PASS with three MINOR findings (M3T2P2-R2-F1, F2, F3) and one NOTE (R2-F4). The owner authorized a restricted correction pass and this closure review under I-34A, reproduced verbatim at the end. **The implementer's documents, scripts and outputs are claims, not evidence.**

## Snapshot and rules
- **The current directory** is a fresh git clone, detached at the pinned head **`8abfae249a58042370e4ac8c71cf13b5de7f6ef6`** (branch `milestone-3-t2-authorization`, the I-34A correction commit). Relevant ancestors:
  - `3bb363783e8a12f034876c23e713f15d3a202c23`: the Review 02 record (the I-34A baseline);
  - `5f96119bcc54d2154cdff50a873791f5f9b26d73`: the packet as Review 02 reviewed it.

  The correction is `git diff 3bb3637..8abfae2`, all under `docs/`.
- **Environment:** a locked Python environment (CPython 3.12.15, macOS x86_64) is in `./.venv`. Use `.venv/bin/python -I`, with `PYTHONDONTWRITEBYTECODE=1` when importing the T0 spike. **The network is not available.**
- **Do not modify tracked files.** Use only `./review_scratch/` for scratch; it is excluded from git.
  - Put every script you write there, named `*.py`, with its output as `*.out` beside it, so that the implementer can preserve them.
  - To run the implementer's evidence, copy `docs/reviews/raw/M3-T2-packet-r2-I34A-evidence/*.py.txt` and the I-33 drafts `docs/reviews/raw/M3-T2-packet-r2-I33-evidence/{pog_lib,witness}.py.txt` into `review_scratch/` as `*.py`. The I-34A README gives the arguments.
  - Do not run the M1/M2 proof scripts.
  - Finish with a clean tracked tree.
- **Your sandbox may be unable to run `sysctl`.** If so, say so. Do not treat an empty result as an observed value.
- **CI for `8abfae2`** may still be running. The implementer reports it separately.
- **Decision boundaries.** You review; you do not decide, approve or fix anything.
  - Do not treat D-0 … D-8, P6, DR-0029 P6(b), X-1, A-FP-2, A-LM-1 or A-LM-2 as approved.
  - Do not propose an unapproved CI, runtime or language migration.
  - Do not silently correct anything.

## Under review
- The I-34A diff to the packet: the header, §2.2 DL-2 and DL-4, §3 testability (iii), §6.3, §6.4 rules 1 and 5, §7 RQ-6, §8.2, the reading note after the §14 table, and §16.1.
- The correction record: `docs/reviews/M3-T2-packet-r2-review-02-corrections.md`.
- The evidence: `docs/reviews/raw/M3-T2-packet-r2-I34A-evidence/`, with its `SHA256SUMS`.
- **Context to read yourself:**
  - Review 02's record and raw output;
  - the I-33 evidence (`pog_lib.py.txt`, `witness.py.txt`, `f2_premise_controls.*`, `f4_fingerprint.*`, `pog_pipeline.out`);
  - the Review 02 evidence (`docs/reviews/raw/M3-T2-packet-r2-codex-review02-evidence/`);
  - packet r1 (`docs/milestones/M3-T2-authorization-packet-r1.md` §5);
  - `docs/science/experiments/m3-t0/t0_termination.py` (A-FP-2, lines about 440–475).
- **Readiness findings (closed; check they stay closed):**
  - `docs/reviews/M3-T2-readiness-review-02.md` (M3T2R-R2-F1 … F3);
  - `docs/reviews/M3-T2-readiness-review-02-corrections.md`;
  - `docs/reviews/M3-T2-readiness-review-03.md`;
  - `docs/milestones/M3-T2-validation-strategy.md` (U-19, PM-4, B-9, U-13);
  - `docs/decisions/requests/DR-0029-P1-P9-owner-decision-packet.md` (P4 item 8).

## What you must independently assess (I-34A §6)
1. **R2-F1, R2-F2 and R2-F3.** For each, decide RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with reasons. Reproduce in your own scripts, not only by rerunning the implementer's:
   - R2-F1: that output equality does not establish NumPy absence or the internal sequence, and that no remaining packet statement claims DL-4 enforces either.
   - R2-F2: the ulp metric definition, the closed-form allowance A(f) = 2|f|/2^e′ + 2^(−1021−e′) (derive it yourself), its inclusive boundary, the cases f = 1.5 and f = 2⁻¹⁰²², the "e ≥ −969" corollary, and the starting-error statement. Check that no threshold, constant or control changed.
   - R2-F3: the admissibility condition, the draft's exception cases (including (2¹⁰²⁰,)³ and the origin), the off-axis threshold near 2¹³⁹, the stated cause (the Newton budget), and that exceptions fail closed and are never converted into a pass or an enclosure. Check that the supported domain is neither expanded nor claimed.
2. **Technical defensibility** of each corrected statement.
3. **Previously closed readiness findings M3T2R-R2-F1 … F3 remain closed:** the corrections are intact and the I-34A diff does not touch or contradict them.
4. **R2-F4 fingerprint provenance:** whether the record accurately represents which fields differ, the evidence's existence and checksums, the independent verification, the inferred cause, the effect on conclusions, and that the proposed correction is only proposed and not applied or backfilled.
5. **Scope:**
   - no unauthorized scope expansion;
   - no change to a protected decision (D-0 … D-8, DRs), threshold, DL acceptance requirement (anything added must be disclosed), protected path, review record or I-33 evidence;
   - the report-only versus gate distinction is preserved.
6. **Contradictions** newly introduced by the corrections, inside the packet or against the records above.
7. **Accuracy of the correction record and evidence:** numbers, counts, file references, validation results, checksums, and byte-identical reruns.

## Output format
Markdown:
1. First line exactly one of: `VERDICT: PASS`, `VERDICT: REQUEST_CHANGES` or `VERDICT: BLOCKED`.
2. A summary.
3. A findings table with these columns: ID (M3T2P2-R3-Fn), severity (BLOCKER / MAJOR / MINOR / NOTE), location (file:line), finding, evidence, recommended disposition.
4. The R2-F1 … R2-F3 resolution table, plus R2-F4 provenance.
5. The readiness-findings check.
6. The scope check.
7. Contradictions found, if any.
8. Your own computations: commands and outputs, and a list of the files in `review_scratch/`.
9. Limitations.

**Severity guide:**
- **BLOCKER:** a defect that prevents closure, or a claim of justification that is false.
- **MAJOR:** an unsupported or misleading scientific claim; a weakened acceptance requirement that is not disclosed; something that fails open; an approval presented as made; a scope violation.
- **MINOR:** an inaccuracy or gap that does not change a decision, a classification or a gate.
- **NOTE:** clarity.

PASS means no BLOCKER or MAJOR finding remains and the three MINOR findings are resolved. It does **not** authorize T2 implementation, any numerical gate, any decision or a merge. State explicitly whether any finding remains.

## Owner authorization I-34A (verbatim, as received; truncated in §6 in the original)

# I-34A — M3 T2 Packet Review 02 MINOR Corrections

**Decision:** APPROVED WITH RESTRICTED SCOPE

**Supersedes:** I-34 in its entirety. Do not execute its mismatched finding instructions.

## 1. Preconditions

Before editing, verify:

- Branch and remote are at `3bb363783e8a12f034876c23e713f15d3a202c23`.
- Working tree is clean.
- CI is green for `5f96119` and `3bb3637`.
- The three actual MINOR findings exist in `docs/reviews/M3-T2-packet-r2-review-02.md`.
- The earlier readiness findings M3T2R-R2-F1 through F3 are closed and their corrections remain intact.

If any precondition fails, STOP and report the discrepancy.

## 2. Authorized corrections

Correct only these three findings:

**M3T2P2-R2-F1 — DL-4 enforcement overclaim**

Distinguish output-equivalence testing from enforcement of internal implementation requirements.

DL-4 must not claim to prove the absence of NumPy or compliance with an internal sequence unless independent evidence actually establishes those properties.

**M3T2P2-R2-F2 — Three-ULP boundary defect**

Investigate and correct the documented three-ULP requirement, including the reported failures at `f = 1.5` and the least normal binary64 value.

Use an explicitly defined binary64 ULP metric, including boundary behavior. Add or identify reproducible evidence for both cases.

Do not weaken numerical acceptance criteria or redefine the metric solely to make the existing result pass. If the intended requirement cannot be satisfied, STOP and request an owner decision.

**M3T2P2-R2-F3 — Admissibility qualification**

Correct the overbroad admissibility statement.

Explicitly distinguish valid input domains from cases where `true_height_enc` may raise an exception, including `(2**1020,)*3`.

Do not silently convert exceptions into accepted outputs or expand the supported numerical domain.

## 3. Fingerprint fields

The empty fingerprint fields are **IN SCOPE FOR INVESTIGATION**.

Determine:

1. Which fields are empty.
2. Whether the referenced evidence exists.
3. Whether its identity and provenance can be independently verified.
4. Whether the missing values affect reproducibility or review conclusions.

If original evidence is available and independently verifiable, propose the minimal record correction.

If evidence is missing, ambiguous, or irreproducible, STOP. Do not invent fingerprints, regenerate evidence without authorization, or backfill values without provenance.

## 4. Protected decisions and findings

Do not modify or reopen:

- M3T2R-R2-F1 through F3, previously closed under I-25.
- The accepted Readiness Review 03 conclusions.
- Existing DR decisions.
- DL-1 through DL-4 acceptance requirements.
- D-0 through D-8.
- Production implementation or numerical algorithms.

Preserve the distinction between report-only checks and acceptance gates.

## 5. Validation

For each correction:

1. Identify the original defective statement.
2. Record the minimal correction and rationale.
3. Verify all directly affected cross-references.
4. Check for contradictory statements elsewhere in the packet.
5. Preserve original numerical thresholds.
6. Produce reproducible supporting evidence where applicable.

Do not expand the correction scope to unrelated findings.

If a correction requires changing an accepted decision, numerical threshold, or protected implementation, STOP and request authorization.

## 6. Independent closure review

After corrections and validation, request a fresh independent Codex review against the exact corrected commit.

The reviewer must verify:

- All three specified MINOR findings are resolved.
- The corrected statements are technically defensible.
- Previously closed readiness findings remain closed.
- Fingerprint provenance is accurately represented.
- No unauthorized scope
