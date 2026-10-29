# M3 T2 S1 I-48 evidence (corrected P-5 verification; I-47 stop record)

This evidence supports `docs/milestones/M3-T2-S1-decision-I48.md`. It adds to the earlier `s1-*`
directories and replaces none of them.

- **No production code or test is involved. S1 is NOT IMPLEMENTED.**
- Every result here is at BASE `ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd`. It was computed from git
  objects, so it does not depend on the state of any checkout.

| File | What it is |
|---|---|
| `p5_verify.py.txt` | The corrected P-5 verifier (P-5A, P-5B, P-5C). Standard library only. Run it as `python3 -I -B p5_verify.py <repo> <commit> [--search-root DIR ...]`. It exits 0 only when all six gates in decision record §4, "Automated gate", hold. Stored as `.py.txt` so CI's ruff does not lint evidence. Revised after Review 01 (R01, R04). |
| `p5_gate_selftest.py.txt`, `p5_gate_selftest.txt` | A negative self-test of the gates: perturbed results, plus a throwaway repository with a directory-escaping entry and an edited-then-reverted list. 12 checks, 0 failures. Run it as `python3 -I -B p5_gate_selftest.py <p5_verify.py> <result.json> <empty scratch dir>`. |
| `p5_render.py.txt` | Renders the verifier's JSON as `p5_summary.txt`. |
| `p5_result.json` | Verifier output at BASE, searching the committed tree only. |
| `p5_summary.txt` | The rendered result: 38 per-manifest P-5A rows, and P-5B/P-5C per list and per non-trivial entry. |
| `historical_p5_transcript_extract.txt` | The I-39 and I-40 P-5 commands and outputs, plus the I-39 report line stating the claim, extracted verbatim from the session transcript. Absolute paths are redacted to `<home>`/`<scratch>`. This is the evidence for the historical defect (decision record §2). |
| `i47/` | The I-47 stop evidence, unchanged: `p1_p2.txt`, `p4_ci.json`, `p5_manifests.txt` (the direct check of all 43, with 5 failures), `p5_diagnostic.txt` and `STOP.txt`. Its own `MANIFEST.sha256` verifies. |

To reproduce from a clone at BASE or later:

```
python3 -I -B docs/science/experiments/m3-t2/s1-i48/p5_verify.py.txt . ee602c5 > out.json
python3 -I -B docs/science/experiments/m3-t2/s1-i48/p5_render.py.txt out.json | diff - docs/science/experiments/m3-t2/s1-i48/p5_summary.txt
```

External evidence is in `~/projects/tars-evidence/I-48/`, listed in `MANIFEST.sha256`. It holds:
- the unredacted transcript extract;
- the host-local-search run (`p5_with_host_search.json` and `p5_summary_host.txt`, identical to the
  committed summary apart from the header);
- the owner texts;
- the Codex review.

Same host only (macOS x86_64). No cross-platform claim.
