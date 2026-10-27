VERDICT: PASS

## Summary

Reviewed commit `8abfae249a58042370e4ac8c71cf13b5de7f6ef6` against baseline `3bb363783e8a12f034876c23e713f15d3a202c23`.

**R2-F1, R2-F2 and R2-F3 are RESOLVED.** Their corrected substantive statements are technically defensible. Previously closed readiness findings remain closed. No BLOCKER or MAJOR finding remains.

**One new MINOR and one NOTE remain**, concerning the correction record’s fingerprint field count and Newton explanation notation. Neither changes a classification, conclusion or gate.

This PASS authorizes no T2 implementation, numerical gate, decision or merge. DL-1 … DL-4 remain drafts; POG accuracy gating remains BLOCKED.

## Findings

Locations below are relative to `docs/`.

| ID | Severity | Location (file:line) | Finding | Evidence | Recommended disposition |
|---|---|---|---|---|---|
| M3T2P2-R3-F1 | MINOR | `reviews/M3-T2-packet-r2-review-02-corrections.md:34`; `reviews/raw/M3-T2-packet-r2-I34A-evidence/i34a_fingerprint_check.py.txt:25` | “3 of 44 fields; the other 41” counts flattened bare keys, losing repeated keys from different JSON sections. There are **47 path-qualified fields: 3 differ and 44 agree**. | My `provenance.py` recursively preserves section paths. The implementer’s `fields()` overwrites repeated leaf names. The independently identified differences are still exactly the three CPU fields. | Record the correct count and use path-qualified keys in any authorized future comparison. Preserve historical evidence. |
| M3T2P2-R3-F2 | NOTE | `reviews/M3-T2-packet-r2-review-02-corrections.md:31` | The Newton explanation says “a + t”; the implemented denominators are **a² + t** and **b² + t**. The stated budget-exhaustion mechanism is otherwise supported. | `_foot_point` source; scratch-only budget experiment in `additional.out`. | Correct the notation in a future authorized documentation pass. No algorithm change is indicated. |

## Review 02 resolution

| Item | Resolution | Independent assessment |
|---|---|---|
| R2-F1 | **RESOLVED** | Output equality cannot establish internal operations or NumPy absence. My independently constructed component with different internal operations returned identical bits; a NumPy-cos variant matched at **100/100** independently selected points. DL-4, §3(iii), §6.3 and RQ-6 now distinguish output comparison from source inspection. The explicit reading note resolves the preserved D-6 wording. No operative packet statement still attributes internal enforcement to DL-4. |
| R2-F2 | **RESOLVED** | The allowance follows algebraically from unchanged A-FP-2. Both reported cases pass, the boundary is inclusive, the corollary is correct in its positive-binade context, and the starting error is accounted for. My **81,840 signed displacements** agreed with the checker. The original 32 controls reran byte-identically. |
| R2-F3 | **RESOLVED** | An exactly on-surface construction and nonzero support direction are necessary qualifications. The huge-point and origin exceptions reproduce. The twin can remain finite while DL-2 raises. The witness propagates the exception without returning a verdict. Coverage remains explicitly unestablished, and sampled rays are not represented as a supported-domain bound. |

For R2-F2, independently dividing the original allowance by the defined spacing gives

