You are an independent reviewer from a separate provider. You did not write any file under review, and you have no context from earlier reviews. This is **independent closure Review 04** of the I-35 documentation corrections to the TARS M3 T2 implementation authorization packet, revision 2 (`docs/milestones/M3-T2-implementation-authorization-packet.md`), and to its correction record, `docs/reviews/M3-T2-packet-r2-review-02-corrections.md`.

Review 03 (record `docs/reviews/M3-T2-packet-r2-review-03.md`; raw output `docs/reviews/raw/M3-T2-packet-r2-codex-review03.md`) returned PASS. It raised one MINOR finding (M3T2P2-R3-F1, the fingerprint field count) and one NOTE (M3T2P2-R3-F2, the Newton-denominator notation). The owner authorized their correction, plus a documentation-only `[U] unavailable` representation of the CPU fingerprint fields, under I-35, reproduced verbatim at the end. **The implementer's documents, scripts and outputs are claims, not evidence.**

## Snapshot and rules
- **The current directory** is a fresh git clone, detached at the pinned head **`154378c14f9eed0fbede53b48e4544079485694e`** (branch `milestone-3-t2-authorization`, the I-35 correction commit).
  - Its baseline is `d30e44910054cdf751819d23708b8c9bca2b36b0`, the Review 03 record.
  - The correction is `git diff d30e449..154378c`, all under `docs/`.
- **Environment:** a locked Python environment (CPython 3.12.15, macOS x86_64) is in `./.venv`. Use `.venv/bin/python -I`, with `PYTHONDONTWRITEBYTECODE=1`. **The network is not available.**
- **Do not modify tracked files.** Use only `./review_scratch/` for scratch; it is excluded from git.
  - Put every script you write there, named `*.py`, with its output as `*.out` beside it, so that the implementer can preserve them.
  - To run the implementer's evidence, copy `docs/reviews/raw/M3-T2-packet-r2-I35-evidence/i35_checks.py.txt` and the I-33 draft `docs/reviews/raw/M3-T2-packet-r2-I33-evidence/pog_lib.py.txt` into `review_scratch/` as `*.py`. The I-35 README gives the arguments.
  - Do not run the M1/M2 proof scripts.
  - Finish with a clean tracked tree.
- **Your sandbox may be unable to run `sysctl`.** If so, report it as unavailable, with the exit status and diagnostic. Do not report it as an observed value.
- **CI for `154378c`** may still be running. The implementer reports it separately.
- **Decision boundaries.** You review; you do not decide, approve or fix anything.
  - Do not treat D-0 … D-8, P6, DR-0029 P6(b), X-1, A-FP-2, A-LM-1 or A-LM-2 as approved.
  - Do not propose an unapproved CI, runtime or language migration.
  - Do not silently correct anything.

## Under review
- **The I-35 diff to the packet:** the header note, the §7.1 rule for unavailable probes, and §16.2.
- **The I-35 diff to the correction record:**
  - §1, R2-F3 row, the cause note;
  - §2, items 1 and 3, and the applied `[U] unavailable` representation table;
  - §3a;
  - §4.
