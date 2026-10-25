You are an independent reviewer from a separate provider. You did not write any file under review. This is a **documentation-only independent review (Review 01)** of the TARS spacecraft simulator's Milestone 3 **owner-decision recording and reconciliation** made under the owner's Authorization I-26 (verbatim at the end). The implementer's documents are claims, not evidence: verify them against the owner's exact wording, the repository and mathematics.

## Snapshot and rules
- **The current directory** is a fresh git clone, detached at the pinned head **`2cd1e6ec1bc2df13827c36d03fda5bf4b4150c09`** (branch `milestone-3-t2-owner-decisions`). Its parent **`a57de3f0fb1a8265f5a493a836ad6305b0396d8c`** is the reviewed planning HEAD (readiness Review 03 PASS, at `628623b` plus its records). `main` = `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`.
- A locked Python environment is in `./.venv`. Use `.venv/bin/python -I`. **The network is not available.**
- **Do not modify tracked files.** Scratch only under `./review_scratch/` (excluded from git). Do not run `toolbox/scripts/run_m1_proof.sh` or `run_m2_proof.sh`. You may read `docs/science/experiments/m3-t0/t0_model.py` and `t0_termination.py` and import them read-only. Finish with a clean tracked tree.
- **Preconditions already performed by the implementer (do not redo; no network):** I-26 §1 baseline verification (origin/main = `fc50aed`, planning HEAD `a57de3f`, Review 03 verdict and evidence digests, no protected-path change in I-23 … I-25), creation and push of `milestone-3-t2-owner-decisions`, and the push of `2cd1e6e`. Treat CI and remote facts as claims you cannot authenticate. The DQ-4 packaging probe was run by the implementer in a scratch copy; its record is `docs/reviews/raw/M3-T2-owner-decisions-I26-evidence/dq4_packaging_probe.out` (you may repeat it in `review_scratch/` with `uv build --offline` if `uv` is available; it is not required).
- **Decision boundaries.** You review; you do not decide. Do not record any item as approved beyond what I-26's text approves. In particular, do not treat P6, DR-0028 P6(b), X-1, A-FP-2, A-LM-1 or A-LM-2 as approved. Do not fix anything.

## What is under review (`git diff a57de3f..2cd1e6e`, 20 files, all under `docs/`)
- **Authoritative records (append-only notes / owner-decision blocks):** `docs/decisions/requests/DR-0029-m3-t0-proposals.md` (P1–P9 owner-decision blocks, summary cells, Blocked work, Resolution incl. Q-GATE); `DR-0024 … DR-0028` ("I-26 note" in each, status-line appends); `docs/decisions/0009-m3-force-context-and-physics-identity.md` (I-26 note).
- **New:** `docs/decisions/requests/DR-0028-P6b-owner-ruling-packet.md` (a ruling packet that must decide nothing); `docs/milestones/M3-T2-authorization-packet-r1.md` (revised T2 packet, must be DRAFT — NOT AUTHORIZED, with the conditional-row register); `docs/reviews/raw/M3-T2-owner-decisions-I26-evidence/` (DQ-4 packaging probe and SHA256SUMS).
- **Companions (append-only):** `docs/milestones/M3-T2-validation-strategy.md` (§6 revision), `M3-decision-matrix.md`, `M3-T0-decision-matrix.md` (amended dependency statement and T2 dependency matrix), `M3-open-issues-register.md`, `M3-T2-authorization-packet.md` (I-23 draft; pointer only), `M3-T2-decision-readiness-report.md`, `README.md`; `DR-0029-P1-P9-owner-decision-packet.md`, `DR-0029-P1-P9-owner-briefing.md`.

