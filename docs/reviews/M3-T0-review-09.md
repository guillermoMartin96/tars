# M3 T0 Review 09 (independent review of the Review 08 correction pass)

**Reviewer:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a15ff0-1a90-7a03-861d-c17cde0c68e6`, 2026-10-21 19:28–19:59 UTC.
- **Sandbox:** `workspace-write`, no network.
- **Invocation:** `codex exec -C snap -s workspace-write --add-dir "<private GMAT copy>" --json -o codex_last_message.md - < M3-T0-codex-review09-prompt.md`. The CLI wrapper on this host reports that `--dangerously-bypass-hook-trust` is enabled. This invocation did not pass that flag, and it does not change the sandbox.

**Reviewed commit:** **`f04f9955d5ae714cc61144990395b8225a379968`**, the validation record of the correction commit `0254664e300c84ae1d102bcf3f930a2dd2573428`.
- **Environment.** The review ran in a fresh GitHub clone with its own `uv sync --locked` environment. It had a private GMAT R2026a copy, whose console digest (`1162803d…52e2`) and atmosphere table (`75762f67…a85e`) match the installation; the implementer checked both before the review, and the reviewer checked them again.
- **Prompt.** It was kept outside the repository during the review. It reproduces Authorization I-11 verbatim and points to the earlier prompts, which hold the earlier Tech Lead texts verbatim. It lists every earlier finding with its current disposition, presents the I-11 corrections as claims to verify, and requires the I-11 §6 items: an independent assessment of R8-F1, a regression check of every earlier finding, an evaluation of the near-surface and first-stage-infinity tests, an inspection of the M3-dropped mutant, a search for new mathematical, floating-point, verification and documentation defects and for unsupported certification claims, and an explicit verdict with finding IDs and severities. It uses the same verdict rule as Reviews 07 and 08. Every commit identifier of the pass under review is a full SHA.
- **Preconditions (I-11 §6: "only after the correction and validation pass"), checked by the implementer before the review:**
  - branch `milestone-3-t0-reference-spike`, HEAD and origin both at `f04f995`, clean tree;
  - the validation of `0254664` recorded in `f04f995` (checks 288/288; mutation 87/87 with 2 equivalents and no survivor; M1 Proof 9/9; M2 Proof 20/20; pytest 1185; five pinned and 21 spike digests; 98 files reproduced twice);
  - CI succeeded on `0254664` (run 39641717044) and `f04f995` (run 39652330844), all four jobs each.

  The reviewer had no network and states that it did not verify CI.

**Authority:** "Authorization I-11 — M3 T0 Review 08 Corrections and Independent Review 09" (Tech Lead, 2026-10-21).

**Files:**
- prompt: `raw/M3-T0-codex-review09-prompt.md`;
- raw output: `raw/M3-T0-codex-review09.md`. This is the reviewer's saved report `review_scratch/M3-T0-codex-review09.md`, which equals the CLI's final message plus a trailing newline. It contains no absolute path;
- reviewer scripts and logs: `raw/M3-T0-codex-review09-evidence/` (`*.py.txt`; `commands.jsonl` and `inspection_commands.md`, the command ledger; the reviewer's own checksum list `review_SHA256SUMS`, written by the reviewer; `reviewer-SHA256SUMS.txt`, written by the implementer over the reviewer's unredacted files). Absolute paths are redacted to `<clone>`/`<review-root>`/`<scratch>`/`<home>`/`<tmp>`. `SHA256SUMS` covers the committed files;
- the implementer's reproduction: `raw/M3-T0-codex-review09-evidence/implementer-reproduction/`.

**Omitted** as large or derivable:
- the reviewer's copies of `git diff 115e747..f04f995` (`correction.diff`) and `git diff 86df2c3..f04f995` (`full.diff`; 11 MB together);
- its copy of `t0_termination.py` at `115e747` (`termination_before.py`).

**Verdict:** **`VERDICT: PASS (unconditional)`**, with two new NOTEs. No BLOCKER, MAJOR or MINOR finding was raised, and every resolution-table item is RESOLVED. The reviewer found no false certification, no deficient force envelope and no unsafe published floor.

**Stop rule applied (I-11 §7, PASS):**
- The output is preserved, and both NOTEs are recorded with their severities. The implementer reproduced each one independently.
- The acceptance dossier is prepared: `docs/reviews/M3-T0-acceptance-dossier.md`.
- **T0 is not declared accepted.** It is not merged, and T1 and T2 are not started. The NOTEs are not corrected: I-11 authorizes no further correction, and Review 10 is not started.
- Not done:
  - DR-0029 P1–P10 and DR-0028 P6(b) not decided;
  - the GMAT geodetic-drag discrepancy not closed: it stays escalated;
  - no protected artifact, test or threshold changed.

## Resolution assessed by Review 09
| Item | Review 09 | Basis (reviewer) |
|---|---|---|
| M3T0-R8-F1 | **RESOLVED** | Re-executed the equatorial 1–9 ulp exterior rejections for B_V1 and +∞, and k = 10 → 55 993.323394842984 m. The surface, pole, β and neighbouring-float checks pass. The docstring and the appended record qualifications disclose the attainable exterior rejection and distinguish computed from mathematical height. The pole quotation's precision is R9-F2 |
| M3T0-R7-F1 | **RESOLVED** | `stage_need(1, 2^-1074)` = 55 992.318990613036, finite with A0 = +∞; path 1 returns −M2 only after A0 succeeds; every consumer certifies only on strict negativity |
| M3T0-R7-F2 | **RESOLVED** | b_R ≤ b is restricted to b > 0; b_R(0) ≈ 1.49716862376135e-325 |
| M3T0-R6-F1 | **RESOLVED** | k = 1…17 re-executed; k = 1 ratio ≈ 0.9999999999988138 |
| M3T0-R6-F2 | **RESOLVED** | Extreme-helper tests; infinite enclosures never certify; the old overflow mutant fails five cases |
| M3T0-R6-F3 | **RESOLVED** | The cap re-solved exactly: 91910196476947 accepted, the next integer rejected |
| Review 06 remark (5 287-point search) | **RESOLVED** | Still explicitly UNREPRODUCED (a provenance resolution, not a reproduction) |
| Review 06 remark (b*, φ_B) | **RESOLVED** | 7.416912861690675e-309 (stored φ) and 1.1125369292536007e-308 (exact φ) |
| M3T0-R5-F1 | **RESOLVED** | Own exact-product grids and the 17/30-unit counterexamples enclosed; the relative-only mutant fails |
| M3T0-R5-F2 | **RESOLVED** | Subset maxima 0.9527274167782528 / 0.982821819954253 and transition maxima 0.9999999999988586 / 0.9999999999988518 distinguished |
| M3T0-R4-F1 | **RESOLVED** | 1.02021455e-315 against 1.110700085e-315 m/s² at 190 681 km; the superseded-envelope mutant is detected |
| M3T0-R3-F1 | **RESOLVED** | 0.062309014504142814 against 0.06230901450421387 m/s² at 120 km; the allowance-removal mutant is detected |
| M3T0-R2-F1 | **RESOLVED** | Sampled perturbed estimates kept distinct from certified two-body bounds; no combined J2/drag missed-dip proof claimed |
| M3T0-R2-F2 | **RESOLVED** | 48.65837703993666 against 48.658377039936795 m/s² at 79 999.9/80 000 m |
| M3T0-R2-F3 | **RESOLVED** | The zeroed-evidence mutant fails 22 selected cases |
| IM-1 | **RESOLVED** | Axis ablation byte-identical twice; RMS 0.9856650955520649 m |
| IM-2 | **RESOLVED** | need(111 511.96, ∞) = +0.0018399073878806404; need(111 511.97, ∞) = −0.008245909394966729; disposition unchanged |
| M3T0-F1 … F5 | **RESOLVED** | Each re-derived or reproduced individually (F5 on documentary evidence) |
| Review 08 M3 coverage observation | **RESOLVED** | The M3-dropped mutant is detected by the first-stage-infinity check for the intended reason; R9-F1 is a narrower surviving corruption |

The GMAT geodetic-drag discrepancy remains **ESCALATED_FOR_INVESTIGATION** (DR-0029 Q-G2-1/P6). DR-0029 P1–P10 and DR-0028 P6(b) are undecided.

**Reviewer's own validation:**
- checks 01–08: 288/288; red before at `115e747`: 2 failed, 25 passed;
- full pytest: 1185 passed, 3 warnings;
- the M1 and M2 validators: PASS (M2 228/228); both GMAT compares: exit 0;
- the 14 R8 mutants, six earlier mutants and both declared equivalents (a declared subset, not the 87-mutant rerun);
- all nine experiments rerun twice, including GMAT, with all 98 tracked files byte-identical;
- five pinned and 21 spike digests, all matching; the protected-path diff and the result-file diff since `115e747`, both empty;
- the docstring-free AST of `t0_termination.py` unchanged;
- the old bytes of the Review 06, 07 and 08 records an exact prefix of the new ones;
- its own probes: 1 792 C1 and 1 601 C2 exact constructions, 598 exterior near-surface states on the E2 ellipsoid (1 095 rejections, 1 895 finite non-certifications, none certified), 226 force evaluations, 30 adversarial RK4 steps above the floors and 21 E4b boundary evaluations;
- the committed seed-20261022 probe, with every count reproduced.

## New findings
| ID | Severity | Finding | Implementer reproduction | Disposition |
|---|---|---|---|---|
| M3T0-R9-F1 | NOTE | **A finite M3 can be omitted without failing a check.** A mutant that keeps `-min(M2, M3, M4)` when M3 = −∞ but returns `-min(M2, M4)` when M3 is finite passes all 288 checks. With an injected envelope of 10^8 at the first call and 0 after it, at h0 = 200 km and b = B_V1: M2 = 144 867.2696173568, M3 = −2 499 855 380.144757 and M4 = 89 239.71048326683. The code returns need = +2 499 855 380.144757 (not certified), and the mutant returns −89 239.71048326683 (a false certification). The I-11 finite control (`test_r8_finite_injected_envelope_certifies`) always has M4 < M3, so it never makes a finite M3 the minimum (`check_review08.py:224`, `:241`, `:248`; `t0_termination.py:1385`). A test-coverage gap, not a defect in the committed code; the injected envelope is a propagation test, not a physical force | **Reproduced** (`implementer-reproduction/repro_r9f1.py.txt`, `.log`): the same five values exactly, and a second case at h0 = 1 000 km (the mutant certifies there too). The mutant (`r9f1_mutant.diff`) passes all 288 checks in a scratch copy of `docs/`, with the mutated module confirmed loaded (`r9f1_mutant.sh.txt`, `r9f1_mutant_checks.log`). With the A0 = +∞ envelope the mutant still returns +∞, which is why the I-11 regression does not see it | **ACCEPTED, not applied** (I-11 §7: no further correction is authorized) |
| M3T0-R9-F2 | NOTE | **The pole check's exact ellipsoid is not the model's.** `check_review08.py:59` takes A·(1 − F) as the exact polar radius. The height formula and `t0_oracle.py` (`:38`, `:42`) use A·√(1 − E2), with binary64 E2. These differ by 2.4767215814979376e-13 m. At z = fl(b) the mathematical height is −2.0348868076669469e-10 m on the first and −2.0373635292484448e-10 m on the second. So the quotation "−2.03e-10 m" (`t0_termination.py:1319`; `validation.md:833`; the Review 07 amendment and the Review 08 correction section) is the F-defined value; on the model's E2 ellipsoid it rounds to −2.04e-10 m. The interior classification, computed height 0, the rejection transition, the E1 enclosure and every floor are unaffected | **Reproduced** (`implementer-reproduction/repro_r9f2.py.txt`, `.log`): the same three values, and E2 = fl(F(2 − F)). Impact checked: the 37 541 states of the seed-20261022 probe (which also classifies on the F ellipsoid) classify identically on the E2 ellipsoid, 36 769 exterior in both (`r9f2_probe_reclassify.py.txt`, `.log`). The pole check's k = 0…12 outcomes cannot change, since the 2.5e-13 m difference is far below the 2^-30 m grid spacing | **ACCEPTED, not applied** (I-11 §7) |

## Implementer's assessment
- **Both findings are correct.** R9-F1 is a gap in the test I wrote for the Review 08 observation. I made the infinite case M3-dominant but chose a finite control where M3 is never the minimum, so a conditional omission survives. R9-F2 is an imprecision in a check and in a quotation I wrote: I took the F-defined polar radius as "the model's ellipsoid", while the model and the oracle use E2.
- **Neither changes a number, a floor or a certification.** The committed `stage_need` uses M3 in every case. The pole classification is unchanged on either ellipsoid.
- **Proposed correction (for authorization; none applied):**
  1. **R9-F1 (checks only):** add the reviewer's finite first-call-only envelope (10^8, then 0) at several heights, asserting need = −M3 > 0 and that `-min(M2, M4)` would certify. Add the finite-M3 omission as a mutant in the harness.
  2. **R9-F2 (check and documentation):** derive the pole expectation from A²(1 − E2) as E1 and the oracle do. Change the quotation by an appended amendment to −2.04e-10 m (E2 ellipsoid), or name the F-defined ellipsoid explicitly. Preserve the earlier wording.
  3. Rerun the checks, the mutation harness and the record checks. Neither item touches executable model or termination code.
- **The verdict rule permits PASS.** Under I-11 §7 the next steps are the acceptance dossier and the Tech Lead's decision. Whether the two NOTEs are corrected before or after acceptance is for the Tech Lead.
- **Remaining conditions (unchanged):**
  - the force and stage guarantees hold only under A-FP-1 to A-FP-3 (A-FP-2 is unresolved, and E4b depends on it explicitly);
  - the C1/C2-only scope with positive finite mass, cd and area;
  - no overflow;
  - negative two-body energy, no thrust and dt = 10 s;
  - no certified J2-plus-drag missed-dip bound;
  - host measurements on macOS x86_64 only;
  - the GMAT geodetic-drag discrepancy stays escalated;
  - DR-0029 P1–P10 and DR-0028 P6(b) are undecided.
