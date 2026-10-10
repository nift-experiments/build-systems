#!/usr/bin/env python3
"""Rotated, same-host observations with setup outside the C timing boundary."""
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
from certify import ROOT,command,mutate,closure,dependency_audit
from native import generate
from tiny import generate as generate_tiny

def sha(data):return hashlib.sha256(data).hexdigest()
def store(root,category,data):
    raw=json.dumps(data,sort_keys=True,separators=(',',':')).encode();digest=sha(raw);path=root/category/(digest+'.json');path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():path.write_bytes(raw)
    return str(path.relative_to(root)),digest
def verify(root,manifest,target,delta):
    hashes={}
    for a in manifest['actions']:
        p=root/a['output'];assert p.is_file(),a['id'];hashes[a['id']]=sha(p.read_bytes())
        if manifest.get('kind')=='tiny-action-microbenchmark':
            h=1469598103934665603
            for b in (root/a['inputs'][0]).read_bytes():h=((h^b)*1099511628211)&((1<<64)-1)
            assert p.read_text()==f'{h:016x}\n',a['id']
    if manifest.get('kind')!='tiny-action-microbenchmark' and not target:
        actual=subprocess.check_output([str(root/'build/bin/app.exe')],cwd=root,text=True)
        assert actual==str(int(manifest['expected_stdout'])+delta)+'\n',actual
    return hashes
def preconditions(root,manifest,scenario,original):
    changed=[]
    for p in (root/'inputs').rglob('*'):
        if p.is_file() and str(p.relative_to(root)) in original:
            relative=str(p.relative_to(root))
            if sha(p.read_bytes())!=original[relative]:changed.append(relative)
    assert bool(changed)==(scenario in ['leaf','private','medium','global','generated','batch10','batch10pct','target'])
    for relative in changed:
        consumers=[a for a in manifest['actions'] if relative in a['inputs']]
        for a in consumers:
            output=root/a['output']
            assert not output.exists() or (root/relative).stat().st_mtime_ns>output.stat().st_mtime_ns,(relative,a['id'],'mutation must be newer than output')
    if scenario in ['full','relink']:
        assert not (root/('build/bin/app.exe' if scenario=='relink' else manifest['actions'][0]['output'])).exists()
    return {'changed_inputs':changed,'content_mutations_verified':True,'timestamp_preconditions_verified':True}

def toolchain():
    tools={}
    for name,argv in {'make':['make','--version'],'ninja':[os.environ.get('NINJA','ninja'),'--version'],'nift':[os.environ.get('NIFT','nift'),'--version'],'compiler':['g++','--version'],'linker':['ld','--version'],'archiver':['ar','--version'],'python':['python3','--version']}.items():
        executable=Path(shutil.which(argv[0])).resolve()
        tools[name]={'version':subprocess.check_output(argv,text=True).splitlines()[0],'binary_sha256':sha(executable.read_bytes())}
    return tools

