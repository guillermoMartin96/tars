import importlib.util
import sys
import pytest
from tars.validation import m2
spec=importlib.util.spec_from_file_location('old_m2','review_scratch/old_m2.py')
old=importlib.util.module_from_spec(spec); sys.modules[spec.name]=old; spec.loader.exec_module(old)
fix=sys.argv[1]
if fix=='F1':
    m2.expected_initial_state=lambda scenario: __import__('tars.sim.runner',fromlist=['initial_state']).initial_state(scenario)
    names=['test_wrong_initial_orbit_fails_o4']
elif fix=='F2':
    m2.check_outcomes=old.check_outcomes
    m2.horizon_s=lambda scenario,events:events[-1].t
    names=['test_premature_success_fails_outcomes_and_o4']
elif fix=='F3':
    orig=m2.reference_metrics
    def no_samples(scenario,events,predicted):
        metrics,ref=orig(scenario,events,predicted)
        metrics['sample_position_error_max_m']=metrics['sample_velocity_error_max_mps']=0.0
        return metrics,ref
    m2.reference_metrics=no_samples
    m2.check_final_consistency=lambda events,result:[]
    names=['test_corrupted_powered_sample_fails_o4','test_inconsistent_final_state_is_detected','test_bogus_completion_at_an_active_stop_is_detected']
else:
    m2.check_event_order=old.check_event_order
    names=['test_missing_or_mismatched_depletion_event_is_detected[delete]']
sys.exit(pytest.main(['-q','-p','no:cacheprovider',*[f'tests/test_m2_validation.py::{n}' for n in names]]))
