from pathlib import Path
import subprocess
src=Path('src/tars/validation/m2_cross_platform.py').read_text()
test=Path('tests/test_m2_cross_platform.py').read_text()
mutations={
 'missing_platform':('if missing:', 'if False:', 'test_missing_required_platform_fails_closed'),
 'rosetta':('if plat["translated"] is not False:', 'if False:', 'test_platform_identity_is_validated'),
 'inputs':('if inputs != expected_inputs:', 'if False:', 'test_mismatched_inputs_fail'),
 'norm':('np.linalg.norm(np.array(a["r"], dtype=float) - np.array(b["r"], dtype=float))','np.max(np.abs(np.array(a["r"], dtype=float) - np.array(b["r"], dtype=float)))','test_euclidean_norm_not_largest_component'),
}
for name,(old,new,selector) in mutations.items():
 path=Path('review_scratch')/f'mutant_{name}.py';path.write_text(src.replace(old,new))
 loader=f'''import sys\n_spec = importlib.util.spec_from_file_location("mutant_{name}", {str(path.resolve())!r})\nxp = importlib.util.module_from_spec(_spec)\nsys.modules[_spec.name] = xp\n_spec.loader.exec_module(xp)'''
 tp=Path('review_scratch')/f'test_mutant_{name}.py';tp.write_text(test.replace('from tars.validation import m2_cross_platform as xp',loader))
 proc=subprocess.run(['.venv/bin/python','-m','pytest','-q','-p','no:cacheprovider',str(tp),'-k',selector],capture_output=True,text=True)
 Path(f'review_scratch/mutation_{name}.log').write_text(proc.stdout+proc.stderr)
 print(name,proc.returncode,proc.stdout.splitlines()[-1:])
