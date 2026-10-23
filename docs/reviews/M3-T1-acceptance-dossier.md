# M3 T1 (J2 force model): acceptance dossier for the Tech Lead's decision

**Prepared under:** "I-20 — M3 T1 Review 02 Corrections and Review 03 Authorization", §8. It says that if Review 03 returns an unconditional `PASS`, the implementer is to "Prepare the T1 acceptance dossier. Include the final validation, mutation limitations, and unresolved assumptions. Stop for my explicit acceptance decision. Do not automatically accept or merge T1."

Review 03 returned `VERDICT: PASS (unconditional)`. It also raised two NOTE findings that need an owner disposition, so the first stop rule of §8 applies as well. The NOTEs are reproduced and classified, and their dispositions are proposed in `M3-T1-review-03.md`. They are **not fixed**, and no Review 04 is started.

**Status: T1 is NOT accepted and NOT merged.** This dossier is a recommendation and an evidence index. It makes no decision, merges nothing, does not start T2 or T3, and resolves no open DR item.

## Recommendation
- **T1 acceptance: READY for the owner's decision**, subject to the owner's disposition of two NOTEs and one observation (below). None of the three is a defect in the reviewed code's behavior.
  - Independent Review 03 (Codex, at `4b85ded298e521f5c72b606cd012dec8b56e9c5e`): `VERDICT: PASS (unconditional)`. No BLOCKER, MAJOR or MINOR finding.
  - **Every earlier finding is RESOLVED**, per the reviewer: M3T1-R1-F1 … F4 and M3T1-R2-F1, F2, F3 and O1.
  - **Open:**
    - M3T1-R3-F1 (NOTE, documentation of the exact-rational fallback's reach);
    - M3T1-R3-F2 (NOTE, timing of a field in a historical reproduction row);
    - M3T1-R3-O1 (observation, a surviving mutant in the upper subnormal band).
- **Implementer's view on the open items.** None changes the behavior of the reviewed code.
  - R3-F1 and R3-F2 can be closed by appended record notes.
  - R3-O1 can be closed by one added test case and one harness mutant, or by recording it as a limitation.
  - Whether they are closed before or after acceptance, and whether a further review is wanted, is the owner's decision. The implementer recommends closing them first, with no further review, if the owner judges the changes to be records and tests only. That would be a new authorization.

## Branch and commits
- **Branch:** `milestone-3-t1-j2-force-model`, created from `main` = `60648b93385a9954194730006aeac29ea14875ad`. `main` is an ancestor, so a fast-forward is possible.
- **Reviewed checkpoint:** `4b85ded`, 19 commits ahead of `60648b9`. A further commit records Review 03 and this dossier. That commit is records only: it changes no source, test, experiment or result file.

| Round | Reviewed commit | Verdict | New findings |
|---|---|---|---|
| 01 | `97b69ef` | REQUEST_CHANGES | R1-F1, R1-F2 (MINOR); R1-F3, R1-F4 (NOTE) |
| 02 | `1cf0ce9` | REQUEST_CHANGES | R2-F1, R2-F2 (MINOR); R2-F3 (NOTE); R2-O1 (count note) |
| 03 | `4b85ded` | **PASS (unconditional)** | R3-F1, R3-F2 (NOTE); R3-O1 (observation) |

- **Records:**
  - `docs/reviews/M3-T1-review-0{1,2,3}.md`;
  - raw outputs and prompts in `docs/reviews/raw/M3-T1-codex-review0{1,2,3}{,-prompt}.md`. Every Tech Lead text from I-17 to I-20 is reproduced verbatim in them;
  - evidence and reproductions under `docs/reviews/raw/`.
- **Commits by pass:**

  | Pass | Commits |
  |---|---|
  | Implementation (I-17) | `5fd24a2` (tests), `e23675c` (code), `81a0d56` (VAL-0020 and evidence), `97b69ef` (report) |
  | Review 01 record | `dbb960a` |
  | Review 01 corrections (I-19) | `62d3684`, `a27f288`, `b0164fd`, `16a8e63`, `1cf0ce9` |
  | Review 02 record | `b1566ae` |
  | Review 02 corrections (I-20) | `56ad329`, `bbcf40e`, `304d796`, `308f126`, `a4dfda1`, `2f82c00`, `c456881`, `4b85ded` |

- **Scope:**
  - `git diff 60648b9..4b85ded -- proof toolbox scenarios .github uv.lock pyproject.toml src/tars/validation` is empty (implementer and reviewer).
  - `src/` changes: `src/tars/sim/constants.py` +58 lines and `src/tars/sim/forces.py` +137 lines, with no lines deleted from either. The existing force classes are AST-identical.
  - Tests: `tests/test_constants.py` and `tests/test_zonal_j2.py`.
  - Nothing is wired into a scenario, the simulator, the runner or a schema.

## What T1 delivers (I-17)
- **Constants:**
  - `EGM2008_C20_TIDE_FREE = -0.484165143790815e-3` (DR-0029 P10 option (a)) is the only authoritative literal;
  - `j2_from_c20`;
  - `EarthJ2Constants` with a derived `j2`;
  - `WGS84_EGM2008_TIDE_FREE`, whose J2 is `0x1.1bcdd00abd9aap-10`, bit-identical on the three CI platforms.
- **`ZonalJ2Gravity(mu, equatorial_radius, j2)`**, name `zonal_j2`, version 1:
  - a = k (x(1 − 5s²), y(1 − 5s²), z(3 − 5s²)), with k = −(3/2) J2 μ R² / r⁵. The axis is the fixed frame +Z axis (DR-0028 J-ax-1). The model is pure and stateless, uses the `(t, r, v)` protocol and needs no mass;
  - **immutable:** `__slots__`, with assignment and deletion raising; no cache (R1-F1);
  - **owned binary64 parameters:** int (not bool), float, NumPy integer and floating scalars, and 0-d arrays of those are converted to built-in `float` before validation; every other type raises `TypeError`, and an unrepresentable int raises `ValueError` (R2-F2);
  - **explicit numerical domain** with `ValueError` instead of a silent loss (R1-F2): finite positive μ and R; finite J2; a finite, normal coefficient; a normal finite r⁵; a normal finite k; no inexact subnormal (underflowing) product in the coefficient chain or in the component products (R2-F1). Exact zeros, exact subnormal products and subnormal final components are returned.

## Final validation evidence
| Check | Implementer (at `c456881`; `4b85ded` changes docs only) | Reviewer (at `4b85ded`) |
|---|---|---|
| Full pytest | 1288 passed | 1288 passed, 3 warnings (28 min 46 s) |
| T1 tests (both files) | 107 passed. Red-first: 26 failed / 81 passed against `b1566ae` | 107 passed; red-first 26 / 81 reproduced |
| T0 checks | 314 passed | 314 passed |
| M1 Proof | PASS 9/9 (fresh clone) | wrapper not run; validator 7/7, golden bit-identical, digest `7a4e1877…20a4` in both processes |
| M2 Proof | PASS 20/20, m2_proof 228/228 (separate fresh clone) | wrapper not run; validator 228/228; determinism for all four `scenarios/m2_*.json` |
| Mutation (committed campaign) | 46/46 killed by assertion | 46/46 by meaningful assertions, messages inspected |
| Bit identity of valid results | 200 004 states: 0 differing; three RK4 trajectories (6 001 states each): bit-identical, against `b1566ae` | the same, against `b1566ae` and `97b69ef`; plus its own 9 919-state sample, identical to both |
| Experiment outputs | correction checks, survivors and informational results byte-identical; the mutation results differ only in memory addresses | the same |
| Equatorial domain | 3.3773820261812166e-57 m … 4.476546622757235e61 m, unchanged | reproduced |
| ruff check / format | clean | clean (236 files) |
| CI (four jobs: ubuntu, macOS arm64, macOS Intel, m2-cross-platform) | success on `a4dfda1` 40002590550, `2f82c00` 40002789138, `c456881` 40002897696 and `4b85ded` 40008016629 | exports internally consistent; not authenticated |

**Physics gates (VAL-0020):**
- constant identity and correct rounding;
- the power-of-two known answers (2γ₁₆);
- the gradient against a separately coded potential, using dual numbers (γ₆₄; DR-0025 Q3 disposition, I-19). The reviewer's interval certificate encloses all 5 904 dense-grid cases, with the largest ratio 0.411;
- exact axisymmetry and z-reflection; radial sign; J2 = 0 gives bitwise point mass;
- polar-plane invariance;
- the invariant-drift structural test (ratio ≤ 1/2).

The secular-rate comparison is informational only.

## Mutation results and limitations
1. **Committed campaign: 46/46 killed, all by assertion.** It consists of:
   - 14 original mutants;
   - 8 from Review 01;
   - 10 R1 protection removals;
   - 14 R2 protection removals (7 F1, 7 F2).

   This is evidence for 46 named defects, **not complete coverage**.
2. **Exploratory mutants:**
   - Review 02's `near_min_normal_zero` is now killed.
   - `canonical_one_ulp` and `narrow_band` survive, accepted by the owner as a documented limitation (I-20 §3). The reasons:
     - the one-ulp change lies inside the gate tolerances, though it would fail the bit-identity comparison;
     - the narrow band is absent from the straight-line production code. That is a code-inspection argument; the 200 004-state set hits the band with probability about 25 % and has 0 states in it.
3. **Review 03's `upper_subnormal_ignored` survives** all 107 T1 tests (M3T1-R3-O1, reproduced). Production behaves correctly; the open question is whether to add the test.
4. **Classifier:** a JUnit failure type `Failed` is accepted whatever its message. Accepted as a limitation (I-20 §3); no misclassification has been observed.
5. **Diagnostic kills:** some protection-removal mutants are killed by the required diagnostic message, not by the acceptance of a formerly rejected state. This is documented.

## Unresolved assumptions and limitations (conditions of every guarantee)
- **IEEE 754 binary64**, with correctly rounded basic operations and gradual underflow, is assumed. It is checked per platform only for `sqrt` and the constant product. Complete IEEE 754 correctness is **not** claimed.
- **Near the latitude-factor zeros** (1 − 5s² = 0, 3 − 5s² = 0) a component has only absolute accuracy, relative to the |k|·|r| majorant. This is the formula's behavior, unchanged.
- **Conservative rejection.** A factor that is mathematically 0 but computed as a small non-zero value raises if k is tiny. This needs non-physical parameters and cannot happen with the canonical constants.
- **Reach.** The R2-F1 raising checks cannot trigger with the canonical constants inside the accepted domain. Exact-zero products do reach the exact-rational comparison (R3-F1); the cost is bounded and the results are correct.
- **Operation counts** behind the γ₁₆ and γ₆₄ bounds are by inspection. The reviewer found the operation graphs no deeper than the recorded counts; a path count alone is not a proof.
- **Dual-number gradient oracle** (DR-0025 Q3, accepted for T1 under I-19). It shares ordinary arithmetic, `sqrt`, the constants and the conventions with the model, so it is not external corroboration.
- **Immutability** covers ordinary assignment and deletion. Deliberate object-model bypasses (`object.__setattr__`, slot descriptors) are outside the promise.
- **Finite evidence.** One host was used for the local numerics (macOS x86_64, CPython 3.12.15, NumPy 2.5.3), plus the three CI platforms for the test suite. The tests, samples and mutation campaigns are finite.
- **dt⁵ invariant drift:** observed, not explained.
- **No external comparison** (GMAT, DOP853) is in T1; that is T4/T5 scope.

## Open decisions
**Raised by Review 03.** Proposals are in `M3-T1-review-03.md`:
1. **M3T1-R3-F1 (NOTE):** proposed ACCEPTED, corrected by an appended VAL-0020 clarification ("non-zero products"). No code change.
2. **M3T1-R3-F2 (NOTE):** proposed ACCEPTED, corrected by an appended provenance note in `M3-T1-review-02.md`. The raw files are preserved.
3. **M3T1-R3-O1 (observation):** recommended to add one upper-band test case and the corresponding harness mutant. The alternative is to record it as a documented limitation.
4. **Coefficient-chain scope.** The implementer extended R2-F1 to the coefficient chain and flagged the extension for the owner. Review 03 judges it within I-20's scope; the owner has not ruled on it.

**Preserved from I-19 §9 and I-20 §9, undecided:**
- DR-0029 P1–P9; Q-G2-1/P6 (escalated GMAT geodetic-drag sensitivity); Q-G2-2 (stays PROPOSED);
- DR-0028 P6(b);
- the secular-rate tolerance and presentation;
- T4/T5 comparison requirements;
- the M3 final time step (Q-G2-4 stays PROVISIONAL);
- the T3 axis representation;
- external corroboration.

## Decisions requested from the Tech Lead
1. Dispose of M3T1-R3-F1, R3-F2 and R3-O1, and say whether they are to be closed before acceptance.
2. Rule on the coefficient-chain extension of R2-F1.
3. Accept or decline T1 at the reviewed checkpoint `4b85ded`, together with the record commit that follows it and any closing commit you authorize.
4. Separately, if T1 is accepted: authorization to merge `milestone-3-t1-j2-force-model` into `main`.
5. Separately: the open items above. T2 needs DR-0029 P1–P9 and its own authorization; T3 needs its own authorization.
