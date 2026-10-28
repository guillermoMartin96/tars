# Independent closure review: TARS M3 T2 S1, I-41 proposal v2 ("option B for the coast closure only")

You are an independent reviewer from a different provider than the implementer. This is a **fresh**
closure review of proposal v2 and its scratch prototype (not committed work). Review is evidence, not
authority. A previous review round (round 1, of proposal v1) returned REQUEST_CHANGES with one MAJOR
finding R-01; its verdict text is supplied so you can judge closure, but you must re-derive every
conclusion yourself and must not rely on round 1's or the implementer's claims.

## Setup and rules
- Working directory: a fresh clone of the repository pinned at BASE
  `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd` (`uv sync --locked` done; run Python with
  `.venv/bin/python -B ...`).
- Materials in `review_scratch/pkg/` (sha256 in `review_scratch/pkg/SHA256SUMS`; verify first):
  - `I-41-proposal-v2.md`: the proposal under review (v1 kept as `I-41-proposal-v1.md` for diffing);
  - `prototype-v2.patch`: the scratch prototype relative to BASE (src/tars/sim/forces.py,
    src/tars/sim/simulator.py, tests/test_s1_failure_paths.py, tests/test_s1_force_context.py);
  - `harness.py` (main differential corpus), `harness_writers.py` (stage-writer corpus), `mutate.py`
    (mutation campaign; argv: prototype root, output dir), `mutation_results.json` (implementer's results),
    `ast_identity.py` (T-10 check): the implementer's evidence scripts;
  - `review-round1-verdict.md`: round 1 verdict and R-01;
  - `M3-T2-S1-authorization.md`: the owner's I-40 record (commit `c91a3ef`), including the approved I-39A §4
    proposal text (with the §8 T-07 plan and §10 mutation table) and the I-39A §5 option definitions.
- Do **not** modify any tracked file of the clone. Work only inside `review_scratch/` (e.g. copy `src/`
  and `tests/` to `review_scratch/proto/`, apply the patch there, run with `PYTHONPATH`; tests import
  `tests.conftest`, which needs `scenarios/` next to it, so copy that too). Use `PYTHONDONTWRITEBYTECODE=1`
  and `python -B`. No network.
- Do not fix anything. Report.

## Owner decisions (verbatim excerpts)
I-40 OD-2: "**APPROVED — Option A.** ForceContext validates `total_mass_kg` at construction according to
the literal U-1 / packet-r2 §3 contract. I explicitly authorize only the characterized failure-path delta
described in §8 for T-07(a) and T-07(b) on the direct `Simulator` API when `dt = +inf`. … That
authorization does **not** extend to any other behavioral difference. Validated scenarios must continue to
reject non-finite `dt_s`. Any T-07 difference other than the specifically recorded T-07(a)/(b) delta is a
mandatory STOP. Do not modify `Simulator.__init__` to reject non-finite `dt` as part of S1."

I-40 OD-4: massless context means mass absent (`None`), never `0.0`.
I-40 OD-5: permitted `simulator.py` changes are limited to necessary imports, `Simulator._derivative`,
`Simulator._powered_derivative` and the closures within them.
F3 / DQ-3 (a): "Existing M1/M2 behavior must remain byte-identical on the specified same-platform
regression gates. No change to tick logic, engine scheduling, step splitting or atomicity is approved."

I-41: "Option 2: Option B for the coast closure only, subject to verification that it preserves existing
finite-`dt` behavior. … For finite `dt`, including cases where `(tick + 1) * dt` overflows to `+inf`,
preserve BASE's observable behavior. The specific regression case discovered in I-40 must remain:
`dt = 1e308`; Zero-force model; Direct Simulator API; Failure at tick 2; Expected exception:
`FloatingPointError`; Expected classification: `non_finite`. Do not convert this failure into `ValueError`."
Option B (I-39A §5): "mass validated when a consumer reads it; zero behaviour change; U-1 reads
'rejected on use'". U-1: "Context is frozen: assignment and deletion raise; mass is converted to owned
binary64; non-finite or non-positive mass rejected".

I-42 (owner, conditional on this review): (1) T-07(k), not T-07(d), is the designated killer of M-14;
(2) T-07(a)/(b) retain BASE behaviour, the OD-2 option-A delta is unused and must not be introduced;
(3) U-1: powered contexts validate at construction, coast contexts use option B (validated on read);
(4) v2 regression-test additions and mutation-plan corrections approved conditional on this review;
(5) M-19 accepted as an equivalent survivor only if the equivalence argument is documented and
independently confirmed. The owner states: "Do not treat a passing prototype test suite as sufficient
proof of behavioral equivalence."

## What to evaluate (each independently, with your own probes)
1. **R-01 closure.** Is v2 §3.4's corrected argument (writable RK4 stage arrays; powered-context safety
   from ordering, not an arithmetic bound) correct and complete? Can any input reach
   `ForceContext(mass)` in the powered closure with an invalid `mass`? Try custom integrators, models
   writing via `r.base`/`v.base`, NumPy subclasses/views, aliasing of stage arrays.
2. **Ordering.** Verify in the patched source the order: finiteness check → F/m check → `law.direction`
   → `thrust_acceleration` → `ForceContext(mass)` → force call. Confirm it equals BASE order apart from
   the added construction.
3. **T-07(k) vs M-14.** Build M-14 yourself (powered context constructed before the finiteness check) and
   confirm T-07(k) kills it *for the intended reason* (ValueError from context construction replacing
   BASE's FloatingPointError), per parameter (NaN, +inf, −inf). Check whether −inf pins anything.
4. **Finite-dt counterexample** (own probe): dt = 1e308 and others; zero-force legacy model; direct API;
   burn inside tick 2. BASE vs prototype vs coast option-A variant; `runner.py` classification.
5. **Exception/state compatibility.** Exception type, message, `__cause__`/`__context__`, warnings,
   tick/sub-step/stage timing, committed state and atomicity on retry, BASE vs prototype. Include
   OverflowError/ZeroDivisionError conversion, BaseException, NumPy scalars, subnormals, −0.0.
6. **dt = +inf** admits no burn (so no split tick); T-07(a)/(b) keep BASE behaviour.
7. **Deferred coast context and U-1/OD-4 semantics**: validated on every read, never cached/repaired;
   type errors at construction; absent mass is `None` not 0.0.
8. **M-19 equivalence** (powered context deferred): confirm or refute with your own argument and probes.
9. **Mutation table and regression additions**: run `mutate.py` (or your own) and check every mutant is
   killed for its declared reason, except documented equivalents; check T-07 (i)(j)(k) and the T-01/T-04/
   T-06 additions are load-bearing and red/green where claimed (T-07 green at BASE; T-01…T-06 red at BASE
   per node with no collection errors; all green on the prototype). Check the proposal text, the
   mutation script and the results agree (e.g. designated killers).
10. **Scope compliance**: F3, OD-2, OD-4, OD-5, allowlisted paths only, no composite/ordering/identifier/
    DL-5/CI/dependency/threshold change, no `Simulator.__init__` change.
11. Any editorial inconsistencies in v2 that an implementer could misread.

## Output
Final message: `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES`, then a findings table (ID, severity
BLOCKER/MAJOR/MINOR/NOTE, location, finding, evidence/reproduction), then an explicit R-01 closure line
(CLOSED / NOT CLOSED), then a short section per evaluation item 1–11 with what you ran and observed.
BLOCKER = Critical, MAJOR = High. PASS requires 0 BLOCKER and 0 MAJOR. Save scripts, outputs and a full
`REVIEW.md` under `review_scratch/reviewer/`.
