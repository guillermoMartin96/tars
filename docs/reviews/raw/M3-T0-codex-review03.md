# M3 T0 Review 03

The correction pass resolves the sampled-bound labelling, strengthens regression protection, and reproduces IM-1. One verified MINOR finding remains: the drag envelope does not cover floating-point height evaluation at downward density jumps. T0 remains BLOCKED.

## Checkpoint and scope

Reviewed detached HEAD `51e110bf1981f9761042f5cf0e87c9f0c7c1962e`, belonging to `milestone-3-t0-reference-spike`. The preceding commits are `14d98f0` (corrections) and `5548d11` (Review 02). Initial and final tracked trees are clean.

I generated both requested diffs. The complete T0 diff from `86df2c3` changes only `docs/`; the correction diff changes 22 files. Production, dependencies, contracts, approved thresholds, goldens and references are unchanged. Prior raw reviews and prompts are preserved byte for byte. DR-0029 P1–P10 and DR-0028 P6(b) remain open; the geodetic-drag discrepancy remains escalated. These scope conclusions rest on my git/file inspection. Remote CI and repository settings were inaccessible.

## Execution ledger

The [complete command ledger](<snap>/review_scratch/command-ledger.md) records executed commands, file inspections, scratch-script creation, retries and progress checks. The reviewer scripts and logs are retained beside this report. No fixes were made.

Key executions, all using `.venv/bin/python`:

| Command or retained driver | Own result |
|---|---|
| `-m pytest -q -p no:cacheprovider docs/science/experiments/m3-t0/check_review01.py docs/science/experiments/m3-t0/check_review02.py` | 50 passed, 164.35 s |
| `review_scratch/run_experiments.py` | Atmosphere, decay, geodetic, frames, regression, termination and axis-ablation JSON outputs reproduce committed bytes |
| `docs/science/experiments/m3-t0/t0_gmat.py --gmat-console "$PWD/../GMAT R2026a/bin/GmatConsole" --out "$PWD/review_scratch/t0_gmat_results.json"` | All cases complete; result JSON byte-identical; all rewritten tracked GMAT artifacts unchanged |
| `docs/science/experiments/m3-t0/mutation_check_review02.py review_scratch/mutations.json` | Control passes 50/50; 15 corruptions detected by declared checks; one equivalent mutant passes. Failure sets match supplied evidence |
| `-m pytest -q -p no:cacheprovider` | 1185 passed, 3 warnings, 1747.56 s |
| `toolbox/validators/m1_proof.py --out review_scratch/m1.json` | PASS |
| `toolbox/validators/m2_proof.py --out review_scratch/m2.json` | PASS, 228 checks, zero failures (without `--quick`) |
| `toolbox/scripts/gmat_m1.py compare`; `toolbox/scripts/gmat_m2.py compare` | M1 and all three M2 comparisons pass |
| `review_scratch/red_before.py` | At `5548d11`: 11 failed, 39 passed. Amended Review 01 checks at `bdcaacf`: 11 failed, 1 passed |
| `review_scratch/independent.py` | Seven required digests match; cubic derivative identity checked; independent QR axis fit: 0.9856650955295294 m RMS |
| `review_scratch/math_audit.py` | Independent two-body endpoint calculation on 10,000 domains agrees within 7.11e-14 m; old/new floors and unchanged two-body table verified |
| `review_scratch/float_boundary.py`; `review_scratch/counterexample.py` | Envelope violations found at seven downward jumps; one input verified with 80-digit arithmetic |
| `-m pytest -q -p no:cacheprovider review_scratch/test_boundary_guarantee.py` | 1 failed, reproducing R3-F1 |
| `review_scratch/audit.py`; `review_scratch/post_audit.py` | Quoted correction quantities, 13 spike/table hashes, preserved reviews, GMAT identity and clean protected paths checked |

