# M3 T2 Slice S1 — Owner Decisions and PC-7(S1) Implementation Authorization (I-40)

- **Status:** **PC-7(S1): GRANTED. PC-7(T2 overall): NONE.** Owner/Tech Lead decision, 2026-10-27 (I-40).
- **Authorizes:** only the S1 scope of §3 below (ForceContext, context-aware protocol, legacy adapter, the authorized simulator closure integration), as modified by the OD decisions in §1.
- **Does not authorize:** S2–S6; the S1 independent review; S1 acceptance; any merge; anything listed in §1 "3. PC-7(S1)" as not authorized.
- **BASE:** `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd` (`main` at the time of this record). This record is committed to `milestone-3-t2-authorization`, not to `main`, so `main` remains at BASE.
- **Contents:**
  - §1: the I-40 owner text, verbatim;
  - §2: the I-39A §5 owner-decision definitions that I-40 decides or defers, verbatim;
  - §3: the approved I-39A §4 proposal text, verbatim.

  §2 and §3 are reproduced from the I-39A response with blockquote markers removed. No word is changed. Where §3 refers to "OD-n", the answer is in §1.

---

## 1. I-40 owner text (verbatim)

# I-40 — M3 T2 Slice S1 Owner Decisions and PC-7(S1) Implementation Authorization

I have reviewed I-39A and the revised, complete PC-7(S1) proposal.

Record the following owner decisions exactly.

## 1. Owner decisions

### OD-1 — Revised S1 scope

**APPROVED.**

Approve the revised S1 scope.

S1 is limited to the ForceContext, context-aware protocol, legacy adapter, and the specifically authorized simulator closure integration described in the revised proposal.

The context-aware composite, canonical reordering, model identifiers, DL-5, and all other excluded work remain outside S1.

No policy for later composition behavior is implied by this approval.

### OD-2 — `dt = +inf` coast incompatibility

**APPROVED — Option A.**

ForceContext validates `total_mass_kg` at construction according to the literal U-1 / packet-r2 §3 contract.

I explicitly authorize only the characterized failure-path delta described in §8 for T-07(a) and T-07(b) on the direct `Simulator` API when `dt = +inf`.

Before the implementation commit, record the exact expected replacement exception type, message, and precedence for those two cases in the S1 design/evidence record.

That authorization does **not** extend to any other behavioral difference.

Validated scenarios must continue to reject non-finite `dt_s`.

Any T-07 difference other than the specifically recorded T-07(a)/(b) delta is a mandatory STOP.

Do not modify `Simulator.__init__` to reject non-finite `dt` as part of S1. That is outside this authorization and may be considered separately later.

### OD-3 — R-6 interpretation

**CONFIRMED.**

For S1, R-6 means:

> CI's four jobs must be green on every **push tip**.

A red-first ancestor commit may exist provided that:

- it is never itself a push tip;
- its red-first result is demonstrated locally per test node and preserved in the authorized evidence;
- the subsequent implementation/evidence commits make the pushed tip green;
- the report explicitly identifies the red-first ancestor;
- no new push occurs while the preceding push tip's CI is pending or failed.

This decision is specific to resolving the red-first/CI sequencing issue identified in I-39A. It does not generally relax CI requirements outside this authorization.

### OD-4 — Massless ForceContext

**CONFIRMED.**

A massless ForceContext carries `total_mass_kg` as **absent**.

Absent mass is semantically distinct from `0.0` and from an invalid supplied mass.

It must never be silently coerced to zero.

### OD-5 — `simulator.py` modification boundary

**CONFIRMED.**

For S1, permitted changes to `src/tars/sim/simulator.py` are limited exactly to:

- necessary import statements;
- `Simulator._derivative`;
- `Simulator._powered_derivative`;
- the closures returned/defined within those specifically authorized regions.

All other module-level statements, class members, methods, functions, and behavior remain protected as specified by the revised proposal and its AST-identity checks.

### OD-6 — S1 run record / DL-5

**CONFIRMED.**

RQ-4 is satisfied for S1 by the §9 S1 run record.

DL-5 is deferred and is **not** an S1 deliverable.

Do not adopt the I-33 draft's 6,235-argument libm set as an approved requirement through this decision.

No CI modification or DL-5 promotion is authorized.

