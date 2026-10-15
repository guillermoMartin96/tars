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
