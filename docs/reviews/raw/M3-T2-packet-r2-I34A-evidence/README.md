# I-34A correction evidence for packet r2 (research, NOT T2 evidence, NOT a gate)

Evidence for the I-34A corrections of the three MINOR findings of independent Review 02 (`docs/reviews/M3-T2-packet-r2-review-02.md`), and for the investigation of the R2-F4 fingerprint fields.

- **Host:** macOS x86_64 (Intel i9-9880H), CPython 3.12.15, the repository's locked environment (`uv sync --locked`) at `3bb3637`.
- **Inputs, unchanged:**
  - the I-33 drafts `pog_lib.py.txt` and `witness.py.txt` (`docs/reviews/raw/M3-T2-packet-r2-I33-evidence/`), copied beside the script as `pog_lib.py` and `witness.py`;
  - the T0 spike (`t0_termination.rounding_allowances`), imported read-only with bytecode writing disabled.
- **No tracked file was modified** by running these scripts. No fingerprint was regenerated.
- **How to run:**
  1. Copy each `*.py.txt` to a scratch directory as `*.py`. Also copy the two I-33 drafts.
  2. `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -I i34a_minor.py <repo>/docs/science/experiments/m3-t0`
  3. `.venv/bin/python -I i34a_fingerprint_check.py <I-33 f4_fingerprint.out> <Review 02 reviewer_f4_fingerprint.out>`. This one needs macOS `sysctl`.

| File | What it is |
|---|---|
| `i34a_minor.py.txt` / `.out` | **R2-F2:** checks the closed-form allowance A(f) in the defined ulp metric against the direct quotient (8 190 samples, every binade and the subnormals). Checks the I-33 checker against the closed form for 1 … 5 ulps (36 855 displacements). Covers Review 02's cases f = 1.5 and f = 2⁻¹⁰²², the e ≥ −969 corollary, and the sin(1) starting error.<br>**R2-F3:** draft DL-2 coverage on 8 fixed rays, 2²³ … 2¹⁰²⁰; the origin; (2¹⁰²⁰,)³ through the draft witness |
| `i34a_fingerprint_check.py.txt` / `.out` | **R2-F4 investigation:** finds which fields differ between the committed I-33 fingerprint and the reviewer's rerun. Re-reads exactly those fields from `sysctl` on the original host, keeping the exit status. Shows that the I-33 `run()` helper records a failing command as `''` |
| `SHA256SUMS` | Checksums of every file above |

## Limits
- **Single host.**
- **The F3 rays are samples.** They are not a supported-domain bound for DL-2.
- **The cause of the reviewer's empty fields is inferred, not observed.** The reviewer's run kept no exit status or stderr. The mechanism shown (stdout kept, exit status discarded) is the only path in `run()` that yields `''` without an exception.
