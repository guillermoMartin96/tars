# ruff: noqa
import importlib.util, runpy
from pathlib import Path

sp = importlib.util.spec_from_file_location("baseline17", "toolbox/scripts/reference_snapshot.py")
t = importlib.util.module_from_spec(sp)
sp.loader.exec_module(t)
expected, failures = t.record_all()
assert not failures
for name in ["baseline_parts16", "baseline_keys16", "nodes16", "wrong_inputs16"]:
    code = Path("review_scratch/" + name + ".py").read_text()
    code = code.replace("t.verify_baseline(d)", "t.verify_baseline(d, expected=expected)")
    code = code.replace("assert not problems", "assert problems").replace(
        "assert not ps", "assert ps"
    )
    exec(compile(code, name, "exec"), {"expected": expected})
    print("REJECTED ALL", name, flush=True)
