# ruff: noqa
import runpy
from tars.validation import reference_snapshot as s

with s.session("m2_proof") as rec:
    rec.mode = "record"
    rec.approved = None
    runpy.run_path("review_scratch/joint_reference.py", run_name="__main__")
    print(
        "corrupted session mode and ledger, snapshot problems",
        rec.finish(),
        "records verified",
        rec.report()["records_verified"],
    )
    assert not rec.finish()
