import pytest
from tars.validation import m2

@pytest.fixture(autouse=True)
def revert_fix(request, monkeypatch):
    n=request.node.name
    if n.startswith('test_o3_detects'):
        old=m2.free_space_metrics
        monkeypatch.setattr(m2,'free_space_metrics',lambda *a,**k:{**old(*a,**k),'timing_violations':0.})
    if n.startswith(('test_auxiliary_runs','test_missions_without_burns')):
        old=m2.reference_metrics
        def ref(*a,**k):
            metrics,states=old(*a,**k)
            return {key:0. for key in metrics},states
        monkeypatch.setattr(m2,'reference_metrics',ref)
    if n.startswith('test_returned_result'):
        monkeypatch.setattr(m2,'check_result_consistency',lambda *a:[])
    if n.startswith('test_cli_summary'):
        monkeypatch.setattr(m2,'cli_summary_violations',lambda *a:[])
    if n.startswith('test_intermediate_propulsion'):
        monkeypatch.setattr(m2,'propulsion_sample_checks',lambda *a:({},[]))
        monkeypatch.setattr(m2,'accounting_metrics',lambda *a:({},[]))
    if n.startswith('test_reversed_thrust'):
        old=m2.reference_metrics
        def ref(*a,**k):
            metrics,states=old(*a,**k);metrics['thrust_direction_vs_reference_max']=0.
            return metrics,states
        monkeypatch.setattr(m2,'reference_metrics',ref)
    if n.startswith('test_transition_payloads'):
        monkeypatch.setattr(m2,'transition_checks',lambda *a:({},[]))
        old=m2.reference_metrics
        def ref(*a,**k):
            metrics,states=old(*a,**k)
            metrics['ignition_position_error_max_m']=metrics['ignition_velocity_error_max_mps']=0.
            return metrics,states
        monkeypatch.setattr(m2,'reference_metrics',ref)
    if n.startswith(('test_plans_and_timing','test_depletion_cutoff_shift')):
        monkeypatch.setattr(m2,'check_receipt_details',lambda *a:({},[]))
        monkeypatch.setattr(m2,'check_start_identity',lambda *a:[])
    if n.startswith(('test_start_provenance','test_rejection_provenance')):
        monkeypatch.setattr(m2,'check_start_identity',lambda *a:[])
        monkeypatch.setattr(m2,'check_receipt_details',lambda *a:({},[]))
    if n.startswith('test_orbit_and_altitude'):
        monkeypatch.setattr(m2,'orbit_checks',lambda *a:({},[]))
    if n.startswith('test_missing_threshold_group'):
        import importlib.util
        original=importlib.util.spec_from_file_location
        def spec(*a,**k):
            s=original(*a,**k)
            if a[0]=='m2_proof':
                execute=s.loader.exec_module
                def load(module):
                    execute(module);module._ungated=lambda *a:[]
                s.loader.exec_module=load
            return s
        monkeypatch.setattr(importlib.util,'spec_from_file_location',spec)
