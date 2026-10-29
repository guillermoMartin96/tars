# Independent plan review 01: TARS M3 T2 S1, I-46 decision record and test/mutation plan amendment A-1

You are an independent reviewer from a different provider than the implementer. This is a **fresh**
review session. Review is evidence, not authority.

## What is under review

The owner issued I-46 (verbatim in `review_scratch/pkg/I-46.md`). It accepts Review 03's `PASS` on S1
proposal v3-S as a proposal-level verdict, and records decisions D1–D7. One of them, D2, adds a
powered-context snapshot-and-lifetime regression test and mutant M-22. That answers Review 03's
note N-01.

The implementer has drafted two records:

1. **The updated decision record:** `review_scratch/pkg/M3-T2-S1-decision-I45.md`. The diff against the
   committed version is `review_scratch/pkg/decision-record.diff`. It adds §4 (the I-46 disposition)
   and §5 (I-46 verbatim, headings demoted by one), plus header and §1 pointers.
2. **The plan amendment:** `review_scratch/pkg/M3-T2-S1-test-plan-amendment-I46.md` ("A-1"). It is
   **plan only**: the tests and M-22 are not implemented.

Nothing has been implemented, and no production code has changed. Implementation commit A is not
authorized.

## Setup and rules

- **Working directory:** a fresh clone of the planning branch, pinned at
  `b52f77cb6693243b1ba681753627bb79c7005264`. Its `src/` and `tests/` equal BASE
  `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`. `uv sync --locked` is done. Run Python with
  `.venv/bin/python -B ...`.
- **Materials.**
  - `review_scratch/pkg/`. Verify `SHA256SUMS` first.
  - The committed records in the clone:
    - `docs/milestones/M3-T2-S1-proposal-v3.md`: FINAL v3-S. I-46 D1 pins it to sha256
      `dd705dd464cfeedac8c7c7918114ce7b893a8c17acb0dc4370f209d52cb9102d`. Verify the pin.
    - `docs/milestones/M3-T2-S1-authorization.md` (I-40): §6 allowlist, §7 invariants, §9a tests,
      §10 mutation, §11 gates, §12 commit sequence, §13 stop conditions.
    - `docs/reviews/M3-T2-S1-proposal-review-01.md`, `-02.md` and `-03.md`.
    - `docs/reviews/raw/M3-T2-S1-proposal-codex-review03-evidence/`, including
      `powered_mutant.py.txt`, `check-powered-lazy.txt`, `powered-lazy-tests.txt` and
      `check-ownership.txt`.
    - `docs/science/experiments/m3-t2/s1-v3/`:
      - `prototype-v3.patch`, the prototype relative to BASE, with tests;
      - `mutate.py.txt`, the campaign; the M-21 `LAZY_FORCES` edits are what M-22 reuses;
      - `v3L-vs-v2.patch` and `prototype-v2.patch`.
- **Workspace.** Do **not** modify any tracked file of the clone. Work only inside `review_scratch/`.
  - To build trees, copy `src/`, `tests/` and `scenarios/` to `review_scratch/<name>/` and apply a
    patch there.
  - Run with `PYTHONPATH=<tree>/src` and `PYTHONDONTWRITEBYTECODE=1`, and run pytest from inside the
    tree.
- **Owner restriction for this round:** "Do not implement the new tests or mutant yet; update the plan
  only."
  - So do **not** author the planned T-04 (d)/(e) tests as test files, and do **not** add M-22 to the
    campaign script.
  - You **may** use your own throwaway probe scripts in `review_scratch/` to check the plan's
    predictions, including re-running Review 03's `powered_mutant.py.txt` approach. Label every such
    result as a reviewer probe, not as the planned test.
- No network. Do not fix anything; report.

## Evaluation items

1. **Package and pin.** Do the `SHA256SUMS` verify? Does the proposal sha256 equal the D1 pin? Is the
   proposal file unchanged by this round?
2. **Verbatim fidelity.** Does decision-record §5 equal `I-46.md` once the heading demotion is undone?
   The record states sha256 `4ba87621…30bd`.
