**M3 T0 Review 04**

The correction covers the known density-boundary counterexamples and substantially improves the oracle and checks. One verified MINOR defect remains: the corrected drag envelope omits underflow error over its declared, unbounded exterior domain. T0 remains BLOCKED.

Reviewed detached HEAD `44260efd29a4c3ff464542f88bccb46010201ec4`, matching local and origin `milestone-3-t0-reference-spike`. The correction commits are `489d4e7` and `44260ef`. The prompt's `44260ef3` is an invalid prefix; the intended commit is unambiguous from the branch and history. Initial tracked status was clean. Both requested diffs were generated using `HEAD` after the literal longer prefix failed. The correction changes 22 files; the complete T0 diff changes only `docs/`. No production code, dependency, approved constant, table, frame, threshold, golden, reference, contract or M1/M2 validation semantics changed. These are my git and file checks.

**M3T0-R4-F1 — MINOR — the floating-point drag enclosure drops underflow errors that violate its bound. VERIFIED.**

References: `docs/science/experiments/m3-t0/t0_termination.py:446–457` (arithmetic/domain assumptions), `:567–571` (density/drag factors), `:640–675` (global envelope); `t0_model.py:118` and `:288` (density and drag arithmetic). The affected guarantee is repeated in DR-0029 P1/P4, VAL-0019, the T0 report, decision matrix and Review 03 correction section.

IEEE round-to-nearest does not imply `fl(x op y) = (x op y)(1+δ)`, `|δ|≤u`, for subnormal results. The derivation explicitly discards their absolute errors as negligible. They are not negligible relative to this envelope, which also tends toward zero. The declared domain excludes overflow, but does not exclude underflow or impose an upper height.

A reproducible state uses the unchanged V1 vehicle and full J2-plus-drag configuration:

```text
r = [197059137.0, 0.0, 0.0] m
v = [0.0, 0.0, 0.0] m/s
mass = 850.0 kg; Cd = 2.2; area = 15.0 m²
L = 190681000.0 m; s = 0.0 m/s
B = 25.757575757575758 kg/m²
```

The true height is exactly `r_x − a = L`, independently of either committed oracle. The computed height equals it. Two-body energy is `−2022745.2929523385 J/kg`, so this is a bound state. All intermediates remain finite. Gravity and J2 have zero y component, allowing the drag magnitude to be measured directly from that component without subtraction or an underflowing binary64 squared norm.

My execution gives:

```text
computed density       = 1.3e-322 kg/m³
exact decimal density  = 1.26316923236358804936…e-322 kg/m³
model drag magnitude   = 1.02021454616158465868…e-315 m/s²
drag_envelope(L, s, B)  = 5.06321922436317430373…e-316 m/s²
model / envelope       = 2.0149523474166813…
```

The exp result is normal (`4.184065029359216e-308`), with measured relative error `1.64e-17`, within A-FP-2. The defect arises in subsequent subnormal density/coefficient arithmetic. It cannot be dismissed as libm exceeding the unresolved assumption. Treating the invalid relative-error identity itself as an extra premise would exclude this state implicitly, contradicting the documented IEEE/no-overflow domain.

Reproduction: `.venv/bin/python -m pytest -q -p no:cacheprovider review_scratch/test_underflow.py` fails its envelope assertion. `independent.py` also scans the top band and reproduces the violation. The committed 92 checks all pass, demonstrating this coverage gap.

Recommended correction: carry absolute underflow terms through density and drag, propagate them into a conservative envelope, and justify the resulting supremum and stage argument over the existing domain. Add high-altitude underflow regressions using component or high-precision norms. Update the affected records and recompute the floors. Do not silently narrow the domain or change the approved atmosphere/physics. If a rigorous enclosure cannot be established, withdraw the affected guarantee and keep it blocked.

The force here is physically tiny. This finding disproves the global envelope lemma; it does **not** demonstrate an RK4 stage below zero at a published floor, or establish that those numerical floors must change.

