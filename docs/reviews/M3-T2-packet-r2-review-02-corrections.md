# M3 T2 packet r2: Review 02 MINOR corrections (I-34A)

- **Authorization:** I-34A, "M3 T2 Packet Review 02 MINOR Corrections" (owner/Tech Lead, 2026-10-26), approved with restricted scope.
  - It supersedes I-34, whose finding descriptions matched the readiness findings M3T2R-R2-F1 … F3 rather than Review 02. The implementer stopped on that mismatch, and I-34 was not executed.
  - Scope: the three MINOR findings, plus an investigation of the R2-F4 fingerprint fields.
  - The I-34A text received was truncated in §6 after "No unauthorized scope". The implementer reads that item as "no unauthorized scope expansion". Its missing remainder is not assumed to grant anything.
- **Baseline:** `milestone-3-t2-authorization` = `3bb363783e8a12f034876c23e713f15d3a202c23`. Preconditions verified:
  - the local and remote HEAD are equal;
  - the worktree is clean;
  - CI is green: `5f96119` run 40394176271 and `3bb3637` run 40395403727, 4/4 jobs each;
  - the three MINOR findings exist in the Review 02 record;
  - the readiness corrections are intact. Exact z-reflection (U-19 (b)) and PM-4 (b) are report-only; E3 is an upper enclosure only (U-13); "smallest-magnitude" stands in DR-0029 P4 item 8. Readiness Review 03 passed (`a57de3f`).
- **Changed:**
  - `docs/milestones/M3-T2-implementation-authorization-packet.md`, in place, with *(I-34A, R2-Fn)* markers and the §16.1 map. The text Review 02 reviewed is preserved at `5f96119`;
  - new evidence in `docs/reviews/raw/M3-T2-packet-r2-I34A-evidence/`;
  - this record.
- **Unchanged:**
  - the Review 01 and Review 02 records and their raw files;
  - the I-33 correction record and I-33 evidence;
  - every decision record;
  - packet r1, the validation strategy and the T0 spike;
  - every protected path.

  D-0 … D-8 remain PROPOSED.

