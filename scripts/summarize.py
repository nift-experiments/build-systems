#!/usr/bin/env python3
"""Recompute summaries from every measured observation; never discard outliers."""
import argparse,json,math,statistics
from collections import defaultdict
from pathlib import Path
def percentile(values,q):
 values=sorted(values);pos=(len(values)-1)*q;lo=int(pos);hi=math.ceil(pos);return values[lo]+(values[hi]-values[lo])*(pos-lo)
def summarize(root):
 identity=json.loads((root/'identity.json').read_text());rows=[json.loads(x) for x in (root/'observations.jsonl').read_text().splitlines()];groups=defaultdict(list);warmups=defaultdict(int)
 for r in rows:
  assert r['passed'],f'Failed observation {r["index"]}'
  for n in ['wall_ms','cpu_ms','peak_rss_kib']:assert math.isfinite(r['metrics'][n]) and r['metrics'][n]>=0
  key=tuple(r[k] for k in ['kind','size','profile','jobs','scenario','system'])
  if r['warmup']:warmups[key]+=1
  else:groups[key].append(r)
 output=[]
 for key,obs in sorted(groups.items()):
  record=dict(zip(['kind','size','profile','jobs','scenario','system'],key));record.update(samples=len(obs),warmups=warmups[key],all_actions_correct=True)
  for metric in ['wall_ms','cpu_ms','peak_rss_kib']:
   values=[o['metrics'][metric] for o in obs];stats={'median':statistics.median(values),'min':min(values),'max':max(values)}
   if len(values)>=20:stats['p95']=percentile(values,.95)
   if len(values)>=100:stats['p99']=percentile(values,.99)
   record[metric]=stats
  output.append(record)
 result={'identity':identity,'cohorts':output,'observations':len(rows),'outliers_removed':0,'percentile_method':'linear interpolation at (n-1)*q; p95 for n>=20, p99 for n>=100'}
 (root/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(f'Recomputed {len(output)} cells from {len(rows)} retained observations')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();summarize(a.directory)
