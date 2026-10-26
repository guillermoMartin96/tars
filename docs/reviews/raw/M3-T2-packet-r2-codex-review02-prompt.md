You are an independent reviewer from a separate provider. You did not write any file under review, and you have no context from earlier reviews: Review 01 was a different session. This is **independent Review 02** of the TARS M3 T2 implementation authorization packet, revision 2, **as corrected under I-33**: `docs/milestones/M3-T2-implementation-authorization-packet.md`. Independent Review 01 (record `docs/reviews/M3-T2-packet-r2-review-01.md`; its raw output is reproduced verbatim below) returned REQUEST_CHANGES. The owner authorized a bounded correction pass and this review under I-33, reproduced verbatim at the end. **The implementer's documents, scripts and outputs are claims, not evidence.**

## Snapshot and rules
- **The current directory** is a fresh git clone, detached at the pinned head **`5f96119bcc54d2154cdff50a873791f5f9b26d73`** (branch `milestone-3-t2-authorization`, the I-33 correction commit). Relevant ancestors:
  - `43a6c29e3080f6b529c5635565324c615c11dfb7`: the Review 01 record (the I-33 baseline);
  - `0e37db60eed706e041666b40abb5238609a83360`: packet r2 as reviewed by Review 01;
  - `0a9c040430138845d529b3d8691a86d0f4fea61e`: `main`.

  The correction is `git diff 43a6c29..5f96119` (all under `docs/`).
- A locked Python environment (CPython 3.12.15, macOS x86_64) is in `./.venv`. Use `.venv/bin/python -I`, with `PYTHONDONTWRITEBYTECODE=1` when importing the T0 spike. **The network is not available.**
- **Do not modify tracked files.** Use only `./review_scratch/` for scratch; it is excluded from git.
  - Put every script you write there, named `*.py`, with its output as `*.out` beside it, so that the implementer can preserve them.
  - To run the implementer's evidence, copy `docs/reviews/raw/M3-T2-packet-r2-I33-evidence/*.py.txt` into `review_scratch/` as `*.py`. Its README gives the arguments.
  - Do not run the M1/M2 proof scripts.
  - Finish with a clean tracked tree.
- **Extra read-only input outside the repository:** the CPython v3.12.15 `Modules/mathmodule.c` cited by packet §6.5, at `/private/tmp/claude-501/-Users-guillermomartin--superset-worktrees-tars-cliff-tarsier-2d0cbac0/13fee5d3-8f4b-4074-8c17-5b993d6398a2/scratchpad/r02/inputs/mathmodule.c` (via `--add-dir`). Its stated sha256 is `436a01da195e3c2b9576a4b9188d5d62e9883e62e74f2d60bc55194bfce98281`; verify it. Web sources are not available to you. Say where a finding depends on them.
- **Preconditions already performed by the implementer (treat as claims):**
  - the I-33 §1 checks at `43a6c29`;
  - the push of `5f96119`;
  - CI for `5f96119`, which may still be running.
- **Decision boundaries.** You review; you do not decide, approve or fix anything.
  - Do not treat D-0 … D-8, P6, DR-0028 P6(b), X-1, A-FP-2, A-LM-1 or A-LM-2 as approved.
  - Do not propose an unapproved CI or runtime migration, or a language migration.
  - Do not silently correct anything.

## What is under review
- **The corrected packet:**
  - §2.2 DL-1 … DL-7;
  - §3 testability;
  - §6.1–§6.9, especially §6.3 "witnessed evaluation" and §6.4 rules 1–7;
  - §7 RQ-4 and §7.1;
  - §8.2, §8.3, §10, §11, §13 item 2, §14 D-0 … D-8 and §16.
- **The correction record:** `docs/reviews/M3-T2-packet-r2-review-01-corrections.md`.
- **The evidence:** `docs/reviews/raw/M3-T2-packet-r2-I33-evidence/`, including `DL1-DL2-draft-derivations.md` (declared unreviewed) and the draft oracles, witness and probes.
- **Context to read yourself:**
  - packet r1 (`docs/milestones/M3-T2-authorization-packet-r1.md`, §5 DQ-1/DQ-2 and §6.2 J-FP2/J-LM1/J-LM2);
  - `docs/milestones/M3-T2-validation-strategy.md`;
  - DR-0024 … DR-0029;
  - `docs/science/experiments/m3-t0/t0_termination.py` (`rounding_allowances`, A-FP-1/A-FP-2 at about lines 440–475, and the E1 derivation in the docstring);
  - `t0_model.py` and `t0_oracle.py`;
  - RES-0001 and ADR-0008, via `git show origin/research/flight-software-architecture:<path>`.

