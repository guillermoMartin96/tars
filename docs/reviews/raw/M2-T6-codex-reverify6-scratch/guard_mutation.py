# ruff: noqa
import importlib.util
from unittest.mock import patch
from pathlib import Path

s = importlib.util.spec_from_file_location("t", "tests/test_gmat_m2.py")
t = importlib.util.module_from_spec(s)
s.loader.exec_module(t)
original = Path.read_text
for snippet in [
    "e = np.maximum.reduce(errors)",
    "e = np.minimum.reduce(errors)",
    "e = np.fmax.reduce(errors)",
    "e = np.fmin.reduce(errors)",
    "e = np.maximum(a,b)",
]:

    def read(p, *a, **kw):
        value = original(p, *a, **kw)
        return (
            value + "\ndef unsafe(np,errors,a,b):\n    " + snippet + "\n"
            if str(p).endswith("src/tars/validation/m2.py")
            else value
        )

    with patch.object(Path, "read_text", read):
        t.test_every_max_min_call_in_the_validators_is_reviewed()
        print("actual guard PASSES mutation:", snippet)

import math
import numpy as np
from tars.validation import m2

p = t._proof_module()
source = original(Path("toolbox/validators/m2_proof.py")).replace(
    "m2.worst(x) if k not in dst else m2.worst(dst[k], x)",
    "float(np.fmax.reduce([dst.get(k, -math.inf), x]))",
)


def read_merge(path, *args, **kwargs):
    return (
        source
        if str(path).endswith("toolbox/validators/m2_proof.py")
        else original(path, *args, **kwargs)
    )


with patch.object(Path, "read_text", read_merge):
    t.test_every_max_min_call_in_the_validators_is_reviewed()
    print("actual guard PASSES unsafe fmax.reduce merge")
ns = dict(p.__dict__, np=np, math=math)
exec(compile(source, "<mutated m2_proof>", "exec"), ns)
good = m2.Audit({}, {"o4_reference": {"sample_position_error_max_m": 0.1}}, {})
bad = m2.Audit({}, {"o4_reference": {"sample_position_error_max_m": math.nan}}, {})
print("unsafe merge hides NaN:", ns["_merge_audits"]([("good", good), ("bad", bad)]).metrics)
