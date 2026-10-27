# External Review: M3 T2 packet r2, Review 03 (closure review of the I-34A corrections)

- **Reviewer/model:** Codex (codex-cli 0.162.0), session `01a17b47-8e0d-7da1-af17-99d515946e66`. The reviewer is from a separate provider from the implementer, in a fresh session separate from Reviews 01 and 02.
- **Date:** 2026-10-26
- **Reviewed revision:** `8abfae249a58042370e4ac8c71cf13b5de7f6ef6`, the I-34A correction commit (`git diff 3bb3637..8abfae2`, eight files, all under `docs/`), on branch `milestone-3-t2-authorization`.
- **Authorization:** I-34A §6 (owner/Tech Lead, 2026-10-26). I-34A was received truncated in §6. The prompt reproduces it as received.
- **Raw records:**
  - `docs/reviews/raw/M3-T2-packet-r2-codex-review03-prompt.md`: the prompt, with I-34A verbatim;
  - `docs/reviews/raw/M3-T2-packet-r2-codex-review03.md`: the final message, verbatim;
  - `docs/reviews/raw/M3-T2-packet-r2-codex-review03-evidence/`:
    - the reviewer's scripts and outputs: `independent`, `additional` (a scratch-only Newton-budget experiment) and `provenance`;
    - the reviewer's reruns of the I-34A evidence: `reviewer_i34a_minor.out`, which is byte-identical to the committed output, and `reviewer_i34a_fingerprint_check.out`, which differs as described below;
    - `implementer_rerun.txt`;
    - `implementer_r03_repro.py.txt` and `.out`;
    - `SHA256SUMS`.
  - **Not committed:**
    - the reviewer's copies of the I-33 drafts, `f2_premise_controls` and the I-34A scripts;
    - `__pycache__/`;
    - the JSONL event stream.
- **How it was run:**
  - a fresh clone pinned at the full SHA;
  - `uv sync --locked`;
  - `review_scratch/` excluded from git;
  - `codex exec -C snap -s workspace-write --json -o codex_last_message.md -`;
  - no network and no extra inputs.

  The tracked tree was clean afterwards, and HEAD was unchanged.
- **Timing:** the review was launched while CI for `8abfae2` was still running. CI status is reported in the I-34A checkpoint.

## Summary
**`VERDICT: PASS`.** 0 BLOCKER, 0 MAJOR, **1 MINOR**, 1 NOTE.

| Review 02 item | Review 03 |
|---|---|
| R2-F1, DL-4 enforcement overclaim | **RESOLVED.** The reviewer built a component with different internal operations and identical bits. `numpy.cos` matches at 100 of 100 points the reviewer chose independently |
| R2-F2, 3-ulp rule | **RESOLVED.** The reviewer derived A(f) independently. 81 840 signed displacements agree with the checker. The 32 controls are byte-identical. sin(1) gives 2.983995602203121 ulps at 150 digits |
| R2-F3, DL-2 admissibility | **RESOLVED.** The first failing exponents are 139, 140, 143, 143 and 141, which reproduces the recorded values. The (2¹⁰²⁰,)³ case raises `ValueError` and the origin raises `ZeroDivisionError`. A scratch-only Newton budget of 2 000 corroborates the diagnosis; it is not a proposal |
| R2-F4, fingerprint provenance | **Accurately represented**, apart from the field count (R3-F1). Only the three CPU fields differ. The correction is proposed and not applied |
| Readiness M3T2R-R2-F1 … F3 | **Remain closed.** I-34A does not touch or contradict them |
| Scope | **No unauthorized expansion.** The added DL-2 review obligation is disclosed. No threshold, decision, protected path or prior record changed |

**All three Review 02 MINOR findings are resolved. One new MINOR and one NOTE remain.**

## Findings register and dispositions
Each disposition is the implementer's evaluation. **No correction is made.** I-34A authorizes no further correction round.

| ID | Severity | Location | Finding | Implementer's reproduction | Disposition |
|---|---|---|---|---|---|
| M3T2P2-R3-F1 | MINOR | `docs/reviews/M3-T2-packet-r2-review-02-corrections.md` §2 item 1; I-34A `i34a_fingerprint_check.py.txt` `fields()` | "3 of 44 fields; the other 41 are identical" counts bare leaf names. Repeated names in different JSON sections overwrite each other. There are **47 path-qualified fields: 3 differ and 44 agree** | **Confirmed** (`implementer_r03_repro.out`): 47 path-qualified fields and 44 distinct leaf names. `note` appears 3 times and `[O] version` twice. Exactly the same three CPU fields differ under either count | **ACCEPTED.** The record should say 47/3/44. Any future comparison should use path-qualified keys. The committed evidence stays unchanged. Not corrected: needs authorization |
| M3T2P2-R3-F2 | NOTE | `docs/reviews/M3-T2-packet-r2-review-02-corrections.md` §1, R2-F3 row ("Cause") | "a + t grows by about 1.5× per step": the denominators are a² + t and b² + t | **Confirmed:** I-33 `pog_lib.py.txt:385`, `ua, wb = a2 + t, b2 + t`. The mechanism is unaffected | **ACCEPTED.** It is a notation fix for a future authorized documentation pass. Not corrected |

## R2-F4: the cause is now observed, not only inferred
The implementer reran the reviewer's `independent.py` in the same pinned clone, outside the reviewer's sandbox (`implementer_rerun.txt`):
- **Reviewer's sandbox:** `sysctl` returns status 1, with empty stdout and stderr "Operation not permitted".
- **Implementer's unrestricted rerun:** status 0, and the values equal the committed I-33 values.

This observes, for this reviewer's sandbox, the mechanism that the I-34A record (§2 item 3) marked as **inferred** for Review 02's sandbox. Review 02's own run still kept no status, so for that run the cause remains inferred. The proposed correction, recording such a probe as `[U] unavailable (exit status, stderr)`, is still only proposed.

## Reruns
- `additional` and `provenance`: byte-identical.
- `independent`: identical except lines 20–22, the three `sysctl` probes, as described above.
- The reviewer's rerun of `i34a_minor` is byte-identical to the committed output.
- The reviewer's rerun of `i34a_fingerprint_check` differs only in the `sysctl` status lines (rc = 1 in the sandbox).
- Manifests:
  - I-34A: 5/5;
  - I-33: 18/18;
  - Review 02: 12/12;
  - this evidence: 11/11.

## Proof gate
- [x] All Critical findings resolved: none raised.
- [x] All High findings resolved: none raised (0 BLOCKER, 0 MAJOR).
- [x] Every substantive finding has an explicit disposition: R3-F1 and R3-F2 are ACCEPTED and **not corrected**.
- [x] Accepted Review 02 fixes re-tested: R2-F1, R2-F2 and R2-F3 are RESOLVED by independent reproduction.
- [x] Escalated scientific claims have authoritative evidence or remain BLOCKED: POG accuracy gating is BLOCKED pending review of DL-1 … DL-4. A-FP-2 rows are report-only. P6 geodetic drag is ESCALATED_FOR_INVESTIGATION.

**Review gate result: PASS.** The I-34A corrections close Review 02's three MINOR findings. **This PASS approves no decision, promotes no row, and authorizes no T2 implementation, numerical gate, correction pass or merge.**

**T2 implementation remains NOT AUTHORIZED.**
