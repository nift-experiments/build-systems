#!/usr/bin/env python3
"""Verify action/hash evidence and exact planned sample counts before publication."""
import argparse,json,hashlib
from collections import Counter
from pathlib import Path
def validate(root,official=False):
 identity=json.loads((root/'identity.json').read_text());rows=[json.loads(x) for x in (root/'observations.jsonl').read_text().splitlines()]
 if official:assert not identity['suite_dirty'],'Official suite had modified tracked files'
 counts=Counter();comparisons={}
 for p in (root/'manifests').glob('*.json'):
  manifest=json.loads(p.read_text());assert hashlib.sha256(p.read_bytes()).hexdigest()==p.stem
  for ref in manifest['definition_refs'].values():
   definition=root/ref['path'];assert definition.resolve().is_relative_to(root.resolve());assert hashlib.sha256(definition.read_bytes()).hexdigest()==ref['sha256']
 for index,r in enumerate(rows):
  assert r['index']==index and r['passed'];assert r['metrics']['exit_code']==0
  fields=[('action_trace','action_trace_sha256'),('output_hashes','output_hashes_sha256')]
  if isinstance(r['expected_actions'],str):fields.append(('expected_actions','expected_actions_sha256'))
  for field,digest in fields:
   p=root/r[field];assert p.is_file() and p.resolve().is_relative_to(root.resolve());assert hashlib.sha256(p.read_bytes()).hexdigest()==r[digest]
  actions=json.loads((root/r['action_trace']).read_text());assert len(actions)==len(set(actions));assert sorted(actions)==sorted(json.loads((root/r['expected_actions']).read_text()) if isinstance(r['expected_actions'],str) else r['expected_actions'])
  hashes=json.loads((root/r['output_hashes']).read_text());group=tuple(r[k] for k in ['kind','size','profile','jobs','scenario'])
  if group in comparisons:assert comparisons[group]==hashes,'Output parity mismatch'
  else:comparisons[group]=hashes
  if 'preconditions' in r:assert r['preconditions']['content_mutations_verified'] and r['preconditions']['timestamp_preconditions_verified']
  key=tuple(r[k] for k in ['kind','size','profile','jobs','scenario','system'])+(r['warmup'],);counts[key]+=1
 for graph in identity['plan']['graphs']:
  for case in graph['cases']:
   for system in ['make','ninja','nift']:
    key=(graph['kind'],graph['size'],graph.get('profile','light'),graph['jobs'],case['name'],system)
    assert counts[key+(True,)]==case['warmups'];assert counts[key+(False,)]==case['samples']
 if any(r['scenario']=='target' for r in rows) and (root/'target-followup').exists():
  followups=[json.loads(p.read_text()) for p in (root/'target-followup').glob('*.json')]
  assert len(followups)==sum(r['scenario']=='target' for r in rows)
  for f in followups:assert f['actions']==['bin/app'] and f['final_stdout_verified']
 expected=sum(3*sum(c['samples']+c['warmups'] for c in g['cases']) for g in identity['plan']['graphs']);assert len(rows)==expected
 print(f'PASS: {len(rows)} observations, sample policy, exact action sets and content-addressed output hashes')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--official',action='store_true');a=p.parse_args();validate(a.directory,a.official)
