# ruff: noqa
import runpy

try:
    runpy.run_path(
        "docs/reviews/raw/M2-T6-codex-reverify13-scratch/anchor_acceptance.py", run_name="__main__"
    )
except RuntimeError as e:
    assert "anchor tick positions disagree" in str(e) or "reference snapshot" in str(e)
    print("EXPECTED REJECTION", e)
else:
    raise AssertionError("reference was not rejected")