## 2. Decisions deliberately deferred

Do **not** decide OD-7 through OD-12 as part of this authorization.

In particular:

- OD-7 must be resolved before authorization of the S1 independent review.
- OD-8 must be resolved before S4.
- OD-9 must be resolved before S2.
- OD-10 must be resolved before S5.
- OD-11 must be resolved before U-19(a′).
- OD-12 must be resolved before S2.

Do not infer any answer to those decisions from this authorization.

## 3. PC-7(S1)

Subject to the decisions above:

**PC-7(S1): GRANTED.**

**PC-7(T2 overall): NONE.**

Implementation of exactly the revised I-39A §4 proposal's S1 scope is authorized.

This authorization includes the preconditions, scope, path allowlist, invariants, tests, mutation campaign, regression gates, commit/push sequence, evidence production, and stop conditions specified by that proposal, as modified only by the explicit OD decisions above.

Nothing outside that scope is authorized.

In particular, this does **not** authorize:

- S2–S6;
- the context-aware composite or canonical ordering;
- model identifiers;
- DL-5 or any other DL promotion;
- CI modifications;
- dependency changes;
- `.python-version` changes;
- scenario or proof changes;
- numerical-threshold changes;
- production numerical-sequence changes except for the explicitly authorized OD-2 failure-path delta;
- DR-0028 P6(b);
- X-1;
- geodetic GMAT acceptance;
- T3–T5;
- the S1 independent review;
- S1 acceptance;
- any merge.

All previously stated boundaries not explicitly lifted here remain in force.

## 4. Execution instructions

First, record these owner decisions and the resulting PC-7(S1) authorization in the appropriate immutable project record.

Then perform the revised proposal's §4 preconditions exactly.

Do not reuse the planning workspace branch for implementation.

Immediately before creating the S1 implementation branch/worktree, re-establish the complete baseline required by §4 in the same execution session.

If every precondition passes, create the dedicated:

`milestone-3-t2-s1-force-context`

branch/worktree from the explicitly verified BASE and execute S1 according to the authorized sequence.

Follow the proposal's red-first, commit, push, CI, evidence, mutation, regression, and protected-path requirements exactly.

Do not broaden scope to resolve a problem.

If any stop condition is reached, stop and report it rather than fixing around it or requesting/performing additional work implicitly.

## 5. Required stopping point

When S1 is implemented, all authorized validation and mutation work is complete, the final authorized S1 implementation/report tip is pushed, and CI is green:

**STOP.**

Do not start the independent S1 review.

Do not accept S1.

Do not merge S1.

Report:

1. branch and full HEAD SHA;
2. BASE SHA and verified ancestry;
3. commits created and their purpose;
4. exact changed paths;
5. OD-2's recorded T-07(a)/(b) replacement expectations and observed results;
6. red-first evidence for T-01 through T-06;
7. T-07 through T-11 results;
8. mutation results, including any survivors and reasoning;
9. R-1 through R-6 results;
10. CI run IDs and per-platform status;
11. evidence/manifests produced and verification status;
12. confirmation that protected paths remained unchanged;
13. any deviations, unexpected behavior, or unresolved questions;
14. explicit status:

`S1 IMPLEMENTED / NOT REVIEWED / NOT ACCEPTED / NOT MERGED`

At that point, wait for separate authorization for the independent review.

---

## 2. I-39A §5 owner-decision definitions (verbatim)

**Required before PC-7(S1) can be executed:**

| ID | Decision | Options | Recommendation |
|---|---|---|---|
| **OD-1** | Approve the revised S1 scope: composite, model identifiers and DL-5 removed | Approve / amend | Approve |
| **OD-2** | The `dt = +inf` coast incompatibility (C2) | **A:** context validation at construction (the literal U-1 and r2 §3 reading). Accepts a pinned, documented delta for T-07 (a)/(b) on the direct-API path only; scenarios reject the input. **B:** mass validated when a consumer reads it; zero behaviour change; U-1 reads "rejected on use" | **A.** It keeps the approved interface text literal, and the delta is confined to an input every scenario rejects and that is already a numerical-failure path. Separately, consider a later Decision Request to reject non-finite `dt` in `Simulator.__init__` (outside T2) |
| **OD-3** | R-6 means "every push **tip**", with red-first ancestors named in the report (C3; T1 precedent) | Confirm / keep the literal reading (then red commits are never pushed, and red evidence comes only from local logs) | Confirm |
| **OD-4** | A massless context carries mass **absent** (DR-0026 body line 81), distinct from rejected invalid mass | Confirm / amend | Confirm |
| **OD-5** | The `simulator.py` permission = imports + `_derivative` + `_powered_derivative` and its closures only | Confirm / amend | Confirm |
| **OD-6** | RQ-4 satisfied for S1 by the §9 S1 run record (DL-5 deferred to a later slice) | Confirm / require DL-5 in S1, with the I-33 6 235-argument set adopted with provenance and reviewed | Confirm |

