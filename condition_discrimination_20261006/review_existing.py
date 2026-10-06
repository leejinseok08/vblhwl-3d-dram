from pathlib import Path
import sys,csv,json
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r/'snapshot'))
from gt_tran import load,at
import make_runs as mr
out=[]
base=Path('/home/e20241515/vblhwl_3d_dram/runs')
for c in range(1,6):
 for flag in ['k','i']:
  rid=f'CF{flag}_c{c}'
  run=next(x for x in mr.RUNS if x['id']==rid)
  p,_,info=mr.build(run)
  files=list((base/rid).glob('*_dev.plt'))
  if not files: continue
  d=load(files[0]); t=d['time']; ta=info['tS']-1e-12
  if max(t)<ta: continue
  for key in d:
   if 'ElectrostaticPotential' not in key and 'hQuasiFermiPotential' not in key: continue
   for refname,ref in [('initial_DC',0),('write_end',info['tS']-p['tHold']*1e-9),('at_1ns',1e-9)]:
    out.append(dict(run=rid,II=p['II'],variable=key,reference=refname,t0_ns=ref*1e9,tA_ns=ta*1e9,
                    value0_V=at(t,d[key],ref),valueA_V=at(t,d[key],ta),delta_mV=(at(t,d[key],ta)-at(t,d[key],ref))*1000,
                    raw_last_ns=max(t)*1e9))
if out:
 with (r/'existing_potential_definitions.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 for x in out:
  if x['reference']=='write_end' and '(.125' in x['variable'].replace(' ',''):
   print(x)
 print('Saved',len(out),'consistent potential differences')
