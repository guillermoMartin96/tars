Correct H-01 from the completed independent S2 review. This authorizes local implementation and validation only. Do not commit, push, launch another review, accept S2, or merge.

BASELINE

Exact H:
`8074a19bf33cf5b6d20f7d211ff44f82bf28ba93`

Expected tree:
`3b70b865abfa4137227ccce0d070ba6484cdef26`

Implementation worktree:
`$HOME/.superset/worktrees/tars/milestone-3-t2-s2-geodetic`

Independent review evidence:
`$HOME/tars-evidence/S2-REREVIEW-H-8074a19/continuation-20261108T211523Z/`

Review MANIFEST.sha256 expected SHA-256:
`8400c3bfd78b5457d5cd06360efb0401c05db9d407765fa30c3f60bf2f61922f`

FIRST ESTABLISH THE INPUTS

Verify the review manifest hash and every entry. Read review.md, H-01-normalization.md, findings-disposition.md, obligation-ledger.json, method-and-evidence-scope.md, and the actual metaclass diagnostic source, output, run record, and environment record.

Read applicable repository instructions and the authoritative normalization requirements. Verify the implementation worktree is clean at exact H before editing. Stop on an integrity failure, unexpected target, or conflicting existing changes.

Do not modify the sealed review or any existing evidence.

FINDING TO CORRECT

H-01 is MINOR/must-fix. At H, src/tars/sim/geodesy.py:110 constructs the unsupported-type TypeError message using t.__name__. A caller-controlled metaclass can intercept that attribute lookup and raise its exact ValueError sentinel instead.

The witness uses an ordinary built-in tuple of length three with an unsupported coordinate object. Its exception is not from caller len/index access and is not permitted structural exception propagation.

Pinned v11 §3.8 step 0 requires every unsupported type to raise TypeError.

AUTHORIZED CORRECTION

Make unsupported-type rejection raise the prescribed TypeError without consulting user-dispatched class-name or formatting behavior. Prefer the smallest correction supported by the governing contract; do not preserve dynamic diagnostic detail at the cost of another callback.

Do not widen the E.1 try, catch and translate unrelated caller exceptions, change approved base-slot normalization, or alter numerical arithmetic.

Add a focused regression using the exact reviewer metaclass witness. It must assert:
- the required TypeError occurs;
- the sentinel does not escape;
- rejection does not invoke the metaclass hook.

Use assertion-based checks, not merely a zero process exit. Preserve existing structural len/index exception propagation and accepted-type normalization tests.

RED BEFORE GREEN

Before changing production source, run the new regression against H’s source in a disposable scratch copy. Preserve its expected assertion failure and bind the execution to the exact H source and new test bytes.

Then apply the minimal source correction and rerun the same regression with unchanged test bytes. Preserve both results and their ordering. Do not count collection errors or unrelated failures as the intended red result.

VALIDATION AND EVIDENCE

Use offline locked setup with:
`UV_OFFLINE=1 UV_PYTHON_DOWNLOADS=never $HOME/Library/Python/3.9/bin/uv sync --locked --offline`

Keep generated artifacts outside the implementation worktree where practical. Use disposable clones or scratch copies for proof-writing and mutation operations.

Run validation required by the governing correction scope, including:
- the exact H-01 regression;
- existing normalization, unsupported-type, structural propagation, and G-06 checks;
- the complete S2 test suite and applicable gates;
- G-17b exact Class X coordinate-bit replay, including signed zeros;
- the existing mutation campaign, preserving exact MG-02/MG-04 witness bindings and qualifying assertion kills;
- the full test suite and repository formatting/lint checks.

Inspect the governing corrected-tip regression requirements. Run applicable required checks on the corrected candidate bytes, including R-1 through R-4 where required; do not present H’s prior results as runs of the modified candidate.

For every new execution used as evidence, satisfy its applicable run-provenance and directly captured ENV/DL-5 duties. Preserve required listing, G-17a, and G-17b records where applicable. Do not extend the I-106 historical exception to any new execution.

Write a new additive correction packet under:
`$HOME/tars-evidence/S2-H01-correction/`

Use a new unused subdirectory if necessary. Include:
- the instruction and baseline identities;
- verified review-input identities;
- the minimal source/test diff and rationale;
- exact red/green commands, ordering, source/test hashes, outputs, and records;
- validation results and limitations;
- an assessment of which obligation evidence the correction affects;
- a proposed concrete commit/push sequence for later owner authorization;
- hashes and a verified manifest.

BOUNDARIES AND STATUS

The four I-104 findings were independently resolved at H; preserve that historical assessment. H’s ledger remains 29 MET, OB-11/OB-27 FAILED, and OB-30/OB-31 later-scope PENDING. Your correction does not itself change the independent verdict or close H-01.

Preserve DQ-1, convergence rules, rejection precedence, the frozen listing, simultaneous membership requirements, and all settled owner decisions.

Class P differences remain report-only where approved. POG accuracy gating remains BLOCKED; A-FP-2 remains unaccepted/unjustified. No new accuracy gate, conditional promotion, or later-scope implementation is authorized.

Do not change dependencies, CI, protected historical records, branches, or Superset workspaces. Use no network or CI queries/reruns.

Stop after delivering the local correction, validation evidence, manifest hash, exact worktree status, and proposed commit/push sequence. Leave everything uncommitted and unpushed.
