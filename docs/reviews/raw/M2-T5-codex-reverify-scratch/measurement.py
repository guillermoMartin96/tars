import json
from pathlib import Path
import numpy as np
from tars.validation import m2
from tars.validation.m2_missions import MISSIONS
from tars.sim.runner import run_scenario
mission=MISSIONS[0]; scenario=mission.build();run=run_scenario(scenario)
metrics,ref=m2.reference_metrics(scenario,run.events,m2.predict_burns(scenario,mission.expected))
errors=[(float(np.linalg.norm(np.array(e.r)-ref[e.t][:3])),e.t) for e in run.events if e.type=='StateSampled']
print(json.dumps({'max_sample_position':max(errors),'final_position':metrics['final_position_error_m']}))
