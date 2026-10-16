# M3 planning checkpoint — independent review 03

**Scope:** the recording of the Tech Lead's decisions after review 02 and the resolution of M3P2-F1/F2/F3 (commit `8a725b6`), plus the review prompt (`007f38c`). No M3 implementation exists.  
**Reviewer:** Codex (separate provider), session `01a14277-40e3-7b80-9608-0715ab11a271`, at `007f38c`, on a git clone with metadata.  
**Prompt:** `raw/M3-planning-codex-review03-prompt.md`. It carries both Tech Lead instructions complete and verbatim: I-1 §1–8 and I-2 §1–7 (correction of M3P2-F2). **Raw output:** `raw/M3-planning-codex-review03.md`.  
**Instruction for this outcome (I-2 §6):** "If Codex returns REQUEST_CHANGES, record the findings and stop. Do not automatically repair them or begin another review round." **No finding below has been applied.** The planning branch is not merged and T0 has not begun.

## Verdict
**REQUEST_CHANGES:** two MINOR findings; no BLOCKER or MAJOR.

**The reviewer confirmed:**
- 39 changed files, all under `docs/`.
- `assumptions.md` 193 additions / 0 deletions; `validation.md` 43 / 0. The SCI-0005 and VAL-0007 notes are unchanged since review 02.
- Approvals, deferrals, Q-G3-7 NOT AUTHORIZED, the retention rule, AC-1 and AT-1…AT-7 are all represented.
- **DR-0028 is justified:** approving the common Earth-fixed axis does not select its inertial realization.
- Termination altitude is explicit, per scenario, in metres, geodetic, with no default or universal number. T0 assignments are correct, and the top-band statement is withdrawn.
- T0 has not started and needs explicit approval. No implementation, merge or language decision.
- **Recomputed:**
  - exp(0.010/7.249) = 1.0013804525694443 (−0.1378549547 %);
  - 25 km jump: −1.8868e-5 with the author's base, +1.36156e-3 in GMAT's table;
  - +7.627e-6 (950 km), +1.5254e-5 (999.999 km), +19.63 % (1100 km), +145.0 % (1500 km), +500.2 % (2000 km);
  - all 27 boundary jumps within 1.11e-16;
  - residual script rerun byte-identical.
- **Local checks:** M1 Proof 7/7, M2 Proof 228/228, M1 golden zero differences, both GMAT comparisons, M1 determinism, Ruff.
- **Not verified by the reviewer:** source digests and errata (no network), full pytest (still running when it reported) and remote CI.

## Dispositions (recorded; none applied)
| ID | Severity | Category | Finding | Disposition | Proposed change (not made) |
|---|---|---|---|---|---|
| M3P3-F1 | MINOR | Coordinate-frame and physics consistency | DR-0024 "Q4 coordinate conventions" states v_EF = R(t)(v_I − ω × r_I) generally. In general v_EF = R v_I + Ṙ r_I, so the stated form holds only when Ṙ = −R[ω×], i.e. rotation about a fixed pole at ω_E (DR-0028 A1). FC-9 replaces only FC-3/FC-4 and leaves the velocity tests unqualified for A2/A3 | **ACCEPTED.** The derivation is correct. The record's form is right for A1, but it is written as if general while DR-0028 leaves A2/A3 open | Scope the relation and FC-1/FC-2/FC-5 to DR-0028 A1. For A2/A3, state the general transformation, distinguish the frame's full angular velocity from the atmosphere's assumed spin, and extend FC-9 to the velocity tests. DR-0028 stays OPEN |
| M3P3-F2 | MINOR | Decision authorization and traceability | The DR-0024 amendment log quotes the withdrawn Q4 row with an ellipsis. It omits the §5.7 quotation and the attribution to the pinned rotation rate / D-rot-1, so the row is not preserved verbatim | **ACCEPTED.** The log claims to preserve the withdrawn text but abbreviates it (the full row is in `git show 23bafd2:docs/decisions/requests/DR-0024-…`). The DR-0026 Q-G3-9 log quotes its row in full | Append the complete previous Q4 row and status verbatim to the amendment log |

## Validation evidence at the reviewed commit (implementer)
See the checkpoint report for the run outputs: Proof in an isolated clone at `8a725b6`, CI at `007f38c`.

## Status after this review
- Not an unconditional PASS, so the stop condition applies. **No acceptance report has been prepared, the planning branch is not ready to merge, and T0 has not started.**
- **Returned to the Tech Lead:** authorization to apply M3P3-F1 and M3P3-F2 and whether to run another review round. DR-0028 remains OPEN.

