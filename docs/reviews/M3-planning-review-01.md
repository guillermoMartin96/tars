# M3 planning checkpoint — independent review 01

**Scope:** research and design only. DR-0024 (G1), DR-0025 (G2), DR-0026 (G3), `docs/milestones/M3-baseline-and-impact.md`, `M3-proposal.md`, VAL-0018, `docs/science/experiments/m3-planning/`, and the ADR-0008 / RES-0001 addenda on `research/flight-software-architecture` (`2d6d7e5`). No M3 implementation exists.  
**Reviewer:** Codex (separate provider), session `01a14180-0e2f-7fa1-877d-42affe40f0f3`, at `8096acd`, using a git clone with metadata.  
**Prompt:** `raw/M3-planning-codex-review01-prompt.md`. **Raw output:** `raw/M3-planning-codex-review01.md`.  
**Severity scale (Tech Lead instruction, 2026-10-15):** BLOCKER / MAJOR / MINOR / NOTE.  
**Rounds:** one, as instructed. There is no re-review of the corrections below; they are mechanical and are listed so the Tech Lead can check them.

## Verdict
**REQUEST_CHANGES:** one MAJOR and four MINOR findings, no BLOCKER.

The reviewer confirmed:
- all changes are under `docs/`, and `docs/science/validation.md` is append-only;
- the Python experiment reproduces every committed number exactly;
- the J2 signs, normalization, secular-rate expressions, mass coupling and dissipation preconditions are correct;
- the NGA and IERS values match the primary material;
- G1–G3 remain open, with no decision taken on the owner's behalf, no borrowed or approved M3 threshold, and no Rust/C/FFI commitment;
- the architecture additions have concrete M3 uses and do not block foreseeable forces.

## Dispositions
| ID | Severity | Finding | Disposition | Change |
|---|---|---|---|---|
| M3P-F1 | **MAJOR** | The density table was called "C0, with discontinuities only in its derivative". The literal table has finite value jumps from rounding (−1.5e-5 relative at 250 km, +1.4e-3 at 25 km), so the measured error ratios cannot be attributed to slope changes alone and are not an asymptotic order | **ACCEPTED** (documentation correction) | DR-0024 §4.3, §5, §11; DR-0025 §5 and Q-G2-3; experiment README; VAL-0018 now describe the table as discontinuous (value jumps plus slope changes). **The engineering-policy question the finding raises is not decided here:** literal table vs a continuity-enforced variant is added for the owner as **DR-0024 Q5a**, and as option (d) in DR-0025 Q-G2-3. The recommendations (literal table; order gates on smooth configurations only) are unchanged. **Owner resolution (2026-10-15):** literal table preserved, discontinuities documented, quantified and tested at every boundary (DR-0024 Q5a); order gates on smooth configurations only (DR-0025 Q-G2-3) |
| M3P-F2 | MINOR | The drag-induced along-track displacement was described as falling behind; it is ahead (+362 km projected on the point-mass velocity), because the lower orbit has higher mean motion | **ACCEPTED** | DR-0025 §4 corrected |
| M3P-F3 | MINOR | The semi-analytic decay oracle and the King-Hele rotation factor are approximate even for spherical height and a smooth atmosphere | **ACCEPTED** | DR-0025 Q6 and the DR-0024 [KH] entry relabelled approximate, with their assumptions and the reviewer's diagnostic (−7 974.5 m vs −7 980.1 m). The README finding is qualified. A more complete averaged model would be a later policy choice; none is made |
| M3P-F4 | MINOR | `M3-proposal.md` T2 and Q5 still described a zero-drag cutoff that DR-0024 rejects | **ACCEPTED** | Both now refer to the approved G1 domain policy |
| M3P-F5 | MINOR | The ω_E relative difference is 2e-8, not 2e-9 | **ACCEPTED** | DR-0024 §3.1 corrected |

No finding was rejected or escalated for investigation. The MAJOR finding's correction changes no proposed engineering decision: it corrects a factual description and adds an owner question.
