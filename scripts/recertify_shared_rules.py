#!/usr/bin/env python3
"""Ninja shared-rule representation regression; native actions stay identical."""
import json,shutil
from certify import ROOT,generate,generate_tiny,run,mutate,dependency_audit
for kind,size,profile,jobs in [('native',1000,'light',2),('native',5000,'light',4),('native',10000,'light',4),('native',1000,'heavy',4),('tiny',10000,'light',4)]:
 old=ROOT/'work'/f'certify-{kind}-{size}-{profile}-j{jobs}'
 if not old.exists():old=ROOT/'work'/f'certify-{size}-{profile}-j{jobs}'
 work=ROOT/'work'/f'shared-rules-{kind}-{size}-{profile}-j{jobs}';assert not work.exists();work.mkdir()
 canonical=work/'canonical';generate_tiny(canonical,size,jobs) if kind=='tiny' else generate(canonical,size,profile,jobs)
 manifest=json.loads((canonical/'manifest.json').read_text());assert manifest==json.loads((old/'canonical/manifest.json').read_text())
 baseline=work/'baseline';shutil.copytree(old/'ninja-baseline',baseline);shutil.copy2(canonical/'build.ninja',baseline/'build.ninja')
 result=ROOT/'results'/f'local-cp17-shared-ninja-{kind}{size}-{profile}-j{jobs}';assert not result.exists();result.mkdir()
 assert (canonical/'build.ninja').read_text().count('\nrule ')==2
 records=[run(baseline,'ninja',jobs,'reencoded-baseline',[],manifest.get('expected_stdout','tiny-outputs-verified'),result)];dependency_audit(baseline,'ninja',manifest)
 for scenario in (['leaf','private','medium','target','relink','rename','deleted','unrelated'] if kind=='native' else ['leaf','batch10','batch10pct']):
  fixture=work/scenario;shutil.copytree(baseline,fixture);expected,delta,target=mutate(fixture,manifest,scenario)
  records.append(run(fixture,'ninja',jobs,scenario,expected,'tiny-outputs-verified' if kind=='tiny' else str(int(manifest['expected_stdout'])+delta)+'\n',result,target));shutil.rmtree(fixture)
 summary={'all_passed':True,'kind':'shared-rule-encoding-regression-not-official','graph_kind':kind,'size':size,'profile':profile,'jobs':jobs,'records':len(records),'shared_rules':2,'native_manifest_unchanged':True,'compiler_include_closures_match':True}
 (result/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True);shutil.rmtree(work)