## What you must independently assess (I-33 §11)
1. **F1–F6.** For each, decide RESOLVED, PARTIALLY RESOLVED or NOT RESOLVED, with your reasons. Reproduce the important counterexamples yourself, in your own scripts, not only by rerunning the implementer's:
   - Review 01's hidden-cosine mutant;
   - sin(1) + 3 ulps and a constructed definite violation;
   - the scale-height mutant;
   - sqrt(nextdown(1)) → 1.0;
   - the shared faulty `math`.
2. **The five observations A–E**, each resolved or not.
3. **Whether the corrected POG strategy (witnessed evaluation) is scientifically defensible.** Examine in particular:
   - whether "the component's output is bitwise equal to a premise-satisfying evaluation of the specified sequence, hence E1 bounds it" is valid, and exactly which hypotheses it needs;
   - whether E1's derivation applies to the twin's evaluation as written (operation order, grouping, iteration and stopping, underflow terms, the sqrt and arithmetic assumptions);
   - whether anything is left unobserved that E1 needs (the packet says A-FP-1 for +, −, ×, ÷ is assumed, not observed);
   - whether the twin is a faithful transcription of DQ-1/DQ-2 (compare it with the r1 §5 text and with `t0_model.py`);
   - whether the completeness self-test (call list, per-index fault injection) is adequate;
   - whether the premise decision (convexity over the enclosure) and the strict E1 decision are correct, including signs, zero, subnormal and boundary cases;
   - whether the draft DL-1 enclosures (series remainder bounds, directed fixed-point rounding, exp squaring, Euler's arctangent series, Machin's formula) and the draft DL-2 enclosure (support-function lower bound, on-ellipsoid upper bound, exterior certification) are mathematically sound, as far as you can check them;
   - **adversarial counterexamples**: try to build a component, a library behaviour or an input for which the witness reports E1-PASS while E1's conclusion fails, or for which an oracle enclosure fails to contain the true value. Also check whether anything fails open.
4. **Remaining unproved assumptions:** list them explicitly.
5. **D-0 … D-8, reassessed individually.** For each give:
   - Recommendation: APPROVE, REVISE, DEFER or REJECT;
   - justification;
   - required evidence;
   - dependencies;
   - consequences of approval;
   - remaining blocker.
6. **Newly introduced contradictions,** inside the packet or against r1, the validation strategy, DR-0024 … DR-0029, the I-33 limits (no implementation, no decision changes, no protected paths) or the scope exclusions (T3/T4/T5, P6/P6(b) open, X-1 unauthorized, unjustified assumptions report-only, implementation completion separated from scientific acceptance).
7. **Accuracy of the correction record and evidence:** numbers, counts, file references and the stated validation results. Check that the evidence checksums verify, and that the reruns are byte-identical where claimed.

## Output format
Markdown:
1. First line exactly one of: `VERDICT: PASS`, `VERDICT: REQUEST_CHANGES` or `VERDICT: BLOCKED`.
2. A summary.
3. A findings table with these columns:
   - ID (M3T2P2-R2-Fn);
   - severity (BLOCKER / MAJOR / MINOR / NOTE);
   - location (file:line);
   - finding;
   - evidence;
   - recommended disposition.
4. The F1–F6 and A–E resolution table.
5. The assessment of POG's scientific defensibility.
6. The remaining unproved assumptions.
7. The D-0 … D-8 table, with all six fields for each decision.
8. Contradictions found, if any.
9. Your own computations: commands and outputs, and a list of the files in `review_scratch/`.
10. Limitations.

**Severity guide:**
- **BLOCKER:** a scientific or prerequisite defect that prevents owner decision review, or a claim of justification that is false.
- **MAJOR:** an unsupported or misleading scientific claim; a gate that can pass despite a meaningful defect without saying so; something that fails open; an approval presented as made; a scope violation.
- **MINOR:** an inaccuracy or gap that does not change a decision, a classification or a gate.
- **NOTE:** clarity.

PASS means no BLOCKER or MAJOR finding remains, and that the packet is suitable for owner decision review. It does **not** authorize T2 implementation or any numerical gate. State explicitly whether any MINOR finding remains.

## Review 01 raw output (verbatim, `docs/reviews/raw/M3-T2-packet-r2-codex-review01.md`)

