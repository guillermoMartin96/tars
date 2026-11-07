# S2 evolute-guard derivation note (M3 T2 S2, commit D)

Authorized by PC-7(S2) (issued, I-99), with owner determinations I-101, I-102 and I-103. Pinned proposal v11, sha256 `f7d88086632e38a773594231c5aae44f86993dd3a6496e5d559d0989a3072809`.
Component `src/tars/sim/geodesy.py`, git blob `e409e26341ec40a0adf8123e5ea47d5fc9788d9d`.

**What this note is.** §3.7.9 of v11 requires "a derivation note … holding §3.7 as reviewed". §3.7 is
reproduced verbatim below, and checked byte for byte against the pinned file. It remains the
implementer's derivation [DER]. The I-72, I-75 and later reviews confirmed parts of it at proposal
level (I-97 decision A). Implementation-level verification (IN-1, OB-11, OB-19) is the
independent §5.2 review's, and nothing here marks an obligation MET.

**What it is not.** Not an accuracy claim. Acceptance means only that DQ-1's stop test was met and
the outputs are finite (OD-12 item 3). Accepted points below the ellipsoid are report-only (P8).

## 1. Owner determination I-101 (generation environment; pinned v11 only)

For v11 §3.10 and the G-17a/G-17b replay rules, "the generation environment" means equality of
these recorded fields:
- `sys.version`;
- `platform.platform()`;
- `platform.machine()`;
- the `uv.lock` sha256;
- the sha256 of the interpreter executable, with its real path resolved before hashing.

Path equality is not compared. The commit SHA and the CI-only run-record fields stay mandatory
under §3.16 and are excluded from this equality. Equal fields select the replay-policy case only.
They do not prove library or build identity, as r83:83 states: "ENV fields with unobservable values
do not certify a perfectly reproduced library/build environment; a controlled regeneration
comparison must record that limitation rather than assume matching proxy fields prove identity."

The author chose these fields during commit-A preparation. I-101 subsequently approved that author
interpretation; it was not prior owner authorization.

## 2. Author's operation-by-operation record against r1 §5 (lines 89-94, blob 4537bcad…)

Author record only, for the reviewer's comparison; the independent IN-1 is the §5.2 review's.

| r1 step | r1 text | geodesy.py | line |
|---|---|---|---|
| 1 | a = 6378137.0 | `_A = WGS84.equatorial_radius` | 49 |
| 1 | F = 1.0/INV_F | `_F = 1.0 / WGS84_INVERSE_FLATTENING` | 50 |
| 1 | e2 = F·(2.0 − F) | `_E2 = _F * (2.0 - _F)` | 51 |
| 2 | p = hypot(x, y) | `p = _LIB.hypot(x, y)` | 159 |
| 3 | φ = atan2(z, p·(1.0 − e2)) | `phi = _LIB.atan2(z, p * (1.0 - _E2))` | 160 |
| 4 | at most 60 times | `for _k in range(1, 61):` | 162 |
| 4 | s = sin φ | `s = _LIB.sin(phi)` | 163 |
| 4 | n = a/√(1.0 − e2·s·s) | `n = _A / _LIB.sqrt(1.0 - _E2 * s * s)` | 164 |
| 4 | φ_new = atan2(z + e2·n·s, p) | `phi_new = _LIB.atan2(z + _E2 * n * s, p)` | 165 |
| 4 | Stop after the update when \|φ_new − φ\| ≤ 1e-15 | `stop = abs(phi_new - phi) <= 1e-15; phi = phi_new; if stop: converged = True; break` | 166 |
| 5 | s = sin φ, c = cos φ | `s = _LIB.sin(phi); c = _LIB.cos(phi)` | 172 |
| 5 | h = p·c + z·s − a·√(1.0 − e2·s·s) | `h = p * c + z * s - _A * _LIB.sqrt(1.0 - _E2 * s * s)` | 173 |

Additions to r1 §5, and only these (§3.7.10 E.1):
- the boolean `converged` and the `break` on the stop branch;
- the loop counter `_k`;
- the `try` (lines 158 to 174), which covers exactly E.1 and catches only `ArithmeticError` and `ValueError`.

The post-checks N2 to N4 (lines 177, 179, 181) use `_isnan` and `_isinf`, bound at import, never `_LIB`. `_LIB` is bound to `math` at line 43 and is used only in E.1.

Guard (author record against §3.7.4 and §3.7.5):
- `_K` = a²·e2² (line 54);
- `_W` = 1 − e2 (line 55);
- D′ = K − p² − W·z² (line 132);
- the closed-region test D′ ≥ 0 and D′³ ≥ 27·K·W·p²·z² (line 133);
- the pre-filter at 65536.0 (lines 58 and 128).

All in exact `Fraction` arithmetic; no libm.

## 3. What a versioned model identifier would version (D-S2-2 (c); assigned in S4, OB-31)

No identifier is assigned in S2. The definition an identifier would version:
- **Constants:**
  - a = `WGS84.equatorial_radius` = 6378137.0;
  - 1/f = `WGS84_INVERSE_FLATTENING` = 298.257223563;
  - F = `0x1.b775a84f3e128p-9`;
  - e2 = `0x1.b6b90f1fe94f0p-8`;
  - the guard constants K = a²e2² and W = 1 − e2 as exact rationals;
  - the pre-filter 65536.0.
- **Sequence:** DQ-1 (α), r1 §5 lines 89-94, with the E.1 additions above.
- **Guard:** the §3.8 steps 0 to 4, in that order, with the closed region.
- **Numerical rules:** N1 to N5 in the order `numerical_failure` → `overflow` → `non_convergence` (D-S2-11 (b-i)); the 60-iteration cap and the 1e-15 stop test unchanged.

## 4. D-S2-11 (b-iv): the P8 evidence sentence

`docs/decisions/requests/DR-0029-m3-t0-proposals.md:568` reads: "Both inverse algorithms are valid
outside the evolute region near the centre."

For DQ-1 as specified (60-iteration cap), this is contradicted near the equatorial cusp outside E
(v11 §3.20; F-01). There, the iteration does not meet its stop test within 60 iterations, and S2
rejects such points with `non_convergence`. On the frozen listing, the host census records 3 081
such DG-CUSP points and 366 DG-DEEP points (RP-6b).

