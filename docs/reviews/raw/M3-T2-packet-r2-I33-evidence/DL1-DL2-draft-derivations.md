# DL-1 / DL-2 draft derivations (I-33 §9)

**Status: DRAFT — UNREVIEWED. Not an accepted proof.** These derivations support the corrected packet r2 (§6.3, §6.4, §6.9). Each one is a **proof obligation** for the T2 independent review (P-ii). No row may gate on them until that review passes and the owner promotes the row (P-iii).

The implementation that accompanies them is `pog_lib.py.txt` and `witness.py.txt`. It is research code: it is not T2 code, and it is not a T2 test.

## 0. Notation and the premise
- **Binary64 values.** Every binary64 value x is converted exactly to a rational, written Fraction(x). An enclosure of an exact real value f is a pair of rationals [lo, hi] with lo ≤ f ≤ hi.
- **A-FP-2** (`t0_termination.py` lines 455–457 and 474–475). For f̂ = lib(args) and f the exact value:

  |f̂ − f| ≤ UF·|f| + ν, with UF = 2·2⁻⁵² and ν = 2·2⁻¹⁰⁷⁴.

  This is a relative-plus-absolute bound. It is **not** a count of ulps. For a normal f in [2ᵉ, 2ᵉ⁺¹), it allows between 2 and 4 ulps, depending on where f lies in the binade (`f2_premise_controls.out`).
- **A-FP-1.** +, −, ×, ÷ and sqrt are IEEE 754 binary64 operations with round-to-nearest-even and gradual underflow. This assumption is already accepted unconditionally (strategy B-1, B-2; checked at run time by X-P4).

## 1. O-1, the premise oracle (DL-1)
### 1.1 Square roots of rationals (`sqrt_enc`)
**Lemma 1.** For a rational q > 0 and an integer k ≥ 1, let s = isqrt(⌊q·4ᵏ⌋). Then s/2ᵏ ≤ √q ≤ (s + 1)/2ᵏ.

*Proof:* s² ≤ ⌊q·4ᵏ⌋ ≤ q·4ᵏ < ⌊q·4ᵏ⌋ + 1 ≤ (s + 1)². ∎

- k is chosen so that the width 2⁻ᵏ is at most 2⁻⁽³²⁰⁺⁸⁾·√q.
- When the numerator and denominator of q are both perfect squares, the root is returned exactly.

### 1.2 sin and cos, for |x| ≤ 2 (`sin_enc`, `cos_enc`)
- **Series.** sin x = x·Σₖ (−1)ᵏ cₖ with cₖ = x²ᵏ/(2k + 1)!, and cos x = Σₖ (−1)ᵏ dₖ with dₖ = x²ᵏ/(2k)!.
- **Term ratios.**
  - sin: cₖ₊₁/cₖ = x²/((2k + 2)(2k + 3)), at most 4/6 for |x| ≤ 2.
  - cos: dₖ₊₁/dₖ = x²/((2k + 1)(2k + 2)), which is below 1 from k = 1 onward. The k = 0 ratio x²/2 may exceed 1.

  Both ratios decrease in k.

**Lemma 2 (alternating series).** Let tₖ ≥ 0 be non-increasing in k from index n onward, with tₖ → 0. Then |Σₖ (−1)ᵏ tₖ − Sₙ| ≤ tₙ, where Sₙ is the partial sum of the terms before index n.

- **Source obligation:** this is Leibniz's criterion, a standard result. The DL-1 review must cite a text.
- **Stopping rule.** The implementation stops only when the current ratio is below 1. All later ratios are then smaller, so the hypothesis of Lemma 2 holds from the first omitted term on.

**Lemma 3 (directed fixed point).** The terms are held as integers C_lo ≤ cₖ·2^FP ≤ C_hi.
- The recurrence uses C_lo′ = ⌊C_lo·u/step⌋ and C_hi′ = ⌈C_hi·u/step⌉ with u = x² ≥ 0, which preserves the invariant.
- Signed sums add the lower or upper bound according to the term's sign.
- Multiplying the final enclosure by x is exact. For x < 0 it swaps the two ends.
- *Proof:* by induction on k. ∎ (Obligation: the T2 code review must check the implementation against this.)

