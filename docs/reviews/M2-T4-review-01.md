# External Review: M2 Task T4: scenario timeline, runner event emission, duration stop

**Reviewer/model:** OpenAI Codex CLI (separate provider), session `01a12bd4-2093-7dd1-8fc2-373c60d3effd`.  
**Date:** 2026-10-11  
**Reviewed revision:** `1d58e15` (diff `7f373cb..1d58e15`).  
**Scope:** Tech Lead T4 requirements:
- deterministic ordering and reproducible JSONL;
- correlation of commands, burns and events;
- commanded vs executed values;
- events for accepted, rejected, completed and interrupted burns;
- duration stop at boundaries, including burns crossing the stop;
- M1 golden hash, Proof and event behavior preserved;
- no duplicate events on retries or repeated runs;
- no partially committed state on failure;
- no new event types, rejection codes or permissions without a DR.

**Raw:** `raw/M2-T4-codex.md`; prompt and probes in `raw/M2-T4-codex-prompt.md` and `raw/M2-T4-codex-scratch/`.

## Summary
**Verdict: FAIL.**

Confirmed by the reviewer:
- 660 tests pass; ruff is clean;
- determinism is exact (`7a4e1877…`); M1 Proof passes; the slice mission succeeds;
- ordering, repeated-run equality, correlation, precedence, ID retry and commanded-vs-executed values are correct;
- end-tick envelopes and tie and depletion ordering are correct;
- the stop boundaries, orbits stop, unsubmitted entries and non-finite rollback all behave as documented;
- v1 takes the M1 path;
- no new event types, codes or permissions;
- the DR-0017 bound stays distinct from trajectory error;
- DR-0018's behavior stays within the approved vocabulary.

The defects are in final telemetry after a failure, strict Python payloads, CLI pair publication, serialization round-trip and an overflow crash.

## Findings
All five are **`ACCEPTED`**. Each fix is mutation-tested: the new test fails with the fix reverted.

### F1: Final propulsion telemetry can omit an accepted pending burn
**Severity:** High  
**Implementer reasoning:** Correct.
- Samples were emitted before the tick's submissions, and a per-tick dedup suppressed a second sample. A step failing right after a submission therefore left a final `PropulsionSampled` that predated the submission and contradicted `final_propulsion`.
- **Root cause:** an order choice that made samples describe the pre-submission schedule.

**Resolution:**
- Submissions now precede their tick's samples, and are made only if the run continues past that tick. A tick that ends the run (stop, impact, escape, timeout) makes no submissions; such entries are recorded as unsubmitted.
- Every sample therefore shows the schedule after its tick's submissions. The M1 order (sample, then `OrbitCompleted`) is unchanged, and so are the M1 bytes.
- **Tests:**
  - `_check_log_invariants` now asserts, for every M2 test log, that the last `PropulsionSampled` equals `final_propulsion`;
  - new failure-after-submission tests at tick 0 and at a sampled tick (60 s);
  - a new test that a timeout tick makes no submission.
- **Mutation:** moving the submission back after the samples fails the 60 s case.

### F2: Python payload validation permits hash ambiguity and changes command semantics
**Severity:** Medium  
**Implementer reasoning:** Correct.
- The finiteness check recursed only through dicts and lists. Tuples, sets, bytes and subclasses passed.
- The runner's JSON round-trip copy could convert an `int` subclass, which `submit()` rejects, into a plain `int`, which it accepts.

**Resolution:**
- `TimelineEntry.command` must consist of exact standard-JSON types (dict with str keys, list, str, int, finite float, bool, None). It is stored as a private deep copy.
- The runner copies with `copy.deepcopy`, which is exact for these types, so timeline and direct submission behave identically.
- **Tests:** nine non-JSON Python payloads are rejected; private-copy and runner-equivalence tests.
- **Mutation:** accepting tuples fails.

### F3: CLI failure can leave outputs from different runs
**Severity:** Medium  
**Implementer reasoning:** Correct. Per-file atomic renames did not make the pair atomic.

**Resolution:** `summary.json` (which records `events_sha256`) is now a commit marker.
- Both files are staged completely, the old summary is removed, then events and summary are renamed into place.
- Any interruption leaves the previous complete pair, or events without a summary (incomplete), and never a mismatched pair.
- **Tests:** failure at each rename and during staging, checked with a pair-consistency check.
- **Mutation:** not removing the old summary fails.

### F4: Duration scenarios cannot round-trip their serialized configuration
**Severity:** Medium  
**Implementer reasoning:** Correct. The default `max_duration_periods = 1.1` was serialized for duration stops and then rejected on reload, and `with_dt` failed for the same reason.

**Resolution:**
- `max_duration_periods` is `null` for a duration stop and defaults to 1.1 for an orbits stop, filled before validation.
- Implicit, explicit and `null` forms of the default hash identically for an orbits stop.
- **Tests:**
  - canonical-JSON, `model_dump` and `model_dump_json` round trips for duration and orbits stops;
  - `with_dt` on a compatible step (5 s) and an incompatible one (7 s).
- **Mutation:** restoring the 1.1 default fails.

### F5: Finite timing inputs can escape validation as an uncaught overflow
**Severity:** Low  
**Implementer reasoning:** Correct. `round(value / dt_s)` overflowed for finite inputs such as 1e308 / 1e-10. The same latent crash existed in the M1 sampling-grid validator.

**Resolution:**
- Non-representable tick ratios are now validation errors, in v2 (`stop.duration_s`, `submit_t_s`) and in the v1 sampling check. This rejects input that previously crashed; M1 bytes are unchanged.
- The CLI also reports undecodable scenario files as invalid input (exit 2).
- **Tests:** schema tests for each ratio, plus CLI exit-code tests.
- **Mutation:** removing the guard fails.