The first GMAT attempt incorrectly resolved the executable symlink and inferred the wrong installation root. It failed before running GMAT; retrying with the absolute `bin/GmatConsole` path succeeded. Two reviewer parsing attempts also failed initially: repeated GMAT headers, and the three-object M2 comparison output. Both scratch parsers were corrected and rerun. These were reviewer-tooling errors, not findings.

Result files inspected: all eight committed `t0_{atmosphere,axis_ablation,decay,frames,geodetic,gmat,regression,termination}_results.json`, their rerun counterparts under `review_scratch/`, the axis-probe report and metadata, the supplied mutation JSON, the new mutation JSON, `m1.json`, `m2.json`, and both comparison outputs. Relevant extracted values are in `audit.log`, `independent.log`, `math_audit.log` and `post_audit.log`. Prior reviews, their prompts, decision/assumption registers, VAL-0019, the report, matrix, README and appended dispositions were inspected; the supplied historical Proof/CI statements remain documentation evidence where explicitly noted below.

The five protected digests match:

- `proof/thresholds/m1.json`: `446e75ee…16fdb3d`
- `proof/thresholds/m2.json`: `9d4eab47…9e5f0ce9`
- GMAT M2 manifest: `f8d6bd78…e5ce585`
- M2 reference snapshot: `a2cddf4b…241448b`
- M2 final-state golden: `dc3baf7a…aa951dc`

The console digest is `1162803de3ed7172bce882b201b00e58de5b604c76a2ba02d16ac6765e7552e2`; its installed atmosphere table is `75762f679f82e089a4a6eadaa1251c797a2151aab5311b36b2ae96cffefda85e`. These are my hashes, matching the claimed installation. Full protected digests are in `independent.log`. Environment: Python 3.12.15, NumPy 2.5.3, SciPy 1.18.1, macOS 26.2 x86_64.

## Resolution table

| Item | Disposition | Evidence and qualification |
|---|---|---|
| M3T0-R2-F1 | RESOLVED | Own reruns and inspection confirm perturbed rows use sampled estimates, without `bound_m`/`bound_holds`. The cubic is correct; refinement exceeds sampling. Current records explicitly disclaim a perturbed bound and block uses requiring one. |
| M3T0-R2-F2 | PARTIALLY RESOLVED | The real-arithmetic product envelope, per-band derivative and height monotonicity are correct; the original counterexample is covered and numerical roots reproduce. Floating-point height evaluation is not covered: R3-F1. |
| M3T0-R2-F3 | RESOLVED | The original zeroed-sweep/floor defect is detected. Independent recomputation, coverage, units, provenance and mutation checks now protect those quantities. The additional boundary-testing weakness is included in R3-F1. |
| IM-1 | RESOLVED | Submitted rerun is byte-identical; independent QR reproduces 0.98566509553 m RMS. Data digest, frames, units, 1792 equations, 60 s sampling and RMS definition agree. The result remains evidence, not an approved threshold. |
| M3T0-F1 | RESOLVED | Chord/curvature theorem retained; two-body bound verified; perturbed estimates correctly separated; phase/refinement checks pass. |
| M3T0-F2 | PARTIALLY RESOLVED | Exact stiffness roots, speed bound, original counterexamples and same-tick semantics reproduce. The added sufficient-domain argument still lacks the numerical-height coverage identified in R3-F1. |
| M3T0-F3 | RESOLVED | Rerun gives k2/k3/k4 height offsets +116.312773/−115.734153/+1.161267 m; records identify k3. |
| M3T0-F4 | RESOLVED | GMAT rerun reproduces 6.95223445873689e-6 m; current records quote 6.95e-6 m against the unchanged 1e-4 m gate. |
| M3T0-F5 | RESOLVED | Record inspection confirms the owner's gate controls: P10 before T1 and P1–P10 before T2; the narrower technical dependency map is explicitly subordinate. |

