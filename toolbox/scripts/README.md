# Scripts

Repeatable project operations with deterministic CLI behaviour and machine-readable output.

| Script | Purpose |
|---|---|
| `run_mission.py` | Run a scenario headlessly. Writes `events.jsonl` and `summary.json`. Exit 0 on mission success. |
| `gmat_m1.py` | Generate, run, and compare the M1 GMAT reference case (DR-0005) |
| `gmat_m2.py` | Generate, run, and compare the M2 GMAT finite-burn references (T6, DR-0015/DR-0016) |
| `reference_snapshot.py` | Generate, verify, compare and measure the M2 approved reference snapshot (DR-0021) |
| `m2_t7_measure.py` | The T7 three-platform measurement bundle (VAL-0016) |
| `run_m1_proof.sh` | The complete M1 Proof suite; writes `proof/records/evidence/M1/` |
| `run_m2_proof.sh` | The single-host M2 Proof suite (T8), including every M1 gate; writes `proof/records/evidence/M2/` (or the directory given, never the M1 evidence). The three-platform gate is the CI job `m2-cross-platform` |

Likely future additions: `replay_mission.py`, `summarize_events.py`.