**Required before the S1 review:**

| ID | Decision |
|---|---|
| **OD-7** | I-30 §4: confirm the transcript text verbatim, or supply the authoritative text, and authorize a docs commit that records it immutably. Alternatively, amend r2 §10's quote list. Until then the S1 review prompt is BLOCKED |

**Required before later slices:**

| ID | Decision | Needed before |
|---|---|---|
| **OD-8** | Composition policy (C5). (a) Composite **sorts** ranked kinds {point mass, J2, drag}, **rejects** unranked models and duplicate ranks with a typed error, and leaves legacy models on `CompositeForceModel`. (b) Composite **validates** that its input is already in canonical order and rejects otherwise; sorting stays with the T3 builder per DR-0026 §5.2. In both: a mass-requiring component with absent mass is rejected. Also: whether U-22's "regardless of input order" means "sort" or "order-independent or reject" | S4 |
| **OD-9** | Merge model: each slice merged to `main` after acceptance, or all slices stacked until T2 acceptance | S2 |
| OD-10 | CI evidence persistence for RQ-8/DL-5 (a CI change is needed for artifacts) | S5 |
| OD-11 | DL-7 review of CI CPython 3.12.10 (macOS) and 3.12.3 (Ubuntu), or U-19 (a′) stays report-only | U-19 (a′) |
| OD-12 | OI-27 confirmation (DR-0026 §5.8 "total" versus the P8 domain rejection) | S2 |

---

## 3. Approved proposal text: I-39A §4 (verbatim)

**I-40 (proposed) — M3 T2 Slice S1: ForceContext and Legacy Adapter — Implementation Authorization (PC-7(S1))**

**§0 Status and effect.**
- On the owner's explicit approval, this text grants **PC-7(S1)**: implementation of exactly the scope in §5. **PC-7 for T2 overall remains NONE.**
- Nothing else is authorized, including:
  - S2–S6;
  - any DL deliverable, row promotion or POG gating;
  - CI, dependency, scenario, proof or protected-path changes;
  - the S1 independent review;
  - S1 acceptance or any merge;
  - DR-0028 P6(b), X-1, geodetic GMAT acceptance, and T3–T5.
- This text is effective only together with the owner's recorded answers to OD-2, OD-3, OD-4, OD-5 and OD-6.

**§1 Definitions.**
- **BASE** = `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`, unless the owner names another `main` SHA in the approval.
- **S1 branch** = `milestone-3-t2-s1-force-context`.
- **Push tip** = the head commit of a `git push`.
- **AST-identical** = `ast.dump(..., include_attributes=False)` is equal, docstrings included.
- **Reachable path** = any execution path through the public `Simulator` API or through a validated scenario.

**§2 Governing documents** (immutable at BASE; blob hash prefixes):
- packet r2 `af260a7cf8e1` (`docs/milestones/M3-T2-implementation-authorization-packet.md`);
- r1 `4537bcadfdea`;
- I-23 draft `9243999c30a4` (its §7–§9);
- validation strategy `ac1400f558e5`;
- DR-0025 `3fd8b2c0db75` (its "I-26 note": the owner floating-point policy);
- DR-0026 `2c016ae05e58`;
- ADR-0009 `a803e05c34ee`;
- `proof/review.md` `367c1a9566bb`;
- `playbook/git.md` `10904f573b56`.

Where this text is stricter, this text governs for S1.

**§3 Decisions, verbatim.**

