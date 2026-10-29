VERDICT: PASS

| ID | severity | location | finding | evidence/reproduction |
|---|---|---|---|---|
| R-04 | MINOR | Proposal §4, “size < 7 or 2-D” sentence | The categorical claim that 2-D inputs raise IndexError is false. A shape (8,1) reaches scalar conversion and raises TypeError. Qualify the statement to the tested (1,8) shape; do not change production code. This is outside §3.2 and does not reopen R-02. | `raw_probe.py`, `edge_probe.py`; BASE coast: concatenate ValueError; v3-S coast: TypeError, both tick 0. Outputs: `raw_probe.txt`, `base-edge.txt`, `v3s-edge.txt`. |
| N-01 | NOTE | T-04 snapshot coverage / mutation plan | Add a powered lazy-reference mutant to the planned campaign. My concrete mutant survives all 86 supplied S1 tests; independent ownership assertions kill it. Current dedicated after-write/lifetime regressions exercise coast only. This is a suggested coverage addition; the actual powered prototype passes the independent checks. | Independent `ownership.py` verifies both closures with shared, row and strided storage; `ownership.txt` records fixed built-in floats and zero live stages; `powered-lazy-tests.txt` records 86 passes on the missing mutant and `check-powered-lazy.txt` kills it for changed mass. |
| D-1 | NOTE | BASE `src/tars/sim/integrators.py:3–4` | The six-component module description is stale for spacecraft simulations. The proposal discloses this accurately. Correct only in a separately authorized documentation change. | `contract-scope.txt`; Simulator, ADR-0007 and DR-0026 describe the augmented spacecraft layout. |

**R-02: CLOSED**  
**R-01: PRESERVED**  
**I44-Q1 interpretation: CONSISTENT**  
**M-19: EQUIVALENT CONFIRMED**

This is evidence about the supplied proposal and isolated prototype, not implementation or merge authorization. Reviews 01 and 02 retain their REQUEST_CHANGES verdicts. PASS has zero BLOCKER and zero MAJOR findings; R-04 is an out-of-contract documentation correction.

## Method and reproducibility

HEAD was independently checked as `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`. All 24 manifest entries passed SHA-256 verification before building trees (`checksums.txt`). All work is beneath `review_scratch/`; no tracked clone file was changed. No network was used. Host: macOS 26.2 x86_64, CPython 3.12.15, NumPy 2.5.3. This is a same-host conclusion.

`build.py` copies src/tests/scenarios and applies the supplied patches separately for BASE, v2, v3-S and v3-L. Proposed v3 tests are copied onto the other trees for discrimination (the unmodified v2/v3-L test results are also retained). Source selection uses absolute PYTHONPATH, PYTHONDONTWRITEBYTECODE=1, `.venv/bin/python -B`, and pytest runs from each tree. `run_checks.py`, `run_extra.py`, `discriminate.py`, `corpora.py`, `regression.py`, `validators.py`, `more_checks.py` and `t1_checks.py` record the orchestration. Individual scripts also run directly with these environment settings.

The first full-suite attempt lacked proof fixtures and failed collection. `regression.py` copies proof/docs/toolbox and project configuration into scratch before rerunning. Initial T1 invocations lacked their historical-source arguments; the corrected run extracts only historical forces.py from local git objects 97b69ef and b1566ae. These were reviewer setup errors, not prototype findings. The memmap probe was corrected to close its temporary file, avoiding probe-generated ResourceWarnings. Corrected outputs supersede those attempts.

## 1. I44-Q1 contract interpretation

I inspected Derivative, Integrator, Simulator and closure interfaces; ADR-0004, ADR-0007, DR-0013, DR-0026; M2 milestone, proof and README references; and BASE integrator/Simulator tests. `inspect_contract_scope.py` saves the relevant passages and constructor expressions. The type alias carries a dtype but no runtime dimension validation. Simulator's explicit augmented layout supplies 3+3+1+1 components; the actual construction is one dimensional. I found no documented or tested spacecraft derivative support for malformed shapes.

Generic RK4 tests do explicitly use one- and two-component ODEs; those are not spacecraft stages and are not narrowed by §3.2. The no-spacecraft Simulator path is six components and stays so. Thus C-1 is necessary and correct. D-1 is incomplete old documentation, not evidence of supported six-component spacecraft stages. No new shape validation is introduced.

## 2. R-02 closure

My independently authored `independent.py` uses Euler, midpoint and RK4 with 14 stage kinds, coast/powered operation, zero/raising force, warnings recorded/as errors, and two attempts per case: 336 rows per source tree. Kinds include masked propellant, nomask, all-false mask, raising/warning/reinterpreting indexing, finalize hooks, recarray, read-only, positive/negative strides, opposite byte order and memmap. It records exceptions including cause/context, committed state hex and propulsion snapshots, warnings in order, derivative times and force-visible subclasses.

