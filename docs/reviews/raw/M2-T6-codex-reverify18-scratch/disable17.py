# ruff: noqa
import sys, importlib.util
from pathlib import Path
import pytest
from tars.validation import reference_snapshot as s

mode = sys.argv[1]
old = importlib.util.module_from_spec


def make(spec):
    mod = old(spec)
    if str(spec.origin).endswith("toolbox/scripts/reference_snapshot.py"):
        loader = spec.loader

        class Loader:
            def exec_module(self, mod):
                source = loader.get_source(spec.name)
                if mode == "inventory":
                    source = source.replace(
                        "problems += _inventory_problems(records, expected, cov)",
                        "_inventory_problems(records, expected, cov)",
                    )
                elif mode == "arcs":
                    a = source.index(
                        "            got_b, got_h =", source.index("def _verify_gmat_mission")
                    )
                    b = source.index('        elif label == "o9.label_times":', a)
                    source = (
                        source[:a] + '            cov.add(key, "bounds_s", "step_s")\n' + source[b:]
                    )
                elif mode == "inputs":
                    source = source.replace(
                        'if got["parts"][part]["values"] == want["parts"][part]["values"]:',
                        "if True:",
                    )
                elif mode == "coverage":
                    source = source.replace("if unverified:", "if False and unverified:")
                elif mode == "crossings":
                    a = source.index(
                        '    got = _arr(rec, "crossings_s")', source.index("def _verify_crossings")
                    )
                    b = source.index("\n\ndef _independent_arcs", a)
                    source = source[:a] + '    cov.add(key, *rec["parts"])\n' + source[b:]
                exec(compile(source, spec.origin, "exec"), mod.__dict__)

        spec.loader = Loader()
    return mod


importlib.util.module_from_spec = make
if mode == "ledger":
    source = Path(s.__file__).read_text()
    source = source.replace('self._problem("no authenticated reference ledger", key)', "pass")
    source = source.replace(
        'self._problem("no authenticated reference ledger", "session finished without it")', "pass"
    )
    exec(compile(source, s.__file__, "exec"), s.__dict__)
selectors = {
    "arcs": "test_baseline_verification_requires_the_complete_inventory and arc-steps",
    "inventory": "test_inventory_rejects_an_extra_record_that_would_verify",
    "inputs": "test_baseline_verification_rejects_wrong_o5_inputs",
    "coverage": "test_coverage_rejects_a_part_no_check_verifies",
    "crossings": "test_crossing_count_is_checked_on_its_own",
    "ledger": "test_session_without_its_ledger_fails_closed or test_ledger_loss_is_reported_at_pin_and_at_finish_independently",
}
raise SystemExit(
    pytest.main(
        ["-q", "-p", "no:cacheprovider", "tests/test_reference_snapshot.py", "-k", selectors[mode]]
    )
)