*3.1 Packet §17, I-37 §2:*
> - D-0: APPROVED.
> - D-1: APPROVED, conditional POG route only.
> - D-2: APPROVED, DL-1 through DL-7 required and independently reviewed before gating.
> - D-3: APPROVED, restricted to reviewed CPython builds.
> - D-4: APPROVED, with the documented limits of local premises.
> - D-5: APPROVED, option (b).
> - D-6 (ii): APPROVED.
> - D-6 (iii): APPROVED.
> - D-7: APPROVED, conditional on validated DL-2 enclosures.
> - D-8: APPROVED, as an output-conformance gate, not an accuracy gate.
>
> D-6 item (i) remains withdrawn.

*3.2 Packet §17.2, I-37 §3:*
> 1. No A-FP-2 or A-LM row is automatically promoted.
> 2. POG accuracy gating remains BLOCKED.
> 3. DL-1 through DL-4 remain unreviewed drafts.
> 4. Per-platform testing remains outstanding.
> 5. Numerical thresholds and production numerical sequences remain unchanged.
> 6. D-6 (iii) requires source inspection; DL-4 alone cannot enforce the implementation requirement.
> 7. No CI modifications are authorized.
> 8. No production implementation is authorized.

Boundary 8 is lifted **only** for §5. Boundaries 1–7 stand unchanged.

*3.3 r1 §5 DQ-3:*
> **DECIDED: (a).**
>
> T2 may add the context-aware force protocol and integrate immutable ForceContext construction into the simulator's derivative closures.
>
> Current stage mass must be used.
>
> Preserve the legacy force-model interface through an adapter.
>
> Existing M1/M2 behavior must remain byte-identical on the specified same-platform regression gates.
>
> No change to tick logic, engine scheduling, step splitting or atomicity is approved by this decision.
>
> Implementation still requires separate authorization.

*3.4 r1 §5 DQ-5:*
> **DECIDED: (a).**
>
> Wrap the accepted T1 J2 implementation through the legacy adapter.
>
> Do not rewrite the J2 force class, change its constants or create a replacement J2 model.
>
> Preserve all T1 evidence and validation gates.

*3.5 Applicability.*
- S1 implements DQ-3 (a) and DQ-5 (a) only.
- D-0…D-8 have no S1 implementation content. They remain binding as constraints, and S1 may not act contrary to them.

**§4 Preconditions** (all performed in one session immediately before branch creation, with outputs recorded in the §S1 section of `docs/milestones/M3-T2-report.md`):
- **P-1.** `git fetch`. Then `main`, `origin/main` and `git ls-remote origin refs/heads/main` all equal BASE. Otherwise STOP.
- **P-2.** No local or remote branch matches `*t2-s*`, `*t2-impl*` or the S1 name. The workspace planning branch `tars-i39-t2-pc7-proposal-0225a8f3` is non-material (it equals BASE with no commits) and **must not** be used or committed to.
- **P-3.** A new dedicated worktree is created with `git worktree add -b milestone-3-t2-s1-force-context <path> <BASE>`. Its `git status --porcelain --ignored` is empty before `uv sync`.
- **P-4.** The CI push run on `main` at BASE has all 4 jobs `success` (for `ee602c5`: run `40593193646`).
- **P-5.** All 43 committed `SHA256SUMS` manifests verify. `git diff --stat a57de3f BASE -- docs/science/experiments/m3-t0/` is empty.
- **P-6.** Baseline gates at BASE pass (§11, R-1…R-4). Any failure → STOP.
- **P-7.** The S1 run record (§9) is captured for the local host.

**§5 Scope (complete).**
- **F1 — `ForceContext`** in `src/tars/sim/forces.py`:
  - immutable;
  - `total_mass_kg` is either an owned built-in `float` that is finite and > 0, or **absent** (OD-4; a distinct representation, never 0);
  - invalid mass raises at the point specified by the OD-2 option the owner approved;
  - construction never raises `OverflowError` or `ZeroDivisionError`.
- **F2 — Context-aware protocol** `acceleration(t, r, v, ctx)`, and a **legacy adapter** that:
  - calls the wrapped `acceleration(t, r, v)` exactly once with the identical objects;
  - returns the identical result object;
  - lets any exception propagate as the identical object;
  - does not mutate the wrapped model.

  Protocol selection must not probe signatures by catching `TypeError`.