The mutation harness requires pytest exit 1 and a failure in a declared detecting check; unrelated failures alone are not counted. My run reproduces all supplied failure sets, including 30 failures for the exact Review 02 mutant. Zeroed/shifted floors fail the independent floor calculation; zeroed/halved/dropped sweeps fail recomputation or coverage. Script provenance failures detect changed regenerated output, rather than independently proving the changed physics wrong. The control and equivalent mutant each pass 50 checks.

## Mathematical and numerical assessment

Writing `c = a − b²/a`, `K = cos δ_max`, and `s = sma`, I independently differentiated

`g(r)/μ = (2/r − 1/s)/(r − c) − K/r²`.

Multiplying its derivative by `s r³(r−c)²` gives exactly

`r³ + (2Ks−4s)r² + (2sc−4Ksc)r + 2Ksc²`.

The multiplier is positive on the declared exterior bound-orbit domain. The implementation retains endpoints and approximately real roots inside `[r_p,r_a]`; no denominator singularity is in that domain. The analytic maximum-normal cosine is `2ab/(a²+b²)`, agreeing with the numerical value to one floating-point step.

The stationary-point mutant is mathematically equivalent on this domain, although a finite scan alone would not establish that. Dividing the cubic by `s r²` gives

`F(r) = r/s + 2K−4 + (2−4K)c/r + 2Kc²/r²`.

Its derivative is positive for `r > 4Kc/(4K−2) ≈ 85,396 m`, well below the domain's `r > a = 6,378,137 m`. Thus any stationary point changes `g′` from negative to positive and is a minimum. An interior maximum cannot beat the endpoints. This independently supports the harness's equivalence classification; it does not turn its domain scan into a proof.

For ideal exact height, the corrected drag product has logarithmic derivative `2ω/(s+ω(a+h)) − 1/H < 0` for nonnegative speed and the pinned scale heights. Maximizing over the lower endpoint and later band bases correctly covers upward/downward jumps and the unbounded top band. Taking a supremum over a shrinking height domain is nonincreasing in its lower limit, while increasing the speed increases the envelope. Consequently V, A0 and A2 decrease and L2, L3 and L4 increase with initial height wherever defined. The three reported crossings are reproduced by the independent bisection checks.

The roots reproduce as 124456.68544482533 m, 118633.50894609134 m and 111511.96182423369 m. B25.8 moved −1.126e-7 m; the other two are unchanged. The rerun's 6000 stress states stay within their recorded bounds; the smallest stage margin is 0.102702 m. My additional 108 explicit polar/equatorial states at the exact floors and immediately above them also stay above zero (`polar_floor.py`/`.log`); the lowest drag-free stage is 11.74682 m. These numerical observations do not repair the missing floating-height enclosure.

The chord inequality and exterior distance-Hessian argument remain valid. The two-body result is an analytic bound evaluated with ordinary floating-point arithmetic, explicitly qualified by rounding; it is not interval-certified computation. The J2+drag sweep is empirical. Its maximum between-sample refinement increment is 8.6409e-10 m; the quoted 0.025 m two-body margin, 0.036 m sampled-estimate gap and 0.087 m initial-two-body-reference gap agree with the result file. A5-b needs endpoint detection and an interpolated crossing time, not a guaranteed maximum missed dip. Accepting its documented missed-crossing limitation remains an owner decision.

IM-1 measures the residual of fitting GMAT EarthFixed Z as `u(t)·r_TOE`, rather than a propagated trajectory error. The quadratic-only nine-parameter fit and full fifteen-parameter fit use two spacecraft, 896 epochs from 0 through 53700 s, and km-to-m conversion. My QR result differs from the stored quadratic RMS by 2.25e-11 m, comfortably within 1e-6 m. The documented conditioning-based rounding scale supports a practical reproduction tolerance; no cross-BLAS worst-case error theorem was independently established.

## New finding

**M3T0-R3-F1 — MINOR — the drag-envelope guarantee omits numerical height error at density discontinuities. VERIFIED.**

