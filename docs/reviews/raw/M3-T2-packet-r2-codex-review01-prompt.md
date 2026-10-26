You are an independent reviewer from a separate provider. You did not write any file under review. This is a **fresh-context, independent scientific and architectural review** of the TARS M3 T2 implementation authorization packet, revision 2: `docs/milestones/M3-T2-implementation-authorization-packet.md`. The owner/Tech Lead authorized this review under I-32, reproduced verbatim at the end. **The packet's statements are claims, not evidence.** Inspect the actual repository documents, decision records, T0 spike code and probe evidence yourself, and where feasible reproduce calculations or construct adversarial counterexamples.

## Snapshot and rules
- **The current directory** is a fresh git clone, detached at the pinned head **`0e37db60eed706e041666b40abb5238609a83360`** (branch `milestone-3-t2-authorization`). Its parent `0a9c040430138845d529b3d8691a86d0f4fea61e` is `main` (the accepted reconciliation). The commit under review is `git diff 0a9c040..0e37db6` (all under `docs/`).
- A locked Python environment (CPython 3.12.15, macOS x86_64) is in `./.venv`; use `.venv/bin/python -I`, with `PYTHONDONTWRITEBYTECODE=1` when importing the T0 spike. **The network is not available.**
- **Do not modify tracked files.** Use only `./review_scratch/` for scratch; it is excluded from git. Put every reproduction script you write there, named `*.py`, and write each script's output next to it as `*.out`, so the implementer can preserve them. Do not run the M1/M2 proof scripts. Finish with a clean tracked tree.
- **Extra input, outside the repository (read-only):** the CPython v3.12.15 `Modules/mathmodule.c` cited by packet §6.5, at the path given by `--add-dir` (`/private/tmp/claude-501/-Users-guillermomartin--superset-worktrees-tars-cliff-tarsier-2d0cbac0/c0fbf38c-4577-4719-9f8a-ccbbc9c6fbf9/scratchpad/rev/inputs/mathmodule.c`). The implementer downloaded it from `https://raw.githubusercontent.com/python/cpython/v3.12.15/Modules/mathmodule.c`; its sha256 is `436a01da195e3c2b9576a4b9188d5d62e9883e62e74f2d60bc55194bfce98281`, matching the packet. Verify the checksum yourself. Web sources cited by the packet (glibc manual, CORE-MATH, Rust docs, Ferrocene, arXiv) are **not** available to you; say where a finding depends on them.
- **Preconditions already performed by the implementer (do not redo them; treat as claims):** branch/HEAD/remote sync, clean worktree, `0a9c040` on `main`, CI green at `0e37db6` (four jobs), I-31 evidence `SHA256SUMS` verifying, no protected path changed. You may re-check anything that is local.
- **Decision boundaries.** You review; you do not decide, approve or fix anything. Do not treat D-0 … D-8, P6, DR-0028 P6(b), X-1, A-FP-2, A-LM-1 or A-LM-2 as approved. Do not propose an unapproved CI or runtime migration as an implicit prerequisite. Do not propose a language migration.

## Where to look (non-exhaustive)
- The packet; `docs/milestones/M3-T2-authorization-packet-r1.md`; `docs/milestones/M3-T2-validation-strategy.md`; other `docs/milestones/M3-*`.
- `docs/decisions/requests/DR-0024` … `DR-0029` (including the DR-0029 P1–P9 and P10 packets and briefing, DR-0028 P6(b) packet); `docs/decisions/0009-m3-force-context-and-physics-identity.md`.
- `docs/science/assumptions.md`; `docs/science/experiments/m3-t0/` (in particular `t0_termination.py` `rounding_allowances`, `t0_oracle.py`, `t0_geodetic.py`, `t0_height_error.py`, `t0_model.py`), and the T0 review records in `docs/reviews/M3-T0-review-*.md` that derived E1.
- `docs/reviews/raw/M3-T2-authorization-I31-evidence/` (probe scripts, outputs, `SHA256SUMS`).
- RES-0001 and ADR-0008: `git show origin/research/flight-software-architecture:<path>` (unmerged branch, `2d6d7e5`); locate the files with `git ls-tree -r --name-only origin/research/flight-software-architecture`.
- `.python-version`, `.github/workflows/`, `pyproject.toml`, `uv.lock` (read only).

## What you must independently assess
Assess every item of I-32 §3 A–G. In particular:

