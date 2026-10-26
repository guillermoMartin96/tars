# External Review: M3 T2 implementation authorization packet r2, Review 01

- **Reviewer/model:** Codex (codex-cli 0.162.0), session `01a17958-0157-7ff0-8b59-2d3600a60e39`. The reviewer is from a separate provider from the implementer, in a fresh session with no earlier review context.
- **Date:** 2026-10-26
- **Reviewed revision:** `0e37db60eed706e041666b40abb5238609a83360` (`git diff 0a9c040..0e37db6`, all under `docs/`), on branch `milestone-3-t2-authorization`. `main` = `0a9c040`.
- **Under review:** `docs/milestones/M3-T2-implementation-authorization-packet.md` (packet r2), its cited decision records, and the I-31 evidence `docs/reviews/raw/M3-T2-authorization-I31-evidence/`.
- **Authorization:** I-32 (owner/Tech Lead, 2026-10-26). A review only: no T2 implementation, no change to scientific decisions, and no approval of D-0 … D-8.
- **Preconditions (I-32 §2), checked by the implementer before the review:**

  | # | Check | Result |
  |---|---|---|
  | 1 | Branch, HEAD, remote sync, clean worktree | `origin/milestone-3-t2-authorization` = local HEAD = `0e37db6`; worktree clean |
  | 2 | `0a9c040` is the merged reconciliation baseline | `origin/main` = `0a9c040`, an ancestor of `0e37db6` |
  | 3 | CI green at `0e37db6` | Run `40357794361`: all four jobs succeeded (`check` on ubuntu-latest, macos-latest and macos-15-intel; `m2-cross-platform`) |
  | 4 | Research-evidence checksums | All 7 I-31 `SHA256SUMS` entries verify |
  | 5 | No protected path changed | `0a9c040..0e37db6` changes 10 files, all under `docs/` |

- **Raw records:**
  - `docs/reviews/raw/M3-T2-packet-r2-codex-review01-prompt.md`: the prompt, with I-32 verbatim;
  - `docs/reviews/raw/M3-T2-packet-r2-codex-review01.md`: the reviewer's final message, verbatim;
  - `docs/reviews/raw/M3-T2-packet-r2-codex-review01-evidence/`, containing:
    - the reviewer's five scripts (`*.py.txt`) and their outputs (`*.out`);
    - `reviewer_review.md` and `reviewer_findings.json`, the longer review and the structured register that the reviewer wrote to its scratch directory, verbatim;
    - `reviewer_SHA256SUMS`, the reviewer's manifest, verbatim. Its paths say `review_scratch/` and `.py`, not this directory and `.py.txt`; the hashes match;
    - `implementer_rerun.txt`: the implementer's rerun of all five scripts in the same pinned clone, each output byte-identical to the reviewer's;
    - `SHA256SUMS`, covering this directory.
  - Not committed: the JSONL event stream (sha256 `b26a3fd93447fb04682f401e5e62fe83675998cd307cec7be268d00a31b04f4c`; it holds about 750 KB of tool output) and stderr, which was empty.
- **Extra reviewer input:** CPython v3.12.15 `Modules/mathmodule.c`, downloaded by the implementer from the URL the I-31 README cites and passed read-only through `--add-dir`. Its sha256 `436a01da…98281` matches the packet, and the reviewer verified it independently. The file is not committed, as at I-31.
- **How it was run:**
  - a fresh clone pinned at the full SHA;
  - `uv sync --locked`;
  - `review_scratch/` excluded from git;
  - `codex exec -C snap -s workspace-write --add-dir <inputs> --json -o codex_last_message.md -`;
  - no network.

  The wrapper on this host reports `--dangerously-bypass-hook-trust` as enabled. This invocation did not pass that flag, and the flag does not change the sandbox. The tracked tree was clean afterwards (0 entries in `git status --porcelain`), with HEAD unchanged.

## Summary
**`VERDICT: REQUEST_CHANGES`.** 0 BLOCKER, **3 MAJOR**, 2 MINOR, 1 NOTE.