BASE/v3-S execution differences: **0/336**. BASE/v2 differences: **36/336**, confined to masked, raising and warning indexing. The supplied independently rerun integrator corpus has 6,216 cases: v2 differs on 500 supported rows; v3-S differs on zero supported rows, plus 392 out-of-contract list/object-None rows. v3-L has zero execution differences but fails ownership. See `own-summary.txt`, `integrator-summary.txt` and raw JSONL files.

## 3. U-1 snapshot ownership

I monkeypatched the adapter in the simulator module, capturing contexts without retaining r/v or stages. `ownership.py` tests both coast and powered closures with a reused buffer, row views and strided views; each evaluation has a distinct known mass. After overwriting all backing storage, repeated reads retain the original hex values, `_mass` is a built-in float, and all stage weakrefs die. `independent.py` additionally checks contexts after integrator writes and after successful steps. The context stores only `_mass`; no array, callable or view is retained. Invalid coast values remain fixed and fail on each property read; powered invalid values fail before a context is handed to the adapter.

## 4. Base ndarray indexing semantics

`raw_probe.py` supplies a hostile float64 subclass with raising indexing, float, item, ufunc, array-function and wrap hooks, a finalize recorder, and dtype/shape properties. For both byte orders and positive/negative/non-unit strides, the added base integer read returns the expected scalar with no hook events or warnings. Additional edge probes include signaling NaN, quiet NaN, infinity, subnormal and negative zero. `snan_probe.py` also compares signaling-NaN propellant through full coast evaluations with seven ordinary NumPy force operations and both warning policies: all 14 output rows match BASE byte for byte (`base-snan.txt`, `v3s-snan.txt`).

For a valid 1-D float64 ndarray, the unbound base descriptor bypasses Python `__getitem__`; indexing is neither ufunc nor array-function dispatch. An integer element read returns a NumPy float64 scalar, not a subclass view, so finalize/wrap and the stage's item/float methods do not run. The scalar float conversion owns an exact binary64. Actual storage byte order and strides are honored; writeability is irrelevant. Memmap is backed by the same ndarray read machinery; my custom-integrator memmap cases match BASE. Buffer validity remains an ordinary ndarray prerequisite. I found no supported stage causing the added read to call user hooks, warn or raise. The analogous universal assertion for 2-D arrays is false (R-04).

## 5. MaskedArray stored-value behavior

Masked, nomask and all-false stages match BASE execution under both warning policies. The stored 300 kg yields coast context mass 1300 kg even when masked. v2 instead converts the masked sentinel and warns/produces NaN. The current legacy adapter ignores mass, so stored-value coast contexts have no new production force consequence in S1. Powered mask handling is unchanged and may still warn as at BASE.

## 6. Reinterpreting subclasses

My scaling-index subclass demonstrates owned stored coast mass while preserving BASE dynamics; powered indexing remains the prior interpreted read. Source inspection confirms r and v still originate from `y[:3]` and `y[3:6]` through subclass dispatch and are passed through the adapter without conversion/copy. Force-visible subclass types and hook event sequences match BASE. Stored versus interpreted coast mass is explicitly disclosed, not hidden.

## 7. Views, aliases and shared buffers

The own ownership probes cover both closures and distinct masses across shared, row and strided storage, with writes through backing arrays. All snapshots survive later writes and no context keeps the stage alive. Proposed shared-buffer/row-view/write-after tests also pass on v3-S and fail on v3-L. Read-only and reversed views match BASE in the execution corpus.

## 8. Exceptions, warnings, timing and retries

My execution corpus records exception type/message/cause/context, ordered warnings, callback times and committed state for two attempts. The supplied direct API and writer corpora independently rerun here add broader fault and scheduling cases, including retries. BASE and v3-S outputs are byte-identical: direct corpus SHA-256 `e0309486277deb101d341f23d57964d2f0c2874ab865d5be80c07f6499f0a814`; writer corpus `3310fd9031bc2c0cd611168e9ae3d1164ac00e87628fbe89d4c9b99401f60415`. These cover 26,880 and 26,112 cases respectively (the direct file also has a metadata row). Failed steps retain state and schedule, and retry timing is preserved. Out-of-contract new failures occur before the legacy force call as disclosed.

## 9. Finite-dt overflow and infinity

`overflow_order.py` independently reproduces the split-tick zero-force counterexample at dt=1e308 and 8.98846567431158e307: tick 1 commits; tick 2 raises FloatingPointError("non-finite state produced at tick 2"), with no cause/context, unchanged committed state/propellant and identical ordered warnings on retry. The burn uses tiny thrust so its acceleration underflows while state remains finite before the infinite final coast substep. `runner_probe.py` injects these prepared direct-API simulations into the real runner and checks classification, also at 1.2e308. Ordinary unsplit zero-velocity coast with huge finite dt need not fail; `edge_probe.py` records that unchanged control. T-07(a)/(b)/(j) and the differential corpora check +inf and no admitted burn; BASE expectations remain intact.

## 10. R-01 preservation

