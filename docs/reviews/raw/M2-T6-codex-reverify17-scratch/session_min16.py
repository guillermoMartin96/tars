# ruff: noqa
from tars.validation import reference_snapshot as s
import math

with s.session("m2_proof") as rec:
    assert rec.approved is not None and rec.sha256
    rec.approved = None
    with s.scope("m2_prograde_burn_o6_k0", "o6"):
        s.pin(
            "o6.midpoint",
            "sim",
            r_m=[0.0, 0.0, 0.0],
            v_mps=[0.0, 0.0, 0.0],
            sma_impulsive_m=[-1e30],
        )
    print(
        "digest",
        rec.sha256,
        "mode",
        rec.mode,
        "problems",
        rec.finish(),
        "values_verified",
        rec.verified_values,
    )
    assert not rec.finish()