References: `docs/science/experiments/m3-t0/t0_termination.py:439–463`, `:549–583`; `check_review02.py:430–439`; DR-0029 P1, especially lines 81–88. VAL-0019 and the Review 02 dispositions repeat the stage-domain guarantee.

The derivation bounds exact geodetic height through a Lipschitz argument, but acceleration evaluates density using the numerically recovered height. A tiny downward error can cross a downward density jump and create an acceleration excess much larger than arithmetic roundoff. The envelope does not include that uncertainty.

Reproduce with `.venv/bin/python review_scratch/counterexample.py`:

```text
L = 120000 m; s = 11000 m/s; B = 850/33 kg/m²
r = [5420209.728043159, 3584286.6758661848, 1.8499824933775928] m
v = [6067.454938935459, -9175.29239664793, 0] m/s
```

Using the exact binary floating-point coordinates as inputs, an independent 80-digit geodetic iteration gives:

- True height: `120000.000000000023302762183195… m`, therefore `h ≥ L`.
- Speed: `10999.9999999998914… m/s`, therefore `|v| ≤ s`.
- Two-body energy: `−840726.088109… J/kg`, inside the unrestricted bound-state domain.
- Model height: `119999.99999999907 m`, selecting the lower band.
- Claimed envelope: `0.06230417914238045 m/s²`.
- Actual model drag: `0.06230901450414247 m/s²`.

The excess is `4.835361762e-6 m/s²`, approximately `7.7609e-5` relative. The committed test's subtraction-roundoff allowance is only `3.36e-14 m/s²`. The retained reviewer test fails even with a larger `1e-12 m/s²` allowance. Similar cases were found at 50, 90, 110, 140, 200 and 250 km.

The committed adversarial test checks a different domain: it replaces the original lower bound with `min(low, h_model)` before checking acceleration. For this input that widened envelope is `0.06230901450414418 m/s²`, so the altered test passes. `stage_lower_heights` does not apply an equivalent numerical-height enclosure.

This disproves the stated envelope as a bound on the implemented force for every point satisfying the geometric height/speed assumptions. It does **not** demonstrate an RK4 stage below zero at the published floors; the real-arithmetic theorem and the observed stress successes remain valid.

Recommended correction: explicitly distinguish exact geometric height from computed height; derive a justified numerical-height enclosure over the supported domain and include any reachable adjacent band in the force envelope. Propagate that enclosure and rounding treatment through the stage condition and recompute its floors. Add exact-base, downward-jump cases that retain the original lower bound. Preserve the pinned table and supported domain; do not substitute an arbitrary multiplier for this derivation.

## Verification limits and checkpoint

I did not run the prohibited M1/M2 wrapper scripts. Their supplied clean-clone 9-step/20-step results at `14d98f0` are documentation-only historical claims. My independent project suite, non-quick validators, comparisons and digest checks are recorded above; they are not a claim to have rerun those exact wrappers.

CI run `39201618112` and the four successful job claims could not be independently checked without network access. The three suite warnings are overflow warnings in existing intentional overflow-rejection tests (see `pytest.log`); all tests pass. Remote branch protection, other platforms/BLAS implementations, printed atmosphere-source provenance and the cause of GMAT's escalated geodetic-drag discrepancy remain unverified. DOP853 and several regression checks share the spike force model, so their agreement is not independent validation of every force equation. Sampling and stress tests do not certify a global perturbed-motion bound.

After the GMAT rerun, `git status --porcelain` and `git diff --stat` were both empty. Exactly zero tracked files changed; no restoration was necessary. Reviewer files exist only under `review_scratch/`.

T0 is not eligible for acceptance review while R3-F1 and the partial resolutions remain. The next required authorization is a narrowly scoped correction and validation pass for R3-F1, plus separate authorization for any further independent review. This review makes no owner decision, begins no T1/T2 work and authorizes no merge.

VERDICT: REQUEST_CHANGES
