# M3 T2 S1 proposal evidence (I-41, I-42; recorded under I-43)

Evidence for the S1 ForceContext proposals v1/v2 (`docs/milestones/M3-T2-S1-proposal-v1.md`,
`M3-T2-S1-proposal-v2.md`) and the two Codex reviews (`docs/reviews/M3-T2-S1-proposal-review-01.md`,
`-02.md`). **Nothing here is production code; S1 is NOT IMPLEMENTED.** The prototype exists only as
`prototype-v2.patch` against BASE `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`.

Scripts are stored as `.py.txt` / `.sh.txt` so that CI's `ruff check .` and `ruff format --check .`
do not lint scratch evidence (same convention as `docs/reviews/raw/*-evidence/*.py.txt`). Copy them
to `.py` / `.sh` to run. Same-host evidence only (macOS x86_64, CPython 3.12.15, uv.lock
`6d784550…50cf`); no cross-platform claim is made.

## Files

| File | What it is |
|---|---|
| `prototype-v2.patch` | Scratch prototype v2 relative to BASE: `src/tars/sim/forces.py`, `src/tars/sim/simulator.py`, `tests/test_s1_failure_paths.py`, `tests/test_s1_force_context.py` (sha256 `66aaf15e…e950`). |
| `harness.py.txt` | Main direct-API differential corpus (26 880 configurations). argv: output JSONL; tree selected by `PYTHONPATH`. |
| `harness_writers.py.txt` | Stage-writer corpus (26 112 lines incl. header) added after R-01. |
| `mutate.py.txt` | Mutation campaign (21 mutants). argv: prototype root, output dir. **R-03 corrected (I-43):** M-14's designated node is now T-07 (k) alone (previously T-07 (d) plus both whole files). |
| `mutation_results.json`, `mutation_summary.txt` | Campaign output with the corrected script (I-43 rerun): control 78/78; 20 killed for their declared reason; M-14 killed by T-07 (k) [NaN, +inf] (−inf pins nothing); M-19 survives 0/78 (equivalent, §M-19 below). Assertion texts contain process-specific object addresses. |
| `ast_identity.py.txt` | T-10 AST identity (51 checks). argv: BASE root, tip root. |
| `repro.sh.txt` | I-42 end-to-end re-verification from fresh clones (tests, corpora, mutants, T-10/T-11, scenarios, R-1…R-4, full suite). |
| `i42_reverification_summary.txt` | `repro.sh` summary log as produced. |
| `i42_missions.sha256` | Hashes of the 5 scenario output trees, BASE and prototype (corrected rerun, see note). |
| `probe_r02.py.txt`, `probe_r02-{base,proto}.json` | Implementer's independent R-02 reproduction (I-42). |

## Results (I-42 re-verification, fresh clones)

- Prototype S1 tests 78/78; at BASE T-07 27/27 green and T-01…T-06 51 nodes red (AttributeError), 0 collection errors.
- Main corpus BASE vs prototype byte-identical (sha256 `e0309486…a814`); option-A control differs in 964 cases (960 at dt = +inf; 4 finite: dt 1e308 and 8.98846567431158e307 with the zero-force and list-returning models; sha `5aa92f5f…eea4`).
- Writer corpus BASE vs prototype byte-identical (`3310fd90…0415`); M-14 differs in 46 cases, M-19 in 0.
- T-10 51/51; T-11 changed paths = the 4 allowlisted files.
- Scenarios: all 5 output trees byte-identical (10 files).
- R-1 M1 Proof PASS 9/9 (golden `7a4e1877…20a4`) at BASE and prototype; R-2 M2 Proof PASS 20/20, `m2_proof` 228/0 at both (final-states record differs only in `revision` and its self-hash); R-3 109 tests, r01/r02 byte-identical at both; R-4 314 at both; full suite BASE 1 290, prototype 1 368 (= 1 290 + 78).

**Note on `i42_reverification_summary.txt` line "missions: DIFFER".** That line is a script defect, not a
result: `repro.sh` did not create `$O/missions` before redirecting into it, so no scenario ran and
every comparison failed. The scenario step was rerun separately in the same clones after
`mkdir -p "$O/missions"`; all 10 runs exited 0 and the trees were identical (`i42_missions.sha256`).
The log is kept as produced.

## Equivalent survivor M-19 (accepted by the owner, I-43, within this scope)

M-19 builds the powered context with `ForceContext.deferred(mass)` instead of `ForceContext(mass)`.
In the current production code the powered `mass` reaching that call has already passed
`thrust_acceleration`'s `_require_positive` (finite, positive built-in float) and the legacy adapter
never reads the context, so eager and deferred validation cannot differ. Confirmed independently by
Codex round 2 (item 8). The equivalence holds only for the current production code; it does not
excuse early construction (M-14) and says nothing about the coast closure.

## External evidence (not committed: size)

Full corpora (30–36 MB JSONL each), clones, Codex event streams and per-mutant trees are kept outside
Git, with manifests:

- `~/projects/tars-evidence/I-41/` — `MANIFEST.sha256` sha256 `8b33f5d43405f46e60c9bbd80ed3ed404471ac1abad4895c75150485787794b2` (6 149 files; includes `proto-d619e50.bundle`, the prototype commit).
- `~/projects/tars-evidence/I-42/` — `MANIFEST.sha256` sha256 `99fba1dd9b1a475d2b06dbbc0e3a3f6eb0205b842afefe771fdbc23ef40e42ce` (975 files).
- `~/projects/tars-evidence/I-43/` — see `docs/science/experiments/m3-t2/s1-i43/README.md`.

The I-40 scratch evidence (precondition logs, probes) was lost to a session restart before it was
copied; the BASE R-1…R-4 runs above (I-42) reconstruct those preconditions.