## Resolution of findings (appended 2026-10-15; the sections above are unchanged)
**Authority:** the Tech Lead's instruction "M3 Planning — Resolve Review 03 and DR-0028" (2026-10-15), referred to as **I-3**. Section 1 authorizes only:
- the M3P3-F1 and M3P3-F2 corrections;
- resolving DR-0028 as J-ax-1;
- updating directly affected planning documents;
- one new review.

### M3P3-F1 (MINOR): velocity transformation needs a fixed-pole qualification
- **Original finding:** the revision-1 relation v_EF = R(t)(v_I − ω × r_I) was stated generally. In general v_B = R v_A + Ṙ r_A. FC-9 left the velocity tests unqualified. Disposition at review time: ACCEPTED.
- **Authorized decision (I-3 §3):**
  - document the general relationship;
  - state that J-ax-1 uses a constant identity rotation, so the derivative term is zero;
  - distinguish rotating and pole-of-date frames, where it cannot be omitted;
  - update FC-1…FC-9, adding checks that would detect omission of the derivative term, without bringing time-dependent rotation into M3 scope;
  - weaken nothing.
- **Exact correction:**
  - DR-0024 "Q4 coordinate conventions" revision 1 is kept unchanged under a "superseded" banner.
  - **Revision 2 is appended.** It contains:
    - the general relation v_B = R v_A + Ṙ r_A, with its fixed-axis special case and the conditions under which that case holds;
    - the M3 model (DR-0028 J-ax-1): the transformation to the inertial frame is the constant identity, so Ṙ = 0;
    - an explicit statement that atmospheric co-rotation, v_air = ω_E Ẑ × r, is air physics rather than a frame derivative, and must not be dropped because Ṙ = 0;
    - the revised specifications FC-1…FC-10, each with its change from revision 1. FC-1 is strengthened to an exact identity. FC-2(b) is added (it detects dropping co-rotation). FC-3/FC-4 are restated as axisymmetry properties. FC-9 is extended to the velocity tests. **FC-10 is a future-gated derivative-term check**: a finite-difference comparison, a known-answer case where omitting Ṙ r_A returns zero, and a test rotation that does not reduce to the fixed-axis shortcut.
- **Evidence:** differentiating r_B = R(t) r_A gives v_B = Ṙ r_A + R v_A (product rule). With Ṙ = −R[Ω×], v_B = R(v_A − Ω × r_A), which reduces to revision 1 only for Ω = ω_E Ẑ. For R ≡ I₃, Ṙ = 0.
- **Residual uncertainty:** none on the mathematics. Tolerances for FC tests come from the later threshold DR.
- **Changes an acceptance decision?** No.

### M3P3-F2 (MINOR): amendment log abbreviated the withdrawn Q4 attribution
- **Original finding:** the DR-0024 amendment log quoted the withdrawn Q4 row with an ellipsis, omitting the §5.7 quotation and the attribution to the pinned rotation rate / D-rot-1. Disposition at review time: ACCEPTED.
- **Authorized decision (I-3 §4):**
  - preserve the complete withdrawn text verbatim;
  - remove the ellipsis abbreviation;
  - preserve the history;
  - record the correction as an append-only amendment;
  - keep the original and amended records distinguishable.
- **Exact correction:**
  - In the first log entry, the abbreviated quotation was replaced in place by a bracketed pointer: "[abbreviated quotation removed 2026-10-15 under review M3P3-F2; …]". This in-place edit, and the abbreviated form, are recorded in the new entry; the abbreviated form remains in commit `8a725b6`.
  - **A new "M3P3-F2" entry is appended.** It quotes the complete withdrawn row verbatim from `23bafd2`, markdown included, in a code block. It then distinguishes three records: the original (withdrawn, commit `54a49e4`), the amended row (current) and the realization (DR-0028).
- **Evidence:** a byte comparison of the quoted row with `git show 23bafd2:docs/decisions/requests/DR-0024-m3-physical-models-and-constants.md` is recorded in the checkpoint report. The DR-0026 Q-G3-9 log already quoted its row in full, and its rows are unchanged.
- **Residual uncertainty:** none.
- **Changes an acceptance decision?** No.

### DR-0028 (owner decision, I-3 §2)
- **Decision:** APPROVED J-ax-1, with requirements R-1…R-4.
- **Recorded in:**
  - DR-0028 Resolution, with the limitations, the implications for future capabilities and the extension point;
  - SCI-0013/0014/0017, "status update 2";
  - ADR-0009 item 17 and a note at DR-0026 §5.7;
  - the decision matrix, M3-proposal and the milestones README.
- **Not authorized:** no Earth-orientation implementation.