3. **Decision fidelity.** Does §4 record D1–D7 accurately, without expanding, narrowing or
   reinterpreting any of them? Check especially:
   - D3, which must not expand the contract;
   - D4, which preserves the legacy model's behaviour;
   - D5, the allowlist question;
   - D7, which forbids a cross-platform claim.
4. **Historical verdicts.** Do the records keep Reviews 01/02 as `REQUEST_CHANGES` and Review 03 as a
   proposal-level `PASS`, and avoid reinterpreting any earlier verdict? Are the I-45 parts of the
   record (§0–§3) preserved apart from the declared pointers?
5. **Test design A-1 §2.** Do T-04 (d) and (e) faithfully mirror the coast T-04 (a)/(b)? Check by
   reading `prototype-v3.patch`'s `tests/test_s1_force_context.py` and `src/tars/sim/simulator.py`,
   and by your own probes on a v3-S tree. In particular:
   - (a) Does `schedule_burn("prograde", 0.0, 30.0)` with `dt = 0.5` route **every** derivative call of
     the first tick to the powered closure, so that the call count equals `integrator.order` for each
     of the 3 integrators?
   - (b) Is recording the expected mass at the call (`_stage_mass(stage)`) sound? Does it compare the
     right quantity (INV-3)?
   - (c) Would the planned assertions pass on v3-S?
   - (d) Would they fail per node with `AttributeError` at BASE (red-first, no collection errors)?
   - (e) Are there hidden flaws, for example a burn rejected for the custom integrators, a split tick,
     the powered finiteness check, or a writer making a stage non-finite?
6. **Non-mirroring of T-04 (c).** Is the reasoning sound that a powered stored-value test is out of
   scope because the powered mass read is BASE's legacy `float(y[_PROP])`, kept by v3-S (R-01) and by
   D4? Or does D2 ("mirroring the coast ownership tests") require it?
7. **M-22 (A-1 §3).**
   - Is it correctly specified and implementable from the campaign's existing pieces?
   - Would every designated node be killed **by assertion failure**, under the I-40 §10 criterion,
     with the mechanism stated?
   - Does it pass the existing 86 nodes, which is the N-01 gap? Is it non-equivalent?
   - Does it disturb M-19's equivalence argument?
8. **Counts (A-1 §4).** Check the arithmetic and the BASE red/green figures:
   - 86 → 90 nodes; 57 → 61 red at BASE; 1 376 → 1 380;
   - BASE plus the tests: 1 319 passed, 61 failed;
   - mutants 24 → 25, killed 23 → 24, control 90/90.
9. **Gates and scope (A-1 §5).** Is any I-40 gate, invariant, allowlist rule, commit-sequence rule or
   stop condition contradicted? Is commit A's content unchanged? Is the D5 deferral correct under the
   allowlist? Does anything add runtime validation (D6)?
10. **Contradictions with the pinned proposal.** Does A-1 contradict proposal v3-S anywhere beyond the
    declared supersession of its §5 counts? Is that supersession itself legitimate under D1+D2?
11. **Commit A readiness.** From the records, list every prerequisite for commit A under I-40 §4/§12 and
    I-45/I-46. Say which are satisfied by the records and which remain open. Owner authorization is
    known to be open.
12. **Any other inconsistency** an implementer could misread.

## Output

Your final message must contain, in this order:
1. `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES`.
2. A findings table with columns ID, severity (BLOCKER/MAJOR/MINOR/NOTE), location, finding, and
   evidence/reproduction. BLOCKER = Critical; MAJOR = High.
3. Explicit lines:
   - **D1 pin: HOLDS / BROKEN**;
   - **I-46 recording: FAITHFUL / NOT FAITHFUL**;
   - **A-1 vs gates and scope: CONSISTENT / CONFLICT**;
   - **M-22 kill by the planned nodes: EXPECTED / NOT EXPECTED**.
4. A short section per evaluation item 1–12 saying what you read, ran and observed.

PASS requires 0 BLOCKER and 0 MAJOR findings. Save your scripts, outputs and a full `REVIEW.md` under
`review_scratch/reviewer/`.
