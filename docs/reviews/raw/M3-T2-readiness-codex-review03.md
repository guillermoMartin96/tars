VERDICT: PASS

## Summary

Reviewed pinned HEAD `628623bdb5fdaee5da4167167be914a68a1734a9`, focusing on `e769f9e..628623b`.

R2-F1, R2-F2 and R2-F3 are **RESOLVED**. No BLOCKER, MAJOR or MINOR finding remains. The new bounded symmetry comparison follows from E1 on its stated domain. Exact reflection and strict density decrease no longer gate.

This verdict assesses the planning package. It approves no decision, assumption, amendment or T2 implementation authorization.

## Findings

| ID | Severity | Location | Finding | Evidence | Proposed disposition/correction |
|---|---|---|---|---|---|
| — | — | Reviewed correction scope | No findings | Derivations and repository checks below | None |

## Assessment of items 1–7

### 1. R2-F1 — RESOLVED

Checked U-19, A-LM-1, B-11, the briefing and draft authorization against `t0_model.geodetic_iterative`.

**Quarter turns:** the narrowed A-LM-1 suffices. A quarter turn maps `(x,y,z)` to a signed permutation of `(x,y)` with `z` unchanged. These transformations are exact for finite binary64 inputs. The code uses `x,y` only in `p = hypot(x,y)`. Hypot symmetry and evenness therefore give the same `p`; every subsequent operation, convergence test and returned height receives identical operands. No sin/atan2 oddness or cos evenness is needed.

**Reflection:** mathematical ellipsoid symmetry is distinguished from computed equality. Exact z-reflection is explicitly diagnostic and report-only. A-FP-2 is not strengthened to imply library parity.

**B-11(c):** valid under its stated conditions:

- Signed permutations are exact, including at subnormal magnitudes; signed zeros represent the same geometric point.
- The model ellipsoid is rotationally symmetric about +Z and symmetric under z-reflection. Thus `h_true(σr) = h_true(r)`.
- Exterior status is preserved. Both evaluations remain within E1’s exterior, path (α), no-overflow domain.
- The triangle inequality gives `|ĥ(r) − ĥ(σr)| ≤ 2(αh + β)`.

The substitution is also valid. From E1,

```text
ĥ ≥ h − (αh + β) = (1 − α)h − β
h ≤ (ĥ + β)/(1 − α).
```

The committed constants satisfy `0 < α < 1` and `β > 0`. Since `ε_h(h) = αh + β` is increasing, evaluating it at that upper bound is conservative. The strategy requires exact-rational comparison, avoiding an inward-rounded test threshold.

### 2. R2-F2 — RESOLVED

Checked PM-4, U-13, B-9, B-10 and G-T2-2 against `rounding_allowances`.

E3 states an **upper enclosure**, with multiplicative and additive terms, at the rounded selection height. The corrected documents infer no lower enclosure from E3 or samples.

Strict decrease is reported pending a reviewed, input-height-referenced two-sided derivation and explicit authorization. U-13 gates only its upper side, conditionally on A-FP-2.

Non-increase remains justified under A-LM-2: conversion, subtraction, division and positive multiplication preserve order; negation reverses it; assumed monotone exp completes the argument within a fixed band. Equal adjacent results and the zero tail remain permitted.

### 3. R2-F3 — RESOLVED

The word diff changes the incorrect extremum description to “smallest-magnitude negative h whose quotient h/1000 is nonzero.”

Independent computation confirms:

- Exactly 500 negative binary64 values immediately below zero produce a zero quotient.
- The 501st, `−2.475e-321`, produces `−5e-324` and raises in the spike.
- Larger-magnitude inputs can produce the same quotient.

The open interval `−2.475e-321 < h_m < 0`, metres-first proposed guard, signed-zero treatment, test criteria and historical evidence are unchanged.

### 4. New numerical or logical errors

None found in the corrections.

The bounded symmetry comparison is a consequence of E1, rather than a tolerance fitted to observations. Its conditional classification and domain restrictions are consistent with U-17 and B-12.

