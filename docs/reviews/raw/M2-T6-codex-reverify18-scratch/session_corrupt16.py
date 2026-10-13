# ruff: noqa
import importlib.util, sys
from pathlib import Path
from unittest.mock import patch
from tars.astro import kepler
from tars.validation import reference_snapshot as snap

spec = importlib.util.spec_from_file_location("proof_record15", "toolbox/validators/m2_proof.py")
proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proof)
original = kepler.propagate
hits = 0


def phase(r, v, dt, mu):
    global hits
    f = sys._getframe(1)
    while f:
        if f.f_code.co_name == "impulsive_row":
            hits += 1
            return original(r, v, dt * 10, mu)
        f = f.f_back
    return original(r, v, dt, mu)


with snap.session("m2_proof") as rec:
    rec.approved = None  # corruption of session data after successful authenticated load
    with patch.object(kepler, "propagate", side_effect=phase):
        rc = proof.main(["--out", "review_scratch/session_corrupt16.json"])
print(
    "verification session, lost ledger: Proof exit",
    rc,
    "wrong-time returns",
    hits,
    "verified values",
    rec.verified_values,
)
assert rc == 0 and hits == 20 and rec.verified_values == 0