**Resolution table**

| Item | Disposition | Evidence |
|---|---|---|
| M3T0-R3-F1 | PARTIALLY RESOLVED | Known 120/200/250 km and all 12 downward-jump cases are covered; independent oracle and selection-height widening are present. The replacement global computed-force guarantee remains invalid through R4-F1. |
| M3T0-R2-F1 | RESOLVED | Own checks/rerun confirm perturbed values are sampled estimates, not certified bounds; between-sample refinement exceeds sampling. Uses needing a perturbed bound remain blocked. |
| M3T0-R2-F2 | PARTIALLY RESOLVED | Radius-product correction and original 80 km counterexample pass; the global envelope used by the sufficient-condition proof still fails through R4-F1. |
| M3T0-R2-F3 | RESOLVED | Own zeroed-evidence mutant fails 22 selected checks; coverage, recomputation, units and provenance protections exist. This resolves the original vacuous-evidence defect. |
| IM-1 | RESOLVED | Own byte-identical rerun reproduces 0.9856650955520649 m RMS. Quantity, data, frames, units, 60 s sampling and RMS procedure are documented; no threshold is approved. |
| M3T0-F1 | RESOLVED | Chord/curvature argument remains valid; two-body bound checks and experiment rerun pass; perturbed estimates are explicitly separated. |
| M3T0-F2 | PARTIALLY RESOLVED | Thresholds, speed bound, admissible failing-stage example and same-tick semantics reproduce. The replacement sufficient-condition proof depends on the defective global force enclosure. |
| M3T0-F3 | RESOLVED | Own rerun gives k2/k3/k4 offsets +116.312773/−115.734153/+1.161267 m; records identify k3. |
| M3T0-F4 | RESOLVED | GMAT rerun reproduces the corrected 6.95e-6 m quotation, below the unchanged 1e-4 m gate. |
| M3T0-F5 | RESOLVED | Record inspection confirms the owner's gate controls: P10 before T1, P1–P10 before T2. The narrower technical dependency map remains explicitly subordinate. |

**Mathematical and numerical assessment**

For exact arithmetic, the support function is `S(λ)=a√(1−e²sin²λ)`. An exterior point satisfies `r=q+h n(φ)`, giving `H(φ)=h`, `H′(φ)=0`. Since `S+S″=M`, differentiation yields `H″=−H−M`. Taylor's theorem gives the stated second-order latitude penalty. The moving-axis-point argument bounds the fixed-point derivative by `Q′/(b−Q)`; the rounded-iteration recurrence and stopping rule give the documented contraction tail. The final height calculation appropriately uses an absolute error bound across the cancellation, rather than a relative error in the small height.

I found no counterexample to ε_h. The constants recompute in the second implementation; my additional 1,200 log-height samples, extending to approximately 1e9 m, use a separate high-precision latitude iteration and stay within 0.191 of ε_h. That calculation reuses the evidence script's decimal trigonometric primitives, so it is independent of the foot-point oracle but not an independent libm-reference implementation. The committed evidence reruns byte for byte: maximum observed height error `2.0564148063e-9 m`, maximum error/bound `0.2166677265`, over 13,050 points. These samples corroborate the derivation; they do not prove its global domain.

A-FP-2 is honestly labelled an unresolved platform assumption. The host measurement reproduces cos at 1.4132 ulp and 0.9361 units of `2^-52` relative; choosing 2 units is not presented as a measured global theorem. The measurement samples exp only between −50 and 0 and does not establish underflow behaviour. A-FP-1's unrestricted relative-error interpretation is the concrete failure identified above. Subnormal errors being far below β in the height calculation does not justify dropping them from the much smaller drag bound.

For the real-valued widened expression, the kilometre-selection allowance and inverse height-to-radius inequality are consistent. Its in-band logarithmic derivative is negative for every pinned scale height. Thus the lower endpoint and subsequent band bases cover upward and downward jumps, including the exact-base band-above rule. This proves the candidate set for that expression, but R4-F1 shows it does not enclose every binary64 force evaluation in the unbounded top band. Decimal padding and final upward conversion cannot repair an omitted model-rounding term.