VERDICT: REQUEST_CHANGES

## 1. Summary

**Findings: 0 BLOCKER, 3 MAJOR, 2 MINOR, 1 NOTE.**

POG is scientifically plausible for explicitly fixed finite executions, but the proposed tracing and mutation requirements need correction. The numerical error budget reproduces, and the supplied CPython source supports the proposed `hypot` evenness argument.

All three I-31 probes reproduced **byte-for-byte** on this host. No tracked files changed.

The detailed review is preserved in [review.md](review_scratch/review.md), with a structured register in [findings.json](review_scratch/findings.json).

**These are review recommendations only. No decision is approved, no row is promoted, and T2 remains NOT AUTHORIZED.**

## 2. Findings

Packet locations below refer to `docs/milestones/M3-T2-implementation-authorization-packet.md`. Reproduction evidence is in [independent_checks.out](review_scratch/independent_checks.out).

| ID | Severity | Location (file:line) | Finding | Evidence | Recommended disposition |
|---|---|---|---|---|---|
| M3T2P2-R1-F1 | MAJOR | `M3-T2-implementation-authorization-packet.md:155`, also :67, :81 | Call counts do not establish complete numerical data flow. Even matching call names, arguments, results and order cannot prove those results were actually used. | A mutant preserves the **entire observed trace**, including the expected eight calls, while using an untraced cosine result and changing height by **64.98137000016868 m**. Accuracy/DL-4 checks can detect it; the claimed completeness assertion cannot. | Revise DL-3 and D-1/D-6. Require an audited primitive/data-flow inventory, independently validated iteration/stopping behavior, and hidden-operation/trace-masking mutants. Retain source inspection separately. |
| M3T2P2-R1-F2 | MAJOR | `M3-T2-implementation-authorization-packet.md:240`, also :255 | A three-ulp perturbation need not violate A-FP-2. The mandatory negative-control outcome can therefore reject a correct checker. | `sin(1)`, shifted upward three ulps, has error **1.773082884660813 × 2⁻⁵² relative**, within the permitted two units, and correctly passes the probe predicate. | Inject an error proved outside `UF·|f| + NU`, accounting for oracle uncertainty. Include an admissible-three-ulp positive control. |
| M3T2P2-R1-F3 | MAJOR | `M3-T2-implementation-authorization-packet.md:176` | The assertion that any grouping, conversion or band-selection defect breaks the monotonicity conclusion is false. | Doubling the exponent scale preserves both the observed `exp` ordering and decreasing density while materially changing the density values. | Revise D-4’s sensitivity rationale; disclose survivors and assign DL-4 or separately justified formula checks as their killers. |
| M3T2P2-R1-F4 | MINOR | `M3-T2-implementation-authorization-packet.md:69`, also :215, :335 | Patch version and the proposed fingerprint do not fully identify an environment for exact independent replay. | Compiler flags/configuration, interpreter artifact identity, linked math-library identity and CPU dispatch are omitted. `platform.libc_ver()` is empty on this macOS host. | Expand evidence provenance and distinguish source-version invalidation from numerical-environment drift. Reobserve POG every run. No migration is needed. |
| M3T2P2-R1-F5 | NOTE | `M3-T2-implementation-authorization-packet.md:68`, also :251, :338 | Bitwise output agreement is useful conformance evidence, not proof of operation sequence or numerical correctness. | A shared faulty cosine produces identical component/twin tuple bits with a **64.98137 m** error. | Compare both height and latitude; specify mutant-killing inputs; retain source inspection and independent accuracy checks. |
| M3T2P2-R1-F6 | MINOR | `M3-T2-implementation-authorization-packet.md:154`; `docs/reviews/raw/M3-T2-authorization-I31-evidence/premise_probe.py.txt:70` | The probe’s `error ≤ ulp(output)/2` predicate does not establish correctly rounded `sqrt` at binade boundaries. | For `sqrt(nextdown(1))`, incorrect output `1.0` passes that predicate. Correct rounding gives `nextdown(1)`, which this host returns. | Qualify the probe claim. Use rigorous rounding cells with asymmetric neighbor spacing and ties-to-even if checking correct rounding. No actual host `sqrt` defect was found. |

## 3. Assessment of I-32 §3 A–G

### A. POG scientific validity

**Finite-domain POG can work, but the packet has not yet established its prerequisites.**

