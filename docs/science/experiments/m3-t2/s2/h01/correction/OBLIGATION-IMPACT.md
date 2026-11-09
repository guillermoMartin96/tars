# Which obligation evidence the H-01 correction affects

**AUTHOR ASSESSMENT.** This is not independent review evidence. It changes no ledger status and closes nothing.

The governing ledger is the independent review of H:
`S2-REREVIEW-H-8074a19/continuation-20261108T211523Z/obligation-ledger.json` (sha256 `494e2c23…f890129`).
At H it records 29 MET, OB-11 and OB-27 FAILED, and OB-30 and OB-31 later-scope PENDING. **It remains the
standing assessment of exact H.** H-01 stays open until an independent review of a pushed corrected tip
closes it. The four I-104 findings remain as independently resolved at H; nothing here reassesses them.

## What changed

There are two uncommitted files; see `diff/`:

- **`src/tars/sim/geodesy.py`:** one statement. The final `_normalize` branch now raises
  `TypeError("geodetic input: unsupported component type")`. It no longer formats `t.__name__`. One comment
  line is added.
- **`tests/test_s2_geodetic.py`:** one new G-06 node,
  `test_g06_h01_unsupported_type_rejection_consults_no_metaclass_hook`. It uses the reviewer's exact
  witness.

No other path changes. Untouched in particular: DQ-1 arithmetic, the guard, the E.1 `try`, N1 to N5,
base-slot normalization, the frozen listing, the generator, the twin, the recorders, dependencies, CI, the
report and every historical record.

## Rows the correction is aimed at, or whose evidence must be regenerated on a new tip

| Row | Standing at H | Effect of the correction | What closes it (later; not by this packet) |
|---|---|---|---|
| **OB-11** (IN-1, including normalization) | FAILED (H-01) | Removes the only identified departure: the class-attribute read in unsupported-type rejection. Red/green and the reviewer's own probe show TypeError with no hook call. | An independent §5.2 review of the pushed corrected tip, re-inspecting IN-1 in full. |
| **OB-27** (completed review PASS) | FAILED (consequence) | None directly. | Depends on that review's verdict. |
| **OB-08** (G-06 green on CI3, including normalization cases) | MET at H | G-06 gains one node, and its fixture set now covers H-01. Host evidence: candidate S2 suite and full suite pass. | CI 4/4 on the pushed commit(s), and review of the new node. |
| **OB-10** (every §3.12 mutant killed by its designated assertion) | MET at H | The source has changed, so the pinned I-105 campaign was rerun on the candidate: control, all 49 mutants, exact MG-02/MG-04 witnesses, qualifying kills and per-execution records (see `candidate/campaign/`). The campaign definition is unchanged, and no new mutant or designation is introduced. | Review of the rerun on the pushed tip. |
| **OB-16, OB-17** (DL-5 ENV and §3.16 run records for every gate-evidence run) | MET at H, under the exact I-106 exception for the 154 named historical executions | Every new execution in this packet has its own run record, captured by the executing interpreter, plus a directly captured DL-5 record. **The I-106 exception is not extended to any of them.** | Same duties apply to the CI runs of the future commits. |
| **OB-18** (CI 4/4 on every pushed commit) | MET at H | Nothing is pushed. Each future commit needs its own 4/4. | CI on each pushed commit. |
| **OB-24** (G-13 green) | MET at H | The G-13 scope check, in working-tree form against K, was run on the candidate (`candidate/g13-scope-check.json`). Both changed paths are already S2-allowlisted. | CI and review on the pushed tip. |
| **OB-26** (REG: R-1 to R-7, R-S1, R-S2) | MET at H | R-1 to R-4, R-S1 and R-S2 were rerun on candidate bytes against a K recomputed offline (`regression/`). H's results are not reused. R-5 to R-7 (scope, protected files and report prefix) are covered on the candidate by G-13 and the full suite. The report is not yet appended, so the R-7 append-only check applies again when it is. | Review on the pushed tip. |
| **OB-22** (§3.17 merge record in the report) | MET at H | The report is not touched here. A later append (proposed commit L) would record the correction. | Review of that append. |

## Rows whose evidence is unaffected, and why

The component's accepted-input path and every reason-coded outcome are unchanged. The only behavioural
change is on inputs that already raised TypeError (and could escape with a caller exception through a
metaclass). Their message text is now fixed, and no caller code runs.

- **OB-01, OB-33** (frozen listing; G-17a; G-17b exact Class X replay, including signed zeros): the
  listing, generator and twin are byte-identical to H. G-17a and G-17b were rerun on the candidate, in the
  red/green, S2-suite and full-suite executions. Every one passed, and the records are complete.
- **OB-02, OB-19** (derivation cross-check; boundary pairs): these do not involve the component. They were not
  rerun.
- **OB-03, OB-04, OB-05, OB-06, OB-07, OB-09, OB-20, OB-21, OB-25** (G-17, G-08, G-14, G-15, G-16, G-07,
  G-10, G-05 and stop 17): the corresponding test nodes pass on the candidate in the S2 suite and in the full
  suite. No numerical change was made.
- **OB-12** (IN-2, the twin): the twin is unchanged.
- **OB-13, OB-32, OB-14, OB-15** (report-only rows; RP-9 census; RP-8): the host report on the candidate is
  compared byte for byte with the reviewer's H host report (`candidate/host-report/`). Each pytest execution
  emits its own schema-2 census, validated against the frozen listing. The RP-8 three-platform listings
  come from future CI.
- **OB-28, OB-29** (`assumptions.md` byte-identical to K; S2-C carry-forward): untouched.
- **OB-30, OB-31:** remain later-scope **PENDING**.

## Boundaries preserved

- DQ-1, the convergence rules, rejection precedence, the frozen listing and the simultaneous membership
  requirements are unchanged.
- Class P differences remain report-only.
- POG accuracy gating remains **BLOCKED**.
- A-FP-2 remains unaccepted and unjustified.
- No accuracy gate, conditional promotion or later-scope work was introduced.
- No dependency, CI, branch or workspace change was made.
- Nothing was committed or pushed.
