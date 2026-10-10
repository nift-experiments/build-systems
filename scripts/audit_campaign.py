#!/usr/bin/env python3
"""Independent read-only order/distribution audit of retained observations."""
import argparse,json,math,statistics
from collections import defaultdict
from pathlib import Path
from validate_campaign import validate

def audit(root,official=True):
 validate(root,official=official)
 identity=json.loads((root/'identity.json').read_text());summary=json.loads((root/'summary.json').read_text());rows=[json.loads(line) for line in (root/'observations.jsonl').read_text().splitlines()]
 expected=[]
 for gi,g in enumerate(identity['plan']['graphs']):
  cases=g['cases'];offset=gi%len(cases);cases=cases[offset:]+cases[:offset]
  for ci,c in enumerate(cases):
   for ri in range(c['warmups']+c['samples']):
    order=['make','ninja','nift'];offset=(gi+ci+ri)%3;order=order[offset:]+order[:offset]
    for system in order:expected.append((g['kind'],g['size'],g.get('profile','light'),g['jobs'],c['name'],system,ri,ri<c['warmups']))
 fields=['kind','size','profile','jobs','scenario','system','round','warmup'];assert len(expected)==len(rows)
 for row,wanted in zip(rows,expected):assert tuple(row[k] for k in fields)==wanted,(row['index'],'rotation/order mismatch')
 groups=defaultdict(list)
 for row in rows:
  if not row['warmup']:groups[tuple(row[k] for k in fields[:6])].append(row)
 variance=[]
 for cell in summary['cohorts']:
  obs=groups[tuple(cell[k] for k in fields[:6])];assert len(obs)==cell['samples']
  for metric in ['wall_ms','cpu_ms','peak_rss_kib']:
   values=[o['metrics'][metric] for o in obs];actual=cell[metric]
   wanted={'median':statistics.median(values),'min':min(values),'max':max(values)}
   if len(values)>=20:wanted['p95']=statistics.quantiles(values,n=100,method='inclusive')[94]
   if len(values)>=100:wanted['p99']=statistics.quantiles(values,n=100,method='inclusive')[98]
   assert set(actual)==set(wanted)
   for key,value in wanted.items():assert math.isclose(actual[key],value,rel_tol=1e-12,abs_tol=1e-9),(metric,key,actual[key],value)
  if cell['samples']<10:
   spread=(cell['wall_ms']['max']-cell['wall_ms']['min'])/cell['wall_ms']['median']
   variance.append({**{k:cell[k] for k in fields[:6]},'samples':cell['samples'],'range_over_median':spread,'needs_explicit_variance_qualification':spread>.25})
 assert summary['observations']==len(rows) and summary['outliers_removed']==0
 result={'all_passed':True,'observations':len(rows),'rotation_order_verified':True,'independent_inclusive_percentiles_verified':True,'small_sample_spreads':variance}
 print(json.dumps(result,indent=2))
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--local',action='store_true');a=p.parse_args();audit(a.directory,not a.local)