I compared powered closure ASTs: v2 and v3-S are identical. The order remains finiteness, mass/F-over-m, direction, thrust_acceleration, context, force. thrust_acceleration validates finite positive total mass before returning; the retained mass is a Python float and cannot change through subsequent stage mutation. `overflow_order.py` independently writes NaN/+inf/-inf via the legacy r-base view during a split tick: failure is FloatingPointError at t=2, tick remains 0, and no invalid powered context is captured. T-07(k) kills M-14 on NaN/+inf for the intended ValueError difference. The -inf parametrization alone does not kill it because max(-inf,0) clamps to zero; the campaign accurately reports 2/3 failures.

## 11. Scope and preservation

Own file comparison finds exactly the four allowlisted paths. Own AST comparison removes only imports/_derivative/_powered_derivative and finds the remainder of simulator.py identical to BASE, including __init__, tick logic, engine splitting and atomicity. The supplied AST checker independently rerun here reports 51 checks, zero failures. Legacy models, integrators and unrelated input handling are unchanged. No new stage runtime validation is added. Mass absence is None, never zero. OD-2's unused option-A delta is not introduced. The direct and writer byte comparisons support F3; they do not imply cross-platform validation.

Full pytest with the proposed tests: v3-S **1,376 passed**; BASE **1,319 passed and 57 expected AttributeError failures** (the 1,290 original tests plus 29 T-07 passes). No other failure or collection error. T0: **314 passed** on each tree. T1 Review01/02 correction-check outputs are byte-identical across trees. Both M1 and M2 proof validators PASS, with byte-identical JSON reports. M1 cross-process determinism retains golden SHA-256 `7a4e18777ccd134b66749e05fba5197f07885bd64e073949692a3baa01f820a4`. These are local validator runs, not a claim that the uv-based proof shell wrappers, remote CI, cross-platform jobs or new GMAT executions were rerun.

## 12. Tests and discrimination

BASE plus proposed tests: 29 T-07 passes and 57 T-01…T-06 failures, all AttributeError, no collection errors. v3-S: 86/86 passes. With all v3 tests applied to v2: 4 fail/82 pass, including both T-07(l) cases and both stored-mass cases. With those tests on v3-L: 6 fail/80 pass, including all three snapshot cases, lifetime, and stored-mass cases; T-07(l) passes. Thus behavior and ownership regressions discriminate independently. See `*-s1.txt` and `*-v3tests.txt`.

## 13. Mutation coverage and M-19

The supplied mutation script was executed against the independently patched v3-S tree; I inspected the mutation edits, designated nodes, JUnit failures and reason checks. Control: 86 pass. All 23 non-equivalent mutants are killed for their declared reasons, including M-20, M-21, M-21b and M-14→T-07(k). M-19 survives 0/86 failures.

Independent argument: at the construction line, mass is already an owned Python float and thrust_acceleration has validated it as finite and positive. Eager versus deferred validation therefore accepts the same fixed value. The current adapter ignores the context. `ownership.py` run against the generated M-19 source produces byte-identical output to v3-S, including invalid-mass precedence and both closure ownership checks. Equivalence is confirmed for current production behavior, excluding instrumentation of the implementation itself; future context consumers or reordered validation require re-evaluation. N-01 is confirmed concretely: `powered_mutant.py` installs v3-L lazy-context machinery but uses it only in the powered closure. All 86 supplied tests pass (`powered-lazy-tests.txt`), while `check_ownership.py` kills it on the powered shared-buffer mass changing through an alias (`check-powered-lazy.txt`). The same independent assertions pass on actual v3-S. Add this mutant and both-closure ownership tests to the future campaign; dedicated supplied ownership regression additions are coast-only.

## 14. Out-of-contract disclosures

The rerun corpus confirms list and object-None differences (196 rows each), and the sampled object-float/float32/longdouble controls match BASE. Shape probes reproduce size6, (1,8) and size10 rows. The explicit table rows are accurate experimental examples, not an exhaustive taxonomy of all unsupported inputs. Shape (8,1), independently added here, has a different exception delta than the broad §4 sentence claims (R-04); disclose it or qualify the sentence. No supported-input difference was concealed by the out-of-contract classification. Object-dtype values can invoke arbitrary float behavior; the sampled float-propellant row should not be read as a guarantee for every object array.

## 15. Records and editorial clarity

I read the supplied review and owner records, and independently checked the actual source/test evidence. Proposal status and §8 explicitly preserve both historical REQUEST_CHANGES verdicts and distinguish finding closure from review disposition. R-03's prototype filename, T-07(k) and M-14 references are corrected. R-04 is the remaining factual editorial correction; D-1 is already disclosed. No record claims this review authorizes implementation.

## 16. Other behavioral differences and limits

No additional supported-input execution difference was found. My probes extend the supplied sample with midpoint integration, negative strides, memmaps, hostile hooks/properties, signaling NaN scalar reads, powered after-write/lifetime checks and an extra malformed shape. These are finite probes plus a source-level argument for the supported raw read, not a proof about arbitrary corrupted memory or external concurrent buffer writes. The verdict concerns only this proposal/prototype and current S1 adapter behavior. No production code was fixed, committed, pushed or merged.
