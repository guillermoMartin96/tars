# Independent review 03: TARS M3 T2 S1, proposal v3-S (owned raw coast snapshot) and prototype v3

You are an independent reviewer from a different provider than the implementer. This is a **fresh**
review of proposal v3-S and its scratch prototype. Nothing has been committed to production. Review is
evidence, not authority.

Two earlier rounds returned `REQUEST_CHANGES`:
- Review 01 (proposal v1): R-01 MAJOR.
- Review 02 (proposal v2): R-02 MAJOR and R-03 MINOR; R-01 recorded CLOSED.

Their records are supplied so you can judge closure. You must re-derive every conclusion yourself
with your own probes. Do not rely on earlier reviews or on the implementer's claims or results.

## Setup and rules
- **Working directory:** a fresh clone of the repository pinned at BASE
  `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd` (`uv sync --locked` done). Run Python with
  `.venv/bin/python -B ...`.
- **Materials:** `review_scratch/pkg/`, with sha256 sums in `review_scratch/pkg/SHA256SUMS`.
  Verify them first.
  - `I-45-proposal-v3S.md`: **the proposal under review.** `proposal-v2.md` is the previous version.
  - `prototype-v3.patch`: the prototype relative to BASE. It touches `src/tars/sim/forces.py`,
    `src/tars/sim/simulator.py`, `tests/test_s1_failure_paths.py` and `tests/test_s1_force_context.py`.
  - `prototype-v2.patch`: v2 relative to BASE.
  - `v3L-vs-v2.patch`: the rejected lazy variant v3-L, relative to v2. Use it to check that the tests
    discriminate.
  - The implementer's evidence scripts:
    - `harness.py`: the main direct-API corpus;
    - `harness_writers.py`: the stage-writer corpus;
    - `harness_integrators.py`: the custom-integrator corpus. Usage: `PYTHONPATH=<tree>/src python
      harness_integrators.py OUT.jsonl`.
    - `compare_integrators.py`: argv `base.jsonl other.jsonl`;
    - `mutate.py`: the mutation campaign. Argv: prototype root, output dir. The root must be a patched
      tree containing `src/` and `tests/` (and `scenarios/`).
    - `ast_identity.py`: argv `base_root proto_root`;
    - `probe_i44.py`: argv `SRC_ROOT OUT.json`;
    - `probe_shapes.py`: argv `tree_root`.
  - The implementer's outputs: `mutation_results.json`, `integrator_corpus_compare.txt`,
    `probe_summary.txt`, `discrimination.txt`.
  - Owner records:
    - `M3-T2-S1-authorization.md`: I-40, including F3, OD-2, OD-4 and OD-5, and the I-39A plan;
    - `M3-T2-S1-decisions-I41-I43.md`;
    - `M3-T2-S1-I43-lazy-coast-investigation.md`;
    - `I-44.md` and `I-45.md`: the owner texts, verbatim;
    - `review-01-record.md`, `review-02-record.md`.
  - `contract_verification.md`: the implementer's I-45 §1 contract inspection. **Re-do it
    independently.**
- **Workspace:** do **not** modify any tracked file of the clone. Work only inside `review_scratch/`.
  - To build trees, copy `src/`, `tests/` and `scenarios/` to `review_scratch/<name>/` and apply the
    patch there.
  - Build at least BASE, v2, v3-S (`prototype-v3.patch`) and v3-L (`prototype-v2.patch` then
    `v3L-vs-v2.patch`).
  - Run with `PYTHONPATH=<tree>/src` and `PYTHONDONTWRITEBYTECODE=1`.
  - Tests import `tests.conftest`, so run pytest from inside the tree directory.
- No network. Do not fix anything; report.

## Owner decisions in force (see the verbatim texts in pkg)

**I-40:**
- F3: existing M1/M2 behaviour byte-identical on the same-platform gates; no change to tick logic,
  engine scheduling, step splitting or atomicity.
- OD-2: option A is authorized only for the T-07(a)/(b) dt = +inf delta. I-42 says that delta is
  unused and must not be introduced.
- OD-4: absent mass is `None`, never `0.0`.
- OD-5: in `simulator.py`, only imports, `_derivative` and `_powered_derivative` (with their closures)
  may change.

**I-41:** option B (validate on read) for the coast closure only. Preserve BASE finite-dt behaviour,
including the dt = 1e308 zero-force case. That case fails at tick 2 with `FloatingPointError`,
classification `non_finite`.

**I-42:** T-07(k) kills M-14; T-07(a)/(b) keep BASE behaviour; powered contexts validate at
construction and coast contexts on read. M-19 is accepted as equivalent only if documented and
independently confirmed.

**I-44 (v3-S selected):**
- "Every constructed ForceContext containing mass must own a binary64 value that cannot change because
  of later mutation to the originating stage array."
- The supported contract is `NDArray[np.float64]`; it must not be broadened to lists or object dtype.
- "For supported ndarray subclasses, preserve BASE's observable execution behavior."
- MaskedArray uses the underlying stored value.
- "Do not claim that a type annotation alone enforces runtime input validity."
- The object-dtype and list differences are provisionally acceptable as out of contract.
- "Do not introduce general-purpose runtime rejection or change unrelated input handling."
- "If additional differences appear within the supported contract, STOP."

**I-45:** approves I44-Q1 option (a).
- The supported stage is a float64 ndarray (including subclasses), 1-D, exactly 8 elements, in the
  documented layout.
