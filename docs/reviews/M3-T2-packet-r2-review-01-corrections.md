# M3 T2 packet r2: Review 01 corrections (I-33)

- **Authorization:** I-33, "M3 T2 Authorization Packet Correction and Review 02" (owner/Tech Lead, 2026-10-26). This is a bounded documentation-and-research correction pass. No production implementation, no approval of a scientific decision, no CI migration and no protected-path change is authorized.
- **Baseline:** `milestone-3-t2-authorization` = `43a6c29e3080f6b529c5635565324c615c11dfb7`. Before starting, the implementer verified:
  - that the local and remote HEAD were identical;
  - that the worktree was clean;
  - that CI was green: run `40374877427`, four jobs.
- **Review corrected:** `docs/reviews/M3-T2-packet-r2-review-01.md`, Codex session `01a17958…`, REQUEST_CHANGES. Its findings were F1, F2 and F3 (MAJOR), F4 and F6 (MINOR) and F5 (NOTE), plus five unnumbered observations, A–E. **All were ACCEPTED in Review 01's record.**
- **Changed:**
  - `docs/milestones/M3-T2-implementation-authorization-packet.md`, in place, with *(corrected under I-33, …)* markers and a correction map in §16. The reviewed text is preserved at `0e37db6`;
  - new evidence in `docs/reviews/raw/M3-T2-packet-r2-I33-evidence/`;
  - this record.
- **Unchanged:**
  - every decision record (DR-0024 … DR-0029, ADR-0009);
  - packet r1, the validation strategy and the T0 spike;
  - every protected path.

  D-0 … D-8 remain PROPOSED.