## 1. Corrections
| Finding | Original defective statement | Correction and rationale | Evidence |
|---|---|---|---|
| **M3T2P2-R2-F1** (MINOR) DL-4 enforcement overclaim | §3 (iii): "This is a **conformance** requirement: DL-4 enforces it at the tested points". §6.3: "Bitwise conformance shows that the execution sequence agrees with the twin's". §7 RQ-6: "Gate by inspection and DL-4" | **Output equality cannot establish internal properties.** Equal bits show that the outputs agree, not which operations computed them.<br>• §3 (iii) is restated as an **implementation** requirement, verified by operation-by-operation source inspection. r1 §5 DQ-1 already names that inspection as "Primary" conformance evidence.<br>• DL-4 is defined as **output** conformance. "Sequence conformance" (DL-4, G-T2-10, D-8) is defined as that output equality.<br>• §6.3 F5 is reworded. RQ-6 is gated by inspection only.<br>• The D-6 and D-8 rows are protected (I-34A §4). They are **not edited**: a reading note after the §14 table aligns their wording, and changes no proposal or recommendation.<br>• **Not weakened:** source inspection was already the primary evidence. The incorrect claim that DL-4 also enforced (iii) is removed, and nothing replaces it | I-33 `pog_pipeline.out` line 30: the `numpy.cos` mutant gives E1-PASS at 631 points with **0** passes on different bits. So it is bit-identical to the specified evaluation, yet it uses NumPy. The Review 02 reviewer cited this preserved result (raw Review 02, R2-F1 row), and the implementer confirmed it when recording Review 02 |
| **M3T2P2-R2-F2** (MINOR) 3-ulp rule | §6.4 rule 1: "it allows 2·f/2ᵉ ulps … So 3 ulps passes iff f > 1.5·2ᵉ (sin(1) + 3 ulps = 1.77 units: inside)". The same wording is in I-33 `f2_premise_controls.py.txt:65` and its output. That file is raw evidence and is **left unchanged**; it is superseded by the corrected rule | **An explicit ulp metric and the exact allowance:**<br>• ulp(f) = 2^(e′−52), with e′ = max(⌊log₂\|f\|⌋, −1022).<br>• \|f̂ − f\| = k·ulp(f) satisfies A-FP-2 iff k ≤ A(f) = 2\|f\|/2^e′ + 2^(−1021−e′), inclusive.<br>• The old rule omitted:<br>  – equality: f = 1.5 gives A = 3 + 2⁻¹⁰²¹;<br>  – the ν term: f = 2⁻¹⁰²² gives A = 4;<br>  – the starting error of a rounded irrational f.<br>• Corollary, for exactly representable f only: for e ≥ −969, 3 ulps passes iff f ≥ 1.5·2ᵉ.<br>• "1.77 units" is now stated as 1.77 × 2⁻⁵² relative, against UF = 2 × 2⁻⁵² (§6.4, §8.2).<br>• **Not weakened:** UF, ν, the checker, the premise decision and the 32 controls are unchanged. The metric is a description of A-FP-2, not a redefinition of it. Expected outcomes still come from the exact inequality | `i34a_minor.out`:<br>• closed form = direct quotient at 8 190/8 190 samples;<br>• checker = closed form at **36 855/36 855** displacements of 1 … 5 ulps (4 095 non-binary64 displacements skipped);<br>• f = 1.5 + 3 ulps: old rule FAIL, closed form PASS, checker PASS;<br>• 2⁻¹⁰²² + 3 ulps: the same;<br>• corollary: holds for every e ≥ −969 with 0 violations; at e = −970, nextdown(1.5·2ᵉ) + 3 ulps PASSES (ν exactly offsets the 2⁻⁵¹ shortfall);<br>• sin(1) + 3 steps is 2.9840·ulp(f) from sin 1, with A = 3.3659: PASS |
| **M3T2P2-R2-F3** (MINOR) DL-2 admissibility | §2.2 DL-2: "The method needs no convergence argument: any foot-point approximation gives a valid enclosure, and its quality only affects the width" | **The statement is qualified.** The enclosure is valid only for an **admissible** construction: a surface point exactly on the ellipsoid (its constructed coordinate within the ellipse's range) and a nonzero support direction m.<br>**The draft's coverage is stated as not established:**<br>• it raises `ValueError` at (2¹⁰²⁰,)³, where the twin's intermediates are finite;<br>• it raises on every sampled off-axis ray from \|r\| ≈ 2¹³⁹;<br>• it does not raise on the sampled axis and equatorial rays;<br>• at the origin it raises `ZeroDivisionError` (m = 0).<br>An oracle exception fails closed: no enclosure, no verdict, never converted into a pass. §6.4 rule 5 now says that its 2¹⁰²⁰ condition is the twin's domain, not DL-2's coverage. A reviewed supported domain, and the reporting of oracle failure, are recorded as DL-2 implementation-review obligations, as Review 02 recommended.<br>• **Domain not expanded:** nothing previously gated becomes gated, and nothing is converted.<br>• **Cause** (from the code): Newton starts from t = 0 with a budget of 200 iterations. Far from the ellipsoid, a + t grows by about 1.5× per step, so the budget is exhausted before convergence. The approximate foot point then lies outside the ellipse's p-range, and √(1 − p²/a²) receives a negative argument | `i34a_minor.out` F3:<br>• first exception at k = 139, 140, 143, 143 and 141 on the five off-axis rays; every larger k raises;<br>• the twin's intermediates are finite at every raising point;<br>• `witness_geodetic` raises `ValueError` at (2¹⁰²⁰,)³ and returns no verdict. Review 02 `boundaries.out` and the implementer's `implementer_r02_repro.out` had reproduced the (2¹⁰²⁰,)³ case |

## 2. R2-F4 fingerprint fields (investigation only, I-34A §3)
1. **Which fields are empty:** the reviewer's rerun has `[O] brand`, `[P] features` and `[P] leaf7 features` empty. These are 3 of 44 fields; the other 41 are identical (`i34a_fingerprint_check.out`).
2. **Does the referenced evidence exist:** yes.
   - The committed I-33 `f4_fingerprint.out` is in commit `5f96119`, and its `SHA256SUMS` verifies 18/18.
   - The reviewer's `reviewer_f4_fingerprint.out` is in `3bb3637`, and its manifest verifies 12/12.
3. **Identity and provenance:** independently verified on the original host.
   - Reading `sysctl -n machdep.cpu.brand_string`, `machdep.cpu.features` and `machdep.cpu.leaf7_features` returns exit status 0 each time. The values are **equal** to the committed ones.
   - The empty values come from the I-33 `run()` helper. It keeps stdout and discards the exit status, so a failing `sysctl` is recorded as an observed `''`: a failing query gives rc = 1 with stderr, and `run()` records `''`.
   - That the reviewer's sandbox `sysctl` failed this way is **inferred**. The reviewer's run recorded no exit status or stderr.
4. **Effect on reproducibility and conclusions:** none on any numerical result or review conclusion.
   - All six numerical outputs reproduced byte-identically in Review 02.
   - The CPU fields identify the host and do not enter any computation.
   - The I-33 claim of a byte-identical rerun stands for the implementer's unrestricted environment, and remains qualified by R2-F4 for restricted environments.

**Proposed minimal correction (NOT applied; for owner decision).** In the DL-5 record (§7.1) and any future fingerprint script, a probe whose command exits non-zero, or returns nothing, is recorded as `[U] unavailable (exit status, stderr)` rather than as an observed value. The committed I-33 output is left unchanged and stands with its provenance. Nothing is backfilled or regenerated.

## 3. Validation (I-34A §5)
| # | Check | Result |
|---|---|---|
| 1 | Original defective statements identified | §1, second column, with locations |
| 2 | Minimal correction and rationale | §1, third column |
| 3 | Directly affected cross-references | Searched: DL-4, §3 (iii), §6.3, RQ-6, D-6, D-8, G-T2-10 ("enforc", "execution sequence", "NumPy"); §6.4 rule 1 and §8.2 ("3 ulp", "1.77", "ulps"); DL-2 and §6.4 rule 5 ("foot point", "2¹⁰²⁰"). Each hit is corrected, defined, or already consistent. Line 431 (a NumPy component is "not a harness defect") already agrees |
| 4 | No contradiction elsewhere in the packet | D-6's "(a conformance requirement)" and "RQ-6 enforced by DL-4 alone" would conflict with the corrected §3 (iii). Both are resolved by the reading note, without editing the protected D-6 row |
| 5 | Original numerical thresholds preserved | UF, ν, α, β, the width requirements, the 32 F2 controls and every gate are unchanged. No numerical algorithm or draft code is changed |
| 6 | Reproducible evidence | Both I-34A outputs are **byte-identical** when rerun from the committed `.py.txt` copies in a fresh directory. The I-34A manifest verifies, and the I-33 (18/18) and Review 02 (12/12) manifests still verify |
| 7 | Scope | The diff touches only the packet, this record and the new evidence directory. No protected path, decision record, review record, readiness record or I-33 evidence file is touched |
| 8 | Repository checks | `git diff --check` on the correction is clean. CI runs on push |

## 4. Status
- R2-F1, R2-F2 and R2-F3 are corrected. R2-F4 is investigated, with a correction proposed and not applied.
- DL-1 … DL-4 remain drafts and unreviewed. POG accuracy gating remains **BLOCKED** (§6.7).
- No per-platform run was made.
- An independent closure review follows in a separate commit (I-34A §6).

**T2 implementation remains NOT AUTHORIZED.**
