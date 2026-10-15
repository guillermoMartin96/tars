# ruff: noqa
from pathlib import Path

code = Path("review_scratch/session_corrupt16.py").read_text()
code = code.replace("rec.approved = None", 'rec.mode = "record"; rec.approved = None')
code = code.replace("session_corrupt16.json", "mode_corrupt17.json")
exec(compile(code, "mode_corrupt17", "exec"))