**Zero.** sin(±0) = ±0 and cos(±0) = 1 are returned exactly. These are identities, not approximations.

**Domain and refusal.** For |x| > 2 or a non-finite x, the function raises, so it fails closed.
- DQ-1 calls sin and cos only at latitudes λ = atan2(·, p) with p ≥ 0.
- Therefore |λ| ≤ fl(π/2) < 2.

### 1.3 exp (`exp_enc`)
For x ≠ 0:
1. Let t = |x|/2ᵐ ≤ 1/2.
2. Sum S_N = Σ_{k<N} tᵏ/k!. The tail satisfies Σ_{k≥N} tᵏ/k! ≤ (t^N/N!)/(1 − t/(N + 1)), because every later term ratio is at most t/(N + 1) < 1 (geometric majorant).
3. Square the positive interval m times. Squaring is monotone on positive intervals.
4. For x < 0, take the reciprocal, [1/hi, 1/lo].
5. Every intermediate is rounded outward to at least PREC + 140 bits.

exp(±0) = 1 is returned exactly. exp_enc accepts exact rationals as well (it is used for E3's upper enclosure in `f3_density`).

### 1.4 atan2, for x ≥ +0 (`atan2_enc`)
- **Special values.** atan2(±0, x > 0) = ±0 exactly, an identity. atan2(y ≠ 0, +0) = sign(y)·π/2. atan2(0, 0) is refused, since the origin is rejected by P8.
- **Main case, |t| ≤ 1 with t = y/x exact.** Euler's series:

  atan t = (t/(1 + t²))·Σₖ cₖ wᵏ, with w = t²/(1 + t²) ≤ 1/2, c₀ = 1 and cₖ₊₁ = cₖ·(2k + 2)/(2k + 3).

  The terms are positive, and every term ratio is at most w, so the tail after a term T is at most T·w/(1 − w). This is bounded through Lemma 3's directed fixed point.
- **|t| > 1.** atan t = sign(t)·π/2 − atan(1/t).
- **π.** Machin's formula, π/4 = 4·atan(1/5) − atan(1/239).
- **Source obligation:** Euler's series and Machin's formula are classical, but **I-33 did not read a primary or textbook statement of Euler's series.** I-33 validated both numerically only:
  - π lies inside its enclosure, checked against 110 published digits;
  - 304 atan2 arguments agree with T0's independent `d_atan2` at 130 digits (`pog_pipeline.out` Part 1).

  The DL-1 review must cite an authoritative statement of both, or the atan2 enclosure stays unreviewed.

### 1.5 hypot (`hypot_enc`)
The exact √(x² + y²), by Lemma 1, applied to the exact rational x² + y².

This is the **aggregate contract** of `math.hypot`, which is what E1 uses. CPython's internal compensated sums and internal square roots are not observed, and E1 does not need them.

### 1.6 The premise decision (`premise`)
**Lemma 4.** Let g(f) = |f̂ − f| − UF·|f| − ν on an enclosure [lo, hi] that does not contain 0 in its interior.
- On that interval, −UF·|f| is linear and |f̂ − f| is convex, so g is convex.
- So max g is attained at lo or at hi, and min g is attained at lo, at hi, or at f = f̂ if f̂ lies in [lo, hi].

The decisions follow:
- **PASS** iff max g ≤ 0: the premise holds for every f in the enclosure, and so for the true f.
- **FAIL** iff min g > 0: the premise is violated for the true f.
- **INCONCLUSIVE** otherwise. The gate treats it as PREMISE-NOT-OBSERVED, which fails closed. If 0 lies inside the enclosure, the decision is INCONCLUSIVE.

**Cross-check.** The F2 controls compare `premise` with the closed form, derived separately for f > 0:
- PASS iff hi·(1 − UF) − ν ≤ f̂ ≤ lo·(1 + UF) + ν;
- FAIL iff f̂ < lo·(1 − UF) − ν or f̂ > hi·(1 + UF) + ν.

**Zero and zero crossings** (observation C). In DQ-1's call domain an exact value is 0 only through an identity: hypot(0, 0), atan2(±0, x > 0) and sin(±0). The oracle then returns the exact [0, 0]. Otherwise the exact value is nonzero, and the enclosure excludes 0:
- sin x ≠ 0 for 0 < |x| ≤ 2 < π;
- cos x = 0 only at ±π/2, which is not a binary64 value;
- atan2(y ≠ 0, x ≥ 0) ≠ 0;
- exp is never 0.

No absolute precision is ever required. For values far below the subnormal range, the absolute term ν dominates, and the enclosure only has to be narrow compared with ν.

### 1.7 sqrt correct rounding (`sqrt_is_rn`; F6)
**Lemma 5.** Let r > 0 be a binary64 value with neighbours r⁻ < r < r⁺. Then r = RN(√a) iff:
- m⁻² ≤ a ≤ m⁺², with m^± = (r + r^±)/2;
- and, where a = m^±² (a tie), the significand of r is even.

The spacings r − r⁻ and r⁺ − r differ at a binade boundary, and the lemma uses each one separately.

**No ties occur.** A midpoint is M·2ᵏ with M odd and 2⁵³ ≤ M < 2⁵⁴. Its square has odd integer part M² ≥ 2¹⁰⁶, so it has at least 107 significant bits and is never a binary64 value a.

The I-31 predicate |r − √a| ≤ ulp(r)/2 takes the half-gap from above. Below a power of two that half-gap is twice the true one, so the predicate accepts 1.0 for a = nextdown(1) (`f6_sqrt.out`).

## 2. O-2, the true-height oracle (DL-2; `true_height_enc`)
- **Model ellipsoid.** K = {p²/a² + z²/b² ≤ 1}, with a = 6378137 and b² = a²(1 − e2). Here e2 is the binary64 value of DQ-1 step 1, so b² is rational and b = √(b²) is enclosed by Lemma 1.

**Lemma 6 (height and distance).** For r outside K, the geodetic height of r equals dist(r, K):
- the nearest point of a closed convex set is unique;
- the segment to it is normal to the surface.

**Source obligation:** the same fact underlies E1 (i) (`t0_termination.rounding_allowances` docstring: "the distance to a convex body is the maximum over supporting planes"), and `t0_oracle.true_height` computes the same quantity. The DL-2 review must cite it.

**Lemma 7 (upper bound).** For any point Q* on ∂K, h ≤ |r − Q*|.
- Q* is taken in r's meridian half-plane, with one coordinate rational (from a high-precision foot point) and the other given by Lemma 1 from the ellipse equation. So Q* lies exactly on ∂K, inside a known box.
- |r − Q*| is bounded above by interval arithmetic: (p − p_Q)² + (z − z_Q)², with p = √(x² + y²) enclosed.

**Lemma 8 (lower bound; support function).** For any m ≠ 0, K ⊂ {X : m·X ≤ σ(m)}.
- σ(m) = max over X in K of m·X = |A·m|, with A = diag(a, a, b), so σ(m) = √(a²(m_x² + m_y²) + b²·m_z²).
- Hence dist(r, K) ≥ (m·r − σ(m))/|m|.
- With m in r's meridian, m·r = m_p·p + m_z·z.
- L is that bound, rounded downward.

**Certification.**
- L ≥ 0 certifies h ≥ 0, which is E1's domain.
- L < 0 gives NOT-CERTIFIED-EXTERIOR: E1 is not applied, and the point is reported.

**Width.** The width depends only on the quality of the foot point. Lemmas 7 and 8 hold for any choice. I-33 measured:
- at most 2.8e-92 m (measured 2.72e-92) over the 633 I-31 points;
- the requirement is δ_O ≤ 1e-6·β = 8.9e-15 m;
- exact collapse to x − a on the equator (`pog_pipeline.out` Part 2).

These are measurements. The bound itself rests on Lemmas 6–8.

## 3. Propagation of oracle uncertainty (observation A)
- **No oracle term is added to any tolerance.** Uncertainty is handled by deciding over the whole enclosure (Lemma 4 for the premise; Lemma 9 for E1), and an undecided case fails closed.

**Lemma 9 (strict E1).** Let g(h) = |ĥ − h| − α·h − β on [L, U], with L ≥ 0. g is convex. Then:
- **PASS** iff g(L) ≤ 0 and g(U) ≤ 0, which implies |ĥ − h| ≤ α·h + β for the true h;
- **FAIL** iff min g > 0;
- **INCONCLUSIVE** otherwise, which fails closed.

α and β are the exact Fractions returned by `rounding_allowances()` (observation D).

**Why packet r2's rule 6 is dropped.** That rule, |ĥ − h_ref| ≤ ε_h(h_ref + δ) + δ, admits outputs that violate E1 at the true height by up to 2(1 + α)·δ. With δ = 1e-6·β, 80 binary64 outputs near 1 m are admitted by the old rule and INCONCLUSIVE under the strict rule (`observations.out` A).

## 4. Applicability of E1 on the observed finite domain (witnessed evaluation)
E1's hypotheses are listed in the `rounding_allowances` docstring and strategy B-12. The table shows how each one is established at one gated point.

| Hypothesis | Established by | Kind |
|---|---|---|
| H1. The evaluated sequence is DQ-1 (α), operation for operation (≤ 60 updates, stop at \|Δφ\| ≤ 1e-15) | The twin is transcribed from the r1 §5 text and reviewed (P-ii). The component's (φ, h) equal the twin's **bitwise**. The T0 spike is a second, independent transcription (X-D1; bitwise at 5/5 points in `f1_witness.out` and 633/633 in `pog_pipeline.out` Part 3, where no correct-component point is nonconformant) | review + exact observation |
| H2. The binary64 model ellipsoid (a, e2) | Constants from the DQ-1 text; RQ-2 bit identity | exact observation |
| H3. A-FP-1 for +, −, ×, ÷ | Accepted unconditionally (B-1, B-2), checked by X-P4 run-time probes. **Not checked per operation** | assumption (accepted) |
| H3′. sqrt correctly rounded | Lemma 5 at **every** sqrt call the twin makes | exact observation |
| H4. A-FP-2 for hypot, atan2, sin, cos | Lemma 4 on **every** call result the twin's arithmetic consumes. The twin is complete by construction, verified by the call-list assertion and by fault injection at every call index | bounded observation |
| H5. True height ≥ 0 | O-2: L ≥ 0 | bounded observation |
| H6. No overflow | Every arithmetic and library intermediate of the twin is finite (observation B) | exact observation |
| H7. E1's derivation is correct | T0 Reviews 03–10 (accepted for reuse on its domain, DQ-1). The O-2 comparison is a consistency check that would expose a gross error | review |

- **Conclusion (drafted).** Suppose H1–H7 hold at a point:
  - E1 states that the DQ-1 output, evaluated with any elementary results satisfying A-FP-2 under A-FP-1, is within α·h + β of h;
  - the twin's output is such an evaluation;
  - the component's output equals the twin's bit for bit.

  Therefore |ĥ − h| ≤ α·h + β at that point.
- **Why this needs no trace of the component** (F1). The claim concerns the output **value**. What the component computed internally is irrelevant once its output equals a premise-satisfying evaluation of the specified sequence.
- **What it does not give:**
  - A-FP-2, or any accuracy, at points that were not gated;
  - any cross-platform statement;
  - any statement about the component's internal behaviour beyond its returned values at the gated points.

## 5. Open proof obligations (for the T2 independent review)
1. Lemmas 1–9 reviewed. Citations supplied for Leibniz's criterion, Euler's arctangent series, Machin's formula and Lemma 6.
2. The implementations reviewed against the lemmas, in particular the directed-rounding invariants (Lemma 3, the outward rounding in exp and atan) and the refusal paths.
3. The witness argument (§4) reviewed, including H3: A-FP-1 is assumed for the arithmetic operations, not observed per operation.
4. The same drafts, or their T2 versions, rerun on each CI platform (RQ-8). That needs the T2 authorization; it is not done here.
5. Until items 1–4 are complete, **every A-FP-2-dependent accuracy row stays report-only, and POG accuracy gating stays BLOCKED** (packet §6.7).