My 166 additional equatorial checks cover every table base and adjacent binary64 values, including the lower edge, upward jumps and top base; they pass. The full committed checks cover the off-equator crossing cases, near-escape, retrograde and straight-down stages, polar/low points and agreement of the foot-point and Vermeille oracles. All pass. No below-zero stage at the published floors was observed.

The computed-height convention, `H0=(h0−β)/(1+α)`, stage displacement inequalities and requirement `M_k>0` correctly address the lower edge. Monotonicity of the symbolic recurrence follows from the envelope's height/speed monotonicities and the positive coefficient `1/(1+α)−u/(1−α)`. The gravity factors and second-implementation calculations reproduce the stored values. The proof for the implemented force nevertheless needs a valid force envelope over its entire declared domain.

The published bracket ends reproduce:

- B25.8: old `124456.68544482533 m`; new `124456.68544510857 m`.
- B100: old `118633.50894609134 m`; new `118633.50894662621 m`.
- Drag-free: old `111511.96182423369 m`; new `111511.96182508787 m`.

My refined second-implementation root brackets are approximately `124456.68544484396…`, `118633.50894610998…` and `111511.96182425225… m`. The published ends satisfy the outward condition, with needs about `−7.17e-7`, `−1.00e-6` and `−8.43e-7 m`. Their bracket-end shifts agree with the records; all quoted two-decimal floors and the P1 recommendation remain unchanged. These reproduce the proposed recurrence, not a repaired global proof.

`t0_oracle.py` uses Newton on the foot-point Lagrange parameter and separately reads decimal table values. It imports constants, the table path and digest helper from the model, but shares no height or band-selection implementation. The Review 02 expected height now comes from this oracle. Its remaining `min(low,true_h)` accounts for a constructed point lying slightly below the requested lower limit and is not the former self-referential substitution. Direct boundary checks preserve the base lower limit whenever the true height qualifies.

The mutation classification requires a declared detecting check, rather than counting arbitrary provenance failures alone. My four full-check-set mutant runs reproduce the supplied failure sets: allowance ÷10 has 10 failures, allowance ×0.9 has 3, wrong exact-base band has 34, and allowance removed plus reverted Review 02 oracle has 33. In the combined case the reverted behavioural Review 02 test passes while Review 03 detects the defect. My three additional declared-check subsets detect the wrong lower limit (25 failures), model-height oracle (3) and zeroed evidence (22).

The ×0.9 mutant protects agreement with the stated derivation, not an experimentally demonstrated failure of the true-height inequality. The records disclose that distinction; it must not be promoted into behavioural evidence. The stationary-point mutant's equivalence is supported by the prior analytic argument that every interior stationary point is a minimum, not merely by its passing scan. The full supplied 25-mutant result is documentation evidence except for the seven rerun cases. None of this mutation coverage establishes the omitted underflow lemma.

**Execution ledger and evidence**

The complete command/inspection ledger is `review_scratch/command-ledger.md`; exact experiment/validator subprocess arguments, exits and timings are in `execution.json`. Reviewer programs and logs are retained beside this report. The ledger includes failed prefix lookups, scratch-file creation, inspections and progress reads. No fixes were made.

Key commands, with `.venv/bin/python` throughout:

