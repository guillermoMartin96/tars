# M3 T2 decision-readiness package: corrections of Review 01 (I-24)

**Authorization:** "Authorization I-24 — M3 T2 Readiness: Review 01 Corrections and Independent Review 02" (Tech Lead, 2026-10-24). Scope: documentation only.  
**Base:** `d8270c248a00479fe715889eca4fcc8a208d8763` (branch `milestone-3-t2-decision-readiness`; `main` = `fc50aed`).  
**Findings corrected:** `docs/reviews/M3-T2-readiness-review-01.md`. That record is **unchanged**. The wording it reviewed is preserved at `5ee6a6a`.  
**Evidence:** `docs/reviews/raw/M3-T2-readiness-I24-evidence/`, holding `i24_reproduction.py.txt`, `i24_reproduction.out` and `SHA256SUMS`. The script imports the T0 spike read-only, runs with `python -I`, and writes nothing. It was written independently of the Review 01 reviewer's script.

## Baseline verification (I-24 §1)
| Check | Result |
|---|---|
| `git fetch origin`; branch | local `tars-m3-t2-readiness-853e0447`, tracking `origin/milestone-3-t2-decision-readiness` |
| HEAD = remote | `d8270c2` = `d8270c2` |
| `origin/main` | `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942` |
| Working tree | clean |
| Existing changes docs-only | `git diff --name-only fc50aed..HEAD`: every path under `docs/` |
| Review 01 | present; VERDICT REQUEST_CHANGES; F1–F6 each ACCEPTED, not applied |
| I-23 deliverables | read in full |

No precondition failed.

## Correction matrix
| Finding | Severity | Original defect | Correction | Where | Evidence | State |
|---|---|---|---|---|---|---|
| M3T2R-R1-F1 | MAJOR | Required continuity "through 1000 km"; the pinned table jumps there | **The requirement is removed.** The 1000 km base is tested like every other base: −1 ulp gives the 900 km band (3.0190482489066557e-15), exact gives the row (3.019e-15), +1 ulp gives the top band. The relative jump is −1.598e-5. Smoothness is claimed only within the top band, above 1000 km. DR-0029 P5's "(continuous, GMAT-identical)" is documented as ambiguous, and an amendment is **proposed, not applied** | Strategy U-15, §3.5; packet P5 items 8, 14; DR-0029 (append-only note); register OI-20 | `i24_reproduction.out` "F1"; DR-0024 Q5a (Resolution); DR-0029 P1 (12 downward jumps) | Corrected |
| M3T2R-R1-F2 | MAJOR | E1's ε_h applied to forward-constructed points and to heights −10 km … 2000 km | E1's derivation, domain and assumptions are stated: exterior (true h ≥ 0), the inverse's evaluation error only, the spike's algorithm, under A-FP-2. Exact-answer points at h ≥ 0 gate with ε_h, using exact references on the **model's** ellipsoid; b_model − b_WGS84 = +1.71e-12 m is reported separately. Forward-constructed points and every negative height are **reported** until the forward-construction (δ_f) or oracle term is derived (B-4). No replacement number | Packet P8 item 14; strategy U-17, U-18, PM-5, PM-6, §3.9 B-4, B-12; draft packet DQ-1 | `t0_termination.rounding_allowances` E1 docstring (i), (iv); `t0_termination_results.json` → `floating_point_enclosure` → `assumptions` → `domain`; `i24_reproduction.out` "F2" | Corrected |
| M3T2R-R1-F3 | MINOR | "Strictly decreasing" density inside a band | **Non-increase** for general inputs. It holds because every operation except exp is correctly rounded and monotone; it is conditional on exp's monotonicity (A-LM-2). Equal outputs are expected: 800 of 2 858 sampled adjacent pairs in band 0, plus the km-route quantisation. **Strict decrease** only for pairs separated by the E3 allowance with normal densities (conditional on A-FP-2). In the zero tail, non-increase only | Strategy PM-4, §3.9 B-9, B-10 | `i24_reproduction.out` "F3" | Corrected |
| M3T2R-R1-F4 | MINOR | "0 m" listed as raising; the spike's km-route guard copied | "0 m raises" is removed; ±0.0 and +5e-324 are in the domain. The guard is specified as a finite h_m < 0 test **in metres, before conversion**. Recorded T0 behaviour: the km route accepts −2.475e-321 < h_m < 0 and returns 1.225; the m route raises. These are separated from the **proposed** T2 requirement under (ii). Path (α) excludes the guard, and no floor or E1–E6 term changes. T0 files are not edited | Packet P4 items 8, 14; N-1; strategy U-14, §3.5; draft packet DQ-2; register OI-21 | `i24_reproduction.out` "F4"; `t0_model.density` lines 110–121 | Corrected |
| M3T2R-R1-F5 | MINOR | "h(t) is C² outside the ellipsoid" | Replaced by the regularity that holds: h is C¹, ḣ is absolutely continuous, and ḧ is piecewise continuous with jumps at base crossings (stated assumption: finitely many crossings per step, outside the evolute region). The chord bound is restated with an essential supremum and derived under that regularity. The certified two-body numbers are unaffected (no drag, h smooth). No perturbed-motion bound is claimed | Packet P2 item 5 | DR-0025 Resolution principle 5; DR-0029 P1, P2 | Corrected |
| M3T2R-R1-F6 | NOTE | Bounds named but not derived; zero cases unstated | **§3.9 bound audit (B-1 … B-15).** Each bound is classed **Gate** (derivation given), **Conditional** (named unproved assumption: A-FP-2, A-LM-1, A-LM-2) or **Deliverable** (reported until derived and reviewed). New derivations: B-1 (U-4 parallelism and sign; PM-1 margin domain), B-2 (exact power-of-two scaling, U-5, PM-3), B-10, B-11, B-13, B-15. Each row's domain and zero cases are stated. Gates G-T2-1 … G-T2-3 are restricted, and G-T2-3a is added. No threshold invented | Strategy principle 1, §3.1–§3.3 rows, §3.9, §4; packet P1 item 14; draft packet §6; register OI-22 | §3.9 derivations; `i24_reproduction.out` "F6" | Corrected |