- **F3 — Closure integration:**
  - `_derivative` passes mass absent;
  - the coast closure computes `spacecraft.dry_mass_kg + max(float(y[_PROP]), 0.0)`;
  - the powered closure builds the context **after** its existing finiteness check, from its existing `mass` variable;
  - the force call keeps its position after `thrust_acceleration`;
  - every arithmetic expression that contributes to the returned derivative is unchanged.
- **F4 — J2 and point mass** (and every legacy model) run through the adapter unchanged.

**Excluded:**
- the context-aware composite and canonical reordering (OD-8, before S4);
- model identifiers;
- DL-5;
- constants;
- geodetic, density, dataset and drag work;
- X-P4.

**§6 Paths** (exact allowlist; any other changed path is a STOP):
- `src/tars/sim/forces.py`: additive. `ForceModel`, `PointMassGravity`, `CompositeForceModel`, `ZonalJ2Gravity`, `_owned_float` and `_underflows` stay AST-identical to BASE.
- `src/tars/sim/simulator.py`: only import statements, `Simulator._derivative`, and `Simulator._powered_derivative` with the closures it returns (OD-5). Every other module-level statement, class member and function is AST-identical to BASE.
- New files `tests/test_s1_force_context.py` and `tests/test_s1_failure_paths.py`. Existing tests, `tests/conftest.py` and `tests/__init__.py` stay unchanged.
- New directory `docs/science/experiments/m3-t2/s1/` (scripts, outputs, `SHA256SUMS`).
- New file `docs/milestones/M3-T2-report.md`.

`.python-version`, `pyproject.toml`, `uv.lock`, `.github/`, `proof/`, `toolbox/`, `scenarios/`, `docs/` outside the two new locations, and every other `src/` file are protected.

**§7 Invariants:**
- **INV-1:** F2 holds.
- **INV-2:** same-platform byte identity of committed states, events and run outputs on all M1/M2 paths (R-1, R-2, T-08).
- **INV-3:** per RK4 stage, the context mass equals `dry + max(prop, 0.0)` of that stage bit for bit; for `prop = −1e-17` it is exactly the dry mass.
- **INV-4:** no floating-point operation is added to, removed from or reordered within any expression contributing to a returned derivative.
- **INV-5:** F1 holds.
- **INV-6:** failure-path compatibility per §8.
- **INV-7:** purity: the architecture scan passes; repeated evaluation is bitwise identical; `vars(simulator)` keys are unchanged.
- **INV-8:** tick logic, step splitting, engine scheduling and atomicity are unchanged (AST rule in §6).

**§8 Failure-path compatibility.**
- Characterization tests **T-07** are written first and must pass at BASE code on all three CI platforms (§12, step 1). They pin the current exception **type, message and precedence** for:
  - (a) `dt = +inf`, spacecraft coasting, PM only → `FloatingPointError("non-finite state produced at tick 1")`;
  - (b) the same with PM+J2 → `ValueError("position must be finite")`;
  - (c) the M1 path with `dt = +inf` → `FloatingPointError`;
  - (d) a non-finite powered stage → `FloatingPointError("non-finite state during a burn at t = …")`;
  - (e) `F/m` overflow → `FloatingPointError("thrust acceleration overflows …")`;
  - (f) a force double raising `OverflowError`/`ZeroDivisionError` → `step()`'s converted message;
  - (g) `law.direction` and the force model both raising → the `law.direction` error surfaces;
  - (h) a scenario with `dt_s = inf` is rejected at validation.
- After implementation every T-07 assertion must hold unchanged. The **only** exception is the delta pre-authorized by OD-2 option A, for (a) and (b): if option A is approved, the new type and message are specified in the S1 design record **before** the implementation commit, and pinned by replacement assertions.
- Any other difference, on any platform, is a **STOP**. No check may be reordered and no exception may be translated to restore equivalence.

**§9 S1 run record (not DL-5).** For every gate-evidence run, record:
- the commit SHA;
- `sys.version`, `platform.platform()`, `platform.machine()`;
- the `uv.lock` sha256;
- for CI: run ID, job names and the CPython lines copied from the logs.

It identifies runs only. It makes no reproducibility claim, and fields that are not observed are written "not recorded".