- Explicit `pytest -q -p no:cacheprovider` on `check_review01.py`, `check_review02.py`, `check_review03.py`: **92 passed in 177.48 s** (`checks.log`).
- `review_scratch/run_evidence.py`: atmosphere, decay, geodetic, frames, regression, termination, height-error, axis-ablation and GMAT outputs reproduce committed bytes. GMAT received the absolute private `bin/GmatConsole` path.
- `toolbox/validators/m1_proof.py --out review_scratch/m1.json` and `m2_proof.py --out review_scratch/m2.json`: PASS; M2 was run without `--quick`.
- `toolbox/scripts/gmat_m1.py compare` and `gmat_m2.py compare`: PASS.
- `independent.py`, `extra_checks.py`, `test_underflow.py`: high-precision/analytic checks, digests, all-base checks, floor refinement and the failing underflow regression described above.
- `red_before.py`: reviewer case plus all 12 downward-jump cases on `c6c0fff`, with the documented alias shim: **13 failed, 29 deselected**.
- `mutations.py` and `focused_mutations.py`: seven selected mutants detected, with expected-check failures retained in their JSON/log files.
- `inspect_records.py`: result/record inventory and digest checks; prior raw reviews and prompts preserved against `c6c0fff`.

Result files inspected are all nine committed `t0_*_results.json` and all nine rerun counterparts, supplied `mutation_check_review03.json`, own `mutations.json`, `focused_mutations.json`, `m1.json`, `m2.json`, experiment hash inventories and execution JSON. The GMAT axis report is input to the reproduced ablation. `inspections.log` inventories the decision/assumption registers, prior reviews/prompts, reports, README and supplied correction logs read. Prior reviewer evidence is historical supporting material, not claimed as a new execution. The new quantitative claims, thresholds, floors, height/libm measurements, axis fit and script/table hashes checked against results reproduce; the global enclosure claim fails as above. I do not claim an independent recalculation of every historical planning number appearing in the registers.

My hashes match all five pinned values:

```text
proof/thresholds/m1.json
446e75ee8d5129a346263b5b06f873e0aed74c33fd756564e43423bbd16fdb3d
proof/thresholds/m2.json
9d4eab47133a4f9eb1125cf7242ada0c720fbe9e4b8dd12b0f698cc79e5f0ce9
toolbox/references/gmat/m2/APPROVED_DIGESTS.json
f8d6bd788eb1e305af72cad2b821b4b85b2c65ab64410059ca43299eee5ce585
toolbox/references/snapshot/m2/REFERENCE_SNAPSHOT.json.gz
a2cddf4bc4b643a164d63191578923787acbd0de8ca0a1ddbe46e1a1f241448b
proof/references/m2_final_states.json
dc3baf7abb209a11ca463b9ca5001ce886c62b92b191ac76249d32924aa951dc
```

The private console hashes to `1162803de3ed7172bce882b201b00e58de5b604c76a2ba02d16ac6765e7552e2`; its installed atmosphere table hashes to `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`. Both match the claimed installation. VAL-0019's current script/table digests also match my calculations.

**Verification limits and checkpoint**

I did not run the prohibited Proof wrappers or a fresh full 1,185-test project suite. The supplied clean-clone M1 9/9, M2 20/20 and full-suite success at `489d4e7` remain documentation-only historical claims; my independent non-quick validators, comparisons and 92 T0 checks are separate evidence. I performed one complete experimental reproduction, not the implementer's two fresh-clone runs. Seven mutants were rerun, not the complete mutation matrix. Other platforms, a global libm theorem, branch protection and external scientific-source provenance were not independently checked.

CI was inaccessible without network. The supplied successful four-job claims for `489d4e7` and `44260ef` were not independently verified. The cause of GMAT's escalated geodetic-drag discrepancy remains unresolved; its numerical discrepancy reproduces and its escalation is preserved.

Final `git status --porcelain` and `git diff --stat` are empty. Exactly zero tracked experiment files changed after regeneration; no `git checkout` restoration was necessary. Reviewer artifacts are confined to `review_scratch/`.

Scope and decision authority were preserved. DR-0029 P1–P10 and DR-0028 P6(b) remain open, with no default chosen. T0 is **not eligible for acceptance** while R4-F1 and the affected dispositions remain open. The next required authorization is a bounded correction/validation pass for R4-F1 and any subsequent independent Review 05. This review performs no fix, merge, acceptance, T1/T2 work or further review round.

VERDICT: REQUEST_CHANGES