## Re-verification 1 (`5098f8a`)
**Reviewer:** Codex, session `01a12bdb-ef2f-7872-b42b-c912e934395b`. **Raw:** `raw/M2-T4-codex-reverify.md`; probes in `raw/M2-T4-codex-reverify-scratch/`.

**Verdict: CONDITIONAL PASS.**
- F1–F5 are all **RESOLVED**. The reviewer re-ran each original probe and confirmed that each defect-specific test fails against the old code.
- No regressions:
  - 687 tests pass;
  - M1 hash is exact; M1 Proof passes;
  - slice JSONL is byte-identical across repeats;
  - no new event types, codes, permissions or scope.

### N1: Orbits-stop timeout arithmetic can still overflow
**Severity:** Low. **Disposition:** `ACCEPTED`.

**Implementer reasoning:** Correct, and it predates T4. The M1 runner computed `ceil(max_duration_periods · orbits · T / dt)` unchecked, so finite inputs such as a 1e308 guard factor or dt = 1e-308 crashed with `OverflowError` instead of being rejected as invalid input.

**Resolution:**
- `Scenario.timeout_ticks` computes the limit with the same expression and order as before, so the M1 limit is unchanged (tested). Scenario validation raises a `ValidationError` when the limit is not representable, for v1 and v2.
- The runner uses the validated value.
- **Tests:** guard-product and dt-quotient overflow (v2), the v1 guard, CLI exit 2, and equality with the M1 formula.
- **Mutation:** removing the validation fails 4 tests.

**Reviewer note:**
- Some new tests (the integer-payload runner check, infinity rejection, two orbits-stop serialization cases) pass against the old code as well.
- These are intended as positive coverage. The defect-specific tests catch each original finding.

## Re-verification 2 (`354914d`)
**Reviewer:** Codex, session `01a12be1-14e9-77d3-af10-a893e08b94b0`. **Raw:** `raw/M2-T4-codex-reverify2.md`; probes in `raw/M2-T4-codex-reverify2-scratch/`.

**Verdict: CONDITIONAL PASS.**
- **N1 RESOLVED:**
  - both probes now exit 2;
  - the new tests fail against `5098f8a`;
  - the M1 timeout limit is unchanged (5908 ticks).
- No Critical, High or Medium issue remains across the full T4 diff.

### M1: Extreme duration-scenario altitude still causes runtime overflow
**Severity:** Low. **Disposition:** `ACCEPTED`.

**Implementer reasoning:** Correct, and it predates T4. A finite altitude whose r³ overflows (1e103 m) passed validation. In a duration-stop scenario the first gravity evaluation then raised `OverflowError` inside the unchanged M1 force model. In an orbits stop, the N1 check already rejected it.

**Resolution:**
- Scenario validation now requires the initial orbit's Keplerian period, which involves the same r³, to be representable for every stop kind, in v1 and v2.
- The M1 force model is untouched.
- **Tests:** v1 and v2 for both stop kinds, plus CLI exit 2.
- **Mutation:** removing the check fails the duration-stop cases.

## Re-verification 3 (`b820588`)
**Reviewer:** Codex, session `01a12be4-3347-76f2-844e-ec5aa50f23b0`. **Raw:** `raw/M2-T4-codex-reverify3.md`; probes and the 4,728-case arithmetic sweep in `raw/M2-T4-codex-reverify3-scratch/`.

**Verdict: CONDITIONAL PASS.**
- No Critical, High or Medium issue in T4; 695 tests pass; M1 hash exact; M1 Proof passes; slice repeatable.
- **M1: NOT RESOLVED.** An altitude of 5.64e102 m passed the period check but still overflowed: the Cartesian |r| rounds above the nominal radius.
- At my request the reviewer swept all scenario-derived arithmetic and reported the whole class together, K1–K5, all Low. Most predate T4 (M1 gravity, M1 schema).

**Implementer reasoning:** Patching validation one input at a time does not converge: RK4 stages can reach radii no validation can predict. The systematic rule is that **a numerical failure during a step is the existing recorded `non_finite` mission failure**, atomic and never an uncaught exception. Validation rejects only structurally invalid input.

All are **`ACCEPTED`**:
- **M1 / K1 (gravity r³ overflow, initial state or RK4 stage).** `Simulator.step` converts Python `OverflowError`/`ZeroDivisionError` raised while integrating into `FloatingPointError`, the same failure NumPy reports as inf. The step is atomic. The M1 force model and the arithmetic of successful steps are unchanged.
- **K3 (finite components, overflowing norm).** A committed state must also have finite |r| and |v|, otherwise it is `non_finite`. This is checked in the simulator, so telemetry and events can always be built.
- **K4 (representable rates, unrepresentable F/m).** The powered RHS checks F/m and raises `FloatingPointError`.
- **K2 (orbits = 10³⁰⁹).** The timeout expression's int-to-float overflow is a validation error.
- **K5 (`force_models: []`).** Schema `min_length=1`, in v1 and v2. `model_dump` and the M1 hash are unchanged.
- The period-representability check from re-verification 2 is kept as an early, clearer rejection of absurd orbits.

**Tests:** the four reviewer reproducers end as recorded `non_finite` failures at tick 0 with nothing committed; simulator unit tests for Python overflow and norm overflow; K2 and K5 schema tests for both versions.

**Mutations:** removing each guard fails its tests (K1: 3, K3: 1, K4: 1, K2: 2, K5: 2).