## What you must independently assess (I-26 §7, plus the specific risks below)
1. **Fidelity to the owner's exact wording.** Every recorded decision (P1–P9, Q-GATE, DQ-1 … DQ-6, the §5 floating-point policy) matches I-26 verbatim, with nothing added to, weakened in, or dropped from the owner's text. Check the implementer's surrounding notes and summaries (tables, "Implementer notes on the record", "Governing reading") for any statement that changes, extends or narrows an approved choice. Specifically examine these implementer readings: P9 V2's C_d = 2.2 (taken from DR-0029's summary row and P9 Evidence); P7's vehicle mapping (V2 for RM-7, V1 for other drag missions); P3's `reentry` identifier (OI-23); DR-0026 §5.8 "total" height conversion vs P8 domain rejection (OI-27); DQ-6 vs DR-0026 AR-7/§5.3 (OI-28); DR-0027 B-4 recorded as DECIDED.
2. **P6 status.** P6 must not appear as fully decided anywhere; method (d) only PROVISIONALLY SELECTED; the geodetic-drag item ESCALATED_FOR_INVESTIGATION; no independent geodetic GMAT gate; DR-0028 P6(b) not decided (and the ruling packet presents options without deciding); X-1 not authorized; the register P6-U1 … P6-U8 is faithful to DR-0029 P6's evidence and introduces no new requirement.
3. **Consistency across dependent records.** DR-0024 … DR-0029, ADR-0009, the matrices, the register, the strategy and packet r1 agree with each other and with the owner's text; status labels DECIDED / PROVISIONALLY SELECTED / OPEN / ESCALATED_FOR_INVESTIGATION / NOT AUTHORIZED are used correctly and distinctly.
4. **The amended gate (Q-GATE).** It supersedes only the T2 clause of the I-15 statement; it does not waive any T3/T4/T5 requirement or any scientific, review, numerical or acceptance gate; P10's T1 clause unchanged.
5. **Validation strategy vs the selected algorithms and arithmetic.** Compare packet r1 §5's operation sequences for DQ-1 (α) and DQ-2 (km) with `docs/science/experiments/m3-t0/t0_model.py` (`geodetic_iterative`, `density`, `band_index`, constants). Is the spec exact (start latitude, stopping rule and its placement, pole-safe height, derived constants F and e2, the km-route grouping, band rule), and is the metres-first guard the only intended difference on the density path? Is the claim "on every input with h_m ≥ 0 this is the T0 km-route arithmetic" correct, including h_m = −0.0?
6. **Conditional-row register (packet r1 §6.2; strategy §6).** Does it identify **every** row whose gating depends on A-FP-2, A-LM-1 or A-LM-2 (search the strategy §3 rows and §3.9 B-1 … B-15)? Is the U-23 third-clause reclassification (T0 E4b depends on A-FP-2) correct? Are the rows kept unconditional (B-1, B-2, B-13, B-14 behaviour part, the exact rows) genuinely independent of those assumptions? Are exact z-reflection (U-19 (b)) and strict decrease (PM-4 (b)) report-only regardless? Is any tolerance invented or any unproved bound promoted? Are the stated promotion evidence standards (J-FP2, J-LM1, J-LM2) consistent with the owner's policy without adding approvals?
7. **Contracts preserved.** Accepted T0, T1 (J2 class, constants, gates), M1/M2 and P10 contracts are unchanged and nowhere weakened.
8. **No implied approval to execute.** Packet r1 and every other new text authorize nothing; T2, T3, T4, T5 remain NOT AUTHORIZED; preconditions are stated honestly (including the unmerged base branch).
9. **Documentation-only and append-only.** Only `docs/` changed; no protected path (`src/`, `tests/`, `proof/`, `toolbox/`, `scenarios/`, `.github/`, `uv.lock`, `pyproject.toml`) or T0/T1 evidence touched; the I-23 … I-25 records (readiness reviews, raw reviews, corrections records, evidence) unchanged; every pre-existing line either unchanged or only appended to (table-cell appends before the closing `|` follow the P10 precedent).
10. **New errors** of fact, arithmetic or citation introduced anywhere in the diff (for example V1's B, the thresholds quoted, line citations into `t0_model.py`, the DQ-4 probe claims).

## Output format
Markdown:
1. First line: `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES`.
2. Summary.
3. Findings table: ID (M3T2OD-R1-Fn), severity (BLOCKER / MAJOR / MINOR / NOTE), location, finding, evidence (commands or derivations, with results), proposed disposition/correction.
4. Assessment of items 1–10, each with what you checked and the result.
5. Your own computations (commands and outputs).
6. Limitations.
Severity guide: BLOCKER/MAJOR = a recorded decision that differs from the owner's text, an approval presented as made, a waived gate, a wrong technical claim that would mislead the T2 authorization, or a scope violation; MINOR = inaccurate or unsupported statement not changing a decision, classification or gate; NOTE = clarity. PASS means no BLOCKER or MAJOR finding remains.

## Owner authorization I-26 (verbatim)

# TARS — Authorization I-26
## M3 Owner Decision Recording, Gate Amendment, and T2 Authorization Preparation

You are working on the TARS spacecraft simulation project.

This authorization follows I-23, I-24, and I-25, which prepared and independently reviewed the M3 T2 decision-readiness package.

The owner has reviewed the recommendations and explicitly approved the decisions specified below.

Your task is to record those decisions in their authoritative decision records, reconcile the resulting requirements, and prepare a revised T2 implementation authorization packet.

**This is a decision-recording authorization, NOT a T2 implementation authorization.**

## 1. Workspace and baseline

This is a new Superset workspace for the owner-decision phase.

Expected repository state:

- `origin/main`: `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`
- Reviewed planning branch: `milestone-3-t2-decision-readiness`
- Reviewed planning HEAD: `a57de3f`
- I-25 Independent Codex Review 03: PASS, no findings
- Review 01: six findings resolved
- Review 02: three findings resolved
- T1: accepted and merged
- T2: not authorized
- DR-0029 P10: previously decided
- DR-0029 P1–P9: open before I-26

### Mandatory checks

1. Fetch all relevant remote references.
2. Verify the exact main and planning-branch SHAs.
3. Verify the reviewed planning worktree is clean.
4. Verify Review 03's verdict and the corresponding evidence.
5. Verify no protected paths changed during I-23 through I-25.
6. Read the complete authoritative decision records before editing.

Read at minimum:

- `DR-0029-m3-t0-proposals.md`
- `DR-0029-P1-P9-owner-decision-packet.md`
- `DR-0029-P1-P9-owner-briefing.md`
- `M3-T2-authorization-packet.md`
- `M3-T2-validation-strategy.md`
- DR-0024 through DR-0028, including applicable amendments
- The M3 proposal and milestone dependency matrix
- I-25 final readiness report and Review 03

The authoritative DR text governs where the briefing or packet differs.

If a discrepancy would materially change an approved choice, STOP and report it rather than guessing.

### Branching

Create a new decision-recording branch and worktree from the verified planning HEAD:

`milestone-3-t2-owner-decisions`

Follow the repository's established Superset worktree and remote-branch conventions.

Do not reuse the T1 implementation worktree.

Do not modify main directly.

## 2. Approved DR-0029 decisions

The following are explicit owner decisions.

Record them append-only in the authoritative DRs, preserving historical proposal text and decision provenance.

### P1 — Termination-altitude admissibility

**DECIDED: A4-b.**

Use:

- v̂ = V_b, the derived bound for bound-state relative velocity.
- κ = 0.01.
- Clause 1: a − b < h_f < h_geod(initial).
- Clause 2: ρ(h_f) × V_b × dt / B_min ≤ 0.01.

The ballistic coefficient uses dry mass.

Record that this is a necessary admissibility screen, not a sufficient numerical stability or trajectory-accuracy guarantee.

The derivation bounds the drag velocity-Jacobian contribution only. It does not bound the full coupled dynamics or ∂a/∂r.

κ is an owner-selected engineering constant, not a physically established universal threshold.

The final M3 timestep remains a separate decision.

### P2 — Termination crossing

**DECIDED: A5-b.**

Detect termination from committed states and report an additional scalar cubic-Hermite estimate of the crossing time.

The simulation ends at the committed state, not the interpolated crossing.

The reported crossing time is not a propagated state.

No final-step splitting is authorized.

Missed crossings or dips between committed states remain a documented limitation. Do not claim a certified perturbed-motion missed-dip bound.

T2 must expose the geodetic normal or latitude required for T3 to compute dh/dt.

### P3 — Outcome precedence

**DECIDED: Adopt the DR-0029 proposal.**

Precedence:

1. `non_finite`
2. `reentry`
3. `impact`
4. `escape`

Preserve `impact` as the legacy backstop.

Termination is determined from geodetic height, independently of atmospheric band selection.

Preserve the published density discontinuities.

This decision specifies future T3 behavior; do not implement it under I-26.

### P4 — Below-domain density

**DECIDED: Option (ii), fail closed.**

Any finite geodetic height below 0 m must cause a typed atmosphere-domain error.

The domain guard must compare height in metres before conversion to kilometres.

Negative zero is in range.

Non-finite heights receive a distinct error classification.

A failing RK4 stage must not commit a partial simulator state.

Explicitly reconcile DR-0026 AR-8 and §5.8: statements that density is total do not apply below the atmospheric table's lower edge.

T3 will define the versioned run-outcome mapping. Do not implement that mapping now.

Do not reproduce the T0 spike's negative-subnormal guard defect.

### P5 — Atmospheric altitude regions

**DECIDED: Adopt the DR-0029 P5 region table**, consistently with P1 and P4.

For heights above the 1000 km base, extrapolate the pinned top atmospheric band. Do not introduce a zero-density cutoff or a new upper-domain failure.

Preserve the pinned density table exactly.

Adopt the proposed wording amendment:

The top band's formula is continuous for h > 1000 km, but the 1000 km base retains its published relative density jump of approximately −1.598 × 10^-5.

Do not impose continuity across band boundaries.

Retain the published GMAT band-selection rule and exact-base behavior.

Explicitly label extrapolated densities above 1000 km as unverified.

### P6 — GMAT reference configuration

**NOT FULLY DECIDED.**

Approve decomposed exact-configuration method (d) as the preferred direction for subsequent validation planning, subject to its authoritative configuration requirements.

Do not mark P6 fully resolved.

The geodetic-drag discrepancy of approximately 0.14–0.38 m remains escalated.

Do not approve an independent geodetic GMAT acceptance gate.

Do not silently decide DR-0028 P6(b). Prepare a separate, explicit owner ruling on whether driving the validator with GMAT's reported axis is within the previously approved Earth-orientation scope.

The proposed X-1 investigation remains unexecuted and requires separate authorization.

Record the provisional method selection without converting unresolved evidence into a PASS.

### P7 — Reference missions

**DECIDED: RM-0 through RM-8.**

Use the P1 admissibility rule for RM-8.

Use the P9 illustrative vehicle definitions.

RM-3b is a candidate to be measured during T4, not a new mandatory gate without subsequent approval.

Preserve all previously accepted M1/M2 requirements.

### P8 — Geodetic-height reference points

**DECIDED: Options (a) and (a′), with the reviewed gating restrictions.**

Use exact mathematical answers as the primary gate source within their justified domain.

Use forward-constructed points as additional reference evidence.

Forward-constructed points become gating only after their numerical construction-error contribution has been derived and reviewed.

Negative-height cases remain report-only until appropriate bounds exist.

GeographicLib, GMAT and the identified IOGP/EPSG example are corroboration sources, not automatically authoritative inverse-height gates.

Do not claim independent verification from a reference that shares the same unexamined assumptions.

### P9 — Validation vehicles

**DECIDED: Option (i).**

Use the specified illustrative V1 and V2 vehicles from DR-0029.

V1:

- Mass: 850 kg
- Area: 15 m²
- C_d: 2.2
- Ballistic coefficient: approximately 25.8 kg/m²

V2 uses the accepted M2 vehicle mass configuration with area 15 m², as specified in DR-0029.

Every scenario and record must label these values:

**ILLUSTRATIVE — VALIDATION ONLY**

Do not claim they are validated representations of a real spacecraft.

## 3. Q-GATE — Approved amendment

The owner explicitly approves narrowing the original I-15 prerequisite for T2.

The replacement rule is:

**Before T2 implementation may be authorized:**

- P1–P5 must be decided.
- P8 and P9 must be decided.
- DQ-1 through DQ-6 must be decided.
- The resulting contracts must be recorded and reconciled.
- An explicit, separate T2 implementation authorization is required.

P10 remains previously decided and binding for T1.

P6 is not a T2 implementation prerequisite. Its unresolved scientific questions remain blockers for geodetic GMAT acceptance in T5.

P7 must be decided before its reference-mission obligations are implemented in T3/T4; it is already approved in this authorization.

This amendment supersedes only the broader T2 dependency statement from I-15. It does not waive any scientific, review, numerical or acceptance gate.

Record the supersession explicitly with provenance.

## 4. Approved T2 design decisions

### DQ-1 — Geodetic algorithm

**DECIDED: α.**

Reproduce the T0 iterative geodetic-height algorithm operation for operation within its applicable domain, including its starting latitude, convergence criterion and pole-safe height calculation.

The T0-specific error bounds may be reused only where their original assumptions and arithmetic sequences actually apply.

The T0 domain-guard defect must not be copied.

Record that this deterministic, data-dependent iterative algorithm satisfies the intended T2 geodetic design requirement.

### DQ-2 — Density arithmetic

**DECIDED: km route.**

Preserve the T0/GMAT kilometre-based density arithmetic for the applicable formula evaluation.

The lower-domain guard must still operate on height in metres before conversion.

Explicitly document the departure from DR-0024 §9's proposed convert-once-to-SI wording.

Do not change the pinned atmospheric table or silently substitute a mathematically equivalent but numerically different expression.

### DQ-3 — Simulator integration

**DECIDED: (a).**

T2 may add the context-aware force protocol and integrate immutable ForceContext construction into the simulator's derivative closures.

Current stage mass must be used.

Preserve the legacy force-model interface through an adapter.

Existing M1/M2 behavior must remain byte-identical on the specified same-platform regression gates.

No change to tick logic, engine scheduling, step splitting or atomicity is approved by this decision.

Implementation still requires separate authorization.

### DQ-4 — Dataset storage and digest

**DECIDED: Pinned data file under `src/tars/sim/data/`, with its SHA-256 digest pinned in `tars.sim`.**

Use the recorded GMAT R2026a source digest.

Do not import `tars.validation.approved_digests` from the physics core.

Use the approved file-access mechanism compatible with the static architecture guard.

Verify the data file is packaged correctly.

If packaging requires a protected `pyproject.toml` change, STOP. Do not silently adopt embedded Python bytes.

The embedded-bytes alternative requires separate approval.

### DQ-5 — J2 integration

**DECIDED: (a).**

Wrap the accepted T1 J2 implementation through the legacy adapter.

Do not rewrite the J2 force class, change its constants or create a replacement J2 model.

Preserve all T1 evidence and validation gates.

### DQ-6 — Drag parameter ownership

**DECIDED: Immutable drag-component constructor parameters.**

C_d and cross-sectional area belong to the drag force component.

Mass comes from ForceContext.

Scenario v3 schema and serialization remain T3 responsibilities.

No new spacecraft schema is authorized in T2.

## 5. Conditional floating-point gates

The owner approves the following policy:

- A-FP-2, A-LM-1 and A-LM-2 are not accepted as universal IEEE-754 guarantees.
- Tests depending on these assumptions may gate only when the precise assumption has been independently justified for the supported execution environment and the resulting criterion has been reviewed.
- Until then, those tests are report-only.
- Exact z-reflection symmetry and strict density decrease remain report-only regardless of the above assumptions.
- Do not promote an unproved numerical bound into a mandatory acceptance criterion.
- Do not invent tolerances.
- Preserve all unconditional, independently justified gates.

The revised T2 authorization must identify every conditional row and the evidence required to promote it.

## 6. Recording and reconciliation

Record the approved decisions in their authoritative home records.

Use append-only resolution entries or the repository's accepted decision-recording convention.

Update:

- DR-0024 through DR-0029 as applicable.
- The M3 decision matrix.
- The T2 dependency matrix.
- The owner-decision briefing and packet.
- The M3 open-issues register.
- The T2 validation strategy.
- The draft T2 authorization packet.
- The milestone index where needed.

Preserve historical proposal text, previous review records and prior owner decisions.

Do not retroactively rewrite the I-23/I-24/I-25 evidence.

Distinguish clearly between:

- DECIDED
- PROVISIONALLY SELECTED
- OPEN
- ESCALATED_FOR_INVESTIGATION
- NOT AUTHORIZED

In particular, P6 must not be recorded as fully decided.

## 7. Independent verification

Before requesting implementation authorization:

1. Verify every recorded decision against the owner's exact wording above.
2. Verify that all dependent DR entries are consistent.
3. Verify the new T2 gate does not waive T3/T4/T5 requirements.
4. Verify the validation strategy matches the selected algorithms and arithmetic.
5. Verify the accepted T0/T1/M1/M2 contracts are preserved.
6. Verify the revised T2 authorization draft contains no implied approval to execute.
7. Verify all changes are documentation-only.

Run applicable documentation checks.

Request an independent Codex review of the decision recording and reconciliation, including the revised dependency gate and conditional validation policy.

If the review returns REQUEST_CHANGES, record and reproduce the findings, then STOP. Do not begin an unapproved correction loop.

If the review returns PASS, prepare the final owner checkpoint.

## 8. Version-control restrictions

All changes under I-26 must be documentation-only.

Do not modify:

- `src/`
- `tests/`
- `proof/`
- `toolbox/`
- `scenarios/`
- `.github/`
- `uv.lock`
- `pyproject.toml`

Do not modify golden references, pinned constants, numerical thresholds or existing accepted implementation artifacts.

Commit the decision recording and independent review evidence separately.

Push using ordinary, non-force pushes.

Do not merge or open a PR.

Do not change main.

## 9. Final deliverables

Produce:

1. Recorded P1–P5, P7–P9 decisions.
2. P6 provisional method-selection record and unresolved investigation register.
3. Explicit Q-GATE amendment.
4. Recorded DQ-1 through DQ-6.
5. Reconciled authoritative decision documents.
6. Updated dependency matrix.
7. Revised T2 validation strategy.
8. Revised T2 implementation authorization packet, marked **DRAFT — NOT AUTHORIZED**.
9. Independent Codex review record.
10. Final I-26 checkpoint report.

The checkpoint must include:

- Branch and exact HEAD.
- Commit list.
- Changed-file list.
- CI results.
- Decision-by-decision recording matrix.
- Independent review verdict.
- Remaining blockers and scientific uncertainties.
- Exact recommended next authorization.

Explicitly confirm that T2 has not started, no implementation files have changed, and nothing has merged.

## 10. Mandatory STOP

Stop after documentation reconciliation, independent review and checkpoint reporting.

Do not create the T2 implementation branch.

Do not implement the drag force.

Do not merge the owner-decision branch.

Do not start the P6 investigation.

Do not approve DR-0028 P6(b).

Do not authorize T3, T4 or T5.

Await the owner's next explicit authorization.

Begin with baseline verification.
