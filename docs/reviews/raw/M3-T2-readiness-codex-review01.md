VERDICT: REQUEST_CHANGES

## Summary

Reviewed `5ee6a6a2d78ef425687ba164bb32033947ee7c01` against `fc50aed5136ba9ac013b4b09f32cbbbf2e0b4942`.

The package respects the documentation-only scope, preserves unresolved decisions, and correctly retains the governing P1–P10 gate. The proposed readiness classifications are broadly defensible.

Two technical problems require correction: the proposed continuity gate at 1000 km contradicts the pinned table, and the geodetic acceptance criteria extend a derived bound beyond its demonstrated domain and error budget. Additional proposed tests need qualification.

No decisions are approved by this review. No tracked files were changed.

## Findings table

Locations abbreviated below: **packet** = `docs/decisions/requests/DR-0029-P1-P9-owner-decision-packet.md`; **strategy** = `docs/milestones/M3-T2-validation-strategy.md`.

| ID | Severity | Location | Finding | Evidence | Recommended correction |
|---|---|---|---|---|---|
| M3T2R-R1-F1 | MAJOR | Strategy U-15, §3.5; packet P5 verification | Continuity **through 1000 km** is an incorrect acceptance requirement. The pinned table has a discontinuity at that boundary. Enforcing continuity would conflict with DR-0024 Q5a. | Using the published 900 km row, the left limit is `3.0190482489066533e-15`; the 1000 km row is `3.019e-15`. Relative jump: `−1.598149571502283e-5`. DR-0024 Q5a explicitly prohibits altering values to force continuity. | Test the documented jump and correct band selection at 1000 km. Distinguish this boundary from smooth extrapolation **within** the top band above 1000 km. Flag the inherited ambiguous “continuous” wording in DR-0029 without silently rewriting accepted records. |
| M3T2R-R1-F2 | MAJOR | Packet P8 acceptance criteria, lines 357–358; strategy U-17/U-18 | The packet assigns E1’s inverse-height error bound to forward-constructed comparisons over **−10 km…2000 km** without establishing that coverage. E1 covers exterior points and inverse evaluation error; it does not automatically cover rounded forward construction or negative heights. | `t0_termination.py::rounding_allowances` derives E1 for exterior points. Committed `floating_point_enclosure.assumptions.domain` explicitly says `true geodetic height >= 0`. Comparing inverse output with the nominal construction height also includes forward-coordinate error. | Restrict reuse of E1 to its proven domain. Derive and include forward-construction error and reference-evaluation error. Derive a separate bound for negative heights, or report those comparisons without claiming the existing derived guarantee. |
| M3T2R-R1-F3 | MINOR | Strategy PM-4 | Strictly decreasing binary64 density is not a valid unrestricted property, even inside one band. Rounded outputs can coincide; the top-band zero tail necessarily does. | At `h=1.0` and `nextafter(1.0,+∞)`, the spike returns the identical density `1.2248310228294286`. At `192000000` and `192000001` m, both return zero. | Test non-increase for general binary64 inputs. Require strict decrease only for explicitly separated inputs whose exact difference exceeds a derived rounding allowance. |
| M3T2R-R1-F4 | MINOR | Packet P4 verification, line 211; N-1 path α; authorization DQ-2; strategy U-14 | The lower-edge specification contains a direct typo and a portability trap. P4 says tests “at 0 m … raise,” then says 0 m evaluates band 0. Also, copying the spike’s km-route guard verbatim fails the proposed smallest-negative-input test. | `density(-5e-324)` returns `1.225`: division by 1000 rounds to `−0.0` before the spike checks negativity. | Remove 0 m from the raising cases. Specify the finite `h_m < 0` guard **before** km conversion. Explain that this domain-guard correction does not change the exterior arithmetic covered by the floors. |
| M3T2R-R1-F5 | MINOR | Packet P2 assumptions, line 138 | “h(t) … is C² … outside the ellipsoid” is false for trajectories crossing discontinuous atmosphere bands. Exterior location alone does not guarantee continuous acceleration. | The pinned density jumps at band boundaries, as explicitly recognized by DR-0025 Resolution principle 5 and DR-0029 P1. A nonzero normal component of the acceleration jump produces a jump in `ḧ`. | State piecewise smoothness. If using the chord inequality across boundaries, formulate it with the appropriate almost-everywhere curvature bound and regularity assumptions. Preserve the existing statement that no certified perturbed-motion bound exists. |
| M3T2R-R1-F6 | NOTE | Strategy D/T rows and §4 gates | Several bounds remain specifications to derive, rather than reviewable bounds with operation counts: examples include U-4, U-7, U-21 and PM-2. Exact-sign rows also need explicit nonzero-force/sample-domain conditions. | The matrix names “γ-bound” or “truncation bound stated” without supplying the count or derivation. For example, U-4’s strict negative dot product fails at zero relative velocity or zero density. | Identify these derivations as outstanding implementation deliverables and require their review before acceptance. State admissible sample domains and zero cases explicitly. |

