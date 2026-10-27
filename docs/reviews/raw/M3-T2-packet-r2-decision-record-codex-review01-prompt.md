You are an independent reviewer from a separate provider. You did not write any file under review, and you have no context from earlier reviews. This is the **independent decision-record review** required by owner authorization I-37 §4. It checks how the owner's decisions D-0 … D-8 are recorded in the TARS M3 T2 implementation authorization packet, revision 2 (`docs/milestones/M3-T2-implementation-authorization-packet.md`). I-37 is reproduced verbatim at the end. **The implementer's text is a claim, not evidence.**

## Snapshot and rules
- **The current directory** is a fresh git clone, detached at the pinned head **`62b9c8dbb4ea5eb3490d400e6b5ca8c1e9e91109`** (branch `milestone-3-t2-authorization`, the I-37 recording commit).
  - Its baseline is `42fc823afdd81c0e6d876e482e948b2428e7c064`.
  - The change under review is `git diff 42fc823..62b9c8d`.
- **The network is not available.** No Python environment is needed: this is a documentation review. Use git and text tools only.
- **Do not modify tracked files.** Use only `./review_scratch/` for scratch notes; it is excluded from git. Finish with a clean tracked tree.
- **Owner confirmation.** I-37 was issued as "PROPOSED — awaiting owner confirmation". The implementer asked the owner, who confirmed on 2026-10-27 with the answer "Confirmed, record them" (record I-37 §2 and §3 exactly as written). You cannot verify this exchange from the repository; treat it as stated and check that the record describes it accurately.
- **Decision boundaries.** You review the record; you do not decide, approve or fix anything.
  - Do not reopen or second-guess the owner's choices. Check that they are **recorded exactly and completely**.
  - Do not expand the review into implementation work, numerical reruns, or proposals for CI, runtime or language changes.
  - Do not treat P6, DR-0028 P6(b) or X-1 as decided, and do not treat T2 implementation as authorized.

## What you must independently assess (I-37 §4)
1. **Exact match.** Each recorded decision in packet §17 matches I-37 §2 word for word, including its qualifier, and nothing is added to or removed from the list. D-6 (i) is recorded as remaining withdrawn.
2. **Correct alternative.** Each §17.1 row maps the decision to the §14 alternative it actually approves. In particular:
   - D-5 is option (b), and option (a) is not chosen;
   - D-6 (ii) and (iii) are each recorded separately;
   - D-7's §14 fallbacks ((a) derive δ_f; (b) keep U-18 report-only) are **not** silently decided;
   - D-8 is an output-conformance gate, not an accuracy gate.
3. **Conditions preserved.** The §17.1 "Conditions kept" column and §17.2 preserve every condition from §14 and from the decisions' qualifiers, and **none is weakened, strengthened or invented**. Check against §2.2 (DL-1 … DL-7, including DL-2's R2-F3 review obligation), §3 (iii), §6.3–§6.7, §7 RQ-4, RQ-6, RQ-8, §7.1 and §10.
4. **Acceptance boundaries.** §17.2 reproduces I-37 §3 items 1–8 verbatim and keeps them consistent with the rest of the packet (§6.7 BLOCKED; PC-7 NONE; the D-6 (iii) source-inspection requirement and the §14 reading note).
5. **Append-only discipline.** The diff only appends §17 and adds one-line pointers (the header, §1 PC-8, after the §14 reading note). The §14 table, the reading note, every DL requirement, threshold, D-0 … D-8 alternative and earlier correction record are unchanged. No other file changed.
6. **No contradiction or overstatement.** Nothing in the packet now presents a row as promoted, POG gating as unblocked, a DL as reviewed, per-platform testing as done, a CI change as authorized, or T2 implementation as authorized. Check that the earlier statements "D-0 … D-8 remain PROPOSED" (§14 reading note, §16, §16.1) are clearly superseded by the pointers and not left as live contradictions.

## Output format
Markdown:
1. First line exactly one of: `VERDICT: PASS`, `VERDICT: REQUEST_CHANGES` or `VERDICT: BLOCKED`.
2. A summary.
3. A findings table with these columns: ID (M3T2-DEC-R1-Fn), severity (BLOCKER / MAJOR / MINOR / NOTE), location (file:line), finding, evidence, recommended disposition.
4. A per-decision check table: D-0 … D-8 (D-6 split into (i), (ii), (iii)), with columns: I-37 §2 text matches (yes/no), §14 alternative correct (yes/no), conditions preserved (yes/no), notes.
5. The acceptance-boundary check (I-37 §3 items 1–8).
6. The append-only and scope check, with the `git diff --stat` and the list of changed hunks.
7. Contradictions found, if any.
8. Your commands and their key outputs.
9. Limitations.

**Severity guide:**
- **BLOCKER:** a decision recorded differently from what the owner confirmed, or an approval recorded that was not given.
- **MAJOR:** a condition dropped, weakened or invented; a fallback silently decided; an authorization presented as given; a protected text changed.
- **MINOR:** an inaccuracy or gap that does not change a decision, condition or gate.
- **NOTE:** clarity.

PASS means no BLOCKER or MAJOR finding remains, and the record matches I-37 exactly. It does **not** authorize T2 implementation, any numerical gate, any promotion or a merge. State explicitly whether any finding remains.

## Owner authorization I-37 (verbatim)

# I-37 — M3 T2 Owner Decision Recording

**Status: PROPOSED — awaiting owner confirmation**

**Baseline:** `42fc823afdd81c0e6d876e482e948b2428e7c064`

## 1. Preconditions

Verify the local and remote branch, clean worktree, green CI run `40536225099`, and closure of all recorded findings.

STOP on any discrepancy.

## 2. Record decisions

Subject to explicit owner confirmation, record:

- D-0: APPROVED.
- D-1: APPROVED, conditional POG route only.
- D-2: APPROVED, DL-1 through DL-7 required and independently reviewed before gating.
- D-3: APPROVED, restricted to reviewed CPython builds.
- D-4: APPROVED, with the documented limits of local premises.
- D-5: APPROVED, option (b).
- D-6 (ii): APPROVED.
- D-6 (iii): APPROVED.
- D-7: APPROVED, conditional on validated DL-2 enclosures.
- D-8: APPROVED, as an output-conformance gate, not an accuracy gate.

D-6 item (i) remains withdrawn.

## 3. Preserve acceptance boundaries

Record explicitly:

1. No A-FP-2 or A-LM row is automatically promoted.
2. POG accuracy gating remains BLOCKED.
3. DL-1 through DL-4 remain unreviewed drafts.
4. Per-platform testing remains outstanding.
5. Numerical thresholds and production numerical sequences remain unchanged.
6. D-6 (iii) requires source inspection; DL-4 alone cannot enforce the implementation requirement.
7. No CI modifications are authorized.
8. No production implementation is authorized.

## 4. Independent decision-record review

After recording, request an independent Codex review verifying that the recorded decisions exactly match the approved alternatives and preserve all conditions.

Do not expand the review into implementation work.

Record the verdict and stop on any new substantive finding.

## 5. Final checkpoint

Return the decision table, exact changed files, commit SHA, independent review result, CI status, and remaining implementation prerequisites.

Do not merge or begin T2 implementation.

**T2 IMPLEMENTATION REMAINS NOT AUTHORIZED.**