**§9a Tests** (every requirement and failure mode named):
- **T-01 (U-1, INV-5).** (a) Assignment and deletion raise. (b) `int`, `np.float64` and 0-d array mass give a built-in `float` (`type(...) is float`); `bool`/`str` raise `TypeError`. (c) NaN, ±inf, 0.0, −0.0 and negatives are rejected. (d) Absent is distinct from 0 and never coerced. (e) No input makes construction raise `OverflowError`/`ZeroDivisionError` (including `int` 10**400).
- **T-02 (U-2, INV-1).** A recording double checks `is`-identity of t, r and v, a single call, `is`-identity of the returned object, propagation of five exception types as the identical object, and no attribute change on the wrapped model. Payloads include −0.0, subnormals and NaN components.
- **T-03 (DQ-5).** `ZonalJ2Gravity` and `PointMassGravity` through the adapter return bit-identical results to direct calls on a seeded state set (stdlib `random`, seed recorded); the T1 tests are unchanged.
- **T-04 (U-3, INV-3).** Per stage, through a spied closure input and a context-recording double: context mass equals the recomputed stage mass bitwise. With `prop = −1e-17` it is exactly the dry mass.
- **T-05 (I-7 (a)).** All 4 stages of powered, coast and split-tick sub-steps (ignition and cutoff inside a tick) carry stage-derived, not committed, mass.
- **T-06 (OD-4).** On the massless path, the context mass is absent at every evaluation.
- **T-07 (INV-6).** As in §8.
- **T-08 (INV-2, INV-4)** (evidence script, recompute only). In fresh clones of BASE and the S1 tip, the same direct-API configurations are run: M1 PM; M2 burn with split ticks; PM+J2 coast and burn. Per-tick hex of r, v and the propellant/Δv state, and all engine events, must be identical.
- **T-09 (INV-7).** Architecture scan; repeated evaluation bitwise identical; `vars(sim)` keys unchanged.
- **T-10 (§6, INV-8).** An AST-identity script against BASE for every protected class and function.
- **T-11 (§6).** `git diff --name-only BASE..tip` ⊆ the allowlist.

Red-first applies to T-01…T-06: each must fail at the red commit, **per test node**, with a failure for its declared reason (assertion failure, or a per-test `AttributeError`/`ImportError` from the absent interface where that is the declared reason). Collection errors are not valid red evidence. T-07…T-11 are regression guards, declared up front and exempt.

**§10 Mutation campaign** (each mutant is applied in a scratch copy and must fail its designated test node with an assertion failure; the unmutated control must pass; JUnit is recorded; a kill by an unrelated exception does not count; survivors are documented with reasoning):

| Mutant | Killed by |
|---|---|
| Adapter copies r | T-02 |
| Adapter swaps r and v | T-02 |
| Adapter copies the result | T-02 |
| Adapter calls twice | T-02 |
| Adapter wraps exceptions | T-02 |
| Context from committed state | T-05 |
| Dry mass only | T-04 |
| No clamp | T-04 |
| Context cached per step | T-05 |
| Mutable context | T-01 |
| Unowned `np.float64` mass | T-01 |
| Validation removed | T-01 |
| Massless path gets 0.0 | T-06 |
| Powered context built before the finiteness check | T-07 (d) |
| Force call moved before `thrust_acceleration` | T-07 (g) |

**§11 Regression gates:**
- **R-1.** Fresh scratch clone A at the code-final tip: `toolbox/scripts/run_m1_proof.sh`, 9/9, golden `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`.
- **R-2.** Separate fresh clone B: `toolbox/scripts/run_m2_proof.sh`, 20/20, `m2_proof` 228/228, with the M2 golden, snapshot, GMAT-manifest and threshold digests equal to BASE.
- **R-3.** T1's 109 tests pass; the J2 hex is as asserted in `tests/test_zonal_j2.py`; the T1 correction-check scripts in `docs/science/experiments/m3-t1/` give byte-identical outputs at BASE and at the tip (recomputed in both).
- **R-4.** The T0 314 checks pass (host only; CI does not collect them).
- **R-5.** T-10 and T-11 pass, and `git diff BASE..tip` over the protected paths is empty.
- **R-6.** CI 4/4 `success` on every push tip (OD-3).

Proof wrappers never run in the S1 worktree (they write to `proof/records/evidence/`). Every comparison is same-platform except the existing CI matrix and its jobs; no new cross-platform claim is made.

