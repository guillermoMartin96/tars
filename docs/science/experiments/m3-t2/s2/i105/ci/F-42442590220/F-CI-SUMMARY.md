# F CI evidence (I-106 §4): run 42442590220, attempt 1

All values below are observed in this run's own logs and records, extracted from the raw job logs
(`logs/`, sha256 in `raw-logs.sha256`). They are not taken from earlier runs.

| Item | Observed |
|---|---|
| Commit | F `9ff5ca903332f4ca3c05b697e6d9bd4224ec8932` (head SHA of the run and of every job; the ENV record's commit) |
| Run | attempt 1; conclusion success; 4/4 jobs success, each `run_attempt` 1, executed, none carried over (`run-check.json`) |
| ubuntu-latest, job 128614777135 | 1517 passed, 3 skipped. Linux x86_64, CPython 3.12.3 |
| macos-latest, job 128614777332 | 1517 passed, 3 skipped. macOS 26.7.2 arm64, CPython 3.12.10 |
| macos-15-intel, job 128614777434 | 1517 passed, 3 skipped. macOS 15.7.9 x86_64, CPython 3.12.10 |
| m2-cross-platform, job 128626352184 | success. Not a check job, so no S2 records |
| Records per check job | S2-ENV-RECORD, S2-G17A-REPORT, S2-G17B-RECORD and the schema-2 S2-XP3-LISTING. All extracted complete, with the listing body sha256 and entry count verified |
| Census, `validate_census.py … ci` | Valid on all three jobs: 22 665 records with all §3.10 fields. Outcomes are 19 154 accepted, 64 evolute_region and 3 447 non_convergence on each |
| G-17b | 0 differences on 8 853 class X entries on each job. `environment_kind` is `other` on all three, as observed |
| G-17a | `other` on each job; 0 class X, 0 label and 0 witness-slot differences. Class P coordinate differences: ubuntu 2 305, arm64 2 188, Intel 0. These are observations in `other` environments |
| Node count | 1 520 per job, against 1 518 at E (1 515 passed + 3 skipped). The difference equals the two added witness nodes; CI's quiet output does not name individual nodes |

**RP-8 / RP-9 (log route; report-only; not a gate).** Recomputed over F's three listings with the
committed `rp8_rp9_ci.py`, unchanged (`rp8-rp9/rp8_rp9_ci.json`).
- 0 outcome differences between any two platforms.
- Iteration-count differences: ubuntu/arm64 18, ubuntu/Intel 24, arm64/Intel 10.
- Max |dh|: 7.45e-9 m (ubuntu/arm64) and 1.49e-8 m (the two Intel pairs).
- Max |dphi|: 5.55e-16 rad (the ubuntu pairs) and 3.33e-16 rad (arm64/Intel).
- Equality of every pair metric with BC2's committed values is recorded as an observation only, not
  as a gate (`rp8-rp9/comparison-with-BC2-observation.txt`).

**Projection onto schema 1 (observation).** Each job's census, without its hex input columns,
differs from the same platform's E CI census in 0 rows (`summary.json`).
