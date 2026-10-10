#!/usr/bin/env python3
"""Independent tiny-action graph; explicitly not a native-code benchmark."""
import argparse,json,subprocess
from pathlib import Path
from native import ROOT,write,dump,render
def generate(root,size,jobs):
 root.mkdir(parents=True,exist_ok=True);(root/'tools').mkdir(exist_ok=True);(root/'build/action').mkdir(parents=True,exist_ok=True)
 for tool in ['action-log','tiny-action']:subprocess.run(['cc','-O2',str(ROOT/f'scripts/{tool}.c'),'-o',str(root/f'tools/{tool}')],check=True)
 actions=[]
 for i in range(size):
  name=f'action/a{i:06}';src=f'inputs/a{i:06}.txt';out=f'build/{name}.out';argv=['./tools/tiny-action',src,out];write(root,src,f'deterministic-{i}\n')
  a={'id':name,'output':out,'inputs':[src],'prerequisites':[],'argv':argv,'recipe':f'recipes/{name}.json','hook':f'hooks/{name}.f'};actions.append(a)
  dump(root,a['recipe'],{'argv':argv});dump(root,f'recipes/{name}.deps.json',{'dependencies':[src]})
  args=', '.join(json.dumps(x) for x in ['./tools/action-log',name,*argv]);write(root,a['hook'],f'r := cmd({args}).cwd(getenv("NIFT_HOOK_ROOT")).run()\nif(!r.launched || r.exit_code != 0) {{throw error("Tiny action failed", "user.build.tiny_failed")}}\n')
 render(root,actions,jobs,' '.join(a['output'] for a in actions));dump(root,'manifest.json',{'schema':1,'kind':'tiny-action-microbenchmark','size':size,'jobs':jobs,'actions':actions});return len(actions)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--size',type=int,default=100);p.add_argument('--jobs',type=int,default=4);a=p.parse_args();print('Generated tiny actions:',generate(a.output,a.size,a.jobs))
