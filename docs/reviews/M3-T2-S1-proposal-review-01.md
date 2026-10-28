# External Review: M3 T2 S1 ForceContext proposal v1 (I-41), Review 01

- **Reviewer/model:** Codex (codex-cli 0.162.0), thread `01a182de-61f6-7562-98a1-cc12cc1b8d43`. The reviewer is from a separate provider from the implementer.
- **Date:** 2026-10-28
- **Reviewed material:** a **proposal and scratch prototype**, not committed work:
  - `I-41-proposal.md` (proposal v1), sha256 `d2fe9b38f340f18c91fa02df4f8cff9e95ad9b3465278aa40420a48e78be0151`, recorded verbatim as `docs/milestones/M3-T2-S1-proposal-v1.md`;
  - `prototype.patch` relative to BASE `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`, sha256 `1562cbf1abf6796e262700809279555fe9e0d8c9251956deb619881ff34bc99e` (kept externally, `~/projects/tars-evidence/I-41/i41/review_pkg/`);
  - evidence scripts `harness.py` (`35791177…8772`), `mutate.py` (`fc630aa9…0db20ced`), `ast_identity.py` (`9aa51fb5…2a4e2f8c`).
- **Authorization:** I-41 (owner, 2026-10-28): independent Codex review of the option-B-for-coast proposal.
- **Raw records:**
  - `docs/reviews/raw/M3-T2-S1-proposal-codex-review01-prompt.md` (sha256 `c6bf09dc…ceb33`);
  - `docs/reviews/raw/M3-T2-S1-proposal-codex-review01.md`: the complete final message, verbatim (sha256 `51d390a4…bc11def`);
  - `docs/reviews/raw/M3-T2-S1-proposal-codex-review01-evidence/`: the reviewer's `REVIEW.md`, `REPRODUCE.md`, scripts (as `.py.txt`) and small outputs. Files over 120 kB and directories are listed with sha256 in `EXCLUDED.txt` and kept externally.
- **How it was run:** a fresh clone pinned at BASE; `uv sync --locked`; `review_scratch/` untracked; `codex exec -C snap -s workspace-write --json -o codex_last_message.md -`; no network. The tracked tree was clean afterwards and HEAD unchanged.

## Summary
**`VERDICT: REQUEST_CHANGES`.** 1 MAJOR, 0 other findings.

The reviewer independently confirmed the I-40 finite-`dt` counterexample (BASE and prototype both raise `FloatingPointError("non-finite state produced at tick 2")`; coast option A raises `ValueError`), found no prototype-vs-BASE difference in 256 edge configurations and 9 × 100-tick trajectories, confirmed the authorization boundaries, and refuted one equivalence claim (R-01).

## Findings

### M3T2S1-R1-F1 (R-01) — M-14 is not an equivalent mutant
**Severity:** High (MAJOR)
**Reviewer claim:** v1 §3.4 argued that the powered stage mass can never be invalid, so building the powered context before the finiteness check (M-14) is unobservable. RK4 stage arrays are writable; a legacy model can write NaN into the stage propellant through `r.base`. M-14 then raises `ValueError("total_mass_kg must be finite and positive, got nan")` where BASE and the prototype raise `FloatingPointError("non-finite state during a burn at t = 2.0")`.
**Evidence:** reviewer's `test_early_mass.py` and probe (raw evidence); reproduced independently by the implementer.
**Affected code/Proof:** proposal §3.4, §4–§6; I-39A §10 mutation table; T-07 plan. The prototype itself is unaffected.

**Implementer disposition:** `ACCEPTED`

**Implementer reasoning:** The finding is correct; the §3.4 bound was false. The powered context is safe because of ordering (finiteness check, F/m check, `law.direction`, `thrust_acceleration`, then the context), not because of an arithmetic bound.

**Resolution/evidence:** Proposal v2 (`docs/milestones/M3-T2-S1-proposal-v2.md`) corrected §3.4, added T-07 (k) (a legacy model writes NaN / +inf / −inf into the stage propellant; NaN and +inf kill M-14), withdrew the equivalence request and designated T-07 (k) as M-14's killer. Writer corpus: M-14 differs from BASE in 46 of 26 112 cases. **Closed by Review 02** (`M3-T2-S1-proposal-review-02.md`).

---

## Proof gate
- [ ] All Critical findings resolved: none raised.
- [ ] All High findings resolved: R-01 was open at the close of this review; closed in Review 02.
- [x] Every substantive finding has an explicit disposition.
- [x] Accepted fixes have been re-tested (in Review 02).
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: none escalated.

**Review gate result: FAIL (REQUEST_CHANGES).** This record does not convert the verdict. It authorizes nothing; **S1 is NOT IMPLEMENTED, NOT ACCEPTED, NOT MERGED.**
