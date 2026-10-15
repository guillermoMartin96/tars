from pathlib import Path
s=Path('docs/reviews/raw/M2-T5-codex-reverify-scratch/fast.py').read_text()
a=s.index('def all_checks():'); b=s.index('\ndef execute',a)
s=s[:a]+'''def all_checks():
    thresholds=load_scoped_thresholds(missions=frozenset(m.name for m in MISSIONS))
    gates=p.Gates(thresholds)
    checks=[]
    for mission in MISSIONS: checks+=p.mission_checks(mission,gates,False)[0]
    checks+=p.boundary_checks(gates)[0]
    checks.append(gates.check('o3_free_space','o3','all',m2.free_space_metrics(m2.vehicle(MISSIONS[0].build()),p.O3_DURATION_S)))
    checks.append(p._exact('thresholds_all_consumed',thresholds.unused()))
    checks.append(p._exact('thresholds_cover_all_metrics',gates.missing))
    return checks
''' +s[b:]
# Ref key must include burns; scenario hash already does.
Path('review_scratch/fast.py').write_text(s)
for name in ['extra','targeted']:
    s=Path(f'docs/reviews/raw/M2-T5-codex-reverify-scratch/{name}.py').read_text()
    if name=='targeted': s=s[:s.index('spec_cli=')]
    Path(f'review_scratch/{name}.py').write_text(s)
