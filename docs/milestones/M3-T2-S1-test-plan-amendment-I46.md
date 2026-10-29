# M3 T2 S1: test and mutation plan amendment A-1 (I-46 D2, Review 03 N-01); plan only, NOT implemented

> **Record status (I-46, 2026-10-29): approved plan amendment, owner decision I-46 D2.**
>
> - This record changes the S1 **test and mutation plan only**. The two tests and mutant M-22 below
>   are **not implemented**. No test, mutant or production file has been written.
> - The design baseline is unchanged: proposal v3-S, `M3-T2-S1-proposal-v3.md`, pinned by I-46 D1 to
>   sha256 `dd705dd464cfeedac8c7c7918114ce7b893a8c17acb0dc4370f209d52cb9102d`. That file is **not
>   edited**, so its pin holds. Where this record and proposal §5 differ (counts), this record governs,
>   by D2.
> - Review 01 and Review 02 remain `REQUEST_CHANGES`; Review 03 remains a proposal-level `PASS`.
> - Decision record: `M3-T2-S1-decision-I45.md` §4 (I-46).
> - **S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED. Commit A is NOT AUTHORIZED.**

## 1. What this amends

| Plan element | Source | Amendment |
|---|---|---|
| T-04 (U-3, INV-3) | I-40 `M3-T2-S1-authorization.md` §9a; proposal v3-S §5 "T-04 snapshot" | Adds T-04 (d) and T-04 (e) (§2). Existing T-04 (a)/(b)/(c) and every other T-04 node are kept unchanged. |
| Mutation campaign | I-40 §10; proposal v3-S §5 "Mutation" | Adds M-22 (§3). M-01…M-21b, including M-19's equivalence argument (proposal §5.1), are kept unchanged. |
| Counts | proposal v3-S §5 ("S1 total: 86 tests") | Updated in §4. |

Everything else is preserved unchanged: T-01…T-03, T-05…T-11 and their red-first rules, R-1…R-6, the
§6 allowlist, INV-1…INV-8, the §12 commit sequence and the §13 stop conditions.

## 2. New regression tests (`tests/test_s1_force_context.py`)

Both tests mirror the coast ownership tests T-04 (a) and (b) on the **powered** path. They use the
existing helpers and setup unchanged: `_record_contexts`, `_ZeroForce`, `_spacecraft()`, the
integrators `_WriteAfter`, `_SharedBufferRK4` and `_RowViewRK4`, and `dt = 0.5`.

The only setup difference is the burn. Before the first `step()`, the simulator schedules the burn
`schedule_burn("prograde", 0.0, 30.0)`, the same "full" burn used by T-04/T-05. The whole first tick is
then powered, and every derivative call goes to the powered closure.

**Expected mass.** Propellant flows during a burn, so the stage masses within a step differ. The
constant `DRY + PROP` that the coast test uses therefore cannot serve as the expected value. Instead,
the expected mass of each call is recorded **at the call**, before the derivative runs, as
`_stage_mass(stage)` from the plain float64 stage that the integrator passes. This is the same quantity
INV-3 defines. A thin wrapper around the integrator's `f` does the recording; the integrators
themselves are unchanged.

**T-04 (d): `test_t04_powered_context_is_an_owned_snapshot_of_the_stage_mass`,
parametrized over `[_WriteAfter, _SharedBufferRK4, _RowViewRK4]` (3 nodes).**

After `step()` returns, every integrator has overwritten its stage storage:
- `_WriteAfter` writes 123.0 to the stage's propellant element after the call;
- `_SharedBufferRK4` writes −7.0 to its shared buffer's propellant element;
- `_RowViewRK4` writes −7.0 to its workspace's propellant column.

The test then asserts:
1. the number of recorded contexts equals the number of recorded calls, which equals
   `integrator.order` (one powered integrator step in the tick);
2. for each context, two reads of `total_mass_kg` are both built-in `float` (`type(...) is float`) and
   `first.hex() == second.hex() == expected.hex()`, where `expected` is that call's recorded mass.

**T-04 (e): `test_t04_powered_context_does_not_keep_the_stage_alive` (1 node).**

