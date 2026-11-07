# S2 governing stop before commit D (I-99 / I-101; v11 §3.15 stop 8)

Recorded 2026-11-06 (UTC evening), author session. Nothing was committed or pushed after BC.

## State

| Item | Value |
|---|---|
| Branch | `milestone-3-t2-s2-geodetic`, worktree `~/.superset/worktrees/tars/milestone-3-t2-s2-geodetic`, clean |
| Commit A | `6c05e53c5ffcb892dacaa6f84e12a163830a4119`; CI 42265640238 attempt 1, 4/4 success |
| Commit BC | `2b975d626e92c76a18efc873e0991084db30617a`; CI 42301740647 attempt 1, 4/4 success (all four jobs executed in attempt 1) |
| Commit D | NOT made. Stop 8 reached during the D evidence run |

## The stop

v11 §3.12: each mutant "must fail its designated test node with an **assertion failure**; a kill by an
unrelated exception does not count"; "A mutant that no test kills is **UNKILLED** … reported UNKILLED,
which is stop 8." §3.15 item 8: "A mutant survives without a documented equivalence argument."

**MN-17** (v11 §3.12 Numerical-rules table, [I75-04]: "the component value used as given, instead of the
base-slot value"; designated killer "G-06 `__abs__`, `__eq__` and `__mul__` override cases").

Mutation (geodesy.py line 107 only):
`return float.__float__(v)  # type: ignore[arg-type]` → `return v  # type: ignore[return-value]`

Results at BC, fresh clone from GitHub, host macOS x86_64, CPython 3.12.15:
- `test_g06_float_subclass_overrides_never_run` (the `__eq__` / `__mul__` / `__float__` case) FAILS, but
  by an uncaught `tars.sim.geodesy.GeodeticDomainError: … not exactly a binary64 value` raised inside
  `geodetic` (the mutant lets `F.__float__` (returns 0.0) run in step 1, then `0.0 != F(7e6)` raises
  `not_binary64`). Not an assertion failure. Campaign verdict: KILLED_WRONG_REASON (not a kill).
  Record: `out/mutation/MN-17.stdout.txt`, `out/mutation/MN-17.xml`, `out/mutation/mutation_results.json`.
- `test_g06_float_subclass_whose_abs_raises_is_normalized` (the `__abs__` case) PASSES against the mutant.
  This node is named by v11's designation but was omitted from the campaign script's MN-17 node list
  (author script defect, recorded). The diagnostic run that establishes it is
  `diagnostic-MN17/mn17-diagnostic.log` (exit 1: 1 failed, 1 passed). It is diagnostic only, run once,
  against the same mutant tree; it is not campaign evidence.

So no v11-designated node kills MN-17 by an assertion. The mutant is behaviourally detected (the test
does fail), but under the v11 counting rule it is UNKILLED: stop 8. There is no documented equivalence
argument, and none is possible: the mutant changes observable behaviour.

## Why I did not continue

Any remedy changes a test file after the red run and after a CI-green push of BC:
- v11 §3.14 step 3: "If any test file must change after the red run, STOP and redo the red run. Never
  edit the red record."
- I-101: "this instruction authorizes no CI rerun or fix-forward. A local gate failure or incomplete
  evidence also requires reporting before proceeding."

Possible remedies (owner's choice; none taken):
1. Make the G-06 override assertion observe the outcome, e.g. capture `GeodeticDomainError` and assert
   on the outcome, so the mutant fails by assertion; then redo the red run for the changed file and
   follow the owner's instruction on how the corrected test reaches the branch (new commit after BC or
   otherwise).
2. Owner ruling that a designated node failing by a `GeodeticDomainError` raised from the component
   under test counts as a kill for MN-17 (it is not "an unrelated exception" in the sense of S1's
   ImportError/AttributeError cases, but v11 requires an assertion failure). The author does not
   claim this reading.
3. Any other owner instruction.

## Other D evidence results (complete, recorded, not committed)

- Mutation control: 73 designated nodes pass. 49 mutants: 43 KILLED by assertion; 5 SURVIVED as the
  documented equivalents (ME-01 to ME-04, M-W2); 1 KILLED_WRONG_REASON (MN-17). Driver exit 1 (NOT OK).
- Observation (for the D report, not a stop): MI-03's v11 designation "G-06 (inf, 0, 0)" cannot kill it
  (the pre-filter returns before the predicate); it is killed by assertion at the `(nan, 0, 0)` row of
  the same G-06 order table (1/8 nodes).
- M1 derivation cross-check: all 8 G-03 pairs located by M1 bisection equal the G-03 constants; M2,
  classical and polynomial agree; 0 of 22 665 listing labels disagree with M1; smallest |M1 relative
  margin| 2.569e-19. No stop 15.
- G-13 scope check K..BC: PASS.
- Report-only RP-1 to RP-7, host RP-9 census: complete (RP-9 22 665/22 665; RP-7 X-D1 0 bit differences
  over 656 points).
- RP-8 / RP-9 by the CI log route (BC run 42301740647): 0 outcome differences between any two
  platforms; census 19 154 accepted / 64 evolute_region / 3 447 non_convergence on each; max |dh|
  1.49e-8 m, max |dphi| 5.6e-16 rad; 22-30 sign/zero crossings near h = 0 per pair. Report-only.
- Red-record blob binding: all three test files at BC equal the red record blob ids.
- BC CI records: per platform identical to commit A's (XP3 body digests, G-17a class P differences
  2 188 / 2 305 / 0, G-17b 0 differences on 8 853).
- Green record at BC, fresh clone from GitHub (`green-bc/`, 23:14:36Z–23:42:36Z): clean clone at BC;
  ruff check exit 0, ruff format --check exit 0, pytest 1 518 passed, exit 0.