**§12 Commit, push and CI sequence:**
1. Commit **A**: T-07 only (green at BASE code). Run local gates, then **push A**. Wait for CI on A: 4/4 `success`, or STOP.
2. Commit **B**: T-01…T-06 (red). Run them locally and save the per-node red output to the scratchpad. **Do not push B by itself.**
3. Commit **C**: the implementation. Run full local gates (ruff check and format, pytest, T-07…T-11).
4. Commit **D**: evidence (red record of B, green record, mutation results, T-08/T-10 outputs, run records, `SHA256SUMS`). **Push B..D together, with tip D.** Wait for CI on D: 4/4 `success`, or STOP.
5. Run R-1…R-4 at D, in scratch clones.
6. Commit **E**: `M3-T2-report.md` §S1, docs only; `git diff D..E` touches no `src/` or `tests/` path. Push and wait for CI: 4/4, or STOP.

At no time is a push made while the previous tip's CI is pending or failed. B is the only red commit, and it is never a tip. A failed tip is a STOP with logs; no fix-forward without the owner's instruction. No force-push, rebase of pushed commits, PR merge or merge.

**§13 Stop conditions** (stop, report, and do not work around):
1. Any precondition in §4 fails, or BASE drift is found at any point.
2. A changed path is outside §6, or a function or class outside the §6 regions changes.
3. Any T-07 difference not pre-authorized by OD-2.
4. Any R-1…R-4 change, or a T-08 or T-10 mismatch.
5. CI is not `success` on any push tip, on any platform.
6. A requirement is missing or contradictory, or the work appears to need the composite, ordering, model identifiers, DL-5, constants, any S2–S6 item, any T3–T5 item, P6, P6(b), X-1, a threshold, or a dependency, CI or `.python-version` change.
7. A mutant survives without a documented equivalence argument.
8. Any record or commit message claims accuracy or promotion, or treats an I-33 draft as a deliverable.
9. Evidence contamination: a manifest fails, evidence is edited after recording, or a stored value is read where a recomputation is required.
10. Any need for an owner decision not recorded in the approval.
11. Completion: S1 is implemented, validated and CI-green → stop for review authorization.

**§14 Completion and review.**
- The S1 independent review needs **separate** authorization. CI success never substitutes for it.
- **Reviewer setup:** separate provider, fresh session, fresh clone at the full SHA of E, `uv sync --locked`, `review_scratch/` excluded, no network, no tracked writes.
- **The prompt quotes verbatim:** this approved text with the OD answers; §3.1–§3.4; the DR-0025 "I-26 note" policy text; I-30 §4 as recorded (OD-7); and the list of preconditions the implementer performed.
- **The reviewer checks:** INV-1…INV-8 mathematically and by reproduction; T-07 per platform via the CI logs; mutants rerun; R-1…R-4 rerun; scope (T-10, T-11); failure reporting; hidden assumptions; evidence provenance; and the absence of any accuracy or promotion claim.
- **Severity:** BLOCKER = Critical, MAJOR = High (`proof/review.md`).
- **PASS:** 0 BLOCKER, 0 MAJOR, and the requested reproductions succeed.
- **REQUEST_CHANGES:** any BLOCKER, MAJOR, or MINOR marked must-fix.
- **Blocking finding:** any byte change on an M1/M2/T1/T0 path, an out-of-allowlist change, a scope breach, an unsupported claim, irreproducible evidence, or an undisclosed T-07 delta.
- The implementer classifies every substantive finding as ACCEPTED, REJECTED_WITH_REASONING or ESCALATED_FOR_INVESTIGATION. **No fix and no further round without authorization.** After PASS: stop. Recording the review is governed by the review authorization.

**§15 Boundaries kept:**
- S1 acceptance needs an explicit owner decision.
- Any merge needs a separate authorization: fast-forward only, ordinary push, pre-merge ancestry check, post-merge fresh-clone validation, and CI on `main` green.
- S2–S6 each need their own PC-7 authorization.
- DL-1…DL-7 stay unreviewed or unbuilt; POG accuracy gating stays BLOCKED; no row is promoted.
- DR-0028 P6(b) stays OPEN, X-1 NOT AUTHORIZED, and geodetic GMAT acceptance stays T5.
- **PC-7 for T2 overall: NONE.**