## Verification of claims 1–12

1. **Questions, alternatives, statuses and T0 numbers — substantially consistent.**  
   Compared P1–P9 with DR-0029 and the relevant home resolutions in DR-0024, DR-0025 and DR-0027. The alternatives are represented across the matrix and individual assessments; recommendations remain recommendations. The P5 matrix cell abbreviates the alternatives, but its individual assessment includes top-band extrapolation, failure and cutoff. Checked committed thresholds, stage floors, stage offsets, crossing results, geodetic errors, GMAT residuals and regression metrics. Quoted rounded values agree. F1 identifies a technical error inherited from existing wording rather than a transcription mismatch.

2. **Readiness classifications — defensible.**  
   P3←P1, P5←P4/P1 and P7←P1/P9 are supported. The assessments additionally identify dt, T3 orbit kinds, P8 algorithm selection, Q-G2-2 and the DR-0028 scope ruling. No missing coupling was found that changes the classifications. P6’s classification is conservative: method (d) can be selected while its geodetic investigation remains unresolved, as the packet itself explains.

3. **Governing gate — verified.**  
   The quotation matches `docs/reviews/raw/M3-T0-codex-review01-prompt.md:275`. Both principal documents retain P1–P10 as the governing prerequisite set. The technical map is explicitly non-governing; narrowing is requested, not applied.

4. **N-1 — accurate with implementation qualifications.**  
   E1 explicitly depends on the iterative latitude algorithm and stopping rule; E2 models km conversion. The force and stage arithmetic also matter. A different implementation does not automatically inherit the floors. Bitwise agreement on samples alone would not establish universal equivalence; inspection of the complete applicable arithmetic and domain is still necessary. See F2 and F4.

5. **N-2 — accurate.**  
   DR-0026 AR-8 and §5.8 contain the quoted totality statements. P4(ii) creates a real textual tension. The Resolution approves D3 with enumerated constraints but does not reproduce those statements verbatim. Requesting explicit reconciliation is appropriate; this review does not resolve it.

6. **N-3, N-5, N-7 — verified.**  
   The geodetic normal gives `dh/dt = n̂·v` on the regular domain. Exposing normal or latitude is a sensible interface consequence. `architecture.py` forbids both `tars.validation` and `importlib` in `sim`/`astro`, including submodules. `pathlib` is already imported by `src/tars/sim/scenario.py`. N-7 correctly restricts the stiffness calculation to the velocity block.

7. **C-1…C-7 — arithmetic corroborated; external provenance remains limited.**  
   Independently recomputed C-1…C-5 below. C-5’s recalled input reproduces the printed coordinates within their rounding. That does not authenticate the input’s provenance, which the packet honestly discloses. C-6 explicitly says the primary source was unread; C-7 explicitly reports failed documentary corroboration. Neither is presented as completed independent validation.

