# ruff: noqa
from pathlib import Path
from tars.validation import reference_snapshot as s

for name in ["session_f50_16", "session_corrupt16"]:
    source = Path("review_scratch/" + name + ".py").read_text()
    source = source.replace("session_corrupt16.json", "lost_ledger17.json")
    try:
        exec(compile(source, name, "exec"), {})
    except AssertionError:
        print("EXPECTED REJECTION", name, flush=True)
    else:
        raise AssertionError("old false-pass returned")
