from pathlib import Path
s=Path('review_scratch/new_probes.py').read_text()
h=s.splitlines()[0]+'\n'
tail=s[s.index('def sample_extrema'):]
Path('review_scratch/more.py').write_text(h.replace('new-results.json','more-results.json')+tail)
