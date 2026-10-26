# I-33 correction evidence for packet r2 (research, NOT T2 evidence, NOT a gate)

Evidence for the I-33 corrections to `docs/milestones/M3-T2-implementation-authorization-packet.md`, made after independent Review 01 (`docs/reviews/M3-T2-packet-r2-review-01.md`).

- **Host:** macOS x86_64 (Intel i9-9880H), CPython 3.12.15. The repository's locked environment (`uv sync --locked`, `uv.lock` sha256 `6d784550…50cf`) at `43a6c29`.
- **Inputs:** the T0 spike modules in `docs/science/experiments/m3-t0/`, imported read-only with bytecode writing disabled. No tracked file was modified.
- **Not run on the CI platforms.** That would need a CI change, which is protected and not authorized.
- **Run as:**
  1. Copy each `*.py.txt` to a scratch directory as `*.py`.
  2. For the scripts that read the T0 spike, run `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I <script>.py <repo>/docs/science/experiments/m3-t0`: `f1_witness`, `f3_density`, `pog_pipeline` and `observations`.
  3. `f2_premise_controls` and `f6_sqrt` take no argument.
  4. `f4_fingerprint` takes the path to `uv.lock`.

| File | What it is |
|---|---|
| `pog_lib.py.txt` | **Draft DL-1** (rigorous rational enclosures of sin, cos, exp, atan2 and hypot; the premise decision; the exact sqrt correct-rounding test), **draft DL-2** (the true-height enclosure from the support function), and the strict E1 decision. Research code |
| `witness.py.txt` | **Draft DL-3/DL-4**: the DQ-1 and DQ-2 twins, transcribed from the r1 §5 text; the checked library; the witnessed-evaluation decision |
| `DL1-DL2-draft-derivations.md` | The derivations behind both (Lemmas 1–9) and the E1 hypothesis inventory. **Unreviewed; open proof obligations listed in its §5** |
| `f1_witness.py.txt` / `.out` | F1: Review 01's mutant reproduced against the r2 count check; the I-33 §2 adversarial designs; harness omission; per-index fault injection; F5 shared faulty `math`; native `hypot` contract; instrumentation neutrality |
| `f2_premise_controls.py.txt` / `.out` | F2: the ulp-to-allowance relation; positive and negative controls, boundary pairs, the subnormal regime, the straddle case and identities, each checked against a separately derived closed form |
| `f3_density.py.txt` / `.out` | F3: Review 01's scale-height counterexample, and a 13-mutant kill matrix over U-11, U-12 (a)/(b), PM-4 (a), U-13, U-15 and DL-4 |
| `f4_fingerprint.py.txt` / `.out` | F4: the expanded DL-5 record on this host, with each field marked [O], [P] or [U]. The node name is redacted |
| `f6_sqrt.py.txt` / `.out` | F6: sqrt(nextdown(1)) → 1.0 accepted by the I-31 predicate and rejected by the exact test; a uniqueness check over 5 198 arguments |
| `pog_pipeline.py.txt` / `.out` | DL-1 and DL-2 draft validation, and the corrected decision over the 633 I-31 points (same generator), with 8 mutants swept and a soundness check |
| `observations.py.txt` / `.out` | Review 01 observations A (comparison semantics), B (overflow), C (oracle zeros) and D (exact coefficients) |
| `SHA256SUMS` | Checksums of every file above |

## Limits
- **Single host.** All results are research evidence from one platform. They are not the per-platform observations that RQ-8 requires.
- **Unreviewed drafts.** The oracle and witness code and its derivations have not been reviewed. Until they are reviewed in T2 (P-ii), every A-FP-2-dependent accuracy row stays report-only, and POG accuracy gating stays BLOCKED (packet §6.7).
- **Unbounded cross-checks.** The independent references used for cross-checks are not bounds: T0's `d_sin`, `d_cos` and `d_atan2` are run at 130 digits. At their default 55 digits, `d_cos` loses relative accuracy near π/2, about 7e-49, a fact found during I-33. Python's `decimal` `exp` is correctly rounded according to its documentation.
- **Sources not read.** I-33 did not read a primary or textbook statement of Euler's arctangent series. It validated the series numerically only (derivations §1.4).