The controlling J-FP2(ii) text permits a proof or exhaustive check “over the input domain the bound is used on,” while rejecting sampled measurements alone. A fixed finite set can be exhausted. That supports only its explicitly recorded executions—not an altitude interval, arbitrary production inputs, or a universal library guarantee. D-1 requests this restricted route; it is not already approved.

I inspected E1’s support-function, stationarity, contraction, stopping-rule and mixed-underflow arguments. For DQ-1, the relevant requirements include:

- The binary64 `a`/`e²` model ellipsoid.
- True height ≥ 0 and **no overflow**.
- A-FP-1 arithmetic and square-root behavior.
- Applicable A-FP-2 bounds for `hypot`, `atan2`, `sin` and `cos`.
- The specified arithmetic, stopping tolerance and maximum 60 updates.

DQ-1 uses neither `exp` nor `pow`. E3/E4b additionally require the density `exp` premise and their specified arithmetic structure.

A Python attribute proxy cannot observe C-internal operations, `float.__pow__`, operators, `fsum` arithmetic or user-defined conversions. **That is not automatically fatal:** checking `hypot` against exact √(x²+y²) establishes the aggregate contract E1 uses without tracing its internal square roots. However, hidden substitute operations must be excluded through reviewed source/data-flow evidence. Counts alone cannot do this—F1.

The preserved tracer produced **zero bit differences in either returned quantity** versus uninstrumented execution across the probe points. That supports local instrumentation neutrality, not a universal proof.

Rigorous O-1 and O-2 bounds are feasible for a stated finite domain:

- O-1 needs bounded argument reduction, series remainders and outward arithmetic, including exact-zero and underflow handling.
- O-2 needs a certified root bracket or equivalent residual-to-height enclosure, plus arithmetic-error bounds.
- Decimal stagnation and a small Newton correction alone are insufficient.
- Uncertain exterior/interior classification must fail closed rather than silently remove a fixed sample.

The packet correctly identifies the existing references as lacking written bounds. Those deliverables remain unfinished scientific dependencies.

Rule 1 is conservative when evaluated rigorously:

\[
|\hat f-r|+\delta\le UF(|r|-\delta)+NU
\]

implies the desired premise. Retain the absolute subnormal term exactly. Under the stated relative-error restriction, `r=0` requires `δ=0`; exact zeros need explicit treatment. Arbitrarily small nonzero uncertainty can still straddle a decision boundary, so it cannot literally be guaranteed never to limit a decision.

Each CI platform must observe its own actual execution. Different library results can change subsequent arguments and iteration counts. **No accuracy row is ready for promotion now.**

### B. Error-budget integrity

Recomputed from `rounding_allowances()`:

| Quantity | Reproduced value |
|---|---:|
| α | `1.2212453270876738e-15` |
| β | `8.877691069434736e-9 m` |
| ε_h(120 km) | `9.024240508685258e-9 m` |
| ε_h(2000 km) | `1.1320181723610084e-8 m` |

α is dimensionless; β and ε_h are lengths. Display-rounded coefficients should not replace the actual gate constants.

E1 has **no 2000 km upper limit**, but retains its no-overflow condition. For example, T0 returns infinite height for the finite input `(DBL_MAX, DBL_MAX, 0)`; E1 cannot supply a finite accuracy guarantee there.

The probe uses **each point’s own** ε_h. Its largest absolute error and largest ratio coincide:

- True height: `145.0304751527136 m`.
- Absolute error: `1.9198142883865285e-9 m`.
- ε_h at that point: `8.877868187224802e-9 m`.
- Ratio: **`0.216247217000713`**.

This remains an empirical maximum.

The `h_ref + δ_O` direction is correct for an **outer reference-comparison enclosure**, since ε_h increases with height. A correct E1-compliant result must satisfy the packet’s inequality.

Passing that comparison does not itself certify the strict original E1 inequality for the unknown true height: it can admit an excess up to `2(1+α)δ_O`. At the proposed maximum δ_O, this is approximately **`1.7755382138869496e-14 m`**. Distinguish this comparison budget from strict certification. A sufficient strict certificate would instead require:

\[
|\hat h-h_{\rm ref}|+\delta_O
\le \epsilon_h(\max(0,h_{\rm ref}-\delta_O))
\]

on an independently certified exterior interval.

### C. Numerical and algorithmic invariants

**Evenness:** The supplied CPython source normalizes builtin-float arguments with `fabs`. Sign changes therefore give identical coordinate arrays and branch state. This reasoning survives:

