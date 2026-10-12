# ruff: noqa
exec(open('review_scratch/oracle_data.py').read().split('with patch(\'scipy.integrate.solve_ivp\'')[0])
from pathlib import Path
import shutil
from tars.validation import gmat_m2 as g
name='m2_prograde_burn'
for key in ('script','report','console','metadata','manifest'):
    dest=Path('review_scratch')/('artifact-'+key)
    shutil.copytree(g.reference_dir(),dest,dirs_exist_ok=True)
    target=g.approved_manifest_path(dest) if key=='manifest' else g.reference_files(name,dest)[key]
    if key in ('manifest','metadata'):
        data=json.loads(target.read_text())
        if key=='manifest':data['references'][name]['report_sha256']='0'*64
        else:data['gmat_console_sha256']='0'*64
        target.write_text(json.dumps(data))
    else:
        target.write_text(target.read_text()+'\nTAMPERED\n')
    try:
        reasons, check=cli._evaluate(name,base=dest)
        accepted=not reasons and check is not None and check.passed
        print(key,'accepted',accepted,'reasons',reasons,flush=True)
        assert not accepted
    except (ValueError,KeyError) as e:
        print(key,'rejected exception',str(e),flush=True)