The reviewer judges POG scientifically plausible for explicitly fixed finite executions. However, as written, its trace-completeness requirement, one mandated negative control and the D-4 sensitivity rationale do not hold. The error budget reproduces. The supplied CPython source supports the `hypot` evenness argument (D-3).

## Findings register and dispositions
Locations are in `docs/milestones/M3-T2-implementation-authorization-packet.md` unless stated otherwise. **Each disposition is the implementer's evaluation.** No correction has been made. Corrections need separate authorization (I-32 §7).

| ID | Severity | Location | Finding | Implementer's check | Disposition |
|---|---|---|---|---|---|
| M3T2P2-R1-F1 | MAJOR | :155 (§6.4 rule 4); also :67 (DL-3), :81 (§3 testability) | Matching call names, counts, arguments, results and order do not show that the traced results are the values the computation **used**. A mutant keeps the whole observed trace (8 calls) but uses an untraced cosine, and its height is off by 64.98 m | Read the mutant (`independent_checks.py.txt` lines 100–118). It replaces `math.cos(lat)` with `(math.cos(lat), hidden_cos(lat))[1]`: the traced call still happens, but its result is discarded. Rerun byte-identical. The packet's premise-to-conclusion step ("E1 applies by derivation") needs the observed values to be the ones in the data flow, and the count check alone does not establish that | **ACCEPTED.** DL-3, D-1 and D-6 need a data-flow requirement (an audited inventory of primitives and their uses, plus trace-masking mutants) in addition to counts. The accuracy gate and DL-4 still catch this particular mutant, but they are not what POG's justification rests on |
| M3T2P2-R1-F2 | MAJOR | :240 (§8.2 POG harness); :255 (§8.3) | A 3-ulp perturbation need not violate A-FP-2 (2·2⁻⁵² relative). The mandated negative control can therefore reject a correct checker | Checked by hand: sin(1) ≈ 0.841 lies in [0.5, 1), where ulp = 2⁻⁵³. Three ulps = 1.5·2⁻⁵² absolute = 1.78·2⁻⁵² relative, which is below 2. The reviewer's 1.773 reproduces | **ACCEPTED.** The negative control has to inject an error proved to lie outside L (with δ); a 3-ulp positive control that is admissible should be added. A-FP-2 itself is unchanged |
| M3T2P2-R1-F3 | MAJOR | :176 (§6.6 "why this is not tautological") | The claim that a defect in band selection, exponent grouping or km conversion "breaks the conclusion" is false. A doubled scale height keeps both the observed `exp` order and the decreasing density, while changing ρ materially | Rerun reproduces it (1.2166 vs 1.2082 at h = 100 m; monotonic either way). Monotonicity is preserved by any positive rescaling of the exponent | **ACCEPTED.** Correct the rationale in §6.6/D-4, list the survivors and name their killers (U-11 … U-16 value rows, DL-4). D-4's local pairwise conclusion stays valid |
| M3T2P2-R1-F4 | MINOR | :69 (DL-5); :215 (RQ-4); :335 (D-5) | The patch version and the DL-5 fingerprint do not identify the numerical environment: compiler configuration, interpreter build, linked libm and CPU dispatch are missing. `platform.libc_ver()` is empty on macOS | `independent_checks.out` shows `('', '')` for libc_ver and a cross-compiled python-build-standalone CONFIG_ARGS string, with `-O3` and LTO | **ACCEPTED.** Extend DL-5 and keep source-version invalidation (DL-7) separate from libm drift. POG is re-observed on every run regardless. The reviewer requires no CI or runtime migration |
| M3T2P2-R1-F5 | NOTE | :68 (DL-4); :251; :338 (D-8) | Bitwise agreement between the component and its twin is conformance evidence, not correctness. A shared faulty `math` gives identical bits with a 64.98 m error | Rerun reproduces it. The packet already pairs DL-4 with accuracy rows, but says this nowhere | **ACCEPTED** (clarification). State that DL-4 compares both h and φ and does not stand in for accuracy, and that accuracy does not stand in for conformance |
| M3T2P2-R1-F6 | MINOR | :154 (§6.4 rule 3, "the probe did"); `M3-T2-authorization-I31-evidence/premise_probe.py.txt:70` | The probe's `err ≤ ulp(out)/2` predicate does not establish correct rounding at a binade boundary: for sqrt(nextdown(1)), the wrong output 1.0 passes it | Checked by hand: √(1 − 2⁻⁵³) ≈ 1 − 2⁻⁵⁴ − 2⁻¹⁰⁹. Its distance to 1.0 is just above 2⁻⁵⁴, which is below ulp(1.0)/2 = 2⁻⁵³, so the predicate passes; the nearest double is nextdown(1). The host's `math.sqrt` returns the correct value | **ACCEPTED.** Qualify §6.4 rule 3's "the probe did". The I-31 evidence stays unchanged, since raw evidence is not edited |

