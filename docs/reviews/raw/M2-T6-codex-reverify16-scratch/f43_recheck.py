# ruff: noqa
import runpy
import sys

sys.argv = ["correlated_probe.py", "correlated"]
try:
    runpy.run_path("review_scratch/correlated_probe.py", run_name="__main__")
except RuntimeError as exc:
    assert "anchor tick positions disagree" in str(exc)
    print("F43 original mutation now rejected:", exc)
else:
    raise AssertionError("F43 did not reject")
