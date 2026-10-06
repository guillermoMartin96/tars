# Scripts

Repeatable project operations with deterministic CLI behaviour and machine-readable output.

| Script | Purpose |
|---|---|
| `run_mission.py` | Run a scenario headlessly. Writes `events.jsonl` and `summary.json`. Exit 0 on mission success. |
| `gmat_m1.py` | Generate, run, and compare the M1 GMAT reference case (DR-0005) |

Likely future additions: `replay_mission.py`, `summarize_events.py`.