## 1. Corrections
| Item | Correction | Original counterexample, after correction |
|---|---|---|
| **F1** (MAJOR), trace-to-computation | **Design replaced: witnessed evaluation** (packet §6.3, §6.4 rule 4).<br>• The premise is observed on every elementary value an independently written twin (DL-4, from the r1 §5 text) consumes, through a library object the harness controls (DL-3).<br>• The component is not instrumented.<br>• Its returned values must equal the twin's bitwise.<br>• The argument: the claim concerns the output **value**, and an output bit-identical to a premise-satisfying evaluation of DQ-1 is bounded by E1, whatever the component did internally.<br>• The packet defines what is observed (the twin's consumed values and the component's outputs) and what is not (the component's internals, native internals such as CPython's `hypot` loop and the libm, other arguments). Native functions are checked at their mathematical contract.<br>• If the witness cannot be established, POG gating stays BLOCKED (§6.3, §11 item 3). | Review 01's hidden-cosine mutant passes the r2 count check with an identical trace and a 64.98 m error (reproduced). Under the witness it is **SEQUENCE-NONCONFORMANT** at 615 of 633 points. The other 16 E1-PASS are axis points, where p = 0 makes the cosine irrelevant and the bits identical; the remaining 2 are not certified exterior.<br>The I-33 §2 designs:<br>• discarded values (stale sin): nonconformant at 163 points, bit-identical at 468;<br>• unobserved calls supplying the value (bound at import, NumPy): bit-identical passes, which are sound; a perturbed unobserved call is nonconformant at 608;<br>• a harness omission: killed by the call-list assertion;<br>• fault injection at every call index: detected 31/31.<br>**Soundness: 0 E1-PASS with different output bits, over 8 mutants × 633 points** (`f1_witness.out`, `pog_pipeline.out`) |
| **F2** (MAJOR), negative controls | Threshold derived from A-FP-2's exact form (§6.4 rule 1). For f in [2ᵉ, 2ᵉ⁺¹) the allowance is 2f/2ᵉ ulps, between 2 and 4; 3 ulps passes iff f > 1.5·2ᵉ. The premise is decided over the oracle's whole enclosure (convexity): PASS, FAIL or INCONCLUSIVE, and INCONCLUSIVE fails closed. §8.2 lists:<br>• constructed definite violations;<br>• the admissible sin(1) + 3 ulps positive control;<br>• inside/outside boundary pairs;<br>• the subnormal regime;<br>• the straddle case;<br>• exact identities.<br>Every expected outcome comes from a separately derived closed form | sin(1) + 3 ulps (1.773 units) **PASS**, as the inequality requires. sin(x) at the bottom of its binade + 3 ulps (3.157 units) **FAIL**. **All 32 controls agree with the closed form** (`f2_premise_controls.out`) |
| **F3** (MAJOR), density and D-4 | The claim that non-increase detects band-selection, exponent, grouping and conversion defects is **withdrawn** (§6.6). It is replaced by a kill matrix and a gate table that gives each gate's defect class and blind spots. PM-4 (a) is a supplementary invariant only. D-4 is revised (§14) | The doubled scale height (Review 01) keeps ρ̂ non-increasing (reproduced). Of 13 mutants, PM-4 (a) kills **only** the flipped sign. DL-4 kills all except a regrouping that is bit-identical to the specified one, and therefore harmless. U-13 misses every defect that lowers density, because E3 is one-sided (`f3_density.out`) |
| **F4** (MINOR), environment | DL-5 is expanded into §7.1. Every field is marked [O] observed, [P] partial or [U] unobservable (for example, macOS libm in the dyld shared cache, and glibc's ifunc variant choice). RQ-4 separates:<br>• (a) source-argument rows, which stop on an unreviewed (patch version, build configuration, executable digest);<br>• (b) POG rows, which re-observe their premises every run.<br>Recording is stated **not** to prove reproducibility. Recommendation: record plus stop; no CI or runtime change (D-5) | `platform.libc_ver()` is empty on this macOS host (reproduced). The draft record captures the compiler, flags, LTO/PGO, executable digests, the OS build, CPU flags, floating-point probes and a libm behaviour digest (`f4_fingerprint.out`) |
| **F5** (NOTE), conformance ≠ correctness | Stated in DL-4, §6.3, G-T2-10 and D-8: conformance shows execution-sequence agreement, not correctness. The accuracy claim comes only from the premise and E1. Sequence conformance is kept as a separate gate | A shared faulty cosine gives identical bits and a 51 m error: conformance **passes**; the witness decision gives **PREMISE-NOT-OBSERVED (FAIL)** (`f1_witness.out`) |
| **F6** (MINOR), sqrt boundary | §6.4 rule 3 now requires the exact rounding-cell test (Lemma 5): midpoints with each neighbour, asymmetric spacing at binade boundaries, ties to even, compared in exact rationals. The r2 statement "the probe did" is qualified, and the I-31 predicate must not be used | sqrt(nextdown(1)) → 1.0: the I-31 predicate **accepts** it, the exact test **rejects** it. Over 5 198 arguments, exactly one of five candidates passes each time. The I-31 predicate accepts 146 wrong candidates on the same set (`f6_sqrt.out`) |
| **A**, comparison semantics | Every gate enforces **strict E1**, decided over O-2's enclosure (convexity; INCONCLUSIVE fails closed). r2's outer rule is withdrawn. No tolerance is added. If O-2's bound cannot be established, U-18 stays BLOCKED, and the alternatives are in D-7 | Review 01's construction: the outer rule admits it, while strict E1 is violated by 1.776e-14 m. Near 1 m, 80 binary64 outputs are admitted by the outer rule and INCONCLUSIVE under the strict rule (`observations.out`) |
| **B**, overflow | E1's domain is restated as true height ≥ 0 **and** every intermediate finite. The twin checks every intermediate and reports OUT-OF-DOMAIN. Sufficient condition (drafted): max \|coordinate\| ≤ 2¹⁰²⁰. Production behaviour is unchanged (DQ-2's distinct non-finite error) | (DBL_MAX, DBL_MAX, 0): T0 returns h = ∞, and the witness gives **OUT-OF-DOMAIN**. (DBL_MAX, 0, DBL_MAX) overflows in p·c + z·s. The box corners at 2¹⁰²⁰ are finite throughout |
| **C**, oracle zeros | Exact zeros in DQ-1's call domain come only from identities (hypot(0, 0), atan2(±0, x > 0), sin(±0)) and are returned exactly. Every other exact value is provably nonzero there, and its enclosure excludes 0. "δ ≤ 2⁻¹⁰⁰·\|r\|" is withdrawn | The identity cases and tiny or underflowing cases (sin(5e-324), atan2(5e-324, DBL_MAX), exp(−800)) are all decided without any absolute-precision requirement (`observations.out`) |
| **D**, coefficients | The gate uses the exact `Fraction`s from `rounding_allowances()` (§6.4 rule 7, §6.1, §6.9) | Rounding to (1.22e-15, 8.9e-9 m) loosens ε_h by 2.2e-11 m at 120 km (`observations.out`) |
| **E**, Rust portability | §13 item 2 is qualified. Pinning a software libm removes one source of difference. Bitwise portability needs a pinned (source, toolchain, flags, target) tuple, accounting for FMA, vectorisation and fast-math, and it must be observed. Still exploratory; no decision | — |
| **§9**, DL-1/DL-2 | Drafted with derivations (Lemmas 1–9) and an E1 hypothesis inventory (H1–H7), in `DL1-DL2-draft-derivations.md`. **Unreviewed; open proof obligations in its §5**: citations for Leibniz's criterion, Euler's series, Machin's formula and Lemma 6; an implementation review; per-platform runs. POG gating stays **BLOCKED** until they are discharged (packet §6.7) | The draft oracles reach relative width ≤ 1.8e-99, and O-2 width ≤ 2.8e-92 m (the requirement is 8.9e-15 m). They agree with independent references. 631 E1-PASS and 2 not certified exterior, out of 633 points |

