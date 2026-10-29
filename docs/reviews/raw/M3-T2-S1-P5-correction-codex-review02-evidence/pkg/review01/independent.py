import subprocess,hashlib,pathlib,posixpath,json,re,collections
P=pathlib.Path('review_scratch/reviewer'); B='ee602c5bfe3176d8f8b62dfa3d59af5dfe52b8fd'
def git(*a): return subprocess.check_output(['git',*a])
def sha(b): return hashlib.sha256(b).hexdigest()
paths=git('ls-tree','-r','--name-only',B).decode().splitlines()
# Batch independently load immutable BASE blobs.
r=git('ls-tree','-r',B).decode().splitlines(); ids={x.split('\t')[1]:x.split()[2] for x in r if x.split()[1]=='blob'}
proc=subprocess.run(['git','cat-file','--batch'],input=('\n'.join(ids.values())+'\n').encode(),stdout=subprocess.PIPE,check=True); data={}; off=0
for p in ids:
 end=proc.stdout.index(b'\n',off); size=int(proc.stdout[off:end].split()[-1]);data[p]=proc.stdout[end+1:end+1+size];off=end+size+2
hashes={p:sha(v) for p,v in data.items()}; idx=collections.defaultdict(list)
for p,h in hashes.items():idx[h].append(p)
def entries(p):
 return [(l[:64],l[66:]) for l in data[p].decode().splitlines()]
ms=[p for p in data if pathlib.PurePosixPath(p).name=='SHA256SUMS']; lists=[p for p in data if p.endswith('SHA256SUMS') and p not in ms]
out={'head':git('rev-parse','HEAD').decode().strip(),'manifests':[],'lists':[],'other_lists':[p for p in paths if re.search(r'sha256|manifest',p,re.I) and p not in ms+lists]}
cover=collections.defaultdict(list)
for m in ms:
 base=posixpath.dirname(m); errors=[]; odd=[]
 for h,n in entries(m):
  target=posixpath.normpath(base+'/'+n);cover[target].append((m,h))
  if not target.startswith(base+'/'):errors.append(('escape',n))
  if hashes.get(target)!=h:errors.append(('digest',n))
  if n.startswith('./') or '/' in n:odd.append(n)
 out['manifests'].append({'path':m,'entries':len(entries(m)),'errors':errors,'non_simple_paths':odd})
for m in lists:
 base=posixpath.dirname(m); counts=collections.Counter(); rows=[]
 for h,n in entries(m):
  clean=posixpath.normpath(n.removeprefix('review_scratch/')); candidates=[base+'/'+clean,base+'/'+clean+'.txt']; local=[p for p in idx[h] if p.startswith(base+'/')]
  if h==sha(b'') and any(p in idx[h] for p in candidates):c='empty'
  elif any(p in idx[h] for p in candidates):c='same'
  elif local:c='renamed'
  elif idx[h]:c='elsewhere'
  elif n in ('correction.diff','full.diff','termination_before.py') and 'review09' in m:
   args={'correction.diff':['diff','115e747','f04f995'],'full.diff':['diff','86df2c3','f04f995'],'termination_before.py':['show','115e747:docs/science/experiments/m3-t0/t0_termination.py']}[n]
   assert sha(git(*args))==h;c='regenerated'
  else:c='unavailable'
  counts[c]+=1;rows.append({'name':n,'class':c,'matches':idx[h],'digest':h,'redaction_tokens':re.findall(rb'<(?:clone|scratch|review-root|home|tmp|SNAP|SCRATCH|HOME)>',data.get(posixpath.normpath(base+'/'+n),b'')).__len__()})
 history=git('log','--follow','--format=%H',B,'--',m).decode().splitlines();intro=history[-1]
 out['lists'].append({'path':m,'counts':dict(counts),'entries':rows,'history':history,'blob':ids[m],'intro_blob':git('rev-parse',intro+':'+m).decode().strip(),'coverage':cover[m]})
text=pathlib.Path('review_scratch/pkg/M3-T2-S1-decision-I48.md').read_text();out['verbatim']={}
for number,end in [(47,'## 9.'),(48,None)]:
 start=text.index('## I-'+str(number)+' —'); s=text[start:];s=s[:s.index(end)] if end else s
 s=re.sub(r'^##', '#',s,flags=re.M).rstrip()+'\n'; orig=pathlib.Path(f'review_scratch/pkg/I-{number}.md').read_bytes()
 out['verbatim'][number]={'equal':s.encode()==orig,'hash':sha(orig)}
out['t0_diff']=git('diff','--stat','a57de3f',B,'--','docs/science/experiments/m3-t0/').decode()
(P/'independent.json').write_text(json.dumps(out,indent=2))
print('P5A',len(ms),sum(r['entries'] for r in out['manifests']),sum(bool(r['errors']) for r in out['manifests']))
print('verbatim',out['verbatim'])
for r in out['lists']:print(r['path'],r['counts'],'history',len(r['history']),'identity',r['blob']==r['intro_blob'],'coverage',len(r['coverage']))
print('other',out['other_lists'])