**Other reviewer observations, not numbered findings, recorded for the correction pass:**
- **Strict E1 certification.** The §6.4 rule 6 gate is an outer comparison enclosure. A pass at equality can exceed strict E1 at the unknown true height by up to 2(1 + α)δ_O, about 1.78e-14 m at the proposed maximum δ_O. The reviewer gives a sufficient strict certificate:
  - |ĥ − h_ref| + δ_O ≤ ε_h(max(0, h_ref − δ_O)),
  - on an exterior interval that is independently certified.

  The packet should say which semantics it intends.
- **No overflow.** E1 has no 2000 km upper limit, but it does need no overflow. T0 returns h = ∞ for the finite input (DBL_MAX, DBL_MAX, 0).
- **Oracle zeros.** Rule 1's "δ ≤ 2⁻¹⁰⁰·|r|" forces δ = 0 at r = 0, so exact zeros need explicit treatment. "Never the limiting factor" cannot hold literally when the error band straddles a decision boundary.
- **Display rounding.** α and β must be the unrounded `rounding_allowances()` values, not the displayed 1.22e-15 and 8.9e-9 m.
- **Rust.** The statement "pinning one software libm gives cross-platform bit reproducibility" (§13 item 2) needs target, compiler and FMA qualifications. The web-sourced Rust, Ferrocene and arXiv claims could not be verified offline.

## Independently reproduced numerical results (reviewer; implementer rerun byte-identical)
| Quantity | Value |
|---|---|
| α | 1.2212453270876738e-15 (dimensionless) |
| β | 8.877691069434736e-9 m |
| ε_h(120 km) | 9.024240508685258e-9 m |
| ε_h(2000 km) | 1.1320181723610084e-8 m |
| Worst \|ĥ − h_true\| | 1.9198142883865285e-9 m at h = 145.03 m. That point's own ε_h is 8.877868e-9 m, giving a ratio of **0.216247**. The largest error and the largest ratio occur at the same point. **This is an empirical maximum, not a bound** |
| I-31 probes | 631 points, 11 867 calls, 0 premise violations, 0 ε_h failures. All three outputs byte-identical to the committed I-31 evidence |
| Instrumented vs plain | 0 bit differences in (φ, h) over the probe points. This is local evidence of instrumentation neutrality, not proof |
| Truncation mutants vs DL-4-style bit comparison | 2 iterations: φ differs at 566 points and h at 296. 3 iterations: φ at 453 and h at 250 |
| hypot | 2 × 10⁶ pairs plus 225 adversarial pairs: 0 evenness and 0 swap failures. These are samples, not proof of swap symmetry |

