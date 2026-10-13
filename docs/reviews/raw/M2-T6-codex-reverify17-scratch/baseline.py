# ruff: noqa
from pathlib import Path

s = Path("docs/reviews/raw/M2-T6-codex-reverify13-scratch/baseline_verify.py").read_text()
s = s[: s.index("protected =")] + s[s.index("clean = json.loads") :]
Path("review_scratch/baseline_checks.py").write_text(s)