**A. POG scientific validity.** Does premise-observed gating genuinely establish, on the finite gated domain, the premises T0 E1 requires? Examine trace completeness (can an elementary call escape a `math`-attribute proxy, e.g. via C-level calls inside `math.hypot`, `math.sqrt`, `float.__pow__`, `**`, implicit conversions, `math.fsum`, or operations the E1 derivation treats as elementary?), whether the instrumentation can change the measured numerics, whether rigorous bounds for O-1 and O-2 are achievable as specified, whether oracle uncertainty is handled conservatively (§6.4 rule 1 inequality, the |r| − δ substitution, the subnormal term), whether "an exhaustive check over the input domain the bound is used on" in J-FP2 (ii) (read the controlling text yourself) supports a finite-sample reading, whether CI platform differences can invalidate the argument, and whether a passing run is independently reproducible. Distinguish feasibility evidence from mathematical proof. Check E1's precise hypotheses (e.g., which calls, which arithmetic operations, iteration count, domain) against what POG observes.

**B. Error budget.** Recompute α and β from `rounding_allowances()` yourself. Check dimensions, the domain (true height ≥ 0; any upper limit?), the gate inequality |ĥ − h_ref| ≤ ε_h(h_ref + δ_O) + δ_O (is h_ref + δ_O the right side of the uncertainty for a function increasing in h?), and whether the probe's "1.92e-9 m = 0.216 ε_h" compares each point against its own ε_h(h) or against one value. Do not accept an empirical maximum as a bound.

