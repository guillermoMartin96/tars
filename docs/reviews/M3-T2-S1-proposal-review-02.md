# External Review: M3 T2 S1 ForceContext proposal v2 (I-42), Review 02 (closure review)

- **Reviewer/model:** Codex (codex-cli 0.162.0), thread `01a1832e-f23d-7dc3-a328-691a3504d551`, a fresh session separate from Review 01. The reviewer is from a separate provider from the implementer.
- **Date:** 2026-10-28
- **Reviewed material:** a **proposal and scratch prototype**, not committed work:
  - `I-41-proposal-v2.md`, sha256 `bd7b26e858ae778efa2547e442c6c0e9bc71b62153a31836bc4b6246c795b667`, recorded as `docs/milestones/M3-T2-S1-proposal-v2.md` with only the R-03 editorial corrections (I-43);
  - `prototype-v2.patch` relative to BASE `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`, sha256 `66aaf15e1d4b9f9c4ea0057056538d5316ae11ff548a2d63f918b0611d88e950` (`docs/science/experiments/m3-t2/s1-proposal/prototype-v2.patch`);
  - evidence scripts `harness.py`, `harness_writers.py`, `mutate.py`, `mutation_results.json`, `ast_identity.py`; v1 and the Review 01 verdict for closure judgement; the I-40 record.
  - Package manifest verified by the reviewer (10 files; external copy `~/projects/tars-evidence/I-42/codex-review02/review_scratch/pkg/SHA256SUMS`).
- **Authorization:** I-42 §3 (owner, 2026-10-28).
- **Raw records:**
  - `docs/reviews/raw/M3-T2-S1-proposal-codex-review02-prompt.md` (sha256 `6b320d7f…4b4276`);
  - `docs/reviews/raw/M3-T2-S1-proposal-codex-review02.md`: the complete final message, verbatim (sha256 `7e528ba2…65c4a7`);
  - `docs/reviews/raw/M3-T2-S1-proposal-codex-review02-evidence/`: `REVIEW.md`, `COMMANDS.md`, scripts (as `.py.txt`) and small outputs; JSONL corpora and directories are listed with sha256 in `EXCLUDED.txt` and kept externally.
- **How it was run:** a fresh clone pinned at BASE; `uv sync --locked`; `review_scratch/` untracked; `codex exec -C snap -s workspace-write --json -o codex_last_message.md -`; no network. Tracked tree clean afterwards, HEAD unchanged.

## Summary
**`VERDICT: REQUEST_CHANGES`.** 1 MAJOR (R-02), 1 MINOR (R-03). **R-01: CLOSED.**

| Item | Review 02 |
|---|---|
| R-01 (Review 01) | **CLOSED.** No input reaches the powered `ForceContext(mass)` with an invalid mass (stage writers, custom integrators, views, aliased arrays). Order confirmed: finiteness → F/m → direction → `thrust_acceleration` → context → force. T-07 (k) kills an independently built M-14 for the intended reason (NaN, +inf); −inf pins nothing |
| Finite-`dt` counterexample | Preserved at 1e308, 8.98846567431158e307, 1.2e308; runner classifies `non_finite` |
| `dt = +inf` | No burn admitted; T-07 (a)/(b) keep BASE behaviour |
| Deferred coast context, U-1, OD-4 | Validated on every read, no cache or repair; type errors at construction; absent mass is `None` |
| M-19 | Equivalence independently confirmed **for the current production code** |
| Mutation plan | Control 78/78; 20 killed; M-19 survives |
| Scope | 4 allowlisted paths; T-10 51/51; no prohibited change; scenarios byte-identical |

## Findings register and dispositions

| ID | Severity | Location | Finding | Implementer's reproduction | Disposition |
|---|---|---|---|---|---|
| M3T2S1-R2-F1 (R-02) | MAJOR (High) | Prototype `simulator.py` coast closure (`float(y[_PROP])`); proposal §3.3 | The coast closure adds a scalar read of the stage propellant that BASE's coast path never performs. A custom integrator supplying a float64 ndarray subclass changes finite-`dt` behaviour: `MaskedArray` with masked propellant adds `UserWarning` (and, with warnings as errors, the tick is not committed); a subclass whose `__getitem__` raises makes the tick fail | **Confirmed and widened** (`docs/science/experiments/m3-t2/s1-proposal/probe_r02.py.txt`): dt = 0.5, zero force; BASE commits in every case; prototype: masked → `UserWarning`; raising `__getitem__` → `LookupError`, tick not committed; object dtype with `None` (outside the `NDArray[np.float64]` annotation) → `TypeError`, tick not committed; standard RK4 and complex controls identical | **ACCEPTED. Not fixed under I-42** (every remedy needs an owner decision). I-43 selected the lazy-coast direction for investigation: `docs/milestones/M3-T2-S1-I43-lazy-coast-investigation.md`. **OPEN** |
| M3T2S1-R2-F2 (R-03) | MINOR | Proposal v2 §2, §6.4; `mutate.py` M-14 node list | Stale references: `prototype.patch` (actual `prototype-v2.patch`); §6.4 omits T-07 (k); the M-14 node list names T-07 (d) before running both whole files (the kill does come from (k)) | Confirmed by reading | **ACCEPTED. Corrected under I-43:** v2 record §2 and §6.4; `mutate.py.txt` M-14 node is T-07 (k) alone; campaign rerun: M-14 failed 2/3 (k)[NaN, +inf], others unchanged, M-19 0/78 |

## Implementer's re-verification (I-42 §4)
All I-41 results reproduced from fresh clones; see `docs/science/experiments/m3-t2/s1-proposal/README.md` (corpora hashes identical to I-41; R-1/R-2 Proof PASS at BASE and prototype; R-3, R-4; full suite BASE 1 290 / prototype 1 368). Same-host only.

## Proof gate
- [x] All Critical findings resolved: none raised.
- [ ] All High findings resolved: **R-02 OPEN.**
- [x] Every substantive finding has an explicit disposition.
- [x] Accepted fixes have been re-tested: R-03 corrections re-run (mutation campaign); R-02 not fixed.
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: none escalated.

**Review gate result: FAIL (REQUEST_CHANGES).** This record does not convert the verdict. It authorizes nothing; **S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED.**
