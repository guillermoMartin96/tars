# ruff: noqa
import runpy
from tars.validation import reference_snapshot as s

with s.session("m2_proof") as rec:
    assert rec.approved is not None
    rec.approved = None
    runpy.run_path("review_scratch/joint_reference.py", run_name="__main__")
    print(
        "outer session lost ledger: problems", rec.finish(), "verified values", rec.verified_values
    )
    assert not rec.finish()
