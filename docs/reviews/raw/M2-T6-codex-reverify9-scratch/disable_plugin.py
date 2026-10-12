# ruff: noqa
import os
import math
import numpy as np
from tars.validation import m2, gmat_m2, thresholds


def pytest_configure(config):
    mode = os.environ["DISABLE_T6_FIX"]
    if mode == "F29":
        original = m2._check_reference_states

        def position_only(times, states, veh, predicted, where):
            if where.startswith("dense"):
                if not np.all(np.isfinite(states[:3])):
                    raise RuntimeError("DOP853 non-finite position")
            else:
                original(times, states, veh, predicted, where)

        m2._check_reference_states = position_only
    elif mode == "F30":
        from tars.astro import kepler

        gmat_m2.kepler_state = kepler.propagate
    elif mode == "F31":

        def finite_only(times, states, veh, predicted, where):
            if not np.all(np.isfinite(states)):
                raise RuntimeError("DOP853 non-finite state")

        m2._check_reference_states = finite_only
    elif mode == "F32":
        gmat_m2.manifest_anchor_problems = lambda base=None: []
    elif mode == "F33":
        thresholds._authenticate = lambda raw, key: None
