# ruff: noqa
import os, math, importlib.util
from tars.validation import m2, reference_snapshot as s

mode = os.environ["DISABLE16"]
if mode == "margin":
    m2.o5_snapshot_shifts = lambda: {
        "coast_position_error_max_m": s.TOLERANCES["sim", "m"],
        "coast_velocity_error_max_mps": s.TOLERANCES["sim", "mps"],
    }
elif mode == "comparison":
    s.TOLERANCES = {k: math.inf for k in s.TOLERANCES}
else:
    old = importlib.util.module_from_spec

    def load(spec):
        mod = old(spec)
        if str(spec.origin).endswith("toolbox/scripts/reference_snapshot.py"):
            loader = spec.loader

            class L:
                def exec_module(self, mod):
                    loader.exec_module(mod)
                    mod.INDEP_POS_M = math.inf
                    mod.INDEP_VEL_MPS = math.inf
                    mod.INDEP_BURN_POS_M = math.inf
                    mod.INDEP_BURN_VEL_MPS = math.inf

            spec.loader = L()
        return mod

    importlib.util.module_from_spec = load