- This is subject to independent verification that it is consistent with the existing documented
  interface.
- Production code must not be modified to enforce it.

## What to evaluate (each independently, with your own probes and scripts)

1. **I44-Q1 contract interpretation.**
   - Inspect the `Integrator` protocol, `Derivative`, `Simulator` and closure docstrings, ADRs, DRs,
     milestone and proof docs, and tests.
   - Is a 1-D size-8 float64 stage consistent with the documented interface? Was any other shape
     explicitly supported or tested?
   - Is the implementer's scoping correct: 8 elements with a spacecraft, while the 6-element M1 path
     is unchanged (C-1)?
   - Check the stale `integrators.py` docstring (D-1).
2. **R-02 closure.**
   - For supported stages (masked propellant, masked nomask and all-false, a raising, warning or
     reinterpreting `__getitem__`, `__array_finalize__` subclasses, `recarray` views, read-only,
     strided, big-endian), does v3-S preserve BASE's observable behaviour? Check outcome, exception,
     tick, committed r/v/propellant hex and warnings, with warnings recorded and with warnings raised
     as errors.
   - Write your own custom integrators (Euler, RK4, others you think of) and compare BASE, v2 and
     v3-S. Run the corpus too if you wish, but your own reproduction is required.
3. **U-1 snapshot ownership.** For every coast and powered context:
   - Is the mass a built-in binary64, fixed at construction?
   - Is it immune to later stage writes, shared buffers, row views or aliasing?
   - Do repeated reads agree?
   - Is no stage reference kept, and is the stage not kept alive?
   - Use a recording adapter, monkeypatched in the simulator module, to capture contexts.
4. **`np.ndarray.__getitem__(y, 6)`.** Analyze its exact semantics on subclasses and views:
   - which hooks it bypasses and which it cannot (`__array_finalize__`, `__array_ufunc__`,
     `__array_function__`, `__array_wrap__`, a Python-level `__getitem__`, properties);
   - byte order, strides, non-contiguous, read-only, and `memmap`;
   - subclasses overriding `__float__` or `item`.
   Try to find a **supported** stage (§3.2 of the proposal) for which the read warns, raises, calls
   user code or differs from BASE observably.
5. **MaskedArray stored-value behaviour.** Is it correctly described? Are there any production-
   observable consequences in S1?
6. **Subclasses that reinterpret indexing.** Does the legacy model still see `r` and `v` through the
   subclass, as at BASE? Is the stored-value mass correctly disclosed?
7. **Views, aliases and shared buffers.** Probe both the coast and powered closures.
8. **Exception and warning compatibility and timing.** Compare BASE, v2 and v3-S on exception type,
   message, `__cause__`/`__context__`, the warning set and order, the sub-step or stage at which the
   failure occurs, and committed state and atomicity on retry.
9. **Finite-dt overflow.** Run dt = 1e308 (I-40/I-41 case) and the others; the `runner` classification
   must stay `non_finite`. Also run dt = +inf and T-07(a)/(b).
10. **R-01 preservation.** The powered closure order must be unchanged from v2: finiteness → F/m →
    direction → `thrust_acceleration` → context → force. Can any input reach `ForceContext(mass)` with
    an invalid mass?
11. **Scope.** Check OD-2, OD-4, OD-5, F3 and the existing authorization boundaries: the 4 allowlisted
    paths only, no `Simulator.__init__` change, no new runtime validation, and no change to unrelated
    input handling.
12. **Tests.**
    - T-07(l) must distinguish v3-S from v2.
    - The T-04 snapshot and lifetime tests must distinguish v3-S from v3-L.
    - Check red/green at BASE as claimed: T-07 green; T-01…T-06 red by AttributeError with no
      collection errors.
    - All tests must be green on v3-S.
13. **Mutation coverage and M-19 equivalence.**
    - Run `mutate.py`, or your own mutants. Every non-equivalent mutant must be killed for its declared
      reason, including M-20 (v2's subclass-sensitive read), M-21 and M-21b (lazy references), and
      M-14 → T-07(k).
    - Confirm or refute M-19 equivalence with your own argument and probes.
    - Suggest any important missing mutant.
14. **Out-of-contract disclosures.** Are the `list`, object-dtype and shape rows of proposal §6 complete
    and accurate? Are there supported-input differences hidden among them?
15. **Records.**
    - Does the proposal avoid claiming that the Review 01/02 REQUEST_CHANGES verdicts are reversed?
    - Are there editorial inconsistencies that an implementer could misread?
16. **Any other new behavioural difference.**

## Output
Your final message must contain, in this order:
1. `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES`.
2. A findings table with columns ID, severity (BLOCKER/MAJOR/MINOR/NOTE), location, finding, and
   evidence/reproduction. BLOCKER = Critical; MAJOR = High.
3. Explicit closure lines: **R-02: CLOSED / NOT CLOSED**; **R-01: PRESERVED / NOT PRESERVED**;
   **I44-Q1 interpretation: CONSISTENT / CONFLICT**; **M-19: EQUIVALENT CONFIRMED / REFUTED**.
4. A short section per evaluation item 1–16 saying what you ran and observed.

PASS requires 0 BLOCKER and 0 MAJOR findings. Save your scripts, outputs and a full `REVIEW.md` under
`review_scratch/reviewer/`.