This is recorded here and in the S2 report. DR-0029 is not edited, and no status note is added
(the owner's option, not taken).

## 5. Owner amendments I-102 and I-103 (external; v11 itself unchanged)

**I-102 (sequence adjustment, MN-17).** The I-101 campaign at BC stopped at stop 8. MN-17 ("the
component value used as given, instead of the base-slot value") failed its G-06 override node only
by an uncaught `GeodeticDomainError`, which v11 §3.12 does not count as a kill. The campaign's
MN-17 node list had also omitted the `__abs__` case.

I-102 authorized:
- a narrow test correction: the override case captures a `GeodeticDomainError` as an observed wrong
  outcome and rejects it by an explicit assertion;
- a supplemental red run at A;
- one supplemental corrective commit after BC, designated BC2.

The uncaught-exception failure is not counted as a kill, and MN-17 is not equivalent.

**I-103 (owner amendment to §3.12, MI-03's designated killer).** Quoted:

> For the mutant “Precedence swap, non-finite after evolute,” designated MI-03 in the campaign,
> replace the designated killer:
> G-06 (inf, 0, 0)
> with:
> G-06 (nan, 0, 0), node test_g06_section_3_8_order_table[r0-non_finite].

Reason: the §3.7.5 pre-filter returns False for any input with an infinite component before any
`Fraction` is built, so the mutant is unobservable at (inf, 0, 0). At (nan, 0, 0), `Fraction(nan)`
raises `ValueError` outside E.1, and `_raises_reason` rejects it by an explicit `AssertionError`.
This corrects the designated witness only. It grants no equivalence exemption.

## 6. Equivalence arguments for the documented equivalent mutation survivors (v11 §3.12, verbatim)

<!-- BEGIN VERBATIM v11 P:2185-2189 -->
**Documented equivalent survivors** (each with a written equivalence argument):
- the pre-filter bound raised (for example 2¹⁷), or `>=` → `>` at 65536: both are equivalent by §3.7.5;
- **[F-07] D′ ≥ 0 clause dropped:** provably equivalent (§3.7.4). On 2 717 points with D′ < 0, I-72 found 0 classification changes. v1's designated kill was impossible;
- **[F-16] closed → open region (≥ → >):** provably equivalent at every G-03 ray point, because no binary64 point lies exactly on the boundary in those planes (I-72 `probe_boundary_points.out`). The general case is undecided.
<!-- END VERBATIM -->

<!-- BEGIN VERBATIM v11 P:2226-2241 -->
**[I-75] Survivors (corrected in v4).** A mutant that no test kills is **UNKILLED**. It may be called *equivalent* only with a written proof of equivalence, never because a grid of points failed to kill it.
- The regrouping mutant `e2 * (n * s)` is the known candidate. If it survives, either an equivalence proof is supplied or it is reported UNKILLED, which is stop 8.
- The documented equivalent survivors are the three in the predicate list above, each with a proof (§3.7.4, §3.7.5, §3.7.6), and **[v5]** M-W2 below.
- **[v6, r79:91]** M-W2's research model (RES-78) normalizes integers before its guard-widened block, so its 12-case agreement does not exercise widening over step 1. The proof covers only the stated mutant (normalized built-ins, the step-1 inner handler intact, `GeodeticDomainError` re-raised unchanged). A handler that also wraps `GeodeticDomainError` is a different, observable mutant, killed by G-06's identity and type assertions. IN-1 remains necessary, and no grid agreement is an equivalence proof.

**[I77-04, v5] Equivalence proof for M-W2** (a `try` widened over steps 1 to 4 only, after structural access and normalization):
- The widened handler catches `ArithmeticError` and `ValueError`. It changes an outcome only if steps 1 to 4 raise one of these, other than `GeodeticDomainError`, which is re-raised. Steps 1 to 4 act on normalized built-in values only (§3.8 step 0).
- **Step 1:** `float(i)` may raise `OverflowError` (10**400). Step 1's own handler catches it first and raises `not_binary64`. `float(i) != i` compares a built-in float with a built-in int, which does not raise.
- **Step 2:** `math.isfinite` on built-in floats does not raise.
- **Step 3:** `==` on built-in floats does not raise.
- **Step 4:** the pre-filter compares built-in floats. The predicate builds `Fraction`s from finite built-in floats (step 2 has already rejected NaN and inf) and uses only `+`, `−`, `×`, integer powers and comparisons, with no division. None of these raises `ArithmeticError` or `ValueError`.
- So the handler is never entered, and the mutant is behaviourally equivalent.
- [RES-78] On 12 guard and evaluation inputs, the narrow and the guard-widened research contracts give identical outcomes. That is corroboration; the proof is the argument above.
- IN-1 checks that the implemented `try` covers exactly E.1.
- **The designated assertions are identity assertions** (SV-1, SV-2, FI-15). A kill by `pytest.raises(ValueError)` would not count: `GeodeticDomainError` is a `ValueError`, so that assertion passes against the mutant (strategy `:141-150`, "a designated assertion … for its declared reason").
- [RES-78] In the research contract, every mutant with a designated case is killed by that case: N2 removed; N1 removed; broad catch; M-W1; M-W3; the three order swaps; cap 59; cap 61; `<=` → `<`; k = 60 treated as failure; and the pre-update iterate returned. **These are model mutants, not implementation evidence** (§5.4 OB-10).
<!-- END VERBATIM -->

## 7. v11 §3.7, verbatim (v11 P:898-1410)

<!-- BEGIN VERBATIM v11 P:898-1410 -->
### 3.7 Domain guard: mathematics and numerical treatment

> **Review status.** Everything in §3.7 is **[DER]**: the implementer's derivation, unreviewed. It is
> a proposal for the independent proposal review (§5) and for D-S2-4. The I-70 figures (about
> 42.7 km and 42.8 km) are used here only as illustrations. No number in this section is an
> approved predicate, bound or threshold, and the proposed predicate contains no tolerance or
> margin.
>
> **v2 note.** The I-72 review independently confirmed R-P1 (evolute and Jacobian), R-P2 (the
> polynomial predicate) and R-P3 (the pre-filter), but as a same-provider review (F-19). The section
> therefore stays [DER] until the separate-provider re-review (§5.1). v2 adds an independent
> boundary cross-check [RES] (§3.7.6) and the F-01 analysis (§3.20).
>
> **v4 note.** I-75 (separate provider) independently re-derived the meridian Jacobian, the centres
> of curvature and E (R-P1: "technically sound, owner boundary choice pending"). It found R-P2 and
> R-P3 PASS, and R-P17 PASS at design level. It reproduced all eight boundary pairs by an astroid
> search that does not use the polynomial. Those results are review evidence, not owner approval,
> so the section stays [DER] until the owner decides D-S2-4. I-75 failed R-P4 and R-P15 over
> S2-ASM-1′; §3.7.8 is rewritten in response (I75-01).

#### 3.7.1 The model ellipsoid

The guard is defined on the **model ellipsoid** used by DQ-1 and by DL-2 (`r2:84`):
- a = 6378137.0, taken from `WGS84.equatorial_radius`;
- e² = the binary64 value `e2 = F*(2.0 − F)` with `F = 1.0/298.257223563`, formed by DQ-1 step 1 (`r1:90`).

Both are binary64 numbers, so they are exact rationals. Write b² = a²(1 − e²), also an exact
rational, though b itself is irrational.

For an input r = (x, y, z) of binary64 numbers:
- p² = x² + y² and z² are exact rationals;
- p = √(p²) is used only in the mathematics; the guard never forms it.

#### 3.7.2 Why some points must be rejected [DER]

**The forward map.** In a meridian half-plane, geodetic coordinates (φ, h) map to

  P(φ, h) = ((N + h) cos φ, (N(1 − e²) + h) sin φ),

where:
- N = a / √(1 − e² sin² φ) is the prime-vertical radius of curvature;
- M = a(1 − e²) / (1 − e² sin² φ)^{3/2} is the meridian radius of curvature.

**Its Jacobian.**
- ∂P/∂h = (cos φ, sin φ), the unit normal.
- ∂P/∂φ = (M + h)(−sin φ, cos φ). This uses ds = M dφ along the meridian.
- So det ∂P/∂(φ, h) = −(M + h).

**Consequences:**
- The map is locally invertible except where h = −M(φ), that is, where the point is a **centre of curvature** of its foot point.
- The locus of the meridian's centres of curvature is, by definition, the ellipse's **evolute**.
- Inside the region bounded by the evolute, a point lies on more than one normal from the ellipse. Apollonius' classical result: four normals inside the evolute, two outside.
- So (φ, h) is not a single-valued function there unless a selection rule is added. P8 does not add one; it requires rejection.
- In three dimensions the region is the solid of revolution of the meridian evolute region about +Z. It contains the origin and the axis segment between the polar cusps.

**This matches the recorded evidence (E-2, `DR-0029-m3-t0-proposals.md:569`):** at (30 km, 30 km, 0), "the iterative algorithm returns a non-nearest solution … and Vermeille divides by zero."

**What this does not establish (corrected in v2) [F-01]:**
- **Uniqueness outside E holds** (§3.20.1). Exactly one fixed point of the DQ-1 map has cos φ > 0. **[I-75] Scope:** this is uniqueness of the principal, same-quadrant solution. Unrestricted normals through the point also include an antipodal foot, even outside E.
- **The specified iteration does not always reach it.** DQ-1 caps the iteration at 60 steps.
  - Near the equatorial cusp, outside E, the cap binds without the stop test being met.
  - DQ-1 then returns latitude errors of up to 6.99e-2 rad and height errors of up to 1.27 m [RES].
  - v1 called convergence outside E only "not established". That understated a demonstrated failure.
- **Where convergence is established:** E1 (T0) proves contraction with rate ≤ 0.00683 for every |r| ≥ b (`DR-0029-m3-t0-proposals.md:89`). That covers the exterior domain of E1 (true height ≥ 0) and every M3 state (§3.20.4).
- No accuracy bound exists for accepted interior points (§3.18).

**References.**
- The evolute of an ellipse and Apollonius' count of normals are classical results of plane geometry. The implementer has not read a specific text for them in this project.
- I-72 R-P1 confirmed them independently: centres of curvature lie on the predicate's zero set exactly, and det = −(M + h) holds to 1.2e-45 relative. That review was same-provider (F-19).
- The separate-provider re-review is asked to confirm them, or to cite a source (§5, R-P1).

#### 3.7.3 The region [DER]

The evolute of the ellipse p²/a² + z²/b² = 1 is the astroid

  (a·p)^{2/3} + (b·z)^{2/3} = (a² − b²)^{2/3}.

**Proposed rejected region E** (the closed region, boundary included):

  E = { r : (a·p)^{2/3} + (b·|z|)^{2/3} ≤ (a² − b²)^{2/3} }.

**Why the closed region [REC]:**
- On the boundary, det = 0 (h = −M) and two normals coincide. The inverse is not smooth there.
- Including the boundary costs nothing measurable. Section 3.7.6 shows that whether boundary points are included can change the outcome only at binary64 points lying exactly on the astroid.

**Illustrative extent (not adopted):**
- equatorial cusp (a² − b²)/a = e²·a ≈ 42 697.67 m;
- polar cusp (a² − b²)/b ≈ 42 841.31 m.

These match the I-70 `evolute_geometry.txt` figures. They play no role in the predicate below.

#### 3.7.4 A cube-root-free exact predicate [DER]

The astroid form needs cube roots. Evaluated in binary64 with `pow` or `cbrt`, those are
libm-dependent and not correctly rounded, so classification near the boundary would vary by
platform. That conflicts with U-20 being an exact gate (strategy `:184`). The proposal therefore
uses an equivalent polynomial form.

**Notation.** Let u = a²p², v = b²z², c = (a² − b²)², and s = u^{1/3}, t = v^{1/3}, w = c^{1/3}, with s, t ≥ 0 and w > 0.
- r ∈ E ⇔ s + t − w ≤ 0.

**Step 1: an identity.**
- x³ + y³ + z³ − 3xyz = (x + y + z)·Q, where Q = ½[(x − y)² + (y − z)² + (z − x)²] ≥ 0, and Q = 0 only if x = y = z.
- Take (x, y, z) = (s, t, −w). Then Q > 0, because s = t = −w is impossible with s, t ≥ 0 and w > 0.
- So sign(s + t − w) = sign(u + v − c + 3·s·t·w).

**Step 2: remove the remaining root.**
- Let D = c − u − v. Then s + t − w ≤ 0 ⇔ D ≥ 3·(u·v·c)^{1/3}.
- That holds ⇔ D ≥ 0 and D³ ≥ 27·u·v·c, because cubing is monotone on non-negative numbers.

**Step 3: divide by a⁶ (positive) and substitute b² = a²(1 − e²), a² − b² = a²e².** With K = a²e⁴ and W = 1 − e²:

  **r ∈ E ⇔ D′ ≥ 0 and D′³ ≥ 27·K·W·p²·z², where D′ = K − p² − W·z².**

**[F-07] The clause D′ ≥ 0 is redundant.** Since 27·K·W·p²·z² ≥ 0, the inequality D′³ ≥ 27·K·W·p²·z² already forces D′³ ≥ 0, and so D′ ≥ 0. The clause may be kept for readability. A mutant that drops it is provably equivalent (§3.12).

**[F-15] The constants actually classified against.** The predicate classifies against the **model ellipsoid**: the exact rationals of binary64 a = 6378137 and e2 = `0x1.b6b90f1fe94f0p-8` (r1 `:90`). It does not use the "ideal" WGS 84 ellipsoid with the exact decimal 1/f.
- e2_model − e2_ideal = −5.351e-19 [RES].
- Test references must therefore be computed on the model ellipsoid (§3.7.6).

**Sanity checks:**
- z = 0 gives p ≤ a·e², the equatorial cusp.
- p = 0 gives |z| ≤ a·e²/√W, the polar cusp.

**Evaluation [REC]:**
- D′ and both comparisons are evaluated **exactly**, in Python integer or `fractions.Fraction` arithmetic, from the exact rational values of x, y, z, a and e2. No rounding, no libm.
- Python's `Fraction(float)` conversion is exact, and integer arithmetic is exact. So the classification of every binary64 input is the mathematical classification on the model ellipsoid, and it is identical on every platform.
- This is why U-20 can be an exact gate on all three CI platforms.

**Checked by probe (Appendix A).** On 10 points the polynomial form agrees in sign with an 80-digit
decimal evaluation of the cube-root form. The points include (30 km, 30 km, 0) inside, the origin,
(5e-324, 0, 0) inside, (43 km, 0, 0) outside, (0, 0, 42.9 km) outside and (30 km, 0, 30 km) outside.
This is corroboration, not proof. The proof is the derivation above, which the review must check.

**Why the squares never overflow.** r2 §8.2 asks for "|r| near overflow of the squared terms" (`r2:422`).
The guard never squares in binary64; p² and z² are exact rationals. Overflow therefore arises only in
the DQ-1 sequence itself (§3.7.8).

#### 3.7.5 An exact pre-filter (an optimisation; does not change any classification) [DER]

**The claim:** r ∈ E implies |x|, |y|, |z| < 2¹⁶ = 65536.

**Proof:**
1. In E, D′ ≥ 0, so p² ≤ K and W·z² ≤ K.
2. Hence |x|, |y| ≤ p ≤ a·e², and |z| ≤ a·e²/√W.
3. Both bounds are below 2¹⁶. This is checked exactly in rationals: K < 2³² and K/W < 2³² (Appendix A).

**Rule.** If any of |x|, |y|, |z| is ≥ 65536.0, the point is outside E, and the exact test is skipped.
- Comparing two binary64 numbers is always exact; that 65536.0 is a power of two is not needed (I-72 R-P3). The bound in step 3 is checked exactly in rationals.
- So the pre-filter changes no classification. It is not a threshold: it is a proven-sound shortcut, and removing it changes only speed.

**Cost (host probe):**

| Operation | Time per call |
|---|---|
| exact predicate | about 9.7 µs |
| one DQ-1 evaluation | about 1.8 µs |
| pre-filter | about 0.06 µs |

Every M3 state passes the pre-filter, so the exact path is never taken in M3 runs.

**[OPEN] Alternative:** always evaluate the exact predicate, with no pre-filter. The proof
obligation disappears, at about 5× the cost of a geodetic evaluation per call. Either is acceptable
to the implementer. The reviewer is asked to accept the proof or to require the alternative.

#### 3.7.6 Boundary cases [DER]

- **No margin.** The predicate classifies exactly. No ulp or metre tolerance is added, so no threshold is created.
- **Open versus closed.** The two differ only at binary64 points exactly on the astroid.
  - **[F-16]** I-72 proved that no such point exists on the axes, in the equatorial plane, or in the meridian planes x = 0, y = 0 and x = ±y (I-72 `probe_boundary_points.out`). The general case is undecided.
  - The ≥ → > mutant is therefore provably equivalent at every G-03 ray point, and is a documented equivalent survivor (§3.12).
  - The closed region stays the recommended reading: P8 does not specify open or closed, and closed is the conservative choice (D-S2-4 (a)).
- **±1 ulp pairs (r2 §8.2 `:421`). [F-05, F-15] Corrected.**
  - **Rays:** at least the five fixed rays (+x equator; the x = y diagonal in the equatorial plane; +z axis; −z axis; the oblique (1, 0, 1)). The three further rays (2, 0, 1), (1, 0, 2) and (1, 1, 1) are recommended.
  - **Outcomes:** the inside point must raise reason `evolute_region`; the outside point must be accepted.
  - **Independent references.** v1 had the test compute the pairs with the component's own predicate. Then a derivation or transcription error shared by component and test (a wrong K, W or coefficient) would pass G-03. In v2 the pairs are **fixed hex constants** in the test, derived by formulations independent of the polynomial predicate, and the provenance is recorded:
    - **axes and equatorial plane:** exact rational comparison with the classical cusp values (p² vs a²e2² on the equator; z² vs a²e2²/(1 − e2) on the axis);
    - **off-axis rays:** two independent methods. M1 is the parametric centre-of-curvature form ((a² − b²)/a·cos³t, (a² − b²)/b·sin³t), evaluated in 80-digit decimal. M2 is the normal count: a point is in E iff the convex function f(λ) = p²a²/(a² + λ)² + z²b²/(b² + λ)² − 1 has a non-positive minimum on (−a², −b²).
  - **[RES] (`f05_guard_crosscheck.out`):**
    - On all 8 rays, M1 and M2 classify the polynomial predicate's pair identically.
    - The hex pairs equal those that I-72 found independently: +x `0x1.4d93586d13537p+15`/`…538p+15`; x = y `0x1.d7bf41722e7d2p+14`/`…7d3p+14`; ±z `0x1.4eb29f7eac4c2p+15`/`…4c3p+15`; (1,0,1) `0x1.d88a1b7a7d48dp+13`/`…48ep+13`.
    - Strategy `:189` ("test points are taken on both sides of it, as computed") is still met: the pairs are computed, but outside the component.
    - **[I-75] Provenance correction.** The I-73 research script first located each pair with the polynomial predicate, and then cross-checked it with M1 and M2. I-75 judged that acceptable corroboration, but not an independently generated oracle.
      - **v4 requires the implementation-time derivation output (§3.14 commit D) to locate each pair by a method that does not use the polynomial.** That method is a high-precision bisection on the astroid form (M1), as I-75 did. M2 and the polynomial are then applied as cross-checks.
      - I-75 independently reproduced all eight pairs this way (`I-75/independent_probe.out`).
  - **[F-15] Model ellipsoid.** The references are computed on the model ellipsoid (§3.7.4).
    - On the ideal WGS 84 ellipsoid the pair differs by one ulp on +x, x = y, (2,0,1) and (1,0,2), and is identical on ±z, (1,0,1) and (1,1,1) [RES].
    - This offset is reported as a constant-definition term, as U-17 does for b. It is not a test tolerance.
- **Points just outside E pass the geometric guard**, even though they lie deep inside the ellipsoid. Example: (30 km, 0, 30 km), outside E per Appendix A, with a negative height near −6.3 × 10⁶ m.
  - Whether they are then accepted is decided numerically (§3.7.10).
  - Their outcomes are covered by DL-4 outcome conformance, and accuracy is report-only.
  - **[F-01] [OPT-b]** Near the equatorial cusp, DQ-1 does not converge within its limit for such points (§3.20). They pass the geometric guard and are rejected with `non_convergence`.
- **Origin and subnormals.**
  - The origin is in E. It is checked first and given its own reason, so that the origin and evolute guards can be told apart (needed for the r2 §8.3 guard-removal mutants).
  - Signed zeros: all eight sign combinations of (±0.0, ±0.0, ±0.0) are the origin.
  - Non-origin subnormal points such as (5e-324, 0, 0) are in E and raise `evolute_region`.
- **Near-axis points outside E** (r2 §8.2 `:419`), for example (5e-324, 0, 7.0e6): accepted, and evaluated by DQ-1 unchanged. The cases exercise gradual underflow, which X-P4 checks.

#### 3.7.7 What is left unchanged for accepted inputs

The normalization and the guard run before the DQ-1 sequence, and the post-evaluation checks
(N1 to N5) run after it. None of them adds, removes or reorders a floating-point operation in the
sequence (r1 `:99`). DL-4 checks this property on the tested points, and source inspection checks
it in general.

#### 3.7.8 Large finite inputs, overflow and library-behaviour strata [DER] [I75-01]

**[I75-01] What changed in v4.**
- v3 opened this section with a table of which intermediates "can be non-finite … assuming S2-ASM-1′". It followed with a completeness argument and with S2-ASM-1′ itself.
- I-75 showed that the premise did not imply those properties, and that its quantifier was circular.
- v4 therefore separates:
  - **(A)** what the construction guarantees with no library premise;
  - **(B)** what it does not establish;
  - **(C)** the known facts by stratum;
  - **(D)** a conditional explanation that nothing relies on;
  - **(E)** what fault injection does and does not show;
  - **(F)** the disposition of S2-ASM-1′.
- The v3 text is preserved in the v3 file (`I-74/S2-proposal-v3.md`, §3.7.8).

**Probe results (Appendix A, host):**

| Input | p | φ | h | Outcome |
|---|---|---|---|---|
| (1.5e308, 1.5e308, 0) | inf | 0.0 | inf | p overflows |
| (1.5e308, 0, 1.5e308) | 1.5e308 (finite) | finite | inf | height term overflows |
| (1e308, 0, 1e308) | finite | finite | 1.414e308 | accepted, finite |
| (1e300, 1e300, 1e300) | finite | finite | finite | accepted, finite |

CPython's `math.hypot` returned `inf`; it did not raise. Python `float` arithmetic does not raise on overflow.

**[F-10] Near overflow of the squared terms.** r2 §8.2 asks for "|r| near overflow of the squared terms" (`r2:422`). In binary64 the squares overflow at |r| ≈ √DBL_MAX ≈ 2⁵¹² ≈ 1.34e154. The guard never squares in binary64, and DQ-1 uses `hypot`. These points are added to G-05 and S-BIG. On the host every one gives finite p, φ and h, and meets the stop test within 1 or 2 iterations [RES] (`corrections_probe.out`):
- (2⁵¹², 0, 0) and its two neighbours;
- (0, 0, 2⁵¹²);
- (2⁵¹¹, 2⁵¹¹, 2⁵¹¹);
- (2⁵¹², 2⁵¹², 2⁵¹²).

**Proposed rule [REC]: finite-result rule.**
- After the unchanged sequence, if p, φ or h is not finite, raise `GeodeticDomainError(reason="overflow")`. **[v4, consistent with v3's §3.7.10]** A NaN is reported first, as `numerical_failure` (N2). The finite-result rule applies to ±inf (N3).
- This adds no constant and no threshold, and leaves the arithmetic unchanged.
- It must never raise `OverflowError`. `Simulator.step` catches `OverflowError` and `ZeroDivisionError` and converts them (packet `:213`), which would hide the domain error once S4 wires the component in.

**A. What the construction guarantees, with no library premise [UNIV by construction] [I75-01, I75-04, I75-05].**

**Scope:**
- a normalized input: built-in binary64 values from §3.8 step 0;
- that has passed steps 0 to 4;
- with the E.1 evaluation block of §3.7.10 executed inside a `try` that catches only `ArithmeticError` and `ValueError`;
- for any library behaviour whatsoever.

**The guarantees:**
- **G1.** No non-finite p, φ or h is ever returned.
  - N2 and N3 test all three after evaluation.
  - They use `math.isnan` and `math.isinf`, bound at import. They never use the evaluation library `_LIB`.
- **G2.** No `ArithmeticError` (including `OverflowError` and `ZeroDivisionError`) or `ValueError` raised inside E.1 escapes.
  - Each becomes `numerical_failure`, with the original exception as `__cause__`.
- **G3.** Every other exception raised inside E.1 propagates unchanged.
  - Examples: `TypeError`, `AttributeError`, `NameError`, `MemoryError`.
  - It is not reported as a domain or numerical outcome.
- **G4.** The component returns only if the stop test was met at some update k ≤ 60 (C3).
- **G5.** The outcome is the first applicable of N1 to N5, for every combination of conditions.

**What these rest on:**
- They depend only on the component's source matching §3.7.10. IN-1 inspects that.
- They are exercised by G-16's fault-injection cases, including overlapping conditions.
- They do not depend on what values the library returns.
- [RES-76] `fault_injection_contract_probe.out`: a research transcription of the contract gives the specified outcome in all 13 injected cases, and each of 10 contract mutants is killed. **[v5, I77-03]** Those fixtures were partial, so some outcomes and one kill depended on the host library. [RES-78] `g16_fixture_scope_probe.out` repeats the cases with complete fixtures (FI-00 to FI-15). This remains model evidence, not implementation evidence.

**B. What is not established, and is withdrawn from v3 as a guarantee [I75-01]:**
- that N1 or N2 is unreachable for any class of inputs;
- which intermediates can be non-finite;
- that an infinite p always converges, or that it is classified as `overflow` rather than `numerical_failure`;
- that the pre-bound alternative (below) makes overflow impossible;
- that the signs and ranges of `sin`, `cos` and `atan2` results are those of the exact functions.

Each of these depends on the values the library returns. Where the outcome matters:
- it is observed per platform, at declared points (G-05, G-14, G-15);
- any non-injected `numerical_failure` is a stop for investigation (stop 17).

**C. Known facts, by stratum.** Each row is labelled with what it rests on. None is a guarantee about the CI builds.

| # | Statement | Stratum | Basis | Used for |
|---|---|---|---|---|
| S-1 | For every real φ, 1 − e2·sin²φ ∈ [1 − e2, 1], because 0 < e2 < 1 | [MATH] | Elementary | Explanation only |
| S-2 | **(corrected in v5, I77-02)** For **finite** binary64 s, the rounded radicand **as DQ-1 evaluates it**, fl(1 − fl(fl(e2·s)·s)) (Python's left-to-right `1.0 - e2 * s * s`), is non-increasing in \|s\| and symmetric in sign. It is positive at s = `0x1.871b35ad1ef4cp+3` (value 1.1102230246251565e-16), the largest binary64 value below e2^(−1/2) (exactly, in rationals), and ≤ 0 at the next value up (−2.220446049250313e-16). **So, for finite s, radicand > 0 if and only if \|s\| < e2^(−1/2) exactly.** ~~fl(1 − fl(e2·fl(s·s)))~~ **[WITHDRAWN v5, I77-02]**: v4 printed a different grouping (value 2.220446049250313e-16 at the same s). The probe already used the actual grouping, and the conclusion survives. Infinite and NaN s are outside this statement | [FP] (A-FP-1 monotone rounding), [RES-76] and [RES-78] | `rounded_radicand_probe.out`; `h2_correction_probe.out` §3 (21 194 finite samples, non-increasing, symmetric); monotone composition | Explanation only. Needs a bound on the computed s, which is [PLAT] |
| S-3 | Python float `+`, `−` and `×` overflow to ±inf without raising. inf − inf and inf·0 give NaN. Float `/` by zero raises `ZeroDivisionError` | [SAMP] on the host. **[v5, I-77] The [LANG] attribution is UNVERIFIED:** the language reference was neither saved nor located precisely | `cpython_behaviour_probe.out` | Why N1 to N3 must all exist |
| S-4 | `math.sin`, `math.cos` and `math.sqrt` go through `math_1` with `can_overflow = 0`. A NaN result from a non-NaN argument raises `ValueError`. An infinite result from a finite argument raises `ValueError`. A finite result with `errno` set may raise `ValueError` or `OverflowError` | [SRC] 3.12.15 `mathmodule.c:956-983, 886-923` | I-75 `external/cpython-3.12.15-mathmodule.c` | The I-75 NaN-`sin` countermodel can arise only by injection, never through this wrapper, if the deployed build matches this source. Also G-16 |
| S-5 | `math.atan2` is `math_2` over `m_atan2`. CPython itself handles NaN and infinite arguments: atan2(±y, +inf) = ±0 for finite y, and atan2(±inf, +inf) = ±π/4. A NaN from non-NaN arguments raises `ValueError`; an infinite result from finite arguments raises `OverflowError`. Otherwise the platform `atan2` is called | [SRC] `:546-571, :1031-1064` | Same file | Explains the p = +inf path |
| S-6 | `math.hypot` is CPython's own `vector_norm`, not libm `hypot`. It returns +inf for an infinite maximum, without raising and without an `errno` check | [SRC] `:2471-2659` | Same file | p can be +inf with no exception |
| S-7 | Documented: atan2's "result is between -pi and pi"; "A NaN will not be returned from any of the functions above unless one or more of the input arguments was a NaN"; `ValueError` for invalid operations and `OverflowError` for overflow | [LANG] | I-75 `external/python-3.12-math.html` | Explanation |
| S-8 | C11 §7.12.4.4: atan2 returns a value in [−π, +π] | Standard. I-75 verified it in N1570; the implementer did not re-read the PDF | `I-75/review.md:118` | Explanation; verifies no deployed libm |
| S-9 | libm `sin` and `cos` results are bounded (about 1 in magnitude) and finite for finite arguments; no spurious `errno` | [PLAT] | Not verified. **(corrected in v5, I77-02)** A-FP-2 (not accepted) would imply the bound \|computed\| ≤ 1 + 2⁻⁵¹ + 2⁻¹⁰⁷³. ~~and the values at ±0~~ **[WITHDRAWN v5]**: A-FP-2 does **not** imply sin(±0) = ±0 or cos(±0) = 1. Its absolute term allows sin(+0) = 2⁻¹⁰⁷⁴, and its relative term allows cos(0) = 1 − 2⁻⁵³ [RES-78]. Nothing in the project implies the `errno` property | Not relied on |
| S-10 | The CI builds (CPython 3.12.3 on Ubuntu, 3.12.10 on macOS) behave as the 3.12.15 source in S-4 to S-6 | [PLAT] | Not inspected (OD-11 and DL-7 territory) | Not relied on |
| S-11 | On the host, no `numerical_failure` occurred on any sampled set; \|sin\| ≤ 1 at every probed input; hypot overflow returns inf | [SAMP] | I-71, I-73, I-74 and I-76 probes | The expectation behind stop 17 only |

**D. A conditional explanation (H-2). It is for information only.** It is not an assumption, it is not proposed by default, and nothing in S2 relies on it. **(Repaired in v5, I77-02: narrowed to a conditional N1 explanation. The v4 sign and N2 steps are withdrawn below.)**

**H-2 is the conjunction of four parts:**
- A-FP-1;
- **A-FP-2 exactly as written** (`DR-0029-m3-t0-proposals.md:106` at K): "libm sin, cos, atan2, hypot, exp and pow satisfy |computed − exact| ≤ LIBM_ULP × 2^-52·|exact| + LIBM_ULP × 2^-1074 with LIBM_ULP = 2".
  - **[v5, I77-02]** v4 summarized this as "≤ 2 ulp plus 2·2⁻¹⁰⁷⁴". That is wrong. In units of ulp(exact) the relative term allows between 2 and 4 ulp: exactly 2 at |exact| = 1, about 3.14 near π/2, and almost 4 just below 2 [RES-78 `h2_correction_probe.out` §1].
  - A-FP-2 names "libm … hypot". CPython's `math.hypot` is its own `vector_norm`, not libm (S-6). So A-FP-2 says nothing about the computed p.
- **E-1:** sin, cos, sqrt and atan2 do not set `errno` spuriously for finite arguments with finite, in-range results;
- **W-1:** the deployed CPython wrappers behave as the 3.12.15 source in S-4 to S-6.

**The quantifier is every normalized input that passes steps 0 to 4**, not only accepted inputs. That removes the circularity I-75 identified.

**Derivation under H-2 [DER], repaired in v5. Its only conclusion is about N1.**
1. **The elementary results.** For a finite argument, A-FP-2 places each sin, cos and atan2 result within LIBM_ULP·2⁻⁵²·|exact| + LIBM_ULP·2⁻¹⁰⁷⁴ of the exact value, so each result is finite. With E-1 and W-1, no `math_1` or `math_2` wrapper raises (S-4, S-5). Python's float `+`, `−` and `×` do not raise (S-3, [SAMP]). So within E.1 the only remaining sources of an N1 exception are `/` and `sqrt`.
2. **The radicand.** Every computed sine satisfies |s| ≤ 1 + 2⁻⁵¹ + 2⁻¹⁰⁷³ < e2^(−1/2) ≈ 12.22, and is finite. By S-2, in DQ-1's actual grouping and for finite s, the rounded radicand is positive. So `sqrt` raises nothing and returns a positive value (A-FP-1: a square root is never subnormal), and `a / sqrt(…)` does not divide by zero. **Under H-2, N1 does not occur from `sqrt` or `/` in the loop or in the final height.**
3. **The sum z + e2·n·s.** n ≤ a/√(fl(1 − e2·(1 + 2⁻⁴⁹)²)), about 6.4 × 10⁶, so |e2·n·s| ≤ 4.3 × 10⁴. For finite z the sum is finite, so the arguments of every later `atan2` are finite or, for p, as CPython's `hypot` returns them.

**Withdrawn from v4 (I77-02).** These steps are kept as history and are not relied on:
- ~~4. The iterates. atan2(·, p > 0) is within 2 ulp of the exact principal value, which lies in (−π/2, π/2) and has the sign of z. So c = cos φ > 0, and sign(s) = sign(z), whenever the exact values are nonzero.~~ **[WITHDRAWN v5]** It does not follow. A-FP-2 allows atan2 to return `0x1.921fb54442d19p+0` = nextafter(fl(π/2), +∞) when the exact value is ≤ π/2. That value exceeds π/2 by 1.608e-16, inside the allowance of 6.976e-16 near π/2, and its cosine is **−1.6081e-16** [RES-78 `h2_correction_probe.out` §2; I-77 `independent_probe.out`]. This is a counterexample to the implication. It is not an observation of a deployed libm.
- ~~5. Signs of the height terms. p·c ≥ 0 and z·s ≥ 0, so their sum cannot be inf − inf … So h is finite or +inf, and never NaN. **N2 is unreachable.**~~ **[WITHDRAWN v5]** It rested on step 4. **No conclusion about N2 is drawn, under H-2 or otherwise.**
- ~~6. p = +inf … s = sin(±0) is within 2·2⁻¹⁰⁷⁴ of 0 … c = cos(±0) ≥ 1 − 2⁻⁵¹ > 0, so h = +inf. **The outcome is `overflow`.**~~ **[WITHDRAWN v5]** A-FP-2 says nothing about CPython's `hypot` (above), so it does not cover the path that makes p infinite. The step also used the sign reasoning of step 4. No outcome is claimed for an infinite p.

**Status of H-2:**
- A-FP-2 is not accepted (r2 §6.7).
- E-1 and W-1 are unverified.
- So H-2 explains only why N1 from `sqrt` and `/` is not expected. It **guarantees nothing**. **It says nothing about N2, about `overflow`, or about whether an accepted value is correct.**
- **Recheck against A-FP-2 (I-75; corrected in v5, I77-02):** v3's claim "parts (i) and (ii) are implied by A-FP-2" was correct only for the bound on |sin| and |cos|. It was not correct for exact values at ±0 (S-9). A-FP-2 says nothing about `errno` (E-1) or about the deployed wrappers (W-1). v3's part (iii) was a CPython recollection, which [SRC] now partly confirms for the 3.12.15 source only.

**E. What fault injection shows, and what it does not [I75-01].**
- **How it works.** G-16 replaces the evaluation library object `_LIB` for the duration of one test.
- **What it shows:** the component's handling of the injected behaviour:
  - the outcome and reason;
  - the chained cause;
  - the propagation of non-arithmetic exceptions;
  - the order under overlapping conditions;
  - the k = 60 and cap boundaries.
- **What it does not show:**
  - that any real library behaves that way;
  - that any library property holds or fails.
- Each G-16 case records which stratum row its injected behaviour departs from. For example, FI-01 (NaN from `sin`) departs from S-4 and S-9.
- **[I77-03, v5] Complete fixtures.** v4 overrode only selected functions, so the other calls in a case still went to the real `math`. A real value could then decide the outcome: for FI-07, I-77 showed that an un-stubbed `cos` of 0 turns `overflow` into `numerical_failure`. In v5 every fixture defines **every E.1 call it is used for**, from a declared call schedule, and nothing falls back to `math`. Only then are the outcomes independent of the platform library (§3.11 G-16).

**F. Disposition of S2-ASM-1′ (v3) [I75-01; D-S2-13].**
- **Recommended, (a): withdraw it, with no replacement assumption.**
  - Every S2 guarantee (G1 to G5, C1 to C5) holds without one.
  - Every numerical outcome that matters is observed at declared points per platform.
  - S2 then adds no `assumptions.md` entry.
- **Alternative, (b): record H-2 as PROPOSED** in `assumptions.md`, for the explanatory statements of D only.
  - It would need E-1 and W-1 verified and A-FP-2 promoted before any use.
  - Not recommended: no S2 gate or claim would use it.
- **Not offered: keeping S2-ASM-1′.** I-75's countermodels satisfy it while giving N2 (a NaN from `sin`) or `overflow` below the pre-bound (a huge `cos`). So it does not support v3's conclusions.
- No assumption is adopted by this proposal.

**Platform behaviour [DER]:**
- Whether a point **near** the overflow edge overflows depends on libm `sin`/`cos` results, so its classification can differ between platforms. RQ-3 applies.
- The gate tests therefore use only points that overflow, or stay finite, with a wide margin: the four probe inputs above, about 18% beyond or below the edge.
- The exact edge is not tested and not claimed.

**[OPEN] Alternatives:**
- **(b) Pre-bound.** Reject any |component| ≥ 2¹⁰²² before evaluation.
  - ~~Under S2-ASM-1′ this makes overflow impossible on accepted inputs, and gives a platform-independent domain.~~ **[WITHDRAWN v4, I75-01]** This is not proved. I-75's countermodel (`cos` returning 1e308) satisfies S2-ASM-1′ and overflows below the pre-bound. Even under H-2 (§3.7.8 D), it would make overflow impossible only for inputs well below the bound, and it would still be a library-dependent outcome.
  - Not recommended: it introduces a new domain constant, which arguably counts as a threshold (r2 §12, "thresholds … not authorized"). It also rejects inputs that evaluate finitely.
- **(c) No rule.** Return h = +inf. Rejected: it contradicts E1's "no overflow" domain and leaves a finite input with a non-finite result.

#### 3.7.8a Non-convergence rule [OPT-b] [F-01]

**Rule:** after the unchanged DQ-1 loop, if the loop ended by completing its 60th iteration **without** the stop test |φ_new − φ| ≤ 1e-15 having been met at any iteration, raise `GeodeticDomainError(reason="non_convergence", category="numerical")`. The full specification is §3.7.10.

**What it adds and what it leaves unchanged:**
- It adds no constant: 60 and 1e-15 are DQ-1's own values (`r1:93`).
- It adds no floating-point operation. The loop already evaluates the stop comparison; the rule records which way the loop exited, with a boolean set when the stop branch is taken.
- On accepted inputs the arithmetic is unchanged (r1 `:99`).

**Order:** after `numerical_failure` and `overflow` (§3.8 steps 6 to 8).
- A NaN forces the loop to run to its limit, because NaN ≤ 1e-15 is false. A NaN case must therefore be reported as `numerical_failure`, not `non_convergence`.
- ~~An infinite p converges in one iteration [RES]; it is reported as `overflow`.~~ **[WITHDRAWN v4, I75-01]** That is host-observed. v4 said it "holds under H-2 only"; **[v5, I77-02]** H-2 no longer establishes it either (§3.7.8 D, step 6 withdrawn). When a value is infinite, `overflow` is reported before `non_convergence` by definition, and G-16 FI-07 tests the overlap with a complete fixture.

**Platform behaviour:** see §3.22.
- Whether a point **near the edge** of the non-convergence set meets the stop test depends on libm results, so its classification can differ between platforms.
- Cross-platform agreement is required only at the declared far-from-edge G-14 points.
- Within a platform, agreement between component and twin is required at every listing entry labelled `passes`, near-edge points included (G-08). **[v5]** Geometric rejects are asserted by G-17 instead.
- The G-14 selection rule is a test-design choice for owner approval, not a component threshold. The component contains no margin.

**What it does not establish:** the stop test is not an accuracy certificate.
- Where it is met with a contraction factor L near 1, the error can exceed 1e-15: 2.76e-15 rad was observed with L ≈ 0.75 [RES].
- The a-posteriori bound |φ_n − φ*| ≤ L/(1 − L)·|φ_n − φ_{n−1}| applies.
- Accepted interior points stay report-only, with no accuracy claim.

#### 3.7.10 Evaluation and post-evaluation behaviour, specified exactly [OPT-b] [UNIV by inspection; DER where marked] (corrected in v4: I75-01, I75-03, I75-04, I75-05)

**Scope.** This subsection applies only to inputs that have passed steps 0 to 4 of §3.8.
- x, y and z are therefore **built-in** binary64 values, produced by the normalization of step 0 (I75-04).
- They are finite, outside E, and not the origin.

**E.1 The evaluation block** is DQ-1 steps 2 to 5 (`r1:91-94`). Every floating-point operation and its order are unchanged:

```
p   = _LIB.hypot(x, y)
phi = _LIB.atan2(z, p * (1.0 - e2))
converged = False                          # boolean bookkeeping only; no floating-point operation
for k in 1 .. 60:
    s       = _LIB.sin(phi)
    n       = a / _LIB.sqrt(1.0 - e2 * s * s)
    phi_new = _LIB.atan2(z + e2 * n * s, p)
    stop    = abs(phi_new - phi) <= 1e-15  # DQ-1's stop test, evaluated after the update
    phi     = phi_new
    if stop: converged = True; break
s = _LIB.sin(phi); c = _LIB.cos(phi)
h = p * c + z * s - a * _LIB.sqrt(1.0 - e2 * s * s)
```

- **Additions to r1 §5.** The only additions are the boolean `converged` and the `break` on the stop branch. The stop branch was already DQ-1's "Stop after the update".
- `k` is the loop counter that DQ-1's "at most 60 times" already implies.
- **[I75-01] The evaluation library.** `_LIB` is a module-level reference, bound to `math` at import. It is used **only** inside E.1.
  - Fault injection (G-16) replaces `_LIB` for one test.
  - The post-checks of E.5 use `math.isnan` and `math.isinf` through separate names bound at import, so an injected library cannot affect them.
- **[I75-05] The `try` covers exactly E.1,** from the `hypot` call to the height expression, and nothing else.
  - The guard (steps 0 to 4) and the post-checks are outside it.

**E.2 Convergence.**
- The input **converged** if and only if the stop test evaluated True at some update k with 1 ≤ k ≤ 60.
- This **includes k = 60**: the stop test met on the 60th update counts as convergence.
  - [RES-76] On the host, 139 natural points of DG-CUSP meet the stop test at exactly k = 60, including I-75's witness (`0x1.b8a74054b25cap+15`, 0, `0x1.0624dd2f1a9fcp-10`).
  - G-16 FI-11 also gives a controlled, platform-independent k = 60 witness (I-75).
- The returned φ is the iterate after that update, and h is computed from it by DQ-1 step 5.

**E.3 Non-convergence.**
- The input **did not converge** if and only if all 60 updates ran and the stop test was False at every one.
- DQ-1 step 5 is still evaluated, so that the post-checks see h.
- The resulting (h, φ) are then **discarded**. They are never returned as a result, and never attached to the exception.

**E.4 Non-finite intermediates (rewritten in v4) [I75-01].**
- **No claim is made about which intermediates can be non-finite.** That depends on the values the library returns (§3.7.8 B).
- **What the construction ensures (§3.7.8 A).** ~~whatever happens inside E.1 ends in exactly one of three ways~~ **[WITHDRAWN v5, I77-02]**: v4's list of three endings omitted the successful ones. **Whatever happens inside E.1, the call ends in exactly one of these six ways, decided in the order N1 to N5:**
  - **(i)** an `ArithmeticError` or `ValueError` is raised inside E.1: `numerical_failure` (N1);
  - **(ii)** another exception is raised inside E.1: it propagates unchanged (G3);
  - **(iii)** p, φ or h is NaN: `numerical_failure` (N2);
  - **(iv)** p, φ or h is ±inf, and none is NaN: `overflow` (N3);
  - **(v)** all are finite, and the stop test was never met: `non_convergence` (N4);
  - **(vi)** all are finite, and the stop test was met: **the pair is returned** (N5).
- **A misbehaving library can reach any of the six.** In particular it can yield (vi) with a **wrong finite value**, or (iv) or (v), and none of these is detected by the construction. I-77's countermodel with `sin` returning 0 is accepted with a wrong finite latitude [RES-78 `h2_correction_probe.out` §4]. That is consistent with the no-accuracy contract (§3.21): N5 never means "accurate".
- **The masking path (v3), kept as an observation and no longer relied on.**
  - An infinite z + e2·n·s gives a finite atan2 (±π/2, or ±π/4 when p = +inf; [SRC] S-5), and that hides the infinity.
  - v3 argued that this path ends in an exception. That argument rested on S2-ASM-1′, and v4 does not rely on it.
  - Whether or not the path occurs, the outcome is one of the six endings above. At worst, a masked infinity yields a wrong finite φ, which may be returned (vi).
  - That is an accuracy question, and no accuracy is claimed (§3.21). It is never a returned non-finite value.
- The behaviour under the conditional premise H-2 is in §3.7.8 D. It is explanation only.

**E.5 Post-evaluation checks, in this order. The first that applies wins:**

| Step | Condition | Outcome |
|---|---|---|
| N1 | An `ArithmeticError` (including `ZeroDivisionError` and `OverflowError`) or a `ValueError` raised inside E.1. No other exception type is caught | `GeodeticDomainError(reason="numerical_failure", category="failure")` [D-S2-4 (j); v3: `"numerical"`], with the original exception chained as `__cause__` |
| N2 | p, φ or h is NaN | `numerical_failure` (category as N1) |
| N3 | p, φ or h is ±inf | `overflow` (category `numerical`) |
| N4 | `converged` is False | `non_convergence` (category `numerical`) |
| N5 | Otherwise | Return (h, φ) as built-in floats |

**Why this order:**
- **NaN before overflow.** NaN means the evaluation failed in a way whose cause is undetermined. inf means the binary64 range was exceeded.
- **NaN before non-convergence.** A NaN φ makes every stop test False. Without this order, an evaluation failure would be reported as non-convergence.
- **Overflow before non-convergence (corrected in v4) [I75-01].** The order is fixed by definition: an evaluation whose values left the binary64 range is reported as `overflow`, whether or not the stop test was met.
  - ~~an infinite p always converges (E.4). So swapping the two is not observable on conforming platforms … The order mutant is a documented equivalent survivor~~ **[WITHDRAWN v4]**. That relied on S2-ASM-1′.
  - The order is now **tested** by G-16 FI-07, in which p = +inf and the iteration does not converge. The order mutant is killed (§3.12).

**Reachability (rewritten in v4) [I75-01]:**
- **No premise makes N1 or N2 unreachable.** v3's "unreachable on conforming platforms" is withdrawn.
- **What is known (corrected in v5, I77-02):** under the conditional H-2, N1 would not occur from `sqrt` or `/` (§3.7.8 D). ~~under the conditional H-2 they would not occur~~ **[WITHDRAWN v5]**: nothing is concluded for N2, under H-2 or otherwise. On the host neither occurred on any sampled set [SAMP; RES-78: 0 among 22 593 geometry-passing listing entries; **[v6]** RES-80: 0 among the 22 601 of the v6 listing].
- **How they are tested:** by fault injection (G-16), which verifies **handling** only.
- **A non-injected occurrence on any platform** is stop 17. It is investigated; it is not explained in advance.
- N3 is reachable (G-05). N4 is reachable (G-14).

**E.6 What each outcome means:**
- **N5 (accepted):** DQ-1's own stop test was met within its limit, and the outputs are finite. **It does not mean the outputs are accurate** (§3.21). **[v5, I77-02]** Under a misbehaving library, an accepted pair can be a wrong finite value. Nothing in S2 detects that, except an accuracy observation at a reported point.
- **N4:** DQ-1, as specified, did not meet its stop criterion on this platform for this input.
  - It is **not** a statement that the geodetic solution does not exist. Outside E the principal same-quadrant solution exists and is unique (§3.20.1).
- **N3:** a value of the evaluation left the binary64 range on this platform.
- **N1/N2 (`numerical_failure`), rewritten in v4 [I75-05]:** the evaluation failed.
  - **The cause is undetermined.** It may be an implementation defect (a wrong expression or denominator, say), an input-normalization defect, or library behaviour. These are indistinguishable at this boundary.
  - It is **not** a domain classification. It is never evidence that domain handling is valid, and never a statement that a particular assumption failed.
  - The chained `__cause__` preserves the original traceback for investigation.
  - S4 and T3 must not handle it as an ordinary numerical domain rejection (§3.18 item 15).

#### 3.7.9 Summary: what is established, what the review must establish

**Established by existing records [REQ]:**
- the rejections must exist;
- U-20 is an unconditional exact gate;
- DQ-1 is unchanged on accepted inputs;
- negative heights are report-only;
- no threshold may be created.

**Established by probe only (host, corroboration):**
- sign agreement of the two predicate forms on 10 points (I-71);
- the overflow behaviour on 6 inputs (I-71), and on 11 inputs including the 2⁵¹² points (I-73);
- the cost figures (I-71);
- **[RES], I-73:**
  - the boundary pairs on 8 rays by two independent formulations;
  - the F-01 counterexamples against a rigorously enclosed reference.

**Checked by the I-72 same-provider review:** R-P1 to R-P3, the check order and DQ-1 preservation. To be re-checked by the separate-provider review.

**Checked by the I-75 separate-provider review of v3:**
- R-P1 was technically sound; R-P2 and R-P3 PASS; R-P17 PASS at design level.
- **R-P4 and R-P15 FAIL** (I75-01). §3.7.8 and §3.7.10 are rewritten in response.
- I-75's results are review evidence, not owner approval.

**To be established by the separate-provider re-review (§5.1):**
- **R-P1:** the evolute characterization and the Jacobian argument (§3.7.2).
- **R-P2:** the exactness and equivalence of the polynomial predicate (§3.7.4).
- **R-P3:** the soundness of the pre-filter (§3.7.5).
- **R-P4 (v4; v5):** the construction guarantees G1 to G5 without a library premise, the strata table, the repaired conditional H-2 (N1 only; steps 4 to 6 withdrawn), the six endings of E.4, and the withdrawal of S2-ASM-1′ (§3.7.8, §3.7.10).
- **R-P5:** the closed-region choice, and its consistency with P8 and OD-12.
- **R-P13:** the F-01 analysis of §3.20, and the option (b) rules and claims (§3.7.8a, §3.7.10, §3.21 to §3.23).

**Recorded in S2 (if authorized):**
- a derivation note, `docs/science/experiments/m3-t2/s2/evolute-guard-derivation.md`, holding §3.7 as reviewed;
- **[I75-01]** no `assumptions.md` entry under the recommended D-S2-13 (a). Under (b), an entry for H-2, status PROPOSED, used for explanation only.
<!-- END VERBATIM -->
