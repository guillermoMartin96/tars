import importlib.util
import os
from tars.validation import m2
spec = importlib.util.spec_from_file_location("old_m2", "review_scratch/old_m2.py")
old = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = old
spec.loader.exec_module(old)
family = os.environ["REVERT_FAMILY"]
if family == "F16":
    m2.check_result_consistency = old.check_result_consistency
elif family == "F17":
    m2.orbit_checks = old.orbit_checks
elif family == "F18":
    m2.check_event_order = old.check_event_order
