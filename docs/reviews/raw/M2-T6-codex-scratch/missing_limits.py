import argparse,importlib.util,json
from pathlib import Path
from tars.validation.thresholds import load_scoped_thresholds
spec=importlib.util.spec_from_file_location('cli','toolbox/scripts/gmat_m2.py'); c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
p=Path('review_scratch/missing_o9.json'); data=json.load(open('proof/thresholds/m2.json')); del data['limits']['o9_gmat']; p.write_text(json.dumps(data))
original=c.load_scoped_thresholds
c.load_scoped_thresholds=lambda **kwargs: original(p,**kwargs)
raise SystemExit(c.cmd_compare(argparse.Namespace(missions=['m2_prograde_burn'])))
