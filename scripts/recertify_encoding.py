#!/usr/bin/env python3
"""Recheck new graph encoding against certified, unchanged native baselines."""
import json,shutil
from pathlib import Path
from certify import ROOT,generate,generate_tiny,run,mutate,dependency_audit

def recertify(kind,size,profile,jobs):
 old=ROOT/'work'/f'certify-{kind}-{size}-{profile}-j{jobs}'
 if not old.is_dir() and kind=='native':old=ROOT/'work'/f'certify-{size}-{profile}-j{jobs}'
 assert old.is_dir(),old
 work=ROOT/'work'/f'recertify-{kind}-{size}-{profile}-j{jobs}';shutil.rmtree(work,ignore_errors=True);work.mkdir()
 canonical=work/'canonical';generate_tiny(canonical,size,jobs) if kind=='tiny' else generate(canonical,size,profile,jobs)
 manifest=json.loads((canonical/'manifest.json').read_text());assert manifest==json.loads((old/'canonical/manifest.json').read_text())
 result=ROOT/'results'/f'local-cp16-reencoded-{kind}{size}-{profile}-j{jobs}';assert not result.exists();result.mkdir()
 scenarios=['noop','leaf','private','medium','target','relink','rename','deleted','unrelated'] if kind=='native' else ['noop','leaf','batch10','batch10pct']
 records=[]
 for system in ['make','ninja','nift']:
  baseline=work/(system+'-baseline');shutil.copytree(old/(system+'-baseline'),baseline)
  for p in (canonical/'inputs').rglob('*'):
   if p.is_file():assert p.read_bytes()==(baseline/p.relative_to(canonical)).read_bytes()
  for name in ['Makefile','build.ninja']:shutil.copy2(canonical/name,baseline/name)
  # The same native input/action manifest and previously certified products
  # survive a definition-only encoding change; no action may execute.
  records.append(run(baseline,system,jobs,'reencoded-baseline',[],manifest.get('expected_stdout','tiny-outputs-verified'),result))
  dependency_audit(baseline,system,manifest)
  for scenario in scenarios:
   fixture=work/(system+'-'+scenario);shutil.copytree(baseline,fixture);expected,delta,target=mutate(fixture,manifest,scenario)
   stdout='tiny-outputs-verified' if kind=='tiny' else str(int(manifest['expected_stdout'])+delta)+'\n'
   records.append(run(fixture,system,jobs,scenario,expected,stdout,result,target));shutil.rmtree(fixture)
 for scenario in ['reencoded-baseline',*scenarios]:
  selected=[r for r in records if r['scenario']==scenario]
  if scenario!='deleted':assert all(r['output_sha256']==selected[0]['output_sha256'] for r in selected)
 summary={'all_passed':True,'kind':'encoding-regression-not-official','graph_kind':kind,'size':size,'profile':profile,'jobs':jobs,'records':len(records),'native_manifest_unchanged':True,'canonical_input_bytes_unchanged':True,'compiler_include_closures_match':True,'scenarios':scenarios}
 (result/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True);shutil.rmtree(work)
if __name__=='__main__':
 for args in [('native',1000,'light',2),('native',5000,'light',4),('native',10000,'light',4),('native',1000,'heavy',4),('tiny',1000,'light',2),('tiny',10000,'light',4)]:
  result=ROOT/'results'/f'local-cp16-reencoded-{args[0]}{args[1]}-{args[2]}-j{args[3]}'
  if (result/'summary.json').exists():
   assert json.loads((result/'summary.json').read_text())['all_passed'];print('Preserved existing completed gate:',result.name)
  else:recertify(*args)
