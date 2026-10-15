# ruff: noqa
import importlib.util, inspect, math, pytest
from pathlib import Path
from unittest.mock import patch
from tars.validation import m2, gmat_m2, thresholds

s = importlib.util.spec_from_file_location("tests_gmat", "tests/test_gmat_m2.py")
t = importlib.util.module_from_spec(s)
s.loader.exec_module(t)


def run(label, fn, args=()):
    mp = pytest.MonkeyPatch()
    try:
        fn(mp, *args) if "monkeypatch" in inspect.signature(fn).parameters else fn(*args)
        print(label, "UNEXPECTED PASS", flush=True)
    except AssertionError:
        print(label, "test FAILS as required", flush=True)
    finally:
        mp.undo()


def mutated(mod, fn, edit):
    ns = dict(mod.__dict__)
    exec(edit(inspect.getsource(getattr(mod, fn))), ns)
    return ns[fn]


old_post = lambda self: setattr(
    self, "failures", [k for k, v in self.thresholds.items() if not self.metrics[k] <= v]
)
with patch.object(thresholds.Check, "__post_init__", old_post):
    run("disabled Check", t.test_non_finite_gated_metrics_fail_every_check)
    run("disabled Check O9", t.test_o9_rejects_a_negative_infinity_metric)
with patch.object(m2, "worst", lambda *vs: math.inf if any(math.isnan(v) for v in vs) else max(vs)):
    run("disabled worst", t.test_worst_rejects_negative_infinity)
p = t._proof_module()
p._merge_audits = mutated(
    p,
    "_merge_audits",
    lambda s: s.replace(
        "m2.worst(x) if k not in dst else m2.worst(dst[k], x)", "max(dst.get(k, -math.inf), x)"
    ),
)
p._merge_audits.__globals__["math"] = math
with patch.object(t, "_proof_module", return_value=p):
    run("disabled merge", t.test_merging_keeps_negative_infinity_as_failure)


def no_finite(s):
    return s.replace("if not math.isfinite(z):", "if False:")


with (
    patch.object(m2, "orbit_checks", mutated(m2, "orbit_checks", no_finite)),
    patch.object(gmat_m2, "_node_crossings", mutated(gmat_m2, "_node_crossings", no_finite)),
):
    for bad in (math.nan, math.inf, -math.inf):
        run(
            "disabled node " + str(bad),
            t.test_node_bisection_rejects_non_finite_oracle_output,
            (bad,),
        )
    run("disabled node integrated", t.test_poisoned_node_oracle_fails_the_integrated_mission)
original = Path.read_text
for snippet in [
    "dst[k] = max(dst.get(k, -math.inf), x)",
    "out['k'] = max(x, out['k'])",
    "e = max(abs(p) for p in orders)",
    "e = np.nanmax(errors)",
    "e = errors.max()",
]:

    def read(path, *a, **k):
        source = original(path, *a, **k)
        if str(path).endswith("toolbox/validators/m2_proof.py"):
            source += "\ndef unsafe(dst,k,x,out,orders,errors,np,math):\n    " + snippet + "\n"
        return source

    with patch.object(Path, "read_text", read):
        run("guard mutation " + snippet, t.test_every_max_min_call_in_the_validators_is_reviewed)

for mod, fn in [(m2, "orbit_checks"), (gmat_m2, "_node_crossings")]:
    with patch.object(mod, fn, mutated(mod, fn, no_finite)):
        run(
            "disabled independently " + fn,
            t.test_node_bisection_rejects_non_finite_oracle_output,
            (math.nan,),
        )