### 5. Scientific justification of proposed gates

Rechecked §3.9 and the E rows referenced by G-T2-1 through G-T2-3a.

- **B-1:** the cross-product allowance follows from componentwise relative rounding; the power sign follows on the stated nonzero, normal-product and exact-rational margin domains.
- **B-2:** power-of-two scaling commutes with rounding through the fixed homogeneous multiplication/division sequence when intermediates remain normal and finite at both scales.
- **B-13:** exact base evaluation follows from exact integer conversions, zero exponent and A-LM-0’s directly tested special value.
- **B-14:** transition positions are reported; no-exception and zero-density/zero-drag behavior remain explicit requirements.
- **B-15:** the bracket-width comparison is valid when both estimates lie in retained brackets containing the same root of the same function. Stored estimates and residuals alone do not establish that premise; the existing Review 02 note remains applicable.
- **B-9 through B-12:** conditional portions now have appropriate derivations, named assumptions and domains.
- **B-3 through B-8:** unsupported comparisons remain reported derivation deliverables.

The other E rows are explicit interface, identity, domain, dataset, composition, determinism or atomicity requirements, with the numerical qualifications stated in the audit.

No contradictory unconditional reflection or strict-decrease gate was found in the strategy, draft authorization or decision packet. G-T2-3a requires review before a new derivation may support gating.

### 6. Previously resolved findings

Previously accepted closures remain intact:

- **Review 01 F1:** published discontinuities are tested; continuity is not required.
- **F2:** E1 remains restricted to exterior inverse evaluation; forward-construction error and negative heights remain outside that gate.
- **F4:** metres-first guard and signed-zero handling remain explicit.
- **F5:** the chord argument uses absolute continuity and an almost-everywhere second-derivative bound, rather than global C² regularity.
- **Accepted parts of F3/F6:** non-increase, zero cases, structural domains and derivation classifications remain intact.

The remaining F3/F6 gaps identified by Review 02 are closed by these corrections.

### 7. Authorization boundaries

Local checks passed:

- Exactly six correction files changed, all under `docs/`.
- Historical Review 01/02 records and raw files are unchanged.
- Authorization-packet and readiness-report prior bytes remain intact as prefixes.
- No protected path or T0 file changed.
- P1–P9 classifications are unchanged: READY P1/P2/P4/P8/P9; dependent P3/P5/P7; additional evidence P6.
- Q-GATE, DQ-1…DQ-6 and P6/X-1 remain open.
- The authorization packet remains **DRAFT — NOT AUTHORIZED**.

No tracked files were modified during this review. Final tracked tree: **CLEAN**.

## Own computations

Executed:

```text
.venv/bin/python -I review_scratch/review03.py > review_scratch/review03.out
```

The script disables bytecode writes and imports the T0 modules read-only. Results:

```text
changed_files 6 docs_only True
authorization_packet_prefix True
readiness_report_prefix True
historical_diff NONE

alpha 1.2212453270876738e-15
beta_m 8.877691069434736e-09
0 < alpha < 1 and beta > 0: True

2000 sampled exterior constructions:
quarter-turn equality failures 0
bounded symmetry failures 0
maximum reflected-height difference 0
2eps_120km 1.8048481017370517e-08

first_raise 501 -2.475e-321
trap_accepted 500
quotients [-5e-324, -5e-324, -1e-323]
signed_zero_densities [1.225, 1.225]
adjacent_density_equal True

1000 km [-1 ulp, exact, +1 ulp]:
[3.0190482489066557e-15, 3.019e-15, 3.0189999999999988e-15]

tracked_status CLEAN
```

The samples corroborate behavior on this host; the gate assessment rests on the derivations and explicit assumptions.

## Limitations

No network, remote-head, push or CI authentication was performed. Implementer baseline and remote claims were treated as supplied claims. No M1/M2 proof scripts, full T0 campaign or implementation tests were run.

A-FP-2 and A-LM assumptions remain unproved and unapproved. This review does not establish cross-platform library behavior.

No fixes, decisions, assumption approvals, implementation, commits or merges were performed.