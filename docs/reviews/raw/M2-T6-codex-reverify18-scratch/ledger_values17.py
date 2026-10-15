# ruff: noqa
import importlib.util, sys, math
import numpy as np
from unittest.mock import patch
from tars.astro import kepler
from tars.validation import reference_snapshot as snap
from tars.validation.m2 import specific_energy

sp = importlib.util.spec_from_file_location("proof17", "toolbox/validators/m2_proof.py")
proof = importlib.util.module_from_spec(sp)
sp.loader.exec_module(proof)
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
    original_digest = rec.sha256
    for key, item in rec.approved.items():
        if "/o6.midpoint#" not in key:
            continue
        p = item["parts"]
        from tars.validation.m2_missions import MISSIONS

        base = next(m for m in MISSIONS if key.startswith(m.name + "_"))
        sc = base.build()
        mu = sc.constants.mu
        r, v = original(
            np.array(p["seed_r_m"]["values"]),
            np.array(p["seed_v_mps"]["values"]),
            p["flight_s"]["values"][0] * 10,
            mu,
        )
        dv = rec.approved[key.replace("o6.midpoint", "o6.delta_v")]["parts"]["dv_mps"]["values"][0]
        sign = 1 if sc.commands[0].command["direction"] == "prograde" else -1
        vi = v + sign * dv * v / np.linalg.norm(v)
        a = -mu / (2 * specific_energy(r, vi, mu))
        p["r_m"]["values"] = r.tolist()
        p["v_mps"]["values"] = v.tolist()
        p["sma_impulsive_m"]["values"] = [a]
    with patch.object(kepler, "propagate", side_effect=phase):
        rc = proof.main(["--out", "review_scratch/ledger_values17.json"])
    print(
        "mutated ledger values, verify mode",
        rec.mode,
        "Proof exit",
        rc,
        "wrong-time returns",
        hits,
        "digest unchanged",
        rec.sha256 == original_digest,
        "problems",
        rec.finish(),
        flush=True,
    )
    assert rc == 0 and hits == 20 and not rec.finish()