**C. Invariants.** Read `math_hypot` / `vector_norm` in the supplied source and decide whether evenness is bit-exact for all binary64 inputs (including ±0, subnormals, inf/nan, the `max == 0` and scaling branches) and whether the U-19 (a′) claim follows for the full DQ-1 sequence (does DQ-1 use x and y anywhere other than through p?). Assess swap symmetry, `exp` monotonicity POG (D-4: is a two-point observed premise sufficient for B-10's conclusion?), P8 (a′)/D-7, DL-4 bitwise conformance (D-8), and construct tests that could pass despite a meaningful defect, or fail despite a correct implementation.

**D. Reproducibility.** RQ-1 … RQ-8 and D-5: is the CPython patch version sufficient for each source-dependent claim (hypot source vs. the platform libm, compiler and flags, architecture, FMA contraction in C code, `libm` version on Linux, macOS version)?

**E. Scope and traceability; F. D-0 … D-8 individually** (Recommendation APPROVE / REVISE / DEFER / REJECT; justification; required evidence; dependencies; consequences of approval; remaining blocker; special attention to D-1, D-3, D-4, D-7, D-8); **G. Rust boundary** (RES-0001, ADR-0008, TL-6, TL-9).

Reproduce numerically where feasible: e.g., rerun the I-31 probes and compare with the committed `.out`; recompute α, β, ε_h(120 km), ε_h(2000 km); recompute the worst ratio per point; test hypot evenness/swap on adversarial inputs (subnormal, huge, equal magnitudes, ±0); attempt a trace-bypass or instrumentation-perturbation counterexample.

## Output format
Markdown:
1. First line exactly one of: `VERDICT: PASS`, `VERDICT: REQUEST_CHANGES`, `VERDICT: BLOCKED`.
2. A summary.
3. A findings table with columns: ID (M3T2P2-R1-Fn), severity (BLOCKER / MAJOR / MINOR / NOTE), location (file:line), finding, evidence, recommended disposition.
4. Assessment of I-32 §3 A–G, section by section.
5. The D-0 … D-8 table (the six required fields each).
6. Required corrections or additional research.
7. Your own computations (commands and outputs; list the files in `review_scratch/`).
8. Limitations.

Severity guide:
- **BLOCKER:** a scientific or prerequisite defect that prevents the packet from being suitable for owner decision review, or a claim of justification that is false.
- **MAJOR:** an unsupported or misleading scientific claim, a gate that could pass despite a meaningful defect without that being stated, an approval presented as made, or a scope violation.
- **MINOR:** an inaccuracy or gap that does not change a decision, classification or gate.
- **NOTE:** clarity.

PASS means no BLOCKER or MAJOR finding. PASS does not authorize implementation or approve any decision.

## Owner authorization I-32 (verbatim)

# I-32 — Independent Review Authorization: M3 T2 Packet r2

## 1. Authorization

Authorize one independent Codex review of:

`docs/milestones/M3-T2-implementation-authorization-packet.md`

Baseline branch: `milestone-3-t2-authorization`

Expected HEAD: `0e37db6`

Review the complete packet, its cited decision records, and the I-31 research evidence.

This is a review authorization only.

Do not implement T2, modify scientific decisions, or approve D-0 through D-8.

## 2. Preconditions

Before review:

1. Verify branch, HEAD, remote synchronization, and clean worktree.
2. Confirm `0a9c040` is the merged reconciliation baseline.
3. Confirm CI is green at `0e37db6`.
4. Verify research-evidence checksums.
5. Confirm no protected implementation paths changed.

STOP if any precondition fails.

## 3. Independent Reviewer Requirements

The reviewer must independently evaluate the following.

### A. Scientific validity of POG

Determine whether premise-observed gating genuinely establishes the assumptions required by T0 E1 for the finite tested domain.

Specifically examine:

- Whether tracing captures every relevant elementary-function call.
- Whether instrumentation changes the numerical behavior being measured.
- Whether the premise oracle can have a rigorous, independently justified error bound.
- Whether the true-height reference can have a rigorous error bound.
- Whether oracle uncertainty is handled conservatively.
- Whether the proposed finite-domain interpretation of J-FP2(ii) is justified by the controlling decision record.
- Whether CI platform differences can invalidate the argument.
- Whether a passing test can be reproduced independently.

The reviewer must distinguish feasibility evidence from mathematical proof.

No A-FP-2-dependent accuracy row may become an acceptance gate until the required derivations and independent validation are complete.

### B. Error-budget integrity

Review the use of:

`ε_h = αh + β`

with:

- `α = 1.22e-15`
- `β = 8.9e-9 m`

Verify the interpretation, dimensional consistency, domain restrictions, and propagation of oracle uncertainty.

Check whether the reported worst-case error of approximately `1.9e-9 m` is compared against the correct bound at each evaluated point.

Do not accept an empirical maximum as a universal error bound.

### C. Numerical and algorithmic invariants

Review:

- CPython `hypot` evenness and proposed unconditional U-19 (a′).
- Conditional argument-swap and quarter-turn symmetry.
- `exp` monotonicity premises.
- P8 (a′) oracle-based gating.
- Bitwise conformance with DQ-1/DQ-2 sequences.
- The possibility that sequence conformance passes while numerical correctness fails, or vice versa.

Identify tests that could pass despite a scientifically meaningful implementation defect.

### D. Cross-platform reproducibility

Review RQ-1 through RQ-8 and D-5.

Evaluate whether recording and checking the exact CPython patch version is sufficient for each source-dependent claim.

Consider operating-system math libraries, compiler behavior, architecture, and other dependencies that could affect numerical reproducibility.

Do not propose an unapproved CI or runtime migration as an implicit prerequisite.

### E. Scope and traceability

Verify that the packet:

- Preserves DR-0024 through DR-0029.
- Implements only authorized T2 scope.
- Keeps T3, T4, and T5 excluded.
- Preserves unresolved P6 and P6(b).
- Does not authorize X-1.
- Keeps unjustified assumptions report-only.
- Separates implementation completion from scientific acceptance.

Review all seven deliverables DL-1 through DL-7 and all proposed acceptance and stop gates.

### F. Decision review

Evaluate D-0 through D-8 individually.

For each decision, provide:

1. Recommendation: APPROVE, REVISE, DEFER, or REJECT.
2. Scientific or architectural justification.
3. Required evidence.
4. Dependencies.
5. Consequences of approval.
6. Any remaining blocker.

Pay particular attention to D-1, D-3, D-4, D-7, and D-8.

### G. Rust research boundary

Verify that the Rust discussion remains exploratory and respects RES-0001, ADR-0008, TL-6, and TL-9.

No language migration or implementation is authorized.

## 4. Review Method

Use an independent Codex reviewer with a fresh review context.

Require the reviewer to inspect the actual repository documents and supporting evidence rather than relying exclusively on the packet's conclusions.

Where feasible, independently reproduce numerical calculations or construct adversarial counterexamples.

Classify findings as:

- BLOCKER
- MAJOR
- MINOR
- NOTE

Each finding must include a precise location, explanation, supporting evidence, and recommended disposition.

Do not silently correct findings during the review.

## 5. Review Verdict

Return exactly one overall verdict:

- **PASS** — No blocking findings; packet is suitable for owner decision review.
- **REQUEST_CHANGES** — Corrections or additional evidence are required.
- **BLOCKED** — A prerequisite or scientific dependency prevents a meaningful review.

A PASS does not authorize implementation or automatically approve D-0 through D-8.

## 6. Records and Validation

Preserve:

- The independent review prompt.
- Raw reviewer output.
- Any reproduction scripts and outputs.
- Evidence checksums.
- A structured findings register.
- The final verdict.

Keep raw evidence unchanged.

Commit and push only authorized review documentation and evidence. Do not edit packet r2 or its decision records during this review.

Verify the final branch state and applicable CI results.

## 7. Stop Condition

After the independent review:

STOP and report:

1. Review verdict.
2. Findings by severity.
3. Independently reproduced numerical results.
4. Assessment of POG scientific validity.
5. Assessment of D-0 through D-8.
6. Required corrections or additional research.
7. Final branch SHA and CI state.

Do not start a correction pass without further authorization.

**T2 implementation remains NOT AUTHORIZED.**
