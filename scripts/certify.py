#!/usr/bin/env python3
"""Local correctness gate; failed records are saved and never used as wins."""
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'generators'))
from native import generate
from tiny import generate as generate_tiny
ROOT=Path(__file__).resolve().parents[1]
SCENARIOS=['noop','leaf','private','medium','global','generated','batch10','batch10pct','relink','target','full','unrelated','rename','deleted']

def command(system,jobs,target=None):
    if system=='nift':return [os.environ.get('NIFT','nift'),'build',*([target] if target else [])]
    tool='make' if system=='make' else os.environ.get('NINJA','ninja')
    return [tool,f'-j{jobs}',*(['build/'+target+'.a'] if target else [])]
def closure(manifest,dirty):
    expected=set(dirty)
    while True:
        more={a['id'] for a in manifest['actions'] if set(a['prerequisites'])&expected}
        if more<=expected:return sorted(expected)
        expected|=more
def mutate(root,manifest,scenario):
    size=manifest['size'];dirty=[];delta=0;target=None
    if manifest.get('kind')=='tiny-action-microbenchmark':
        if scenario in ['leaf','batch10','batch10pct']:
            count=1 if scenario=='leaf' else (10 if scenario=='batch10' else max(1,size//10))
            for i in range(count):
                p=root/f'inputs/a{i:06}.txt';p.write_text(p.read_text()+'changed\n');dirty.append(f'action/a{i:06}')
        elif scenario=='full':
            shutil.rmtree(root/'build');(root/'build/action').mkdir(parents=True);dirty=[a['id'] for a in manifest['actions']]
        elif scenario!='noop':raise ValueError(scenario)
        return sorted(dirty),0,None
    def replace(path,old,new):
        p=root/path;s=p.read_text();assert old in s;p.write_text(s.replace(old,new))
    if scenario in ['leaf','batch10','batch10pct','target']:
        count=1 if scenario in ['leaf','target'] else (10 if scenario=='batch10' else max(1,size//10))
        for i in range(count):replace(f'inputs/src/u{i:06}.cpp','PRIVATE_VALUE+','1+PRIVATE_VALUE+');dirty.append(f'obj/u{i:06}')
        delta=count
        if scenario=='target':target='lib/module00'
    elif scenario=='private':replace('inputs/include/private000000.h','PRIVATE_VALUE 1','PRIVATE_VALUE 2');dirty=['obj/u000000'];delta=1
    elif scenario=='medium':replace('inputs/include/module00.h','MODULE_VALUE 1','MODULE_VALUE 2');dirty=[f'obj/u{i:06}' for i in range(0,size,10)];delta=len(dirty)
    elif scenario=='global':replace('inputs/include/global.h','GLOBAL_VALUE 3','GLOBAL_VALUE 4');dirty=[f'obj/u{i:06}' for i in range(size)];delta=size
    elif scenario=='generated':replace('inputs/spec.json','"value": 7','"value": 8');dirty=['gen/config','gen/generated'];delta=size+1
    elif scenario=='relink':(root/'build/bin/app.exe').unlink();dirty=['bin/app']
    elif scenario=='full':
        shutil.rmtree(root/'build')
        for d in ['gen','obj','lib','bin']:(root/'build'/d).mkdir(parents=True)
        dirty=[a['id'] for a in manifest['actions']]
    elif scenario=='unrelated':(root/'inputs/unrelated.txt').write_text('Not a dependency.\n')
    elif scenario=='rename':
        old='inputs/src/u000000.cpp';new='inputs/src/renamed000000.cpp';(root/old).rename(root/new)
        for path in ['Makefile','build.ninja','hooks/obj/u000000.f','recipes/obj/u000000.json','recipes/obj/u000000.deps.json']:
            p=root/path;p.write_text(p.read_text().replace(old,new))
        (root/'build/obj/u000000.o').unlink()
        (root/'build/obj/u000000.o.d').unlink(missing_ok=True)
        dirty=['obj/u000000']
    elif scenario=='deleted':(root/'inputs/src/u000000.cpp').unlink()
    expected=closure(manifest,dirty)
    if target:expected=[n for n in expected if n in ['obj/u000000',target]]
    return expected,delta,target
def dependency_audit(root,system,manifest):
    observed={}
    if system=='ninja':
        text=subprocess.check_output([os.environ.get('NINJA','ninja'),'-t','deps'],cwd=root,text=True);current=None
        for line in text.splitlines():
            if line and not line.startswith(' '):current=line.split(': #deps',1)[0];observed[current]=[]
            elif line.startswith('    ') and current:observed[current].append(line.strip())
    else:
        for a in manifest['actions']:
            if a['output'].endswith('.o'):
                text=(root/(a['output']+'.d')).read_text().replace('\\\n',' ');observed[a['output']]=text.split('\n')[0].split(':',1)[1].split()
    for a in manifest['actions']:
        if a['output'].endswith('.o'):assert sorted(observed[a['output']])==sorted(a['inputs']),(system,a['id'],observed[a['output']],a['inputs'])
    return {'objects_checked':sum(a['output'].endswith('.o') for a in manifest['actions']),'all_include_closures_match':True}

def run(root,system,jobs,scenario,expected,stdout,record_dir,target=None):
    expected=sorted(expected)
    trace=root/'trace.log';trace.unlink(missing_ok=True);env=os.environ.copy();env.update(BUILD_TRACE=str(trace),LC_ALL='C',TZ='UTC')
    cmd=command(system,jobs,target);start=time.perf_counter_ns();proc=subprocess.run(cmd,cwd=root,env=env,capture_output=True,text=True);elapsed=(time.perf_counter_ns()-start)/1e6
    executed=trace.read_text().splitlines() if trace.exists() else []
    failure_case=scenario=='deleted'
    action_ok=len(executed)==len(set(executed)) and sorted(executed)==expected
    output=None;hashes={}
    manifest=json.loads((root/'manifest.json').read_text())
    if proc.returncode==0 and manifest.get('kind')=='tiny-action-microbenchmark':
        for a in manifest['actions']:
            h=1469598103934665603
            for byte in (root/a['inputs'][0]).read_bytes():h=((h^byte)*1099511628211)&((1<<64)-1)
            assert (root/a['output']).read_text()==f'{h:016x}\n',a['id']
        output='tiny-outputs-verified'
    elif proc.returncode==0 and not target:
        output=subprocess.check_output([str(root/'build/bin/app.exe')],cwd=root,text=True)
    if proc.returncode==0:
        for a in json.loads((root/'manifest.json').read_text())['actions']:
            p=root/a['output']
            if p.exists():hashes[a['id']]=hashlib.sha256(p.read_bytes()).hexdigest()
    ok=proc.returncode!=0 and set(executed)<= {'obj/u000000'} if failure_case else proc.returncode==0 and action_ok and (target is not None or output==stdout)
    rec={'system':system,'scenario':scenario,'command':cmd,'elapsed_ms':elapsed,'exit_code':proc.returncode,'expected_actions':expected,'executed_actions':executed,'action_ok':action_ok,'stdout_oracle':stdout,'executable_stdout':output,'output_sha256':hashes,'passed':ok}
    record_dir.mkdir(parents=True,exist_ok=True);(record_dir/(system+'-'+scenario+'.json')).write_text(json.dumps(rec,indent=2)+'\n');(record_dir/(system+'-'+scenario+'.log')).write_text(proc.stdout+proc.stderr)
    if not ok:raise RuntimeError(f'Certification failed {system}/{scenario}; see {record_dir}')
    return rec
def certify(size,profile,jobs,scenarios,result,kind='native'):
    work=ROOT/'work'/f'certify-{kind}-{size}-{profile}-j{jobs}';shutil.rmtree(work,ignore_errors=True);work.mkdir(parents=True)
    canonical=work/'canonical';(generate_tiny(canonical,size,jobs) if kind=='tiny' else generate(canonical,size,profile,jobs));manifest=json.loads((canonical/'manifest.json').read_text());records=[];baseline_hashes=None
    for system in ['make','ninja','nift']:
        baseline=work/(system+'-baseline');shutil.copytree(canonical,baseline)
        rec=run(baseline,system,jobs,'initial',[a['id'] for a in manifest['actions']],manifest.get('expected_stdout','tiny-outputs-verified'),result);records.append(rec)
        rec['dependency_audit']=dependency_audit(baseline,system,manifest)
        (result/(system+'-initial.json')).write_text(json.dumps(rec,indent=2)+'\n')
        if baseline_hashes is None:baseline_hashes=rec['output_sha256']
        else:assert baseline_hashes==rec['output_sha256'],f'Initial binary hash mismatch: {system}'
        for scenario in scenarios:
            fixture=work/(system+'-'+scenario);shutil.copytree(baseline,fixture)
            expected,delta,target=mutate(fixture,manifest,scenario)
            stdout='tiny-outputs-verified' if kind=='tiny' else str(int(manifest['expected_stdout'])+delta)+'\n'
            records.append(run(fixture,system,jobs,scenario,expected,stdout,result,target))
            shutil.rmtree(fixture)
    for scenario in scenarios:
        rows=[r for r in records if r['scenario']==scenario]
        if scenario!='deleted':assert all(r['output_sha256']==rows[0]['output_sha256'] for r in rows),f'Binary mismatch: {scenario}'
    summary={'size':size,'profile':profile,'jobs':jobs,'kind':'local-certification-not-official','all_passed':True,'records':len(records),'scenario_names':scenarios}
    (result/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=['native','tiny'],default='native');p.add_argument('--size',type=int,default=100);p.add_argument('--profile',choices=['light','heavy'],default='light');p.add_argument('--jobs',type=int,default=4);p.add_argument('--scenarios',nargs='+',default=SCENARIOS);p.add_argument('--results',type=Path,required=True);a=p.parse_args();certify(a.size,a.profile,a.jobs,a.scenarios,a.results,a.kind)