## 2. Validation (I-33 §10)
| # | Check | Result |
|---|---|---|
| 1 | Every accepted finding reproduced | **Yes.** Review 01's `independent_checks` was rerun at `0e37db6` in a reconstructed layout, with `mathmodule.c` re-fetched (sha256 `436a01da…98281` matches): **byte-identical** to the committed reviewer output. I-33's own reproductions are in `f1_witness`, `f2_premise_controls`, `f3_density`, `f4_fingerprint`, `f6_sqrt` and `observations` |
| 2 | Each correction addresses its counterexample | Yes; §1, right-hand column |
| 3 | Focused adversarial checks | The F1 designs (1)–(4) and (4′); 8 mutants × 633 points with the soundness check; per-index fault injection; 32 F2 controls; 13 density mutants; the sqrt uniqueness check over 5 198 arguments; the observation A–D constructions |
| 4 | Document and decision consistency | The packet was searched for superseded statements: "3 ulp", "trace completeness", "2⁻¹⁰⁰", the outer rule, "not tautological", module-attribute calls and rounded coefficients. Every remaining hit is a marked withdrawal or a correct use. §16 maps every item. Every cited repository path exists |
| 5 | No unauthorized scientific decision changed | The diff touches only the packet, this record and the new evidence directory. No file under `docs/decisions/`, `docs/science/`, `src/`, `tests/`, `proof/`, `toolbox/`, `scenarios/` or `.github/` is touched, nor `uv.lock` or `pyproject.toml`. DQ-1 … DQ-6 and P1–P9 are unchanged; D-0 … D-8 are PROPOSED |
| 6 | Evidence checksums | I-31 manifest: 7/7. Review 01 manifest: 14/14. The new I-33 manifest (`SHA256SUMS`) verifies |
| 7 | Documentation and repository checks | `git diff --check` is clean. The full CI suite runs on push (§3) |
| 8 | Reproducibility of the I-33 evidence | All 7 outputs are **byte-identical** when rerun from the committed `.py.txt` copies in a fresh directory |

**Limitations.**
- Single host (macOS x86_64).
- The drafts are unreviewed.
- The cross-check references are unbounded (T0's at 130 digits). Python's `decimal` `exp` is correctly rounded according to its documentation.
- Euler's series has not been checked against a cited source.
- No CI-platform observations (they would need a CI change).

## 3. Status
- Corrections complete for F1–F6 and A–E.
- **DL-1 and DL-2: drafted, unreviewed.**
- **POG accuracy gating: BLOCKED** until the draft derivations, the witness harness and the twin are reviewed, per-platform runs exist and the owner promotes rows (packet §6.7).
- This record is the correction commit. Review 02 is recorded in a separate commit (I-33 §10).

**T2 implementation remains NOT AUTHORIZED.**
