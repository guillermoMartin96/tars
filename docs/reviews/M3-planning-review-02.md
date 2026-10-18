# M3 planning decision checkpoint — independent review 02

**Scope:** the recording of the Tech Lead's G1–G3 decisions (commit `54a49e4`): DR-0024/0025/0026 Resolutions, DR-0024 §3.4–§3.5 (Q10 verification, GM/a consistency), DR-0027, ADR-0009, SCI-0005 and VAL-0007 correction notes, SCI-0013…0017, milestone documents, the Q10 script. No M3 implementation exists.  
**Reviewer:** Codex (separate provider), session `01a141c7-1591-7f63-8e57-f94c05c008eb`, at `ea56e76`, on a git clone with metadata.  
**Prompt:** `raw/M3-planning-codex-review02-prompt.md`. **Raw output:** `raw/M3-planning-codex-review02.md`.  
**Severity scale:** BLOCKER / MAJOR / MINOR / NOTE.  
**Instruction for this outcome (Tech Lead, 2026-10-15, section 6):** "If Codex returns REQUEST_CHANGES, record the findings and STOP. Do not repair them automatically." **No finding below has been applied.** The planning branch is not merged and T0 has not begun.

## Verdict
**REQUEST_CHANGES:** two BLOCKER and one MINOR finding.

The reviewer confirmed:
- 32 changed files, all under `docs/`; no implementation;
- `assumptions.md` 185 additions / 0 deletions and `validation.md` 43 / 0: historical lines unchanged;
- both correction notes separate historical result, incorrect description, corrected interpretation and (unchanged) acceptance, and their factual claims are supported (gating GMAT scripts use point masses with `Earth.Mu`; informational scripts use `JGM3.cof`);
- Q10: 25 identical rows, 2 differing, 1 absent; all 27 boundary jumps recomputed (+1.3616e-3 at 25 km, +9.589e-5 at 80 km, −1.5345e-5 at 250 km);
- DR-0024 §3.5 magnitudes (2.195e-7, 7.53e-10, 8.98e-6; ratio ≈ 41) and its consistency conclusion;
- thresholds, dt, reference missions, geodetic source, snapshot treatment, termination altitude and dataset residuals remain open or deferred; AC-1 accepted; AT-1…AT-7 open; no language, runtime or hardware decision.

The reviewer could not fetch the author's file (no network) and did not re-verify the source digests or errata.

## Dispositions (recorded; none applied)
| ID | Severity | Finding | Disposition | Proposed change (not made) |
|---|---|---|---|---|
| M3P2-F1 | **BLOCKER** | DR-0024 Q4 (frame-z axis for J2, ellipsoid and atmosphere rotation) and DR-0026 Q-G3-9 (two-body `escape` check) are labelled "APPROVED via D3", although the owner's decision text did not address them. Inferring them from the D3 approval is an attribution the owner did not make | **ACCEPTED.** The implementer's records say "flagged for confirmation", but the status column still claims approval; that overstates the owner's decision | Mark Q4 and Q-G3-9 **OPEN (BLOCKED ON OWNER)**, keeping J-ax-1 and the two-body check as recommendations; propagate to SCI-0013/0014/0017 status lines and M3-proposal §9. **Owner decision needed:** confirm or reject J-ax-1 and the escape simplification |
| M3P2-F2 | **BLOCKER** | The documents call T0 "authorized after the planning merge", which the reviewer found unsupported | **REJECTED_WITH_REASONING.** The Tech Lead's instruction, section 8, says: "After the planning merge succeeds, create a fresh M3 implementation branch from the new main and perform T0 only", with the T0 scope listed there. The review prompt included the owner's sections 1–5 only, so the reviewer could not see sections 6–8. The finding comes from the prompt's omission, not from the records. The records' wording ("authorized after the planning merge") matches the conditional authorization | None. A future review prompt should include sections 6–8 |
| M3P2-F3 | MINOR | DR-0024 §3.4 and DR-0027 §B say the 0.0 vs 0.010 km lowest base altitude affects "heights below 10 m only". For any height in the lowest band, ρ_author/ρ_GMAT = exp(0.010/7.249) = 1.00138 (verified), i.e. **0.138 % throughout 0–25 km**. The claim that every reachable band is confirmed is also overstated for that band | **ACCEPTED** (documentation correction; the dataset choice stays OPEN in DR-0027 B) | Correct both descriptions to "0.138 % density difference throughout the 0–25 km band"; qualify the "confirmed" statement. No effect on LEO validation orbits, but relevant to the termination floor (DR-0027 A) |

## Status after this review
- **Merge conditions (section 7) not met:** the review is not an unconditional PASS. The planning branch stays unmerged; **T0 has not started** (section 8 depends on the merge).
- **Decisions returned to the Tech Lead:** F1 (Q4 axis, Q-G3-9 escape check) and authorization to apply the F1 and F3 corrections, followed by a further review round if wanted.

## Resolution of findings (appended 2026-10-15; the sections above are unchanged)
**Authority:** the Tech Lead's instruction "M3 planning checkpoint continuation" (2026-10-15), sections 1–4. Referred to below as **I-2**; the earlier instruction ("M3 planning decision checkpoint", sections 1–8) is **I-1**. Consolidated status: `docs/milestones/M3-decision-matrix.md`.

### M3P2-F1 (BLOCKER): unaddressed choices recorded as approved
- **Original finding:** DR-0024 Q4 (common axis) and DR-0026 Q-G3-9 (two-body `escape`) were labelled "APPROVED via D3", although the owner had not addressed them. Disposition at review time: ACCEPTED.
- **Authorized decision (I-2 §1):**
  - **Q4 APPROVED with constraints:** the Earth-fixed +Z axis is the common physical symmetry/rotation axis for J2, the reference ellipsoid and atmospheric rotation. Earth-fixed and inertial representations must be distinguished and transformed correctly, and the conventions and frame-consistency tests recorded.
  - **Q-G3-9 APPROVED with constraints:** the two-body specific-energy escape diagnostic is retained as an approximation, neither an exact escape criterion in perturbed dynamics nor independent authorization for safety-critical actions.
