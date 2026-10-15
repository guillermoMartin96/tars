# ruff: noqa
import sys, pytest
from tars.validation import reference_snapshot as s

mode = sys.argv[1]
if mode == "digest":
    s.Session._integrity_problems = lambda self: None
    select = "test_ledger_changed_during_the_run_is_detected or test_artifact_replaced_during_the_run_is_detected"
else:
    s.run_mode_problems = lambda *args, **kwargs: []
    select = "test_run_mode_problems or test_gmat_comparison_in_the_wrong_mode_fails or test_m2_proof_in_the_wrong_mode_fails"
raise SystemExit(
    pytest.main(["-q", "-p", "no:cacheprovider", "tests/test_reference_snapshot.py", "-k", select])
)