def campaign(plan,out,cpus):
    assert not out.exists(),'Never overwrite a campaign directory';out.mkdir(parents=True)
    assert set(cpus)<=os.sched_getaffinity(0),'Requested CPUs are not available'
    os.sched_setaffinity(0,set(cpus))
    measure=ROOT/'work/tools/measure';measure.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['cc','-O2',str(ROOT/'scripts/measure.c'),'-o',str(measure)],check=True)
    identity={'suite_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'suite_dirty':bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True).strip()),'cpus':cpus,'plan':plan,'toolchain':toolchain(),'nift_source_sha':os.environ.get('NIFT_SOURCE_SHA'),'machine':{'kernel':subprocess.check_output(['uname','-sr'],text=True).strip(),'architecture':subprocess.check_output(['uname','-m'],text=True).strip(),'cpu':subprocess.check_output(['lscpu'],text=True),'os_release':Path('/etc/os-release').read_text(),'memory':Path('/proc/meminfo').read_text(),'filesystem':subprocess.check_output(['df','-T',str(ROOT)],text=True)},'nift_binary_sha256':sha(Path(shutil.which(os.environ.get('NIFT','nift'))).read_bytes()),'boundary':'C CLOCK_MONOTONIC before fork/exec through wait4; setup and correctness outside timing','peak_rss_scope':'Linux wait4 maximum-child high-water RSS; not summed concurrent memory'}
    (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    comparisons={};index=0
    for graph_index,graph in enumerate(plan['graphs']):
        size=graph['size'];jobs=graph['jobs'];kind=graph['kind'];profile=graph.get('profile','light')
        work=ROOT/'work'/('campaign-'+str(out.name))/f'{kind}-{size}-{profile}-j{jobs}';work.mkdir(parents=True)
        canonical=work/'canonical';generate_tiny(canonical,size,jobs) if kind=='tiny' else generate(canonical,size,profile,jobs)
        manifest=json.loads((canonical/'manifest.json').read_text())
        definition_refs={}
        for filename in ['Makefile','build.ninja','.nift/config.json','.nift/tracked.json']:
            data=(canonical/filename).read_bytes();digest=sha(data);path=out/'definitions'/(digest+Path(filename).suffix);path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():path.write_bytes(data)
            definition_refs[filename]={'path':str(path.relative_to(out)),'sha256':digest}
        manifest['definition_refs']=definition_refs
        manifest['input_sha256']={str(p.relative_to(canonical)):sha(p.read_bytes()) for p in (canonical/'inputs').rglob('*') if p.is_file()}
        store(out,'manifests',manifest)
        baseline={}
        for system in ['make','ninja','nift']:
            base=work/(system+'-baseline');shutil.copytree(canonical,base);env=os.environ.copy();env['BUILD_TRACE']=str(base/'initial.trace')
            p=subprocess.run(command(system,jobs),cwd=base,env=env,capture_output=True,text=True,timeout=3600);assert p.returncode==0,p.stderr
            assert sorted((base/'initial.trace').read_text().splitlines())==sorted(a['id'] for a in manifest['actions'])
            hashes=verify(base,manifest,None,0);dependency_audit(base,system,manifest)
            if baseline:assert hashes==verify(next(iter(baseline.values())),manifest,None,0),'Baseline output mismatch'
            baseline[system]=base
        cases=graph['cases'];offset=graph_index%len(cases);cases=cases[offset:]+cases[:offset]
        for scenario_index,case in enumerate(cases):
            scenario=case['name'];warmups=case['warmups'];samples=case['samples']
            for round_index in range(warmups+samples):
                start=(round_index+scenario_index+graph_index)%3;order=['make','ninja','nift'];order=order[start:]+order[:start]
                for system in order:
                    fixture=work/'current';shutil.rmtree(fixture,ignore_errors=True);shutil.copytree(baseline[system],fixture)
                    if scenario=='clean-rebuild':expected=[a['id'] for a in manifest['actions']];delta=0;target=None
                    else:expected,delta,target=mutate(fixture,manifest,scenario)
                    prepared=preconditions(fixture,manifest,scenario,manifest['input_sha256'])
                    trace=fixture/'measured.trace';env=os.environ.copy();env.update(BUILD_TRACE=str(trace),LC_ALL='C',TZ='UTC')
                    cmd=command(system,jobs,target)
                    if scenario=='clean-rebuild':
                        # Cleanup is included and identical; source/metadata retained.
                        cmd=['sh','-c','rm -rf build && mkdir -p build/gen build/obj build/lib build/bin build/action && exec "$@"','build-clean',*cmd]
                    resource=fixture/'resource.json';proc=subprocess.run([str(measure),str(resource),*cmd],cwd=fixture,env=env,capture_output=True,text=True,timeout=3600)
                    metrics=json.loads(resource.read_text());executed=trace.read_text().splitlines() if trace.exists() else [];action_ok=len(set(executed))==len(executed) and sorted(executed)==sorted(expected)
                    hashes=verify(fixture,manifest,target,delta) if proc.returncode==0 else {};passed=proc.returncode==0 and action_ok
                    key=(kind,size,profile,jobs,scenario)
                    if key in comparisons:passed=passed and hashes==comparisons[key]
                    else:comparisons[key]=hashes
                    hash_ref,hash_digest=store(out,'output-hashes',hashes);action_ref,action_digest=store(out,'action-traces',executed);expected_ref,expected_digest=store(out,'action-oracles',sorted(expected))
                    obs={'index':index,'kind':kind,'size':size,'profile':profile,'jobs':jobs,'scenario':scenario,'system':system,'round':round_index,'warmup':round_index<warmups,'command':cmd,'preconditions':prepared,'metrics':metrics,'expected_actions':expected_ref,'expected_actions_sha256':expected_digest,'action_trace':action_ref,'action_trace_sha256':action_digest,'output_hashes':hash_ref,'output_hashes_sha256':hash_digest,'passed':passed};index+=1
                    with (out/'observations.jsonl').open('a') as f:f.write(json.dumps(obs,separators=(',',':'))+'\n')
                    if not passed:
                        (out/f'failure-{index}.log').write_text(proc.stdout+proc.stderr);raise RuntimeError(f'Failed sample {obs}')
                    if target:
                        follow_trace=fixture/'followup.trace';env['BUILD_TRACE']=str(follow_trace)
                        follow=subprocess.run(command(system,jobs),cwd=fixture,env=env,capture_output=True,text=True,timeout=3600)
                        follow_actions=follow_trace.read_text().splitlines() if follow_trace.exists() else []
                        assert follow.returncode==0 and follow_actions==['bin/app'],(system,follow_actions,follow.stderr)
                        verify(fixture,manifest,None,delta)
                        store(out,'target-followup',{'observation':index-1,'system':system,'actions':follow_actions,'final_stdout_verified':True})
                    shutil.rmtree(fixture)
            print(f'Passed {kind}/{size}/{profile}/j{jobs}/{scenario}: {samples} measured rounds',flush=True)
        shutil.rmtree(work)
    (out/'validation.json').write_text(json.dumps({'all_passed':True,'observations':index,'all_warmups_retained':True,'outliers_removed':0},indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--cpus',required=True);a=p.parse_args();campaign(json.loads(a.plan.read_text()),a.output,[int(x) for x in a.cpus.split(',')])