- **Exact correction:**
  - DR-0024: Q4 row replaced by the owner's decision; new section "Q4 coordinate conventions" (representations I and EF, transformations, tests FC-1…FC-9); amendment log quoting the withdrawn row verbatim.
  - DR-0026: Q-G3-9 row replaced by the owner's decision, with an explanatory note; amendment log quoting the withdrawn row; a note on the §5.7 proposal text.
  - SCI-0013/0014/0017: appended status updates; the original status lines are kept.
  - ADR-0009: items 14–15. M3-proposal §9 and the milestones README updated.
  - **New DR-0028 (OPEN):** the owner's text names a physical axis, not a DR-0024 option. Whether the Earth-fixed +Z coincides with the inertial z axis (J-ax-1) or follows the pole of date (J-ax-2/3), and any Earth rotation angle, is not decided. Following I-2 §7 ("If a decision remains ambiguous, create a new decision request rather than assuming approval"), the implementer raised it as a DR instead of reading the approval as J-ax-1.
- **Evidence:** I-2 §1 (verbatim in `raw/M3-planning-codex-review03-prompt.md`). Under J-ax-1 all three models are axisymmetric about the shared +Z, so J2, geodetic height and v_rel do not depend on the rotation angle (DR-0028 Facts). FC-3, FC-4 and FC-2 make that a test.
- **Residual uncertainty:** DR-0028 A and B. T1/T2 are blocked on it; T0 is not, provided it labels the realization it assumes.
- **Changes an acceptance decision?** No. No M1/M2 acceptance depends on M3 axes or `escape` in perturbed dynamics; `escape` keeps its v1/v2 meaning.

### M3P2-F2 (BLOCKER): T0 authorization unsupported
- **Original finding:** the records called T0 "authorized after the planning merge", which the reviewer could not support from the supplied sections 1–5. Disposition at review time: REJECTED_WITH_REASONING (I-1 §8 does authorize T0 after the merge; the prompt omitted sections 6–8).
- **Authorized decision (I-2 §1):** "The next Codex review must receive the complete applicable instructions, including sections 1–8, rather than the truncated sections 1–5."
- **Exact correction:**
  - The review 03 prompt (`raw/M3-planning-codex-review03-prompt.md`) includes I-1 sections 1–8 and I-2 sections 1–7 verbatim, extracted from the session transcript and not paraphrased.
  - **Independently of F2,** I-2 §7 changes the T0 gate ("Do not merge or begin T0 until I explicitly approve the checkpoint"). Every record that said T0 is authorized after the planning merge now carries an appended note: T0 also needs the explicit checkpoint approval (DR-0024 Follow-up, DR-0027, M3-proposal status and T0 row, milestones README).
  - The original wording is kept.
- **Evidence:** I-1 §8 text: "After the planning merge succeeds, create a fresh M3 implementation branch from the new main and perform T0 only". I-2 §7 text quoted above.
- **Residual uncertainty:** none on the records. Whether I-2 §7 suspends I-1 §7's conditional merge authorization is read conservatively: the planning merge waits for explicit approval.
- **Changes an acceptance decision?** No. It narrows authorization; nothing was merged and T0 has not started.

### M3P2-F3 (MINOR): lowest-band discrepancy affects the whole band
- **Original finding:** DR-0024 §3.4 and DR-0027 §B said the 0.0 vs 0.010 km base altitude affects "heights below 10 m only"; in fact ρ_author/ρ_GMAT = exp(0.010/7.249) = 1.00138 throughout the band. Disposition at review time: ACCEPTED.
- **Authorized decision (I-2 §1):** correct the explanation, quantify the consequences, preserve the historical finding.
- **Exact correction:**
  - DR-0024 §3.4: a correction sub-list under the original bullet, which is kept.
  - DR-0027 §B: the table cell annotated, plus a "Correction M3P2-F3" block and a "Disputed cells" table in the Resolution.
  - SCI-0015: appended status update.
  - New research script `q10_residual_consequences.py` and its results.
- **Evidence (quantified):**
  - The GMAT density is **0.13785 %** below the author's file for every 0.010 ≤ h < 25 km; below 0.010 km the author's table selects no band.
  - With the author's base, the 25 km jump would be −1.89e-5 instead of +1.36e-3.
  - The drag acceleration scales with density, so the drag difference is the same 0.138 % in that band.
  - The other disputed cells: +1.5e-5 below 1000 km from the 900 km scale-height rounding; above 1000 km +19.6 % at 1100 km and +145 % at 1500 km, because the author's file has no 1000 km row.
  - Rerun byte-identical. The ratio matches review 02's independent value 1.00138045256944.
- **Residual uncertainty:** the printed table was not read; no trajectory effect simulated (no planned orbit enters 0–25 km).
- **Changes an acceptance decision?** No. It bears on DR-0027 A-4/A-6 if a termination altitude below 25 km is ever proposed.

### Corrections found by the implementer while applying the decisions (not review findings)
- **DR-0024 Q8 / SCI-0015, behaviour above the top band.** The Q8 row and SCI-0015 said "Above the top band, the table's own top-band exponential applies as the source defines", under an "APPROVED" status. The owner never decided that. With I-2 §2 requiring the domain behaviour to be defined explicitly (DR-0027 B-4), the statement is withdrawn (amendment logs) and the behaviour is OPEN, to be proposed at T0. It is the same class of error as F1.
