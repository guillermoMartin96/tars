# External Review: M3 T2 implementation authorization packet r2, Review 02 (after I-33 corrections)

- **Reviewer/model:** Codex (codex-cli 0.162.0), session `01a179dc-e7e4-79d2-97dd-f4024d2e1e69`. The reviewer is from a separate provider from the implementer, in a fresh session separate from Review 01.
- **Date:** 2026-10-26
- **Reviewed revision:** `5f96119bcc54d2154cdff50a873791f5f9b26d73`, the I-33 correction commit (`git diff 43a6c29..5f96119`, all under `docs/`), on branch `milestone-3-t2-authorization`. `main` = `0a9c040`.
- **Authorization:** I-33 §11 (owner/Tech Lead, 2026-10-26).
- **Raw records:**
  - `docs/reviews/raw/M3-T2-packet-r2-codex-review02-prompt.md`: the prompt, with Review 01's raw output and I-33 verbatim;
  - `docs/reviews/raw/M3-T2-packet-r2-codex-review02.md`: the final message, verbatim;
  - `docs/reviews/raw/M3-T2-packet-r2-codex-review02-evidence/`:
    - the reviewer's own scripts and outputs (`run_evidence`, `independent_checks`, `boundaries`, `final_state`);
    - `reviewer_f4_fingerprint.out`, the reviewer's rerun of the fingerprint, which differs (R2-F4);
    - `implementer_rerun.txt` (the reviewer's three scripts rerun byte-identically in the same pinned clone);
    - `implementer_r02_repro.py.txt` and `.out` (the implementer's independent reproduction of R2-F2 and R2-F3);
    - `SHA256SUMS`.
  - **Not committed:**
    - the reviewer's copies of the I-33 evidence and their outputs: six are byte-identical to the committed files, per `run_evidence.out`;
    - `__pycache__/`;
    - the JSONL event stream.
  - **Local paths kept verbatim:** a traceback in `boundaries.out` and the `--add-dir` path in the prompt contain local scratch paths. As at I-32, raw evidence is not edited.
- **Extra reviewer input:** CPython v3.12.15 `Modules/mathmodule.c` (sha256 `436a01da…98281`), read-only via `--add-dir`, verified by the reviewer. Not committed.
- **How it was run:**
  - a fresh clone pinned at the full SHA;
  - `uv sync --locked`;
  - `review_scratch/` excluded from git;
  - `codex exec -C snap -s workspace-write --add-dir <inputs> --json -o codex_last_message.md -`;
  - no network.

  The wrapper reports `--dangerously-bypass-hook-trust` as enabled. This invocation did not pass it, and it does not change the sandbox. The tracked tree was clean afterwards and HEAD unchanged.

## Summary
**`VERDICT: PASS`.** 0 BLOCKER, 0 MAJOR, **3 MINOR**, 1 NOTE. **MINOR findings remain.**

The reviewer judges witnessed evaluation scientifically defensible for explicitly recorded finite executions: an output bitwise equal to a premise-satisfying evaluation inherits that evaluation's bound. It does not establish the component's internal operation sequence. The reviewer found no false E1-PASS and no enclosure-containment counterexample.

**DL-1 and DL-2 remain draft research, and POG accuracy gating remains BLOCKED.**

| Review 01 item | Review 02 |
|---|---|
| F1 trace-to-computation | **RESOLVED.** Twin integrity still requires source review |
| F2 negative controls | **PARTIALLY RESOLVED.** The checker and controls are correct; the explanatory "iff" rule is inexact (R2-F2) |
| F3 density sensitivity | **RESOLVED** |
| F4 environment provenance | **RESOLVED** |
| F5 conformance vs correctness | **PARTIALLY RESOLVED.** The numerical separation is correct; some wording still attributes implementation conformance to output equality (R2-F1) |
| F6 sqrt boundary | **RESOLVED** |
| A–E | **All RESOLVED.** R2-F3 concerns DL-2's coverage inside the non-overflow domain, not an overflow escape |

## Findings register and dispositions
Locations are in `docs/milestones/M3-T2-implementation-authorization-packet.md` unless stated otherwise. Each disposition is the implementer's evaluation. **No correction is made.** Under I-33 §12, a PASS stops for owner decision review, and a further correction pass needs authorization.

| ID | Severity | Location | Finding | Implementer's reproduction | Disposition |
|---|---|---|---|---|---|
| M3T2P2-R2-F1 | MINOR | :88 (§3 testability (iii)); :192 (§6.3) | Some wording attributes implementation-sequence evidence to output equality. DL-4 cannot enforce "no NumPy", and it cannot show which operations produced matching bits | **Confirmed from I-33's own evidence:** the `numpy.cos` mutant passes with identical bits at all 631 exterior points (`pog_pipeline.out`), yet line 88 says DL-4 "enforces" (iii). The numerical witness argument is unaffected | **ACCEPTED.** Describe DL-4 as output conformance with the specified evaluation. Keep the operation-by-operation source inspection (r1 §5 DQ-1 "Primary" conformance evidence) for internal sequence and arithmetic requirements |
| M3T2P2-R2-F2 | MINOR | :204 (§6.4 rule 1); I-33 evidence `f2_premise_controls.py.txt:65` | "3 ulps passes iff f > 1.5·2ᵉ" is not exact. It fails at equality, at the absolute underflow allowance, and when the shifted value already carries an error | **Reproduced** (`implementer_r02_repro.out`): f = 1.5 exactly gives an allowance of 3.0 ulps, so f + 3 ulps PASS although f > 1.5·2ᵉ is false. At f = 2⁻¹⁰²² the allowance is 4.0 ulps (ν term), so 3 ulps PASS although f/2ᵉ = 1. The decision procedure and the 32 controls are correct | **ACCEPTED.** Qualify the rule as intuition away from underflow and for exact starting values. Expected outcomes already come from the exact inequality |
| M3T2P2-R2-F3 | MINOR | :73 (DL-2 "any foot-point approximation"); I-33 evidence `pog_lib.py.txt` (surface-point construction) | "Any foot-point approximation gives a valid enclosure" needs a qualification: the construction needs a coordinate within the ellipse's range, and the fixed Newton budget does not guarantee that over the whole finite, non-overflow domain | **Reproduced:** `true_height_enc(2¹⁰²⁰, 2¹⁰²⁰, 2¹⁰²⁰)` raises `ValueError` (the square root of a negative number), although the twin's intermediates are finite. It **fails closed**: no false certificate | **ACCEPTED.** State the draft's supported range, or require an admissible surface-point construction with explicit handling of oracle failure (a stop or report, never a pass). Add this to DL-2's implementation-review obligations (derivations §5) |
| M3T2P2-R2-F4 | NOTE | I-33 evidence `f4_fingerprint.out`; correction record §2 item 8 | The fingerprint is not byte-identical in the reviewer's restricted sandbox. The CPU brand, features and leaf7 fields come back empty there. All six numerical outputs reproduce exactly | **Confirmed:** `reviewer_f4_fingerprint.out` differs only in those three fields. The implementer's unrestricted rerun was byte-identical (I-33 correction record §2) | **ACCEPTED.** An unavailable `sysctl` result should be reported as [U] unavailable, not as an observed empty value. The I-33 claim stands for the implementer's environment |

## Reviewer's D-0 … D-8 recommendations (not owner decisions)
| ID | Review 02 | Remaining blocker (reviewer) |
|---|---|---|
| D-0 | APPROVE | None |
| D-1 | APPROVE | DL reviews, platform evidence and owner promotion |
| D-2 | APPROVE | The drafts are not accepted deliverables (includes R2-F3) |
| D-3 | APPROVE | No swap theorem; platform builds to be reviewed |
| D-4 | APPROVE | No interval-wide theorem; no current promotion |
| D-5 | APPROVE option (b) | Reviewed platform fingerprints |
| D-6 | APPROVE (ii), (iii) | DL-4 alone cannot enforce internal implementation (R2-F1) |
| D-7 | APPROVE | DL-2 validation and promotion pending |
| D-8 | APPROVE | Reviewed implementation and platform evidence; source inspection kept separate |

Full justification, evidence, dependencies and consequences for each decision are in the raw output §6. **Approval is the owner's decision.**

## Remaining unproved assumptions (reviewer §5, summarized)
- A-FP-1 for every arithmetic operation.
- Correct interpreter execution and exact rational infrastructure.
- Source review of the twin and its library routing.
- Implementation review of DL-1 and DL-2.
- E1's derivation and its applicability to every gated execution.
- DL-2 coverage over the gated domain.
- Authoritative citations for the draft derivations.
- Observations on all three CI platforms.
- DL-7 build correspondence.
- Derivations for the other conditional rows.
- Owner approval of the route and promotion of individual rows.

Production-input A-FP-2, A-LM-1 and A-LM-2 remain unjustified.

## Reviewer's computations (reproduced)
- **Manifests:** I-33 18/18, I-31 7/7, Review 01 14/14.
- **Evidence reruns:** 6/6 numerical outputs byte-identical; the fingerprint differs as in R2-F4.
- **Pipeline:** 631 E1-PASS, 2 not certified exterior.
- **Coefficients:** α = 1.2212453270876738e-15 and β = 8.877691069434736e-9 m.
- **Independent counterexamples:**
  - hidden cosine: 64.98 m, nonconformant;
  - shared faulty cosine: 56.00 m, bits identical, premise FAIL;
  - doubled scale height: still monotone, 14.79 % density change at 2 km;
  - sqrt(nextdown(1)) → 1.0: rejected.
- **Decimal cross-checks:** 200 independent comparisons passed.
- **Implementer rerun:** the reviewer's `independent_checks`, `boundaries` and `final_state` are byte-identical in the same clone.

## Evidence note
**`git diff --check` on this review commit exits 2.** The 7 flagged lines are all in the reviewer's raw `run_evidence.out` (lines 20–26). Each ends with `stderr ` followed by the empty stderr text, which leaves a trailing space. The raw evidence is kept as received and is not altered to make the check pass (I-29 precedent). Every other file in the commit passes the check.

## Proof gate
- [x] All Critical findings resolved: none raised
- [x] All High findings resolved: none raised (0 BLOCKER, 0 MAJOR)
- [x] Every substantive finding has an explicit disposition: R2-F1 … R2-F4 ACCEPTED, **not corrected** (I-33 §12)
- [ ] Accepted fixes re-tested: not applicable; no correction authorized
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: POG accuracy gating BLOCKED pending DL-1 … DL-4 review; A-FP-2 rows report-only; P6 geodetic drag ESCALATED_FOR_INVESTIGATION

**Review gate result: PASS.** The packet is suitable for **owner decision review** of D-0 … D-8, with the three MINOR findings open. **This PASS approves no decision, promotes no row, and authorizes no T2 implementation, numerical gate, correction pass or merge.**

**T2 implementation remains NOT AUTHORIZED.**