The test mirrors T-04 (b). An Euler integrator keeps only a `weakref` to its stage copy, and the burn is
the same as in T-04 (d). After `step()` and `gc.collect()`, it asserts:
- exactly one context and one stage were recorded;
- the stage has been collected (`stage() is None`);
- the context's mass equals the mass recorded at the call.

**Deliberately not mirrored: T-04 (c), the stored-propellant test for subclass stages.**
- The powered mass is computed by BASE's own `mass = spacecraft.dry_mass_kg + max(float(y[_PROP]), 0.0)`.
  That read is not changed by v3-S: proposal §1 keeps v2's powered closure, which preserves R-01.
- That read goes through the subclass's indexing.
- A powered stored-value test would require changing the legacy read. That would contradict D4
  ("Preserve the legacy model's existing behavior outside the new context boundary") and widen the
  design.
- D2 authorizes only the snapshot and lifetime pair.

**Red and green.**
- **Red at commit B, at BASE code.** Like the existing T-04 nodes, each new node fails on its own with
  an `AttributeError`. The failure comes from `forces.LegacyForceAdapter`, which `_record_contexts`
  reads and which is absent at BASE. Collection errors are not valid red evidence (I-40 §9a).
- **Green at commit C.** This is expected from reading the design. The powered closure builds
  `ForceContext(mass)` eagerly, and the constructor converts `mass` to an owned built-in float through
  `_owned_float`, so nothing references the stage after the call.
- **Prior evidence for this expectation:**
  - Review 03's recording adapter found powered contexts owned on v3-S
    (`raw/M3-T2-S1-proposal-codex-review03-evidence/check-ownership.txt`);
  - the existing T-04/T-05 bit-for-bit node already checks powered stage masses at the call.

  Neither of these is a run of the planned tests, which do not exist yet.

**What the new nodes do not distinguish.** v2, v3-L and v3-S share v2's powered closure, so all three
are expected to pass T-04 (d)/(e). The nodes target defects in the powered path itself (M-22), not the
choice between those designs. The existing T-07 (l) and T-04 (a)/(b)/(c) discrimination is unchanged.

## 3. New mutant M-22

**Name:** "M-22 powered lazy stage reference (v3-L machinery, powered path only)".

**Edits** (applied in a scratch copy, as in the existing campaign script):
1. the same `forces.py` edits as M-21 and M-21b (`LAZY_FORCES`, which adds `ForceContext.lazy`);
2. in the powered closure, the context argument `ForceContext(mass)` is replaced by
   `ForceContext.lazy(lambda: spacecraft.dry_mass_kg + max(float(y[_PROP]), 0.0))`.

The coast closure stays as in v3-S. This is the mutant Review 03 built for N-01
(`raw/M3-T2-S1-proposal-codex-review03-evidence/powered_mutant.py.txt`).

**Designated nodes:** the 3 T-04 (d) nodes and the T-04 (e) node.

