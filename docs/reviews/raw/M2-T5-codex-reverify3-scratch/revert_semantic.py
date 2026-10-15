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
    def old_extrema_with_current_names(*args, **kwargs):
        metrics, violations = old.orbit_checks(*args, **kwargs)
        metrics["min_altitude_error_m"] = metrics.pop("min_altitude_below_reference_periapsis_m")
        metrics["max_altitude_error_m"] = metrics.pop("max_altitude_above_reference_apoapsis_m")
        return metrics, violations
    m2.orbit_checks = old_extrema_with_current_names
elif family == "F18":
    m2.check_event_order = old.check_event_order