- Signed zero and `max == 0`.
- Subnormal scaling and recursion.
- Ordinary scaling and compensation.
- Infinity handling and the canonical NaN-return path.

Non-finite inputs are rejected by the geodetic domain guard. Arbitrary objects with side-effecting conversions are outside the builtin-binary64 claim.

DQ-1 subsequently uses x and y only through `p`. Thus identical `p` and unchanged z imply identical arithmetic and stopping behavior for accepted points. The public component’s guard must separately preserve these sign symmetries. **D-3’s proposed evenness result is sound within these qualifications.**

**Swap symmetry:** Order dependence of the primary compensated sum is not, by itself, proof of a swap mismatch; nor does it provide a swap proof. I established no general swap theorem. The reproduced two-million-pair probe and my 225 adversarial pairs had zero mismatches. These are samples, not proof.

**D-4/B-10:** Observing `exp` order at the two actual exponent arguments is sufficient for the **pairwise** conclusion when the specified same-band preprocessing and positive multiplication are established. It proves neither interval-wide monotonicity nor correct density values. F3 supplies a meaningful passing defect.

**D-7:** Referencing the true height of the actual binary64 point is scientifically sound. It avoids pretending nominal forward coordinates are exact, subject to O-2’s bound and exterior classification.

**D-8:** Bitwise conformance usefully catches the named truncation mutants. On the probe set:

- Two-iteration truncation changes latitude bits at 566 points and height bits at 296.
- Three-iteration truncation changes latitude bits at 453 points and height bits at 250.

Compare both outputs. A shared library defect can pass conformance while failing accuracy; an accurate alternative sequence can fail conformance because it violates DQ-1/DQ-2. These are different properties.

Strict density decrease and exact z-reflection correctly remain report-only.

### D. Cross-platform reproducibility

- **RQ-1:** Useful sampled repetition check; not an unrestricted determinism theorem.
- **RQ-2:** Appropriate for constants built from the specified correctly rounded operations.
- **RQ-3:** Correctly avoids cross-platform bit equality.
- **RQ-4/D-5:** Necessary source-version invalidation, incomplete replay provenance.
- **RQ-5:** Useful active-environment checks; not proof of every arithmetic/libm operation. F6 limits the probe’s square-root claim.
- **RQ-6:** Python scalar arithmetic avoids Python-level implicit contraction. It does not constrain C-internal FMA/compiler behavior in `hypot` or libm. DL-4 covers DQ-1/DQ-2; drag still needs its specified inspection/derivation.
- **RQ-7:** Preserves the accepted same-platform regression policy.
- **RQ-8:** Essential; retain per-platform, fail-closed observation.

Record interpreter artifact/distribution identity, compiler configuration and available flags, OS build, architecture/CPU features and linked math-library provenance. Linux libc version alone need not identify libm code/dispatch. macOS version/build matters.

Prefer D-5(b), with expanded provenance. **No CI or runtime migration is proposed.**

### E. Scope and traceability

The docs-only diff preserves the controlling decisions and reconciliations:

- DR-0024 through DR-0029 and ADR-0009 remain authoritative.
- The km-route exception, stage-mass context, unchanged T1 J2, pinned table and force order are retained.
- T3 contracts/events/scenarios, T4 validators/trajectory accumulation and T5 GMAT remain excluded.
- P6 is not a T2 prerequisite under Q-GATE, but P6/P6(b) remain unresolved.
- X-1 remains unauthorized.
- No threshold or language migration is implicitly required.

All seven deliverables fit test/evidence scope:

- **DL-1/DL-2:** Need reviewed bounded algorithms.
- **DL-3:** Needs F1’s correction.
- **DL-4:** Useful partially independent conformance evidence.
- **DL-5:** Needs fuller provenance.
- **DL-6:** Unsupported derivations remain report-only.
- **DL-7:** Supports reviewed-source evenness only.

Keep P-i/P-ii/P-iii conjunctive. G-T2-10/11 must depend on the specifically approved decisions and corrected test requirements. Implementation completion on unconditional gates must remain distinct from geodetic scientific acceptance.

### F. D-0 … D-8

“APPROVE” below is a **recommendation**, not an owner decision.