**Kill criterion:** the I-40 §10 criterion, unchanged. Every designated node must fail, and each
failure must be an assertion failure (the campaign's `ASSERT` reason pattern). A kill by any other
exception does not count. The unmutated control must pass all 90 S1 nodes.

**Expected mechanism** (from reading the design, and from Review 03's evidence for the shared-buffer
case):

| Node | M-22 reads at assertion time | Result |
|---|---|---|
| T-04 (d) write-after | `DRY + 123.0` instead of the recorded stage mass | assertion failure |
| T-04 (d) shared-buffer | `DRY + max(−7.0, 0.0) = DRY` | assertion failure |
| T-04 (d) row-view | `DRY` | assertion failure |
| T-04 (e) | the lambda keeps `y` alive, so `stage()` is not `None` | assertion failure |

- Review 03 observed the shared-buffer case: before `0x1.4440000000000p+10`, after
  `0x1.18c0000000000p+10`, with 4 stages kept alive (`check-powered-lazy.txt`).
- The same mutant passed all 86 current S1 nodes (`powered-lazy-tests.txt`). That is the N-01 gap.

**If M-22 survives or is killed for another reason, that is STOP condition 7** (I-40 §13). M-22 is a
real defect, not an equivalent mutant, so no equivalence argument is available. The plan would then
return to the owner. It may not be weakened or fixed around.

## 4. Updated counts (plan; every figure is a requirement or prediction until implemented)

| Quantity | I-45 plan (proposal v3-S §5, prototype evidence) | Amended plan A-1 |
|---|---|---|
| S1 test nodes | 86 | **90** (+3 T-04 (d), +1 T-04 (e)) |
| T-07 nodes (commit A, green at BASE) | 29 | 29 (unchanged) |
| T-01…T-06 nodes red at BASE (commit B) | 57 | **61** |
| Full suite on the implementation | 1 376 (prototype, same host) | **1 380** expected |
| BASE plus the proposed tests | 1 319 passed, 57 failed | **1 319 passed, 61 failed** expected |
| Mutants | 24 (M-01…M-21b) | **25** |
| Killed for the declared reason | 23 | **24** |
| Documented equivalent survivors | 1 (M-19) | 1 (M-19, unchanged) |
| Mutation control | 86/86 | **90/90** |
| Writer-corpus mutant runs | M-14 (46 differ), M-19 (0) | unchanged; M-22 is not added to the corpus runs |

Other counts are unchanged: T-08, T-10 (51 checks) and T-11 (4 allowlisted production/test paths,
plus the allowlisted evidence and report locations).

## 5. Consistency checks (I-46 authorized work item 4)

| Check | Result |
|---|---|
| Allowlist (I-40 §6) | Both tests go in `tests/test_s1_force_context.py`, an allowlisted new file. M-22's script and results go in `docs/science/experiments/m3-t2/s1/`, an allowlisted evidence directory. No new path. |
| Production scope | No production edit. M-22 exists only in scratch copies. INV-3, INV-4 and INV-8 are untouched. |
| Commit sequence (I-40 §12) | **Commit A is unchanged (T-07 only).** The new nodes belong to commit B (red) and turn green at C. M-22's result is evidence in D. So "before or with commit A" (I-45 report) is met as **planned before A**, not as a change to A's content. |
| Red-first (I-40 §9a) | The new nodes are T-04 nodes, so red-first applies to them per node, with the declared reason `AttributeError` from the absent interface. |
| Mutation rules (I-40 §10) | Assertion-failure kill, recorded JUnit, unmutated control. Unchanged. |
| Final proposal v3-S | The design is not contradicted: the tests observe the powered closure as proposed. Only the §5 counts are superseded (§4). Proposal §7's open points are resolved by I-46 in the decision record, not by editing the pinned file. |
| D4 (legacy behaviour) | The powered stored-value test is not mirrored (§2). The legacy `y[_PROP]` read is kept. |
| D6 (no runtime validation) | The tests and the mutant observe only. No check is added to production. |
| D5 (D-1 docstring) | `src/tars/sim/integrators.py` is a protected path under I-40 §6 ("every other `src/` file"), and commit A is tests-only. The correction is **not permitted** in commit A, so under D5 it is **deferred** to a separately authorized change. |
| D7 (platform) | The predictions in §4 rest on single-host evidence (macOS x86_64, CPython 3.12.15, NumPy 2.5.3). The established CI matrix (R-6, 4/4) is required on every implementation push tip. |
| Earlier verdicts | Not reinterpreted. N-01 was a Review 03 NOTE. This amendment answers it by owner decision; it does not alter Review 03's verdict. |

## 6. Verification still owed at implementation (not claimed here)

The following are verified only when the S1 sequence runs, under I-40 §12 with this amendment:

1. T-04 (d)/(e) fail per node with `AttributeError` at commit B.
2. T-04 (d)/(e) pass at C; their call counts equal the integrator order.
3. M-22 is killed on all 4 designated nodes by assertion failure, and the control passes 90/90.
4. The full suite passes with 1 380 tests at the tip.
5. CI is 4/4 `success` on every push tip.

Any deviation is reported as a STOP under I-40 §13, not corrected around.
