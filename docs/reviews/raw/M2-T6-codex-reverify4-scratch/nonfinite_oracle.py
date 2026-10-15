# ruff: noqa
import importlib.util, json
from unittest.mock import patch
import numpy as np
from tars.validation import m2

spec = importlib.util.spec_from_file_location("cli", "toolbox/scripts/gmat_m2.py")
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
original = m2.dop853_reference
for bad in [float("nan"), float("inf")]:

    def corrupt(*args, **kw):
        ref = original(*args, **kw)
        if 650.0 in ref:
            ref[650.0] = ref[650.0].copy()
            ref[650.0][:6] = bad
        return ref

    with patch.object(m2, "dop853_reference", corrupt):
        try:
            rejected, check = c._evaluate("m2_prograde_burn")
            print(
                repr(bad),
                json.dumps({"rejected": rejected, "passed": check.passed if check else None}),
                flush=True,
            )
        except Exception as e:
            print(repr(bad), "raised", type(e).__name__, str(e), flush=True)
