#!/usr/bin/env python3
"""One canonical native graph; three encodings of exactly the same actions."""
import argparse,json,shutil,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def write(root,path,text):
    p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def dump(root,path,data):write(root,path,json.dumps(data,sort_keys=True,indent=2)+'\n')
def render(root,actions,jobs,default):
    make=['MAKEFLAGS += --no-builtin-rules --no-builtin-variables','.SUFFIXES:', '.DELETE_ON_ERROR:','.PHONY: all','all: '+default]
    ninja=['ninja_required_version = 1.10','rule compile','  command = $action_command','  depfile = $out.d','  deps = gcc','rule action','  command = $action_command']
    tracked=[]
    for idx,a in enumerate(actions):
        cmd=' '.join(['./tools/action-log',a['id'],*a['argv']]);deps=a['inputs']
        make.extend([a['output']+': '+' '.join(deps),'\t'+cmd])
        rule='compile' if a['output'].endswith('.o') else 'action'
        ninja.extend([f'build {a["output"]}: {rule} '+' '.join(deps),f'  action_command = {cmd}'])
        tracked.append({'name':a['id'],'title':a['id'],'content-ext':'.json','output-ext':Path(a['output']).suffix,'build':a['hook'],'depends':a['prerequisites']})
    make.append('-include '+' '.join(a['output']+'.d' for a in actions if a['output'].endswith('.o')))
    ninja.append('default '+default)
    write(root,'Makefile','\n'.join(make)+'\n');write(root,'build.ninja','\n'.join(ninja)+'\n')
    dump(root,'.nift/config.json',{'config':{'content-dir':'recipes/','content-ext':'.json','output-dir':'build/','output-ext':'.o','default-template':'','build-threads':jobs,'incremental-mode':'modified','minify-exts':[]}})
    dump(root,'.nift/tracked.json',{'tracked':tracked})

def generate(root,size,profile,jobs):
    root.mkdir(parents=True,exist_ok=True)
    for d in ['tools','build/gen','build/obj','build/lib','build/bin']: (root/d).mkdir(parents=True,exist_ok=True)
    subprocess.run(['cc','-O2',str(ROOT/'scripts/action-log.c'),'-o',str(root/'tools/action-log')],check=True)
    shutil.copy2(ROOT/'scripts/generate-input.py',root/'tools/generate-input.py')
    dump(root,'inputs/spec.json',{'value':7})
    write(root,'inputs/include/global.h','#pragma once\n#define GLOBAL_VALUE 3\n')
    for m in range(10):write(root,f'inputs/include/module{m:02}.h',f'#pragma once\n#include "global.h"\n#define MODULE_VALUE {m+1}\n')
    actions=[]
    def add(name,ext,inputs,prereqs,argv):
        out=f'build/{name}{ext}';recipe=f'recipes/{name}.json';hook=f'hooks/{name}.f'
        a={'id':name,'output':out,'inputs':inputs,'prerequisites':prereqs,'argv':argv,'recipe':recipe,'hook':hook};actions.append(a)
        dump(root,recipe,{'argv':argv})
        dump(root,f'recipes/{name}.deps.json',{'dependencies':inputs})
        args=', '.join(json.dumps(v) for v in ['./tools/action-log',name,*argv])
        write(root,hook,f'result := cmd({args}).cwd(getenv("NIFT_HOOK_ROOT")).run()\nif(!result.launched || result.exit_code != 0) {{ throw error("Action failed: " + result.stderr, "user.build.action_failed") }}\n')
        return name
    add('gen/config','.h',['inputs/spec.json','tools/generate-input.py'],[],['python3','tools/generate-input.py','header','build/gen/config.h'])
    add('gen/generated','.cpp',['inputs/spec.json','build/gen/config.h','tools/generate-input.py'],['gen/config'],['python3','tools/generate-input.py','source','build/gen/generated.cpp'])
    flags=['g++','-std=c++17','-O2','-g0','-fno-ident','-MMD','-MP','-Iinputs/include','-Ibuild/gen']
    modules=[[] for _ in range(10)]
    for i in range(size):
        m=i%10;src=f'inputs/src/u{i:06}.cpp';private=f'inputs/include/private{i:06}.h'
        write(root,private,f'#pragma once\n#define PRIVATE_VALUE {i+1}\n')
        heavy='\n'.join(f'template<int N> struct T{t} {{ static constexpr unsigned value=T{t}<N-1>::value+N; }}; template<> struct T{t}<0> {{static constexpr unsigned value=0;}};' for t in range(16)) if profile=='heavy' else ''
        write(root,src,f'#include "private{i:06}.h"\n#include "module{m:02}.h"\n#include "config.h"\n{heavy}\n{''.join(f'static_assert(T{t}<128>::value==8256);' for t in range(16)) if profile=='heavy' else ''}\nint value_{i}(){{return PRIVATE_VALUE+MODULE_VALUE+GLOBAL_VALUE+GENERATED_VALUE;}}\n')
        name=f'obj/u{i:06}';out=f'build/{name}.o'
        add(name,'.o',[src,private,f'inputs/include/module{m:02}.h','inputs/include/global.h','build/gen/config.h'],['gen/config'],flags+['-MF',out+'.d','-c',src,'-o',out]);modules[m].append(name)
    write(root,'inputs/src/main.cpp','#include <cstdio>\n'+''.join(f'int value_{i}();\n' for i in range(size))+'int generated_value();\nint main(){long long sum=generated_value();\n'+''.join(f'sum+=value_{i}();\n' for i in range(size))+'std::printf("%lld\\n",sum);}\n')
    add('obj/generated','.o',['build/gen/generated.cpp','build/gen/config.h'],['gen/generated','gen/config'],flags+['-MF','build/obj/generated.o.d','-c','build/gen/generated.cpp','-o','build/obj/generated.o'])
    add('obj/main','.o',['inputs/src/main.cpp'],[],flags+['-MF','build/obj/main.o.d','-c','inputs/src/main.cpp','-o','build/obj/main.o'])
    for m,names in enumerate(modules):
        out=f'build/lib/module{m:02}.a';rsp=f'response/module{m:02}.rsp';write(root,rsp,'\n'.join(f'build/{n}.o' for n in names)+'\n')
        add(f'lib/module{m:02}','.a',[rsp,*[f'build/{n}.o' for n in names]],names,['ar','rcsD',out,'@'+rsp])
    libs=[f'lib/module{m:02}' for m in range(10)];write(root,'response/link.rsp','\n'.join(['build/obj/main.o','build/obj/generated.o',*[f'build/{n}.a' for n in libs]])+'\n')
    add('bin/app','.exe',['response/link.rsp','build/obj/main.o','build/obj/generated.o',*[f'build/{n}.a' for n in libs]],['obj/main','obj/generated',*libs],['g++','@response/link.rsp','-o','build/bin/app.exe'])
    render(root,actions,jobs,'build/bin/app.exe')
    dump(root,'manifest.json',{'schema':1,'size':size,'profile':profile,'jobs':jobs,'expected_stdout':str(sum(i+1+(i%10)+1+3+7 for i in range(size))+7)+'\n','actions':actions})
    return len(actions)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--size',type=int,default=100);p.add_argument('--profile',choices=['light','heavy'],default='light');p.add_argument('--jobs',type=int,default=4);a=p.parse_args();print('Generated actions:',generate(a.output,a.size,a.profile,a.jobs))