8. **Validation strategy — requires changes.**  
   Measurements are generally kept informational, and no arbitrary numerical tolerance was found. However, F1–F6 prevent accepting every proposed gate as presently justified. Specifically:
   - **U-3:** dry mass plus clamped negative propellant is exact for owned finite positive binary64 dry mass; it matches the existing thrust expression.
   - **U-5:** power-of-two homogeneity is defensible for a fixed homogeneous operation sequence when affected intermediates avoid underflow/overflow. It is not an unconditional guarantee for every future algebraic rearrangement.
   - **U-12:** all 28 tabulated base values returned their exact parsed `ρ₀` in the spike; the 27 nonzero boundaries have exact integer metre/km bases. No counterexample was found to this claim.
   - **U-15, U-18 and PM-4:** see the findings.

9. **Draft authorization — structurally complete and appropriately bounded.**  
   Explicitly marked **DRAFT — NOT AUTHORIZED**. Includes decision records, design answers, baseline verification and separate implementation authorization as preconditions; protected paths, stop conditions, independent review, owner acceptance and separate merge authorization are present. Permitted shared-infrastructure edits align with baseline-and-impact class C and preserve T1 classes. T3/T4/T5 work remains excluded. Its incorporated validation requirements need the corrections above before execution.

10. **Open-issues register — complete for I-23 §9 E.**  
    Contains Q-G2-1/P6, Q-G2-2, DR-0028 P6(b), secular tolerances, T3 axis representation, T4/T5 requirements, final dt and external corroboration. No resolution or unauthorized expansion was found.

11. **Append-only edits and I-22 record — verified locally.**  
    All four append-only files retain the complete baseline bytes as prefixes. The README changes one row by adding another dated update while retaining its prior content; this follows its existing pattern and is acceptable. Git reports **24 commits, zero merge commits** for `60648b9..fc50aed`. Remote and CI statements are internally consistent but unauthenticated.

12. **Scope — verified.**  
    Exactly ten changed files, all under `docs/`: **917 insertions, one deletion**. No production, test, scenario, threshold, reference, constant, CI or lock change. Final tracked tree is clean.

## Own computations

Reproducible script: [check_claims.py](review_scratch/check_claims.py). Captured output: [check_claims.out](review_scratch/check_claims.out).

Command:

```sh
.venv/bin/python review_scratch/check_claims.py
```

Principal outputs:

```text
RK4 negative real boundary: -2.785293563405282

z=-0.01:
exp(z)-R(z) = -8.319464260940228...e-13
z^5/120    = -8.333333333333333...e-13

z=-0.1:
exp(z)-R(z) = -8.196404042683575...e-8
z^5/120    = -8.333333333333333...e-8

a-b = 21384.685754820704 m

C5 XYZ:
3771793.967641783
140253.34189961312
5124304.349350536 m

C5 differences from printed coordinates:
[-2.35821726, +1.89961313, -0.64946339] mm
```

For drag, differentiation gives

\[
J_v=-\frac{\rho}{2B}
\left(\|v\|I+\frac{vv^\mathsf T}{\|v\|}\right).
\]

At `v=(7000,-2000,500)`, `ρ=1e-10`, `B=25.8`, the numerical eigenvalues were:

```text
[-2.82839526e-08, -1.41419763e-08, -1.41419763e-08]
```

These agree with the longitudinal rate `−ρ‖v‖/B` and two transverse rates half its magnitude.

Other checks:

```text
.venv/bin/ruff check .
All checks passed!

.venv/bin/ruff format --check .
244 files already formatted

git rev-list --count 60648b9..fc50aed
24

git rev-list --merges 60648b9..fc50aed
[empty]

git status --porcelain
[empty]
```

`git diff --check` reports Markdown trailing spaces used for hard line breaks; these were not treated as substantive findings.

## Limitations of this review

- No network access: CI runs, remote refs, push status, branch protection and external-source retrieval claims could not be authenticated.
- No GMAT reruns or external PDF inspection were performed. External comparisons were checked against committed records and independently recomputed arithmetic where possible.
- M1/M2 proof scripts were not run, as instructed. The full T0 check suite was not rerun; this review inspected its code and committed evidence.
- Numerical computations are finite, single-host corroboration—not universal proofs or cross-platform certification.
- Scratch work is confined to `review_scratch/`. No fixes, approvals, commits or merges were performed.