| Decision | Recommendation | Justification | Required evidence | Dependencies | Consequences of approval | Remaining blocker |
|---|---|---|---|---|---|---|
| D-0 | APPROVE | Correctly separates per-evaluation rounding from T4 trajectory accumulation. | Explicit E1/E2 scope traceability. | I-30 interpretation; T4 exclusion. | Bounds the requested T2 analysis. | None for this scope recommendation. |
| D-1 | REVISE | Finite-domain route is valid in principle; trace completeness is unsupported as specified. | F1/F2 corrections; bounded oracles; full hypothesis inventory; platform certificates. | A-FP-1, D-2/D-6; D-7 where applicable. | Opens a route to P-i only. | DL-1…DL-3 validation and later owner promotion. |
| D-2 | REVISE | Deliverables fit scope but inherit tracing/provenance defects. | Corrected DL-3/DL-5; oracle derivations; independent review and mutation matrix. | Revised D-1/D-6; D-8 for its gate. | Adds future test-side evidence work. | Reviewed deliverables do not yet exist. |
| D-3 | APPROVE | `fabs` normalization supports sign-evenness; DQ-1 then sees identical p. | Source/build provenance; guard-equivariance checks. | DL-7, D-5, exact DQ-1 sequence. | Adds sign-reflection/half-turn equality only. | Unreviewed build/version; no swap proof. |
| D-4 | REVISE | Local premises can support local conclusions, but sensitivity is overstated. | Correct pairwise predicate; same-band/preprocessing checks; disclosed survivors and killers. | Corrected tracing; B-10/B-11; D-3 for sign part. | Local metamorphic gates only. | No universal monotonicity/swap justification; promotion remains separate. |
| D-5 | REVISE | Prefer (b), but patch version is not the whole environment. | Expanded artifact/build/library fingerprint and invalidation policy. | DL-5/DL-7; RQ-8. | Stops unreviewed source versions without migration. | Incomplete replay provenance. |
| D-6 | REVISE | Attribute calls and scalar floats help but do not prove completeness. | Primitive/data-flow audit; iteration validation; masking mutants; traced/plain comparisons. | D-1/DL-3; DQ-1/DQ-2. | Constrains future testability. | F1 and explicit treatment of hidden/operator paths. |
| D-7 | APPROVE | Correctly references the actual rounded point. | Rigorous O-2 error/exterior certificate; clear comparison semantics. | D-1/DL-2; P-ii/P-iii. | Alternative route for U-18. | O-2 certificate and promotion remain pending. |
| D-8 | APPROVE | Useful explicit conformance gate alongside inspection and accuracy checks. | Independent twin; both returned quantities; fixed mutant-killing cases; platform runs. | Exact DQ-1/DQ-2; independent review. | Makes specified output differences acceptance failures. | Actual twin/kill matrix remains future work. |

### G. Rust boundary

I located and read RES-0001 and ADR-0008 at research-branch SHA `2d6d7e59c880ace48c25fd8ed3bcd18ecdfc5233`.

The packet preserves Python as reference, Rust only as a future candidate, TL-6’s requirements-based deferral, TL-9’s prohibition, PC-1’s boundary trigger and the open AT items.

The new Rust/libm/Ferrocene/arXiv factual claims could not be independently verified offline. Pinning software-libm source alone should not be asserted to guarantee cross-platform bits without target/compiler/FMA qualifications. POG’s logical principle can transfer; its current implementation assumptions cannot simply be presumed to transfer unchanged.

No language implementation or migration is authorized or required.

## 4. Required corrections or additional research

1. Replace count-based completeness justification with audited actual-used data flow and stronger mutants.
2. Replace the unqualified three-ulp negative control with a proved premise violation.
3. Correct D-4’s sensitivity claims and identify surviving defects’ designated killers.
4. Expand replay provenance and correct the square-root probe claim.
5. Complete independent validation of O-1/O-2 bounds and domain classification before dependent rows gate.
6. Demonstrate DL-4’s mutation matrix for both height and latitude; preserve all promotion and scope boundaries.

## 5. Computations and preserved evidence

