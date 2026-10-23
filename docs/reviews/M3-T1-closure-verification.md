# M3 T1: focused closure verification after Review 03 (I-21 §7)

**Verifier:** Codex (separate provider), `codex-cli 0.162.0`, using the CLI's configured default model.
- **Session:** `01a16b20-6f91-7e00-aba1-0e29a838d58b`; final message written 2026-10-23 23:42:09 UTC. One attempt.
- **Sandbox:** `workspace-write`, no network.
- **Invocation:** `codex exec -C snap -s workspace-write --json -o codex_last_message.md - < M3-T1-codex-closure-prompt.md`. As before, the wrapper on this host reports `--dangerously-bypass-hook-trust` as enabled; this invocation did not pass it.
- **Authority:** "Authorization I-21 — M3 T1 Review 03 Closure" (Tech Lead), §7: "a focused independent Codex verification of the I-21 closure changes … not an automatic full Review 04".

**Verified commit:** **`e404b0f40a3a46c0a71041636e0f87eb5fa247f3`**, head of `milestone-3-t1-j2-force-model`.
- The closure commits are `481a62e` (tests) and `e404b0f` (records and harness), on top of the Review 03 record `d01d6aa`. The production code is that of `4b85ded`.
- **Environment:** a fresh GitHub clone detached at the pinned SHA, with its own `uv sync --locked` environment and `review_scratch/` excluded from git. The implementer placed CI exports in `review_scratch/ci/`:
  - run 40034728330 (`e404b0f`);
  - run 40020290720, attempts 1 and 2 (`d01d6aa`).
- **Prompt:** reproduces I-21 verbatim. It lists the implementer's claims, including the validation and CI figures, as claims to verify, and maps the five I-21 §7 items into the verification.
- **Precondition:** CI on `e404b0f` was green on all four jobs before launch.

## Files
- **Prompt:** `raw/M3-T1-codex-closure-prompt.md`.
- **Raw output:** `raw/M3-T1-codex-closure.md`, the verifier's saved `review_scratch/M3-T1-codex-closure.md`. The CLI's final message is the same text without the trailing newline. Absolute paths are redacted as `<SNAP>`, `<SCRATCH>` and `<HOME>`.
- **Verifier scripts and logs:** `raw/M3-T1-codex-closure-evidence/` (33 files plus `SHA256SUMS` and `reviewer-SHA256SUMS`).
  - `*.py.txt` are the verifier's scripts, renamed from `.py`, and `COMMANDS.md` is its ledger.
  - `target.diff` and `alternative.diff` were derived by the implementer from the verifier's two mutated `src/` copies: the targeted mutant and the verifier's own alternative wrong implementation.
  - `reviewer-SHA256SUMS` covers the verifier's original files.
  - **Omitted** as copies derivable from git: the verifier's archives of `b1566ae` and `97b69ef`, `archived_forces.py` (identical to `b1566ae:src/tars/sim/forces.py`), `historical_tests/` (identical to the T1 tests at `4b85ded`), the two mutated `src/` trees and `__pycache__/`.

## Verdict
**`VERDICT: CLOSURE VERIFIED`.** There are **no new findings**.

| Item | Verifier's status | Basis (verifier's own execution) |
|---|---|---|
| M3T1-R3-F1 | CLOSED | Canonical example re-run: result (−0.0, −0.0, −0.0005692785957521009), computed factor exactly 0, two `Fraction` constructions during evaluation and none during construction. The non-zero reach bound recomputed as ≈ 1.6262597531022472e-299 (normal). The bound of two comparisons per evaluation and three at construction confirmed by code inspection; each comparison constructs two operand Fractions |
| M3T1-R3-F2 | CLOSED | Alias sequence re-run on archived `b1566ae`: μ = −1 at acceleration time, x = 3.991922438949618e-17, μ = 0 when the row is built. Raw files byte-identical to `d01d6aa` |
| M3T1-R3-O1 | CLOSED | See below |

The verifier's derivation of the boundary construction, in units u = 2⁻¹⁰⁷⁴:
- μ = (2⁵² + 1) u is representable and normal, since the spacing at MIN_NORMAL is u.
- p1 = −3/4 exactly.
- The exact p2 is −(3·2⁵⁰ + 3/4) u and the rounded p2 is −(3·2⁵⁰ + 1) u. The distances to the neighboring representable values are u/4 and 3u/4, so the product is inexact and not a tie.
- Both magnitudes lie strictly between 2⁵¹ u and 2⁵² u.
- Both later multiplications are exact, and k ≈ −1.749869284693536e-302 is normal. Production therefore raises specifically at p2.
- In the companion, p2 = −3·2⁵⁰ u is exact; construction and evaluation succeed within 2γ₁₆.

## Further results from the verifier's own execution
- T1 tests: 109 passed, collected as 97 + 12. Full-suite collection: 1290 tests; the full suite was not run.
- Ruff check and format: clean (238 files).
- `src/` is unchanged from `4b85ded`. The protected paths are unchanged from `60648b9`. The Review 03 record, the dossier, all of `docs/reviews/raw` and the I-20 mutation results are unchanged from `d01d6aa`. The records are append-only.
- **Targeted mutant:** the harness's replacement is the reviewer's threshold change only, and the exactness logic is retained. Result: 1 failed (the new rejection test, with "DID NOT RAISE ValueError"), 108 passed. Against the Review 03 tests: 107 passed.
- **The verifier's own alternative wrong implementation:** exempting only the rounded band product `−0x0.c000000000001p-1022` from underflow, with the threshold intact. It is caught by the same test: 1 failed, 108 passed.
- **Full campaign:** 47/47 detected, 47 by assertion. None of the earlier 46 lost a failing test.
- **Exploratory survivors:** `canonical_one_ulp` and `narrow_band` still survive, and `near_min_normal_zero` stays killed. The survivor, correction-check and informational outputs are byte-identical.
- **CI exports:** internally consistent. In run 40020290720 attempt 1 only the Upload Proof report step failed; attempt 2 succeeded.

## Verification limits (from the verifier)
- **Not independently reproduced:** the implementer's Proof runs (9/9, 20/20), the 228/228 validator result, the 314 T0 passes, the 1290 full-suite passes, the exit-127 attempts and reruns, and CI authenticity. The supplied golden digest agrees with the historical value, and the golden artifacts are unchanged.
- **The ENOTFOUND text** and the push grouping are not established by the exports.
- **Finite evidence:** this is test and code-inspection evidence, not exhaustive numerical or mutation coverage. The two exploratory survivors remain documented limitations.
- **Decisions:** no DR item or owner decision is resolved. The verifier states that T1 remains IMPLEMENTED — REVIEW PASSED — NOT ACCEPTED — NOT MERGED.

## Stop rule (I-21 §7, §9)
No defect and no blocking finding were identified. Per I-21 §9, the pass stops after this verification and the dossier completion; no further correction or review cycle is started.
