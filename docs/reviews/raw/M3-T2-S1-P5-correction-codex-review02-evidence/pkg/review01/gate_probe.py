import runpy,sys,contextlib,io,json
ns=runpy.run_path('review_scratch/pkg/s1-i48/p5_verify.py.txt'); main=ns['main'];g=main.__globals__
a=json.load(open('review_scratch/reviewer/supplied.json'))
g['p5a']=lambda *args:a['P-5A']
b=a['P-5BC']
for row in b['lists']:
 if row['covered_by_sibling_entry']:
  row['covered_by_sibling_entry']['matches']=False
  row['sibling_manifest_p5a']=False
 row['commits_touching']=2
# Invalid coverage and history facts must not produce success for corrected P-5.
g['p5bc']=lambda *args:b
with contextlib.redirect_stdout(io.StringIO()):code=main(['probe','.','ee602c5'])
print('Synthetic failed sibling coverage, failed sibling PASS and two touching commits: exit',code)
print('resolve sibling escape:',g['resolve']('docs/evidence','../outside'))