- **The evidence:** `docs/reviews/raw/M3-T2-packet-r2-I35-evidence/`, with its `SHA256SUMS`.
- **Context to read yourself:**
  - the Review 03 record, raw output and evidence (`docs/reviews/raw/M3-T2-packet-r2-codex-review03-evidence/`, especially `independent.out` lines 20–22 and `implementer_rerun.txt`);
  - the I-34A evidence (`docs/reviews/raw/M3-T2-packet-r2-I34A-evidence/`, especially `i34a_fingerprint_check.*`);
  - the I-33 evidence (`f4_fingerprint.py.txt` / `.out`, and `pog_lib.py.txt`'s `_foot_point` near line 385);
  - the Review 02 evidence (`reviewer_f4_fingerprint.out`).
- **Closed items (check they stay closed):**
  - Review 02's M3T2P2-R2-F1 … F3, found RESOLVED by Review 03;
  - the readiness findings M3T2R-R2-F1 … F3:
    - `docs/reviews/M3-T2-readiness-review-02.md`, `-02-corrections.md` and `-03.md`;
    - `docs/milestones/M3-T2-validation-strategy.md`;
    - `docs/decisions/requests/DR-0029-P1-P9-owner-decision-packet.md`, P4 item 8.

## What you must independently assess (I-35 §5)
1. **Closure of R3-F1.** Count the fingerprint fields yourself, by full JSON path and by leaf name. Verify:
   - 47 fields, of which 3 differ and 44 agree;
   - the explanation of the 44 (repeated names and their sections);
   - that no fingerprint value or underlying evidence changed.
2. **Closure of R3-F2.** Check the corrected expression against `_foot_point` and Review 03's finding. Derive the approximately 1.5× growth of a² + t (and b² + t) yourself. Check the implementer's trace claims: the (2¹³⁸,)³ point is non-converged but admissible, and (2¹³⁹,)³ is inadmissible.
3. **Accuracy of fingerprint reporting:**
   - the `[U] unavailable` representation, with exit status and diagnostic;
   - that the observed cause (restricted `sysctl` access) is stated for Review 03's sandbox, while Review 02's remains inferred;
   - that inaccessible metadata is distinguished from a numerical validation failure;
   - that the §7.1 rule is documentation-only, with no script, runtime or CI change;
   - that nothing is backfilled or regenerated.
4. **Preservation of evidence provenance:**
   - every original evidence file and manifest is unchanged (I-33, Review 02, I-34A, Review 03);
   - the original-host comparison is preserved;
   - the I-35 manifest verifies, and its output reruns byte-identically.
5. **Absence of new contradictions,** inside the packet and record, or against the records above. In particular, check that R2-F1 … F3 stay resolved and the readiness findings stay closed.
6. **Absence of unauthorized scope expansion:** no change to production code, numerical algorithms, thresholds, DL-1 … DL-4 requirements, D-0 … D-8 alternatives, readiness corrections, CI or platform configuration, or prior review records.

## Output format
Markdown:
1. First line exactly one of: `VERDICT: PASS`, `VERDICT: REQUEST_CHANGES` or `VERDICT: BLOCKED`.
2. A summary.
3. A findings table with these columns: ID (M3T2P2-R4-Fn), severity (BLOCKER / MAJOR / MINOR / NOTE), location (file:line), finding, evidence, recommended disposition.
4. The R3-F1 and R3-F2 closure table.
5. The fingerprint reporting and provenance assessment.
6. Closed-items check (R2-F1 … F3; readiness).
7. Scope check.
8. Contradictions found, if any.
9. Your own computations: commands and outputs, and a list of the files in `review_scratch/`.
10. Limitations.

**Severity guide:**
- **BLOCKER:** a defect that prevents closure, or a claim of justification that is false.
- **MAJOR:** an unsupported or misleading claim; a weakened requirement that is not disclosed; something that fails open; an approval presented as made; a scope violation.
- **MINOR:** an inaccuracy or gap that does not change a decision, a classification or a gate.
- **NOTE:** clarity.

PASS means no BLOCKER or MAJOR finding remains, and R3-F1 and R3-F2 are closed. It does **not** authorize T2 implementation, any numerical gate, any decision or a merge. State explicitly whether any finding remains.

## Owner authorization I-35 (verbatim)

# I-35 — M3 T2 Review 03 Findings and Fingerprint Cleanup

**Decision: AUTHORIZED — RESTRICTED DOCUMENTATION CORRECTIONS**

**Baseline:** `d30e449` on `milestone-3-t2-authorization`

**Scope:** R3-F1, R3-F2, and the previously investigated fingerprint-reporting defect.

## 1. Preconditions

Before editing, verify:

- Local HEAD and remote both equal `d30e449`.
- Working tree is clean.
- CI runs `40440998830` and `40441600981` passed all four jobs.
- Review 03 records PASS for the three original Review 02 findings.
- Previously closed readiness findings remain intact.

STOP if any precondition fails.

## 2. Authorized corrections

### R3-F1 — Fingerprint field count

Correct the inaccurate statement "3 of 44 fields."

Use the verified total of 47 distinct fields, counted by full JSON path, and explain why counting repeated field names produced 44.

Do not change fingerprint values or underlying evidence.

### R3-F2 — Cause-note correction

Correct the mathematical or technical misstatement identified in Review 03.

Use the exact reviewer finding and independently verify the corrected expression.

Do not infer the missing wording from this authorization. If the review record does not unambiguously establish the intended correction, STOP and request clarification.

### Fingerprint reporting

Authorize a documentation-only correction representing unavailable CPU fingerprint fields as `[U] unavailable`, accompanied by the observed command exit status and diagnostic.

Requirements:

- Preserve all original committed evidence and checksums.
- Do not backfill missing fingerprint values.
- Do not regenerate evidence.
- Distinguish inaccessible metadata from a numerical validation failure.
- State that the observed sandbox failure was caused by restricted `sysctl` access.
- Preserve the original-host comparison and provenance.

If implementing this representation requires changing scripts, runtime behavior, or CI, STOP and request separate authorization.

## 3. Protected scope

Do not modify:

- Production code or numerical algorithms.
- Numerical acceptance thresholds.
- DL-1 through DL-4 requirements.
- D-0 through D-8 decision alternatives.
- Previously accepted readiness corrections.
- CI workflows or platform configuration.

Do not expand the scope to unrelated defects.

## 4. Validation

After corrections:

1. Verify the corrected field count.
2. Verify the technical correction for R3-F2.
3. Check fingerprint provenance and original checksums.
4. Confirm the three Review 02 findings remain resolved.
5. Confirm the earlier readiness findings remain closed.
6. Run applicable documentation and repository validation checks.

## 5. Independent closure review

Request a fresh, independent Codex Review 04 against the corrected commit.

Require the reviewer to assess:

- Closure of R3-F1 and R3-F2.
- Accuracy of fingerprint reporting.
- Preservation of evidence provenance.
- Absence of new contradictions.
- Absence of unauthorized scope expansion.

Record the complete review output and all findings.

If the verdict is REQUEST_CHANGES, STOP. Do not automatically correct new findings.

## 6. Repository controls

- Use the existing authorization branch.
- Commit corrections and review records separately.
- Use ordinary pushes only.
- Verify CI on the final commit.
- Do not merge.

## 7. Final checkpoint

Report:

- Exact branch and HEAD SHA.
- Correction summary.
- Review 04 verdict and findings.
- CI results.
- Remaining blockers.
- Whether the packet is ready for owner decisions.

**T2 implementation remains NOT AUTHORIZED.**

No DL acceptance, per-platform CI changes, D-0 through D-8 decisions, or merge is authorized by I-35.