## Related defects found during the I-24 audit (I-24 §5.3)
These are not Review 01 findings. Each is corrected in its row.
- **U-21: n̂ is not exactly ±Ẑ on the axis.** The spike's latitude there is fl(π/2), and cos(fl(π/2)) = 6.12e-17. U-21 is now reported until B-6 is derived.
- **U-23 contradicted §3.5.** U-23 listed "C_d·A = 0 ⇒ zero drag", but §3.5 requires positive parameters. A zero parameter is now a domain error. Positive parameters with C_d·A ≤ 2⁻¹⁰⁷⁵ give exactly zero force (T0 E4b, for the spike's sequence).
- **U-6 "bitwise" was too strong.** v − (±0) can change the sign of a zero component, so the check is IEEE equality.
- **U-16's transition points are specific to the spike's arithmetic.** Under path (β) or route (m) they must be recomputed.
- **U-19 and PM-2 relied on unstated libm and dot-product symmetry** (A-LM-1; FMA under A-FP-3).
- **I-2 and I-7 (b) claimed signs that are not derived.**

## Unchanged by this pass
- **P1–P9:** classification, options and recommendations unchanged, and no decision made.
  - READY FOR OWNER DECISION: P1 (κ, v̂), P2, P4, P8, P9.
  - BLOCKED BY ANOTHER DECISION: P3 (P1), P5 (P4, P1), P7 (P1, P9).
  - NEEDS ADDITIONAL EVIDENCE: P6.
- **Q-GATE:** open; the governing gate P1–P10 is not narrowed.
- **DQ-1 … DQ-6:** open.
- **P6 investigation (X-1):** open and not authorized.
- No production, test, proof, toolbox, scenario, CI, lock or `pyproject.toml` change. No golden reference, pinned constant, numerical contract or accepted decision changed. No T0 file edited.

## Proof gate (this record)
- [x] Every Review 01 finding has a correction and a location
- [x] Corrections are documentation-only (`git diff --name-only d8270c2`: `docs/` only)
- [x] No invented tolerance: every new gate bound is derived in §3.9; everything else is reported
- [ ] Independent Review 02: see `docs/reviews/M3-T2-readiness-review-02.md`