## POG scientific validity (reviewer's assessment, summarized)
- **J-FP2 (ii)** allows "an exhaustive check over the input domain the bound is used on". A fixed finite set can be exhausted, so finite-domain POG is admissible in principle. It covers only the recorded executions: no altitude interval, no production inputs and no library guarantee. **D-1 is not approved.**
- **Proxy coverage.** A `math`-attribute proxy cannot see C-internal operations, operators or `float.__pow__`. That is not fatal by itself: checking `hypot` against exact √(x² + y²) covers the aggregate contract E1 uses. Hidden substitute operations still have to be excluded by reviewed source and data-flow evidence (F1).
- **Oracle bounds.** Rigorous O-1 and O-2 bounds are feasible but do not exist yet. Decimal stagnation and an unbounded Newton correction are not enough. Ambiguous exterior/interior classification must fail closed.
- **Per-platform observation.** Each platform must observe its own execution, because library differences change later arguments and iteration counts.
- **No accuracy row is ready for promotion.**

## D-0 … D-8 (reviewer's recommendations; not owner decisions)
| ID | Reviewer | Remaining blocker (reviewer) |
|---|---|---|
| D-0 | APPROVE | None |
| D-1 | **REVISE** | F1/F2 corrections; DL-1 … DL-3 bounded and reviewed; full E1 hypothesis inventory; per-platform observation; later owner promotion |
| D-2 | REVISE | Deliverables not yet written; DL-3/DL-5 inherit F1/F4 |
| D-3 | APPROVE | Build and version provenance (D-5/DL-7); guard equivariance; no swap proof |
| D-4 | **REVISE** | F3; no universal monotonicity or swap justification |
| D-5 | REVISE (prefer (b)) | F4: provenance incomplete; no migration |
| D-6 | REVISE | F1: data-flow audit and masking mutants |
| D-7 | APPROVE | O-2 bound and exterior certificate; promotion separate |
| D-8 | APPROVE | Twin and kill matrix comparing both h and φ, still to be written |

Full justification, evidence, dependencies and consequences for each decision are in the raw output §3 F.

## Scope, traceability and Rust (reviewer)
- **Scope and traceability: preserved.**
  - DR-0024 … DR-0029 and ADR-0009 remain authoritative.
  - T3, T4 and T5 are excluded.
  - P6 and P6(b) remain unresolved, and X-1 remains unauthorized.
  - No threshold is introduced.
  - Implementation completion on the unconditional gates stays separate from scientific acceptance of geodetic accuracy.
- **Rust:** exploratory. Consistent with RES-0001 and ADR-0008 (`2d6d7e5`), TL-6 and TL-9; no migration authorized or required.

## Required corrections or additional research (for a separately authorized pass)
1. F1: replace count-based trace completeness with a data-flow requirement (D-1, D-6, DL-3), and add trace-masking mutants.
2. F2: make the negative control a proved premise violation, and add an admissible 3-ulp positive control.
3. F3: correct the D-4 sensitivity rationale, and name the killers of the surviving defects.
4. F4: extend DL-5 provenance, and separate DL-7 source invalidation from libm drift.
5. F5: clarify what DL-4 and the accuracy rows each establish.
6. F6: qualify the `sqrt` statement in §6.4 rule 3.
7. The unnumbered observations above: gate semantics (outer vs strict), the no-overflow domain, oracle zeros, unrounded constants and the Rust wording.
8. Unchanged prerequisites for any A-FP-2 gate: the DL-1/DL-2 derivations with independent review.

## Proof gate
- [ ] All Critical findings resolved: none raised (no BLOCKER)
- [ ] **All High findings resolved: NO.** F1, F2 and F3 (MAJOR) are ACCEPTED and not yet corrected
- [x] Every substantive finding has an explicit disposition: F1–F6 ACCEPTED
- [ ] Accepted fixes re-tested: not applicable until corrections are authorized
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: A-FP-2 rows remain report-only; P6's geodetic-drag item remains ESCALATED_FOR_INVESTIGATION

**Review gate result: REQUEST_CHANGES.** Packet r2 is not yet suitable for owner decision review on D-1, D-2, D-4, D-5 and D-6. **This review approves no decision, promotes no row and authorizes no implementation or correction pass.**

**T2 implementation remains NOT AUTHORIZED.**