\[
\frac{2^{-51}|f|+2^{-1073}}{2^{e'-52}}
=
\frac{2|f|}{2^{e'}}+2^{-1021-e'}.
\]

Thus the comparison is **\(k\le A(f)\)**:

- At \(f=1.5\), \(A=3+2^{-1021}\): three ulps pass.
- At \(f=2^{-1022}\), \(A=4\): three and four ulps pass; five fail.
- Immediately below \(1.5\,2^e\), the relative term falls short of three by \(2^{-51}\). The absolute term exactly compensates at \(e=-970\), but is smaller for every \(e\ge-969\). Monotonicity within the binade establishes the stated corollary for positive representable \(f\).
- An independent 150-digit Decimal Taylor calculation gives **2.983995602203121 ulps** for the displacement from exact sin(1) after three nextafter steps from its rounded library value.

For R2-F3, the independently observed first failing exponents were **139, 140, 143, 143 and 141**, matching the recorded rays. At `(2**1020,)*3`, the twin’s intermediates are finite but the oracle raises `ValueError`; the origin raises `ZeroDivisionError`.

Source inspection explains the cause: far from convergence, the dominant Newton equation behaves approximately as \(C/u^2-1\), producing \(u_{\text{next}}\approx1.5u\). Two hundred steps can be insufficient. A **scratch-only** change to 2,000 iterations produced in-range approximate coordinates at exponents 139, 143 and 1020. This corroborates the diagnosis; it is not a proposed implementation correction or coverage proof.

### R2-F4 provenance

The original fingerprint files exist and are byte-identical to their historical versions at `5f96119` and `3bb3637`. Their manifests verify.

A path-preserving comparison independently confirms that **only CPU brand, features and leaf7 features differ**. The count discrepancy is R3-F1 above.

This sandbox returns status **1**, empty stdout and `Operation not permitted` for all three CPU queries. Those values are **unavailable**, not observed empty CPU identities. Consequently, I could not reproduce the implementer’s successful original-host reads.

The helper demonstrably discards command exit status and retains stdout. Its explanation for Review 02’s empty values is plausible and correctly identified as **inferred**, since that historical run retained neither status nor stderr.

The six numerical reruns reported by Review 02 are supported by its preserved run output. CPU metadata does not enter the numerical calculations. The proposed unavailable-field correction remains **proposed only**; no original fingerprint, script or DL-5 record was backfilled.

## Readiness findings

All three remain closed:

- **M3T2R-R2-F1:** exact z-reflection remains diagnostic/report-only; the bounded comparison remains separately qualified.
- **M3T2R-R2-F2:** U-13 uses E3 only as an upper enclosure. PM-4(b) strict decrease remains report-only pending derivation, review and authorization.
- **M3T2R-R2-F3:** DR-0029 P4 item 8 retains “smallest-magnitude,” the original trap interval and metres-first guard.

The strategy, decision packet and readiness review records are untouched by I-34A. The correction introduces no contradiction with these closures.

## Scope check

The diff contains **eight files, all under `docs/`**: the packet, correction record and new I-34A evidence.

No production code, numerical algorithm, protected path, decision record, prior review record or I-33 evidence changed. Numerical thresholds, constants, premise predicates and existing controls are unchanged.

The added DL-2 supported-domain and failure-reporting review obligation is explicitly disclosed. No acceptance requirement is loosened. D-0 … D-8 remain proposed; P6/P6(b), X-1 and the named floating-point assumptions are not presented as approved. Report-only checks remain distinct from gates.

`git diff --check 3bb3637..8abfae2` exits **0**.

## Contradictions

No new substantive contradiction found.

The preserved D-6 enforcement wording would conflict if read alone, but the immediately following reading note explicitly corrects its interpretation. The older I-33 three-ulp statement is preserved as historical raw evidence and explicitly superseded.

## Own computations and preserved files

Commands executed:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/independent.py > review_scratch/independent.out

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/i34a_minor.py "$PWD/docs/science/experiments/m3-t0" > review_scratch/i34a_minor.out

.venv/bin/python -I review_scratch/i34a_fingerprint_check.py \
  docs/reviews/raw/M3-T2-packet-r2-I33-evidence/f4_fingerprint.out \
  docs/reviews/raw/M3-T2-packet-r2-codex-review02-evidence/reviewer_f4_fingerprint.out \
  > review_scratch/i34a_fingerprint_check.out

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/additional.py > review_scratch/additional.out

.venv/bin/python -I review_scratch/provenance.py > review_scratch/provenance.out
```

Principal outputs:

```text
independent signed displacements agree: 81840
independent NumPy-cos output matches 100 /100
f2_premise_controls byte identical True controls 32
i34a_minor byte identical True
i34a_fingerprint_check byte identical False
path-qualified fields 47; differences 3
I-34A manifest: 5/5 verified
I-33 manifest: 18/18 verified
Review 02 manifest: 12/12 verified
correction diff check rc 0
tracked status clean
```

The numerical I-34A rerun independently reproduces **8,190/8,190** allowance comparisons and **36,855/36,855** representable displacements, with **4,095** skipped non-binary64 displacements. The fingerprint output difference is the sandbox restriction described above.

`review_scratch/` contains these `.py` / `.out` pairs:

- `independent`
- `additional`
- `provenance`
- `i34a_minor`
- `i34a_fingerprint_check`
- `f2_premise_controls`
- `pog_lib`
- `witness`

The last two outputs identify their use as unchanged imported helpers. Scratch also contains `__pycache__/`.

## Limitations

Single-host, offline review. CI, remote state and historical prerequisite checks were not independently authenticated. Successful unrestricted CPU queries could not be reproduced in this sandbox. I did not rerun all six historical I-33 numerical programs; their prior rerun record was inspected and checksummed. No M1/M2 proof scripts ran.

Samples do not establish universal oracle coverage or library guarantees. Required deliverable reviews, platform evidence and owner decisions remain outstanding.

Final HEAD is the pinned `8abfae249a58042370e4ac8c71cf13b5de7f6ef6`; the tracked tree is clean. **One MINOR and one NOTE remain; all three Review 02 MINOR findings are resolved.**