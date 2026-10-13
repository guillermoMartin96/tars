# Decision Request: Is runtime mutation of validator-internal state in the review scope? (clarifies DR-0019 B)

**Status:** OPEN  
**Requested from:** Guillermo / Tech Lead  
**Date:** 2026-10-13  
**Related milestone/issue:** M2 T6; DR-0019 (approved B), DR-0020 (approved A), DR-0021 (approved A); review record `docs/reviews/M2-T6-review-01.md`, re-verifications 16 and 17

## Problem
DR-0019 B puts out of scope "adversarially replacing or modifying the validator's own internal helper implementations". It keeps in scope bad data that reaches the validator: simulator output, GMAT references, threshold files, reference-library outputs, workflow failures, missing observations and non-finite metrics.

Two findings mutate the validator's **in-memory state** while it runs:

| Finding | Mutation | Status |
|---|---|---|
| F57 (round 16) | `Session.approved` set to `None` after authentication | Fixed: a verify session without its ledger fails closed. A missing ledger can also come from an ordinary bug, so failing closed is good practice anyway |
| **F58** (round 17, High) | (a) the authenticated ledger's *contents* edited in memory after loading; (b) the session's `mode` switched from `"verify"` to `"record"` | Open. With either, the F50 acceptance reversal and the F51 O6 change pass the Proof |

F58 is the same class as F57, taken further. Any guard in memory, such as a digest re-check at the end or a frozen mode flag, is itself in-memory state that the same mutation can edit. Code that can rewrite the ledger can equally rewrite:
- the loaded thresholds (already authenticated by digest at load);
- a `Check`'s result;
- the report dictionary before it is written.

So there is no fixed point. This is the regress that DR-0020 resolved for reference outputs, now applied to the validator itself.

The decision: does DR-0019 B's exclusion cover **runtime mutation of validator-internal state**, or only edits to validator *source code*?

## Options
### A — Clarify: validator runtime state is part of the validator (recommended)
DR-0019 B's out-of-scope boundary covers mutation of the validator process's own state after its inputs are loaded and authenticated. That includes:
- reference-snapshot sessions;
- loaded thresholds and manifests;
- `Check` objects and reports;
- module-level validator tables.

Modifying any of these requires the same access as editing validator code, and code review, mutation tests and the AST guard cover it.

**Unchanged:**
- Every input crossing into the validator stays in scope. That covers files (authenticated by digest), simulator output, reference-library outputs (pinned by the snapshot), workflow results and observations.
- F57's fail-closed behaviour stays.

F58 is recorded as `REJECTED_WITH_REASONING` under this clarification, with its mechanism documented.

**Pros**
- Bounded.
- Consistent with DR-0019 B's intent and with how thresholds and manifests are already treated, since they are authenticated at load and never re-checked in memory.

**Cons**
- No runtime defence against in-process tampering; that defence rests on review.

### B — A plus low-cost hardening
A, plus belt-and-braces checks that catch accidental corruption from a bug, not an adversary:
- At `finish`, recompute the ledger digest and compare it with the authenticated one.
- Make the Proof and the GMAT `compare` and `run` entrypoints assert that their session is in verify mode unless a recorder was explicitly passed.

These add about 2–3 s per Proof. The documentation would state that they do not defend against deliberate in-memory edits.

**Pros**
- Catches some accidental corruption.
- Costs little.

**Cons**
- Can be misread as an adversarial defence.
- Adds code with no threat-model justification under A.

### C — Treat in-memory mutation as in scope
Harden every in-memory structure against adversarial edits: ledger, mode, thresholds, checks, report.

**Cons**
- Unbounded, as shown above: each guard is itself mutable state.
- There is no fixed point short of running verification in a separate trusted process, which is out of proportion for M2.

## Recommendation
**A.** It matches DR-0019 B's intent, under which the validator is trusted code under review, and it bounds the review. B is acceptable if you want the accidental-corruption checks, with their limits stated.

## Impact
- **Architecture:** none under A; two small checks under B.
- **Science and validation:** none. No gate, threshold or measured value changes.
- **Effort:** A, documentation only; B, about an hour; C, open-ended.
- **Reversibility:** high.

## Blocked work
- The final T6 review round and the T6 checkpoint.

## Work continuing independently
- F59 (round 17, the 10-ulp tolerance floor) is fixed: tolerances are recomputed from the actual class maxima under one uniform rule, with a regression test.
- F57's fail-closed fix stays.

## Requested response
`A` / `B` / `C` / `discuss`.