Commands used:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/premise_probe.py "$PWD/docs/science/experiments/m3-t0" > review_scratch/premise_probe.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/mutant_probe.py "$PWD/docs/science/experiments/m3-t0" > review_scratch/mutant_probe.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/hypot_probe.py > review_scratch/hypot_probe.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/independent_checks.py > review_scratch/independent_checks.out
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I review_scratch/final_state.py > review_scratch/final_state.out
```

Reproduced probe output includes **631 eligible points, 11,867 calls, zero measured premise violations and zero ε_h failures**. The mutant and two-million-pair outputs also match their committed bytes.

The supplied source SHA-256 independently matches:

```text
436a01da195e3c2b9576a4b9188d5d62e9883e62e74f2d60bc55194bfce98281
```

All seven I-31 manifest entries verify.

`review_scratch/` contains:

- `premise_probe.py/.out`
- `mutant_probe.py/.out`
- `hypot_probe.py/.out`
- `independent_checks.py/.out`
- `final_state.py/.out`
- `findings.json`
- `review.md`
- `SHA256SUMS`

The scratch manifest also verifies.

## 6. Limitations and final state

No network, other-platform execution, live CI query, GMAT run or M1/M2 proof run was performed. External web-source claims remain unverified. Existing unbounded T0 references limit the empirical accuracy evidence; this review does not replace their required rigorous derivations.

Final HEAD remains **`0e37db60eed706e041666b40abb5238609a83360`**, detached, with a **clean tracked tree**. No commit, push or correction pass occurred.

CI at this SHA is **reported by the implementer as four green jobs**, not independently queried.

**T2 implementation remains NOT AUTHORIZED.**

## Owner authorization I-33 (verbatim)

# I-33 — M3 T2 Authorization Packet Correction and Review 02

## 1. Authorization

Authorize a bounded documentation-and-research correction pass addressing I-32 Review 01.

Baseline:
- Branch: `milestone-3-t2-authorization`
- Expected HEAD: `43a6c29`
- Review: `docs/reviews/M3-T2-packet-r2-review-01.md`
- Packet: `docs/milestones/M3-T2-implementation-authorization-packet.md`

Verify the exact full HEAD SHA, remote synchronization, clean worktree, and green CI before proceeding. If any differ, STOP.

The authorization covers corrections to packet r2, associated research evidence, and review records only.

No production implementation, scientific decision approval, CI migration, or protected-path modification is authorized.

## 2. Correction F1 — Trace-to-Computation Integrity

MAJOR.

Replace the assumption that matching call counts or traces establishes numerical correctness.

The corrected design must demonstrate that the elementary-function results checked against the premise oracle are the values actually consumed by the geodetic computation.

Address:

1. Complete capture of relevant elementary-function invocations.
2. Trace-to-consumer linkage.
3. Hidden or bypassed calls.
4. Values replaced after tracing.
5. Instrumentation effects on computation.
6. Calls occurring inside native implementations.

Include adversarial test designs for:

- A correct trace with a hidden incorrect cosine.
- A correct trace whose returned values are discarded.
- An unobserved call supplying the actual computation.
- A trace that omits one relevant invocation.

Explicitly define what the test infrastructure can and cannot observe.

For native operations such as `hypot`, distinguish internal implementation behavior from the externally observable mathematical contract.

If trace-to-computation integrity cannot be established, POG accuracy gating remains BLOCKED.

## 3. Correction F2 — Premise Checker Negative Controls

MAJOR.

Replace the ambiguous 3-ulp negative-control requirement.

Derive the premise threshold using the exact definition of the error units in A-FP-2.

Provide:

- A constructed perturbation that demonstrably exceeds the premise threshold.
- A negative control that must fail.
- A 3-ulp perturbation that remains within the premise and therefore must pass.
- Boundary tests immediately inside and outside the permitted error.
- Explicit handling of rounding and oracle uncertainty.

Do not assume that a fixed number of ulps always corresponds to a fixed absolute or relative error.

A premise-checker test is valid only if its expected outcome follows from the actual numerical inequality.

## 4. Correction F3 — Density Validation and D-4

MAJOR.

Remove the claim that monotonic density detects every error in:

- Atmospheric band selection.
- Exponent grouping.
- Kilometer conversion.
- Scale-height handling.

Provide counterexamples, including the scale-height mutation identified in Review 01.

Replace the overclaim with independent, discriminating validation requirements.

Consider:

- Pinned dataset integrity.
- Band-boundary and adjacent-band tests.
- Independent density reference calculations.
- Unit-conversion checks.
- Exponent and scale-height mutation tests.
- Monotonicity as a supplementary invariant.

Every proposed gate must identify the specific defect class it can detect and its known blind spots.

Revise D-4 accordingly.

## 5. Correction F4 — Environment Reproducibility

MINOR.

Expand DL-5 to record sufficient information to reproduce the numerical environment.

Include, where applicable:

- Python implementation and exact patch version.
- Interpreter build information.
- Compiler and relevant build flags.
- Operating system and architecture.
- Linked mathematical-library implementation and version.
- CPU architecture and relevant dispatch behavior.
- Relevant floating-point configuration.

Separate information that can be reliably observed from information that cannot.

Recommend recording and stopping on unreviewed environments rather than changing CI or pinning a new runtime under this authorization.

Do not claim that recording metadata alone proves numerical reproducibility.

## 6. Correction F6 — Square-Root Boundary Test

MINOR.

Correct the statement that the existing square-root test detects all incorrect results near the binade boundary.

Include the counterexample:

`sqrt(nextdown(1)) → 1.0`

Explain why the existing test can miss this defect.

Specify a test with a mathematically justified expected result or rigorous reference interval that rejects this counterexample.

Do not substitute a looser empirical tolerance.

## 7. Correction F5 — Bitwise Sequence Conformance

NOTE.

Clarify that bitwise conformance with DQ-1/DQ-2 proves execution-sequence agreement, not numerical correctness.

A faulty component and a faulty reference implementation may agree exactly.

Retain sequence conformance as a separate gate, but require independently justified numerical validation for accuracy claims.

## 8. Additional Review Observations

Resolve all five observations explicitly.

### A. Comparison semantics

Distinguish strict E1 acceptance from any comparison allowing additional oracle uncertainty.

State which inequality each proposed gate enforces.

Do not silently weaken E1 or introduce a new tolerance.

If strict E1 cannot be established, leave the affected gate BLOCKED and present the alternatives for owner decision.

### B. Overflow

Define the applicable finite-input and finite-intermediate domain.

Address the `(DBL_MAX, DBL_MAX, 0)` counterexample.

Do not assume finite inputs imply finite results.

### C. Oracle zeros

Specify mathematically justified treatment of exact-zero reference values and zero-crossing cases.

Avoid an implicit requirement for an oracle to provide impossible absolute precision.

### D. Rounded coefficients

Use the full independently derived numerical values of α and β when evaluating E1.

Rounded presentation values must not silently replace the operative coefficients.

### E. Rust portability

Qualify any claim of bit-identical results across platforms.

Pinning a software math library alone does not establish bitwise portability without accounting for compilation, target architecture, floating-point behavior, and relevant optimizations.

Keep Rust exploratory.

## 9. Scientific Prerequisites

DL-1 and DL-2 remain unresolved.

Document the required derivations for:

- The premise oracle's error bound.
- The true-height oracle's error bound.
- Propagation of oracle uncertainty.
- Applicability of E1 to the observed finite domain.

Research and draft these derivations where feasible, but do not represent an unreviewed derivation as accepted proof.

If a rigorous derivation cannot be completed within this correction pass, record the missing proof obligation and preserve the corresponding BLOCKED gate.

Do not expand into T2 implementation.

## 10. Correction Validation

Before independent Review 02:

1. Reproduce every accepted finding.
2. Demonstrate that each correction addresses its original counterexample.
3. Run focused adversarial checks.
4. Verify document and decision consistency.
5. Confirm no unauthorized scientific decision changed.
6. Verify evidence checksums.
7. Run applicable documentation and repository checks.
8. Record all validation results and limitations.

Keep correction and review commits separate.

## 11. Independent Codex Review 02

After completing and validating the bounded corrections, launch a fresh independent Codex review.

The reviewer must:

- Read the corrected packet and Review 01.
- Verify F1–F6 dispositions independently.
- Examine the five additional observations.
- Reproduce important counterexamples.
- Evaluate whether the corrected POG strategy is scientifically defensible.
- Identify any remaining unproved assumptions.
- Reassess D-0 through D-8 individually.
- Check for newly introduced contradictions.

Use the verdicts:

- PASS
- REQUEST_CHANGES
- BLOCKED

Classify findings as BLOCKER, MAJOR, MINOR, or NOTE.

A PASS means the packet is suitable for owner decision review, not that T2 implementation or its numerical gates are authorized.

## 12. Stop Conditions

If an unexpected prerequisite failure, scope expansion, or scientific contradiction arises, STOP and report.

If Review 02 returns REQUEST_CHANGES or BLOCKED, record and independently reproduce the findings where feasible, but do not correct them or start Review 03.

If Review 02 returns PASS, stop for owner decision review.

Report:

1. Final branch SHA and CI status.
2. Corrections completed.
3. Counterexamples and validation results.
4. Review 02 verdict and findings.
5. Status of DL-1 and DL-2.
6. Assessment of POG readiness.
7. Recommendations for D-0 through D-8.
8. Remaining blockers.

**T2 implementation remains NOT AUTHORIZED.**
