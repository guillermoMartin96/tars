You are an independent reviewer from a separate provider; you did not write these documents. This is TARS Milestone 3 **planning checkpoint** (research and design only; no M3 implementation exists or is authorized). Review round 1 (the only planned round).

The snapshot is the current directory: a git clone of branch `milestone-3-planning` at HEAD, with git metadata. The research branch is available as `origin/research/flight-software-architecture`. A ready Python environment is in `./.venv`. You review; you do not fix. Do not modify `src/`, `tests/`, `toolbox/`, `scenarios/`, `proof/` or `docs/`. Put scratch files only under `./review_scratch/` (git-ignored by `.git/info/exclude`).

## Context
- Planning baseline: `main` = `d92ab894907d06b2b13aefff6c005caa0026a68f` (M2 accepted and merged; M2 is CLOSED and must not be reinterpreted).
- The Tech Lead approved G0 = M3 Option A (J2 + atmospheric drag) and asked for research and Decision Request drafts for G1 (physical models and constants), G2 (validation strategy) and G3 (force/scenario/event architecture), plus an M1/M2 → M3 artifact impact analysis. Nothing may be decided on the Tech Lead's behalf; no thresholds may be invented or borrowed; no Rust/C/FFI.
- Documents under review (all on this branch; `git diff d92ab89..HEAD`):
  - `docs/decisions/requests/DR-0024-m3-physical-models-and-constants.md` (G1)
  - `docs/decisions/requests/DR-0025-m3-validation-strategy.md` (G2)
  - `docs/decisions/requests/DR-0026-m3-force-scenario-event-architecture.md` (G3)
  - `docs/milestones/M3-baseline-and-impact.md` (baseline verification; class A/B/C impact)
  - `docs/milestones/M3-proposal.md`, `docs/milestones/README.md`
  - `docs/science/validation.md` (appended VAL-0018 only)
  - `docs/science/experiments/m3-planning/` (planning experiment scripts, results, GMAT probe scripts)
  - On the research branch: `git diff 27ad862..origin/research/flight-software-architecture` (ADR-0008 PC-1, AT-1 hypothesis analysis; RES-0001 §13).
- Accepted context you may consult: ADR-0001…0007, DR-0001…0023, `docs/science/assumptions.md`, `proof/`, `src/tars/` (the current architecture the DRs describe).
- GMAT R2026a may not be available in your sandbox; GMAT probe numbers can be checked against the committed scripts and results only. The Python experiment can be re-run: `.venv/bin/python docs/science/experiments/m3-planning/perturbation_experiment.py $PWD/src scenarios/m1_leo_250km.json review_scratch/pert.json` (about 1 minute).

## Look specifically for
1. Incorrect orbital mechanics (formulas, secular-rate expressions, decay theory, invariants, sign conventions, magnitudes).
2. Incorrect J2 formulation assumptions (normalization, J2 = −√5 C̄20, tide systems, reference radius / GM pairing, axis/frame).
3. Incorrect drag assumptions (equation, v_rel, rotation, density model behaviour, scale heights, geodetic vs spherical height, mass coupling, domain).
4. Reference-frame mistakes (ECI/MJ2000 vs pole of date, the TOEEq technique and what it does and does not establish).
5. False claims of validation independence (two codings of one equation called independent; GMAT agreement over-interpreted).
6. Arbitrary thresholds (any numeric acceptance value without derivation, measurement, authoritative source or explicit owner judgment) and any M1/M2 threshold silently borrowed.
7. Hidden changes to M1/M2 assumptions, evidence or meaning (confirm with `git diff d92ab89..HEAD --stat` that only `docs/` changed and that existing M1/M2 records were not rewritten; `docs/science/validation.md` must be append-only).
8. Over-engineered architecture (abstractions without a concrete M3 need) — and, conversely, architecture that would block foreseeable forces (higher-order gravity, third body, SRP, thrust, attitude-dependent aero).
9. Reproducibility / versioning gaps ("same scenario, different physics"; physics identity; references bound to the right identity; v1/v2 frozen).
10. Premature Rust/C commitments or anything exceeding ADR-0008 TL-6…TL-9.
11. Missing owner decisions (anything decided on the owner's behalf, or a needed decision not listed).
12. Factual accuracy of cited sources and of the numbers quoted from the experiments (spot-check against `perturbation_results.json`, `gmat_probe_results.json`, the IERS/NGA values quoted).

## Output
Your final message, in Markdown. One block per finding, numbered from M3P-F1:

### M3P-F<n> — <title>
**Severity:** BLOCKER | MAJOR | MINOR | NOTE
**Where:** file and section
**Claim:** ...
**Evidence:** ...
**Suggested resolution:** ... (state whether it is a mechanical/documentation correction or requires choosing between engineering policies)

Severity meaning: BLOCKER — the checkpoint must not go to the Tech Lead as is (e.g. wrong physics that a recommendation rests on, a hidden M1/M2 change, a decision taken on the owner's behalf). MAJOR — a substantive error or gap that would mislead a G1–G3 decision. MINOR — a local inaccuracy or omission. NOTE — observation, no change required.

Then a **Summary** with exactly one verdict — PASS (no BLOCKER/MAJOR), PASS_WITH_FINDINGS (MINOR/NOTE only) or REQUEST_CHANGES (any BLOCKER/MAJOR) — a list of what you verified (with numbers you reproduced), and a one-line statement of whether the planning checkpoint is ready to go to the Tech Lead.
